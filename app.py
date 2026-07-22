import re
from flask import Flask, render_template, request, jsonify
from textwrap import dedent

app = Flask(__name__)

PROJECTS = {
    'Fretless Minds — AI-Powered Robotic Ukulele (ECE Capstone Project)': {
        'name': 'Fretless Minds — AI-Powered Robotic Ukulele (ECE Capstone Project)',
        'description': 'Group capstone project that takes a natural language text prompt, generates sheet music using a locally-run transformer model, and physically plays it on a ukulele in under 45 seconds. The hardware uses four SG90 servo motors for strumming and eight linear solenoids for fretting, all mounted on custom 3D-printed housings and controlled via an Arduino over serial. The software layer is a Python REST API that parses AI-generated ABC notation into hardware commands using music21, with a Flutter frontend for mobile input. My contribution was the hardware assembly and system integration, coordinating the software and hardware subsystems into a working prototype.',
        'website': 'https://uwaterloo.ca/capstone-design/project-abstracts/2026-capstone-design-projects/2026-electrical-and-computer-engineering-capstone-designs#58',
        'demo': 'just ask and I can dust it off for a live performance',
    },
    'Highway Path Planning for Autonomous Vehicle': {
        'name': 'Highway Path Planning for Autonomous Vehicle',
        'description': 'Built a path planner in C++ that drives a simulated car around a busy highway: merging, passing slower traffic, and dodging other cars, all while keeping the ride smooth (no sudden jerks or hard braking). It reads live sensor data every 20ms and re-plots a fresh route using spline curves so the car never jolts around like it\'s had too much coffee.',
        'github': 'https://github.com/jmogen/CarND-Path-Planning-Project',
    },
    'Kinematic Bicycle Model Trajectory': {
        'name': 'Kinematic Bicycle Model Trajectory',
        'description': 'Implemented a kinematic bicycle model from scratch in Python (state variables, sideslip angle, Euler integration) and used it to drive a virtual vehicle through circles, squares, spirals, wave paths, and a figure-8 loop with two 8m-radius circles in 30 seconds. Turns out getting a car-like robot to trace a clean figure 8 using only pre-computed speed and steering-rate inputs (no feedback) is trickier than it sounds, small timing errors compound fast, which is basically why real self-driving cars use closed-loop control instead.',
        'github': 'https://github.com/jmogen/trajectory_planning',
    },
    'Extended Kalman Filter for LIDAR Vehicle Localization': {
        'name': 'Extended Kalman Filter for LIDAR Vehicle Localization',
        'description': 'Built an EKF from scratch in Python to track a vehicle\'s 2D pose (x, y, heading) using noisy odometry and LIDAR range/bearing measurements to known landmarks. Implemented the full prediction-correction loop by hand, including Jacobians, Kalman gain, and covariance propagation, and watched the estimated trajectory converge onto ground truth once the math clicked into place. Basically taught me why every self-driving car and drone runs some flavor of this filter under the hood.',
        'github': 'https://github.com/jmogen/extended_kalman_filter',
    },
    'Single-Stage Object Detector (YOLO)': {
        'name': 'Single-Stage Object Detector (YOLO)',
        'description': 'Built a YOLO-style single-stage object detector in PyTorch on top of a MobileNetV2 backbone, implementing anchor generation, IoU matching, proposal decoding, and a full multi-part loss (confidence, bounding box regression, classification) from scratch. Trained and evaluated it on PASCAL VOC 2007 using mean Average Precision, and even hand-rolled non-max suppression just to see how it stacks up against torchvision\'s optimized version. It\'s a scaled-down version of the real thing, but it\'s the same core recipe every modern real-time detector still builds on.',
        'github': 'https://github.com/jmogen/object_detection',
    },
    'Semantic Segmentation on VOC (U-Net + ResNet34)': {
        'name': 'Semantic Segmentation on VOC (U-Net + ResNet34)',
        'description': 'Built a semantic segmentation network in PyTorch by grafting a U-Net-style decoder with skip connections onto a pretrained ResNet34 encoder, then trained it on the PASCAL VOC dataset to label every pixel in an image (car, bicycle, person, background, etc). Wrote custom data augmentation (random crop, horizontal flip) that had to stay in sync between the image and its segmentation mask, which turned out to be sneakier than it sounds since one off-by-one error and your labels no longer line up with your pixels. Evaluated the final model using mean IoU on a few driving-relevant classes, since pixel-level scene understanding is basically the backbone of how self-driving cars "see" the road.',
        'github': 'https://github.com/jmogen/semantic_segmentation',
    },
    'Two-Layer Neural Network from Scratch (CS231n)': {
        'name': 'Two-Layer Neural Network from Scratch (CS231n)',
        'description': 'Implemented a fully-connected two-layer neural network in NumPy, writing the forward pass, softmax loss, backward pass, and SGD training loop by hand instead of relying on autograd. Verified every gradient with numerical checks before trusting it, then trained the network on CIFAR-10 and tuned hyperparameters (hidden layer size, learning rate, regularization) to push validation accuracy up. It\'s basically the "build your own PyTorch, one layer at a time" exercise.',
        'github': 'https://github.com/jmogen/vanilla_neural_network',
    },
    'Lane Line Detection with Classical Computer Vision': {
        'name': 'Lane Line Detection with Classical Computer Vision',
        'description': 'Built an image processing pipeline in OpenCV that finds lane lines on the road using grayscale conversion, Gaussian blur, Canny edge detection, and Hough transform line detection, then applied it to a video stream frame by frame. Went a step further than basic averaging by using RANSAC regression to fit a single continuous line per lane, which made the pipeline far more resistant to outlier line segments and noisy detections. It\'s a good reminder that before deep learning ate computer vision, this kind of classical pipeline is genuinely how early self-driving systems found their lane.',
        'github': 'https://github.com/jmogen/CarND-LaneLines-P1',
    },
    'Deer Tracker (Real-Time YOLO Detection)': {
        'name': 'Deer Tracker (Real-Time YOLO Detection)',
        'description': 'Built a real-time deer detection system using a custom-trained YOLO model running on a live USB camera feed, drawing bounding boxes and confidence scores directly onto the video stream. Implemented two modes: full object detection (with boxes for deer, cow, and horse-like classes) and a lighter classification-only mode for full-frame "deer or not" predictions. Started as a random idea but ended up being a solid intro to deploying a trained model against live sensor input instead of a static dataset.',
        'github': 'https://github.com/jmogen/Deer_Tracker',
    },
    'Parallel Matrix Multiplication (MPI)': {
        'name': 'Parallel Matrix Multiplication (MPI)',
        'description': 'Built a distributed matrix multiplication system in C++ using MPI, splitting the workload across multiple processor cores on a compute cluster. Ran strong-scaling experiments (fixed problem size, more processors) and time-to-solution benchmarks (bigger matrices, same processor count) up to 3072x3072, then validated every result against a NumPy ground truth to make sure "faster" didn\'t quietly become "wrong." Watching near-linear speedup actually show up on a graph after tuning communication patterns was a genuinely satisfying payoff.',
        'github': 'Available upon request',
    },
    'Distributed Data Processing (Apache Spark)': {
        'name': 'Distributed Data Processing (Apache Spark)',
        'description': 'Implemented a series of data processing tasks in Scala using Apache Spark\'s RDD API, covering filtering, aggregation, grouping, and multi-stage join operations across a real Spark cluster. Also built a classic word-count job to sanity check the setup before tackling the harder transformations. It\'s a solid crash course in why "lazy evaluation" matters once your dataset actually needs to be split across machines instead of fitting comfortably on one laptop.',
        'github': 'Available upon request',
    },
    'Fault-Tolerant Password Hashing Service (Apache Thrift)': {
        'name': 'Fault-Tolerant Password Hashing Service (Apache Thrift)',
        'description': 'Built a distributed bcrypt hashing microservice using Apache Thrift RPC, with a frontend node that dynamically discovers and load-balances across any number of backend worker nodes. The interesting design challenge was graceful degradation: if every backend drops offline, the frontend falls back to hashing locally instead of just failing outright. Tested it under concurrent client load to make sure the load balancing logic actually held up and not just in the happy-path demo.',
        'github': 'Available upon request',
    },
    'Distributed Coordination Experiments (Apache ZooKeeper)': {
        'name': 'Distributed Coordination Experiments (Apache ZooKeeper)',
        'description': 'Ran a series of fault-injection experiments on a multi-node ZooKeeper ensemble, covering leader election, node failure and recovery, network partition handling, and client session continuity. Deliberately killed nodes and simulated partitions mid-experiment to see how the consensus protocol actually behaved under quorum loss, rather than just reading about it in the Raft/Zab papers.',
        'github': 'Available upon request',
    },
    'Fibonacci Benchmark Suite (Python + C++/pybind11)': {
        'name': 'Fibonacci Benchmark Suite (Python + C++/pybind11)',
        'description': 'Inspired by Sheafification of G\'s "largest Fibonacci number in 1 second" video, I built a test bench comparing six Fibonacci implementations, naive recursion, iterative, and fast doubling, each written twice, once in pure Python and once in C++ exposed back to Python via pybind11. The harness runs every implementation for a fixed time window and tracks throughput and max-n-reached, then auto-generates comparison graphs and a ranked summary report so the numbers speak for themselves. Watching naive recursion flatline while fast doubling keeps climbing is a much more visceral way to feel the difference between exponential and logarithmic time than any textbook chart, and re-implementing the ideas myself (rather than just watching someone else\'s benchmark) was half the fun.',
        'github': 'https://github.com/jmogen/fast_fibonacci',
    },
    'MySQL Database/Table Explorer (C API)': {
        'name': 'MySQL Database/Table Explorer (C API)',
        'description': 'Built a command-line tool in C++ (using C++ as "a better C," no exceptions or RTTI) that connects directly to a MySQL server through the low-level C API to list databases and tables, complete with optional pattern matching to filter results by name. Handled secure password entry, command-line argument parsing with getopt, and SQL injection prevention by strictly validating any user-supplied pattern before it ever touches a query string. It\'s a good exercise in working close to the metal with a real database driver instead of an ORM, where every connection handle and result buffer has to be managed by hand.',
        'github': 'Available upon request',
    },
    'M/M/1 Queue Simulator (Discrete Event Simulation)': {
        'name': 'M/M/1 Queue Simulator (Discrete Event Simulation)',
        'description': 'Built a discrete event simulator in Python modeling a single-server queue with Poisson packet arrivals and exponentially distributed packet lengths, then used random "observer" arrivals (rather than direct sampling) to estimate steady-state metrics like average queue size E[n] and probability of an idle server, avoiding the bias that comes from sampling only at arrival or departure events. Validated the random number generators first by checking that generated exponential variables matched their theoretical mean and variance before trusting them in the full simulation. Sweeping utilization (rho) from lightly loaded to overloaded and watching E[n] blow up past rho = 1 is a pretty visceral way to see why network engineers sweat over keeping utilization comfortably below 100%.',
        'github': 'Available upon request',
    },
    'Web Crawler with HTML Parsing (libcurl + libxml2)': {
        'name': 'Web Crawler with HTML Parsing (libcurl + libxml2)',
        'description': 'Built a web crawler in C, using libcurl\'s custom write and header callbacks to buffer received data and extract sequence numbers from HTTP headers. Parses fetched HTML with libxml2 using XPath queries to extract hyperlinks, handles both HTML and PNG content types differently, and manages memory correctly across callbacks to prevent buffer corruption. Supports HTTP redirects and authentication credentials.',
        'github': 'Available upon request',
    },
    'VHDL Compiler (Java)': {
        'name': 'VHDL Compiler (Java)',
        'description': 'Built a VHDL compiler in Java with a recursive descent parser and AST construction. Implemented a boolean expression optimizer using the visitor pattern and common subexpression elimination (CSE). Developed compiler backends that generate x86 and JVM bytecode, plus a Java simulator with register allocation.',
        'github': 'Available upon request',
    },
    'Real-Time Scheduler Simulator (Deadline Monotonic)': {
        'name': 'Real-Time Scheduler Simulator (Deadline Monotonic)',
        'description': 'Implemented a real-time task scheduler simulator in Python that performs schedulability analysis and job-level simulation for periodic tasks. Uses response time analysis with Audsley\'s algorithm to check if task sets can meet deadlines under deadline monotonic priority assignment. Generates jobs across the hyperperiod and simulates preemptive scheduling, tracking preemption counts per task. Optimizes for large hyperperiods by using limited simulation windows to avoid timeout issues while maintaining accuracy.',
        'github': 'Available upon request',
    },
    'Daily Automated Counter PR (Git + GitHub Actions)': {
        'name': 'Daily Automated Counter PR (Git + GitHub Actions)',
        'description': 'Experimented with GitHub Actions by building a cron job that automatically increments a counter file and opens a daily PR. Spins up timestamped branches, commits the change, pushes to remote, and generates PRs via GitHub CLI—all completely hands-off. Mainly just wanted to see if I could get the whole workflow to run unsupervised and validate that the Actions pipeline actually triggers on each PR.',
        'github': 'Available upon request',
    },
    'Blackjack Simulator with Card Counting (Python)': {
        'name': 'Blackjack Simulator with Card Counting (Python)',
        'description': 'Built a blackjack game just for fun to see if I could implement basic strategy and card counting. Spun up a multi-deck shoe with proper dealer logic, hit/stand decisions, and payout rules. Added a Hi-Lo card counter that tracks the running count and feeds into strategy decisions to see if counting actually gives an edge. Wrote unit tests to validate the core mechanics—dealing, busting, payouts—and make sure the strategy layer actually works. Mostly just wanted to play around with game logic and see if card counting in code matches the theory.',
        'github': 'https://github.com/jmogen/Card_Counting',
    },
    'RTX Real-Time Operating System (ARM Cortex-M3)': {
        'name': 'RTX Real-Time Operating System (ARM Cortex-M3)',
        'description': 'School group project building a real-time operating system from scratch on the Keil MCB1700 Cortex-M3 platform. Implemented core kernel functionality including memory management with a from-scratch malloc, preemptive task scheduling, context switching in ARM assembly, inter-task message passing, console I/O, and real-time deadline-driven execution with timer support.',
        'github': 'Available upon request',
    },
    'VHDL Compiler (Java) - School Project': {
        'name': 'VHDL Compiler (Java)',
        'description': 'School project building a multi-stage compiler for VHDL in Java. Implemented a recursive descent parser with full AST construction, a boolean expression simplifier using the visitor pattern with common subexpression elimination (CSE), and code generation backends targeting x86 assembly, JVM bytecode, and a Java simulator with register allocation. Also handled VHDL-specific passes including desugaring, elaboration, and process splitting to synthesize combinational logic from behavioral descriptions.',
        'github': 'Somewhere on uwaterloo ece servers, beyond my reach',
    },
    'QAOA Max-Cut Optimizer (iQuHACK 2023 - Quantinuum Challenge)': {
        'name': 'QAOA Max-Cut Optimizer (iQuHACK 2023 - Quantinuum Challenge)',
        'description': 'Hackathon project at MIT\'s iQuHack 2023, tackling Quantinuum\'s quantum optimization challenge. Improved on a naive parameter-sampling implementation of QAOA (Quantum Approximate Optimization Algorithm) for the Max-Cut problem by experimenting with three optimization strategies: Basin Hopping, Nelder-Mead, and Gradient Descent. Best results came from Nelder-Mead, which achieved an 8% increase in highest energy found and a 180% decrease in average runtime compared to the baseline. None of us had touched quantum computing before that weekend.',
        'github': 'https://github.com/jmogen/Espada',
    },
}


