

#os : ubuntu
#step 1 : First, copy the "defualt_trex_khosrow"  file to the following location on the destination server where T-Rex is installed: 
#/root/defualt_trex_khosrow/
#step 2 : T-Rex must be positioned along this path:
#/root/v3.05          ###I used version 3.05.





# TRex GUI Controller

A PyQt5-based graphical interface for managing and controlling the TRex Traffic Generator over SSH.

## Features

- Run TRex in Stateless, Stateful, and Advanced Stateful modes
- Generate YAML configuration files for PCAP-based scenarios
- Connect to a remote server via SSH
- Real-time output display with terminal-like formatting
- Dark theme for better readability
- Configurable rate multiplier, duration, cores, and more

## Requirements

- Python 3.8 or higher
- PyQt5 - GUI framework
- paramiko - SSH communication
- sshpass - system tool for password-based SSH (required by `base_tab.py`)
- A TRex installation on the target server

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/khosrow-esteghlali/trex-gui.git
cd trex-gui
