# app.py
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Project data
PROJECTS = {
    'project1': {
        'name': 'Bug Free Engine',
        'description': 'A terminal-themed personal statement website built with xterm.js',
        'tech': 'Flask, JavaScript, xterm.js',
        'status': 'In Progress'
    },
    'project2': {
        'name': 'Data Visualization Dashboard',
        'description': 'Interactive dashboard for visualizing complex datasets in real-time',
        'tech': 'React, D3.js, Python',
        'status': 'Completed'
    },
    'project3': {
        'name': 'API Rate Limiter',
        'description': 'Distributed rate limiting service for high-traffic applications',
        'tech': 'Python, Redis, FastAPI',
        'status': 'Completed'
    },
    'project4': {
        'name': 'ML Pipeline Manager',
        'description': 'Automated machine learning pipeline orchestration tool',
        'tech': 'Python, Scikit-learn, Docker',
        'status': 'In Progress'
    }
}

# Terminal state
terminal_state = {
    'current_dir': '/home/user',
    'logged_in': 'user'
}

def get_prompt():
    """Generate terminal prompt"""
    return f"{terminal_state['logged_in']}@terminal:{terminal_state['current_dir']}$ "

def execute_command(command_input):
    """Execute terminal commands and return output"""
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
    else:
        return f"Command not found: {cmd}\nType 'help' for available commands."

def cmd_help(args):
    """Display help information"""
    return """Available commands:
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

def cmd_projects(args):
    """List all projects"""
    output = "Available Projects:\n\n"
    for proj_id, proj in PROJECTS.items():
        output += f"[{proj_id}] {proj['name']}\n"
        output += f"    Status: {proj['status']}\n"
    output += "\nUse 'project <id>' for details (e.g., 'project project1')"
    return output

def cmd_project(args):
    """Display specific project details"""
    if not args:
        return "Usage: project <project_id>"
    
    proj_id = args[0]
    if proj_id in PROJECTS:
        proj = PROJECTS[proj_id]
        return f"""Project: {proj['name']}
Description: {proj['description']}
Technologies: {proj['tech']}
Status: {proj['status']}"""
    else:
        return f"Project '{proj_id}' not found. Use 'projects' to see available projects."

def cmd_about(args):
    """About information"""
    return """Welcome to my terminal-themed portfolio!

I'm a software engineer passionate about building scalable systems
and creating innovative solutions to complex problems.

This portfolio showcases my projects in a retro terminal interface.
Feel free to explore using the available commands!

Use 'projects' to see my work or 'skills' for technical expertise."""

def cmd_skills(args):
    """Display skills"""
    return """Technical Skills:
  Languages: Python, JavaScript, Java, SQL, Go
  Frontend: React, Vue.js, Vanilla JS, HTML/CSS
  Backend: Flask, FastAPI, Node.js, Django
  Databases: PostgreSQL, MongoDB, Redis
  Tools: Docker, Git, Kubernetes, AWS
  Other: REST APIs, gRPC, WebSockets, System Design"""

def cmd_ls(args):
    """List directory contents"""
    # Return newline-separated entries so output is anchored to the left
    if terminal_state['current_dir'] == '/home/user':
        entries = [
            'projects/',
            'documents/',
            'downloads/',
            '.gitconfig',
            'README.md'
        ]
        return "\n".join(entries)
    elif terminal_state['current_dir'] == '/home/user/projects':
        # Show project ids one-per-line
        return "\n".join([f"{k}/" for k in PROJECTS.keys()])
    else:
        return "."

def cmd_pwd(args):
    """Print working directory"""
    return terminal_state['current_dir']

def cmd_whoami(args):
    """Display current user"""
    return terminal_state['logged_in']

def cmd_echo(args):
    """Echo text"""
    return " ".join(args) if args else ""

def cmd_cat(args):
    """Display file contents"""
    if not args:
        return "Usage: cat <filename>"
    filename = args[0]
    
    if filename == 'README.md':
        return "# Welcome to My Portfolio\n\nThis is my personal portfolio website.\nExplore the projects and skills!"
    elif filename == '.gitconfig':
        return "[user]\n    name = Developer\n    email = dev@example.com"
    else:
        return f"cat: {filename}: No such file or directory"

def cmd_cd(args):
    """Change directory"""
    if not args:
        terminal_state['current_dir'] = '/home/user'
        return ""
    
    path = args[0]
    if path == '/home/user' or path == '~':
        terminal_state['current_dir'] = '/home/user'
    elif path == '/home/user/projects' or path == 'projects':
        terminal_state['current_dir'] = '/home/user/projects'
    elif path == '..':
        terminal_state['current_dir'] = '/home/user'
    else:
        return f"cd: {path}: No such file or directory"
    return ""

def cmd_uname(args):
    """System information"""
    return "Linux portfolio-terminal 5.10.0 #1 SMP x86_64 GNU/Linux"

def cmd_date(args):
    """Current date and time"""
    from datetime import datetime
    return datetime.now().strftime("%a %b %d %H:%M:%S UTC %Y")

def cmd_mkdir(args):
    """Create directory - with funny response"""
    if not args:
        return "Usage: mkdir <directory>"
    return f"Permission denied: Cannot create '{args[0]}'. This is a read-only portfolio! 🔒"

def cmd_sudo(args):
    """Sudo - with funny response"""
    if not args:
        return "sudo: no command specified"
    return f"sudo: nice try, but you don't have administrator privileges here! 😄"

def cmd_clear(args):
    """Clear terminal"""
    return "[CLEAR]"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """API endpoint for executing commands"""
    data = request.json
    command = data.get('command', '')
    
    output = execute_command(command)
    prompt = get_prompt()
    
    return jsonify({
        'output': output,
        'prompt': prompt,
        'current_dir': terminal_state['current_dir']
    })

if __name__ == '__main__':
    app.run(debug=True)