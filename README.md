# TRex GUI Controller

A PyQt5-based graphical interface for managing and controlling the TRex Traffic Generator over SSH.

## Server Prerequisites

- Operating System: Ubuntu
- Copy the `defualt_trex_khosrow` folder to `/root/defualt_trex_khosrow/` on the target server
- TRex must be installed at `/root/v3.05`

## Features

- Run TRex in Stateless, Stateful, and Advanced Stateful modes
- Generate YAML configuration files for PCAP-based scenarios
- Connect to a remote server via SSH
- Real-time output display with terminal-like formatting
- Dark theme for better readability

## Requirements

- Python 3.8 or higher
- PyQt5
- paramiko
- sshpass
- A TRex installation on the target server

## Installation

    git clone https://github.com/ntw1990/trex-gui.git
    cd trex-gui
    pip install -r requirements.txt
    sudo apt install sshpass

## Usage

    python main.py

Then:

1. Open the file menu and click Connect to Server
2. Enter host, username, password, and TRex version
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
