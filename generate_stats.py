import asyncio
import json
import os

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


async def fetch_stats(session, username):
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            forkCount
          }
        }
        contributionsCollection {
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
    result = await run_query(session, query, {"login": username})
    user_data = result["data"]["user"]

    repos = user_data["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    total_forks = sum(r["forkCount"] for r in repos)

    contrib = user_data["contributionsCollection"]

    stats = {
        "repos": user_data["repositories"]["totalCount"],
        "stars": total_stars,
        "forks": total_forks,
        "contributions_last_year": contrib["contributionCalendar"]["totalContributions"],
        "commits": contrib["totalCommitContributions"],
        "pull_requests": contrib["totalPullRequestContributions"],
        "pr_reviews": contrib["totalPullRequestReviewContributions"],
        "issues": contrib["totalIssueContributions"],
    }

    lines_added, lines_deleted = await fetch_lines_changed(session, username, repos)
    stats["lines_added"] = lines_added
    stats["lines_deleted"] = lines_deleted
    stats["lines_changed"] = lines_added + lines_deleted

    return stats


async def fetch_lines_changed(session, username, repos):
    """
    Sums additions/deletions across all commits authored by `username`
    in each owned repo, using the REST commit-stats endpoint.
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
                continue
            data = await resp.json()
            if not isinstance(data, list):
                continue
            for contributor in data:
                if contributor.get("author", {}).get("login") == username:
                    for week in contributor.get("weeks", []):
                        total_added += week.get("a", 0)
                        total_deleted += week.get("d", 0)

    return total_added, total_deleted


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