def slugify(name):
    """Convert a project name into a safe lowercase filename stem."""
    slug = re.sub(r'[^\w\s-]', '', name)
    slug = re.sub(r'[\s]+', '_', slug.strip())
    return slug.lower()


# Maps filename (with .txt) -> project dict, built once at startup
PROJECT_FILES = {f"{slugify(name)}.txt": data for name, data in PROJECTS.items()}


def format_project(data):
    """Render a project dict in capitalized label format matching source docs."""
    label_map = {
        'name': 'Project',
        'description': 'Description',
        'website': 'Website',
        'github': 'Github',
        'demo': 'Demo',
    }
    lines = []
    for key, value in data.items():
        label = label_map.get(key, key.capitalize())
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


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
        'about': cmd_about,
        'mkdir': cmd_mkdir,
        'sudo': cmd_sudo,
        'cd': cmd_cd,
        'uname': cmd_uname,
        'date': cmd_date,
    }

    if cmd in commands:
        return commands[cmd](args)
    return f"Command not found: {cmd}\nType 'help' for available commands."


def cmd_help(args):
    return normalize_output(
        """Available commands:
          about        - Learn about me
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


def cmd_about(args):
    return normalize_output(
        """Welcome to my terminal-themed portfolio!

        I'm a software engineer passionate about building scalable systems
        and creating innovative solutions to complex problems.

        This portfolio showcases my projects in a retro terminal interface.
        Feel free to explore using the available commands!

        Use 'cd projects' then 'ls' to see my work."""
    )


# Files available at each directory path
DIRECTORY_FILES = {
    '/home/user': {
        'README.md': "# Welcome to My Portfolio\n\nThis is my personal portfolio website.\nExplore the projects and skills!",
        '.gitconfig': "[user]\n    name = Developer\n    email = dev@example.com",
    },
    '/home/user/projects': PROJECT_FILES,  # filename -> project dict
}

DIRECTORY_SUBDIRS = {
    '/home/user': ['projects/', 'documents/', 'downloads/'],
    '/home/user/projects': [],
}


def cmd_ls(args):
    current = terminal_state['current_dir']
    files = list(DIRECTORY_FILES.get(current, {}).keys())
    subdirs = DIRECTORY_SUBDIRS.get(current, [])
    entries = subdirs + files
    return "\n".join(entries) if entries else "."


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
    current = terminal_state['current_dir']
    files = DIRECTORY_FILES.get(current, {})

    if filename not in files:
        return f"cat: {filename}: No such file or directory"

    content = files[filename]
    if current == '/home/user/projects':
        return format_project(content)
    return content


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