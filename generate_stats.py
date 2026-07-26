import asyncio
import json
import os
from datetime import datetime, timezone

import aiohttp

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"


async def run_query(session, query, variables=None):
    headers = {"Authorization": f"Bearer {os.environ['ACCESS_TOKEN']}"}
    async with session.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=headers,
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch_repos_and_account_info(session, username):
    query = """
    query($login: String!) {
      user(login: $login) {
        createdAt
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            forkCount
          }
        }
      }
    }
    """
    result = await run_query(session, query, {"login": username})
    return result["data"]["user"]


async def fetch_all_time_contributions(session, username, created_at):
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
          }
          totalCommitContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalIssueContributions
        }
      }
    }
    """
    start_year = int(created_at[:4])
    current_year = datetime.now(timezone.utc).year

    totals = {
        "contributions_all_time": 0,
        "commits": 0,
        "pull_requests": 0,
        "pr_reviews": 0,
        "issues": 0,
    }

    for year in range(start_year, current_year + 1):
        result = await run_query(session, query, {
            "login": username,
            "from": f"{year}-01-01T00:00:00Z",
            "to": f"{year}-12-31T23:59:59Z",
        })
        c = result["data"]["user"]["contributionsCollection"]
        totals["contributions_all_time"] += c["contributionCalendar"]["totalContributions"]
        totals["commits"] += c["totalCommitContributions"]
        totals["pull_requests"] += c["totalPullRequestContributions"]
        totals["pr_reviews"] += c["totalPullRequestReviewContributions"]
        totals["issues"] += c["totalIssueContributions"]

    return totals


async def fetch_lines_changed(session, username, repos):
    """
    Sums additions/deletions across all commits authored by `username`
    in each owned repo, using the REST commit-stats endpoint.
    Note: GitHub computes these stats asynchronously per-repo. If a repo
    hasn't been queried before, this may return 202 with empty data on
    the first run - simply re-running the workflow later will pick up
    the cached results once GitHub finishes computing them.
    """
    headers = {
        "Authorization": f"Bearer {os.environ['ACCESS_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    total_added = 0
    total_deleted = 0

    for repo in repos:
        repo_name = repo["name"]
        url = f"{REST_URL}/repos/{username}/{repo_name}/stats/contributors"

        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                print(f"{repo_name}: status {resp.status}, skipping")
                continue
            data = await resp.json()

        if not isinstance(data, list):
            continue

        for contributor in data:
            login = contributor.get("author", {}).get("login")
            if login and login.lower() == username.lower():
                for week in contributor.get("weeks", []):
                    total_added += week.get("a", 0)
                    total_deleted += week.get("d", 0)

    return total_added, total_deleted

async def fetch_language_breakdown(session, username, repos):
    headers = {
        "Authorization": f"Bearer {os.environ['ACCESS_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    language_totals = {}

    for repo in repos:
        repo_name = repo["name"]
        url = f"{REST_URL}/repos/{username}/{repo_name}/languages"
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                print(f"{repo_name}: languages status {resp.status}, skipping")
                continue
            data = await resp.json()

        for lang, bytes_count in data.items():
            language_totals[lang] = language_totals.get(lang, 0) + bytes_count

    total_bytes = sum(language_totals.values())
    if total_bytes == 0:
        return {}

    breakdown = {
        lang: round((count / total_bytes) * 100, 2)
        for lang, count in language_totals.items()
    }
    return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

async def fetch_stats(session, username):
    account_info = await fetch_repos_and_account_info(session, username)
    repos = account_info["repositories"]["nodes"]

    stats = {
        "repos": account_info["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "forks": sum(r["forkCount"] for r in repos),
    }

    contrib_totals = await fetch_all_time_contributions(
        session, username, account_info["createdAt"]
    )
    stats.update(contrib_totals)

    lines_added, lines_deleted = await fetch_lines_changed(session, username, repos)
    stats["lines_added"] = lines_added
    stats["lines_deleted"] = lines_deleted
    stats["lines_changed"] = lines_added + lines_deleted

    language_repos = [r for r in repos if r["name"] != "Repository"]
    stats["languages"] = await fetch_language_breakdown(session, username, language_repos)

    return stats


async def main():
    username = os.environ["GITHUB_ACTOR"]
    async with aiohttp.ClientSession() as session:
        stats = await fetch_stats(session, username)

    os.makedirs("generated", exist_ok=True)
    with open("generated/stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(main())