from flask import Flask, render_template, request, jsonify
from textwrap import dedent

app = Flask(__name__)

PROJECTS = {
    'project1': {
        'name': 'Bug Free Engine',
        'description': 'A terminal-themed personal statement website built with xterm.js',
        'tech': 'Flask, JavaScript, xterm.js',
        'status': 'In Progress',
    },
    'project2': {
        'name': 'Data Visualization Dashboard',
        'description': 'Interactive dashboard for visualizing complex datasets in real-time',
        'tech': 'React, D3.js, Python',
        'status': 'Completed',
    },
    'project3': {
        'name': 'API Rate Limiter',
        'description': 'Distributed rate limiting service for high-traffic applications',
        'tech': 'Python, Redis, FastAPI',
        'status': 'Completed',
    },
    'project4': {
        'name': 'ML Pipeline Manager',
        'description': 'Automated machine learning pipeline orchestration tool',
        'tech': 'Python, Scikit-learn, Docker',
        'status': 'In Progress',
    },
}

terminal_state = {
    'current_dir': '/home/user',
    'logged_in': 'user',
}


def normalize_output(text):
    """Remove accidental indentation while preserving intentional line breaks."""
    if not text:
        return text
    return dedent(text).strip('\n')


def get_prompt():
    return f"{terminal_state['logged_in']}@terminal:{terminal_state['current_dir']}$ "


def execute_command(command_input):
    if not command_input.strip():
        return ""

    parts = command_input.strip().split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    commands = {
        'help': cmd_help,
        'ls': cmd_ls,
        'pwd': cmd_pwd,
        'whoami': cmd_whoami,
        'clear': cmd_clear,
        'echo': cmd_echo,
        'cat': cmd_cat,
        'projects': cmd_projects,
        'project': cmd_project,
        'about': cmd_about,
        'mkdir': cmd_mkdir,
        'sudo': cmd_sudo,
        'cd': cmd_cd,
        'uname': cmd_uname,
        'date': cmd_date,
        'skills': cmd_skills,
    }

    if cmd in commands:
        return commands[cmd](args)
    return f"Command not found: {cmd}\nType 'help' for available commands."


def cmd_help(args):
    return normalize_output(
        """Available commands:
          about        - Learn about me
          projects     - List all projects
          project [id] - View specific project details
          skills       - Display technical skills
          ls           - List directory contents
          pwd          - Print working directory
          whoami       - Display current user
          echo [text]  - Echo text
          cat [file]   - Display file contents
          cd [path]    - Change directory
          uname        - System information
          date         - Current date and time
          clear        - Clear terminal
          help         - Show this message

          (Try: mkdir, sudo for some fun!)"""
    )


def cmd_projects(args):
    output = "Available Projects:\n\n"
    for proj_id, proj in PROJECTS.items():
        output += f"[{proj_id}] {proj['name']}\n"
        output += f"  Status: {proj['status']}\n"
    output += "\nUse 'project <id>' for details (e.g., 'project project1')"
    return normalize_output(output)


def cmd_project(args):
    if not args:
        return "Usage: project <project_id>"

    proj_id = args[0]
    if proj_id in PROJECTS:
        proj = PROJECTS[proj_id]
        return normalize_output(
            f"""Project: {proj['name']}
            Description: {proj['description']}
            Technologies: {proj['tech']}
            Status: {proj['status']}"""
        )
    return f"Project '{proj_id}' not found. Use 'projects' to see available projects."


def cmd_about(args):
    return normalize_output(
        """Welcome to my terminal-themed portfolio!

        I'm a software engineer passionate about building scalable systems
        and creating innovative solutions to complex problems.

        This portfolio showcases my projects in a retro terminal interface.
        Feel free to explore using the available commands!

        Use 'projects' to see my work or 'skills' for technical expertise."""
    )


def cmd_skills(args):
    return normalize_output(
        """Technical Skills:
          Languages: Python, JavaScript, Java, SQL, Go
          Frontend: React, Vue.js, Vanilla JS, HTML/CSS
          Backend: Flask, FastAPI, Node.js, Django
          Databases: PostgreSQL, MongoDB, Redis
          Tools: Docker, Git, Kubernetes, AWS
          Other: REST APIs, gRPC, WebSockets, System Design"""
    )


def cmd_ls(args):
    if terminal_state['current_dir'] == '/home/user':
        entries = [
            'projects/',
            'documents/',
            'downloads/',
            '.gitconfig',
            'README.md',
        ]
        return "\n".join(entries)
    if terminal_state['current_dir'] == '/home/user/projects':
        return "\n".join([f"{key}/" for key in PROJECTS])
    return "."


def cmd_pwd(args):
    return terminal_state['current_dir']


def cmd_whoami(args):
    return terminal_state['logged_in']


def cmd_echo(args):
    return " ".join(args) if args else ""


def cmd_cat(args):
    if not args:
        return "Usage: cat <filename>"

    filename = args[0]
    if filename == 'README.md':
        return "# Welcome to My Portfolio\n\nThis is my personal portfolio website.\nExplore the projects and skills!"
    if filename == '.gitconfig':
        return "[user]\n    name = Developer\n    email = dev@example.com"
    return f"cat: {filename}: No such file or directory"


def cmd_cd(args):
    if not args:
        terminal_state['current_dir'] = '/home/user'
        return ""

    path = args[0]
    if path in ('/home/user', '~'):
        terminal_state['current_dir'] = '/home/user'
    elif path in ('/home/user/projects', 'projects'):
        terminal_state['current_dir'] = '/home/user/projects'
    elif path == '..':
        terminal_state['current_dir'] = '/home/user'
    else:
        return f"cd: {path}: No such file or directory"
    return ""


def cmd_uname(args):
    return "Linux portfolio-terminal 5.10.0 #1 SMP x86_64 GNU/Linux"


def cmd_date(args):
    from datetime import datetime

    return datetime.now().strftime("%a %b %d %H:%M:%S UTC %Y")


def cmd_mkdir(args):
    if not args:
        return "Usage: mkdir <directory>"
    return f"Permission denied: Cannot create '{args[0]}'. This is a read-only portfolio! 🔒"


def cmd_sudo(args):
    if not args:
        return "sudo: no command specified"
    return "sudo: nice try, but you don't have administrator privileges here! 😄"


def cmd_clear(args):
    return "[CLEAR]"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/api/execute', methods=['POST'])
def api_execute():
    data = request.json or {}
    command = data.get('command', '')

    output = execute_command(command)
    prompt = get_prompt()

    return jsonify(
        {
            'output': output,
            'prompt': prompt,
            'current_dir': terminal_state['current_dir'],
        }
    )


@app.get("/api/ip")
def api_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return jsonify({"ip": ip or "unknown"})


if __name__ == '__main__':
    app.run(debug=True)