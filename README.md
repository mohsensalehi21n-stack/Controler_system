# Controler_system
Modular Python system for remote shell execution, AI model interaction via Ollama, and file transfer with progress tracking — built for automation, control, and extensibility.
📦 Python Remote Shell & File Transfer System
This project is a modular, socket-based Python system for remote command execution, AI model interaction, and file transfer between clients and a server. It’s designed for automation engineers, system administrators, and developers who want a lightweight, extensible solution for distributed control and data exchange.
🧠 Overview
The system is divided into two complementary modules:
- Part 1 (part1/): Full-featured remote shell with support for executing commands, navigating directories, and interacting with local AI models via Ollama.
- Part 2 (part2/): Optimized file transfer system with progress bar feedback for downloads and smart command parsing.
⚠️ Note: Each part has strengths and limitations. For a complete experience, it's recommended to run both parts in parallel:
- Use Part 1 for shell commands and AI interaction.
- Use Part 2 for file upload/download with progress tracking.

project-root/
│
├── part1/                  # Remote shell + Ollama + basic file transfer
│   ├── server.py
│   └── client.py
│
├── part2/                  # File transfer with progress bar
│   ├── server_2.py
│   └── client2.py
│
├── README.md               # Project documentation
└── LICENSE                 # MIT License
🚀 Getting Started
🔹 Part 1: Remote Shell + Ollama
Server:
cd part1
python server.py
Client:
cd part1
python client.py
Available Commands:
# Change server directory
cd /path/to/folder

# Run shell command
ls -la

# Upload file to server
upload local_file.txt /server/save/path

# Download file from server
download server_file.txt

# Query Ollama model
ollama llama2 What is the capital of France?

# Exit client
exit
🔹 Part 2: File Transfer with Progress Bar
Server:
cd part2
python server_2.py
Client:
cd part2
python client2.py
Available Commands:
# Download file from server
download filename.txt
dl filename.txt
get filename.txt
d:filename.txt

# Exit client
exit
🧠 Ollama Integration
To use AI model queries, install and run Ollama on the server. Supported models (e.g., llama2, mistral, etc.) can be queried like this:
ollama llama2 What is the capital of France?
⚠️ Known Issues & Contributions
Some parts of the system may contain bugs or need refinement. For example:
- File transfer in Part 1 lacks progress feedback and may fail silently.
- Part 2 does not support shell commands or AI queries.
If you encounter issues or want to improve the system, contributions are welcome! Fork the repo, submit pull requests, or open issues to help us build a more robust and intelligent remote control system.
📜 License
This project is licensed under the MIT License. You are free to use, modify, and distribute it with proper attribution.
🚧 Project Status: Actively in Development
This project is a living system — evolving, expanding, and improving with every iteration.
We’re currently in active development, and new features, modules, and architectural enhancements are on the way. Expect smarter automation, cleaner interfaces, and deeper integration with AI tools like Ollama in upcoming versions.
🔄 What’s coming soon:
• 	Improved error handling and fallback logic
• 	Unified client interface across modules
• 	Enhanced security and permission controls
• 	Expanded support for AI model orchestration
• 	Community-driven improvements and plugin support
If you’re exploring this repo today, you’re catching it in its early stages — and your feedback or contributions could help shape its future.
Stay tuned. The next release is never far away.













