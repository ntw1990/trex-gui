# TRex GUI Controller

A PyQt5-based graphical interface for managing and controlling the TRex Traffic Generator over SSH.

## Environment

This tool is designed to run on the client machine and control a remote server where TRex is installed.

- **Client (where this GUI runs):** Ubuntu
- **Server (where TRex is installed):** Fedora 25

## Server Prerequisites

Before using this tool, prepare the target server (Fedora 25) as follows:

**Step 1:** Copy the `defualt_trex_khosrow` folder to the following location on the server:

    /root/defualt_trex_khosrow/

**Step 2:** TRex must be installed at:

    /root/v3.05

Note: This project was developed and tested with TRex version `v3.05`.

## Features

- Run TRex in Stateless, Stateful, and Advanced Stateful modes
- Generate YAML configuration files for PCAP-based scenarios
- Connect to a remote server via SSH
- Real-time output display with terminal-like formatting
- Dark theme for better readability

## Requirements

### Client Machine (Ubuntu)

- Python 3.8 or higher
- PyQt5
- paramiko
- sshpass

Install them with:

    pip install -r requirements.txt
    sudo apt update
    sudo apt install sshpass

### Server Machine (Fedora 25)

- TRex installed at `/root/v3.05`
- The `defualt_trex_khosrow` folder placed at `/root/defualt_trex_khosrow/`
- `tmux` installed (used for background sessions)

To install tmux on Fedora:

    sudo dnf install tmux

## Installation

### 1. Clone the repository on the client machine

    git clone https://github.com/ntw1990/trex-gui.git
    cd trex-gui

### 2. Install Python dependencies

    pip install -r requirements.txt

### 3. Install sshpass (Ubuntu client)

    sudo apt update
    sudo apt install sshpass

## Usage

    python main.py

Then:

1. Open the file menu and click Connect to Server
2. Enter the server details (host, username, password, TRex version)
3. Select the desired tab and fill in the parameters
4. Click the green Start TRex button

## Project Structure

- main.py - Entry point
- base_tab.py - Shared base class
- stateless_tab.py - Stateless mode
- stateful_tab.py - Stateful mode
- advanced_stateful_tab.py - Advanced Stateful mode
- generator_tab.py - YAML generator
- dialogs.py - SSH and file dialogs

## License

MIT License - see the LICENSE file for details.
