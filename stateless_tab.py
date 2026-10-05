# stateless_tab.py
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QSizePolicy, \
    QSpacerItem, QLabel, QTextBrowser, QDialog, QWidget
from PyQt5.QtCore import QProcess, QTimer, Qt
from PyQt5.QtGui import QFont, QTextOption, QColor, QPalette
from dialogs import HostFileDialog
from base_tab import BaseTRexTab
import re


class StatelessControlPanel(BaseTRexTab):
    def __init__(self):
        super().__init__()
        self.output_timer = None
        self.last_output_size = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Main buttons
        button_layout_1 = QHBoxLayout()

        self.start_button = QPushButton("Start TRex")
        self.start_button.setStyleSheet("background-color: green; color: white;")
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.clicked.connect(self.connect_and_execute)
        button_layout_1.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop TRex")
        self.stop_button.setStyleSheet("background-color: red; color: white;")
        self.stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stop_button.clicked.connect(self.stop_command)
        button_layout_1.addWidget(self.stop_button)

        self.stop_stateless = QPushButton("STOP Command")
        self.stop_stateless.setStyleSheet("background-color: #990000; color: white;")
        self.stop_stateless.clicked.connect(self.stop)
        button_layout_1.addWidget(self.stop_stateless)

        layout.addLayout(button_layout_1)

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(5)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        checkbox_style = """
            QCheckBox {
                padding: 0px;  
                margin: 0px;    
                spacing: 0px;   
                color: black;
            }
        """

        self.soft_checkbox = QCheckBox("Software")
        self.soft_checkbox.setStyleSheet(checkbox_style)
        self.soft_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.soft_checkbox.setToolTip("Run in software mode (no hardware required)")
        checkbox_layout.addWidget(self.soft_checkbox)

        self.sym_checkbox = QCheckBox("Symmetric")
        self.sym_checkbox.setStyleSheet(checkbox_style)
        self.sym_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.sym_checkbox)
        self.sym_checkbox.setToolTip("Each flow is sent both client->server and server->client")

        self.ipv6_checkbox = QCheckBox("IPv6")
        self.ipv6_checkbox.setStyleSheet(checkbox_style)
        self.ipv6_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.ipv6_checkbox)

        self.unbind_checkbox = QCheckBox("Unbind")
        self.unbind_checkbox.setStyleSheet(checkbox_style)
        self.unbind_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.unbind_checkbox)
        self.unbind_checkbox.setToolTip("Automatically unbind unused ports (i40e only)")

        self.information_checkbox = QCheckBox("Verbose")
        self.information_checkbox.setStyleSheet(checkbox_style)
        self.information_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.information_checkbox)
        self.information_checkbox.setToolTip("Show more information for debugging")

        self.force_checkbox = QCheckBox("Force")
        self.force_checkbox.setStyleSheet(checkbox_style)
        self.force_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.force_checkbox)
        self.force_checkbox.setToolTip("Force command execution")

        # Ports
        for i in range(4):
            checkbox = QCheckBox(f"Port {i}")
            checkbox.setStyleSheet(checkbox_style)
            checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            checkbox_layout.addWidget(checkbox)
            setattr(self, f"port{i}_checkbox", checkbox)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        checkbox_layout.addSpacerItem(spacer)
        layout.addLayout(checkbox_layout)

        # First row of inputs
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        # PCAP file path
        file_path_widget, self.file_path_input = self.create_file_input("PCAP File Path:", "browse_file", "Push PCAP",
                                                                        "push_command")
        input_layout.addLayout(file_path_widget)

        # Python file path
        python_widget, self.yaml_input = self.create_file_input("Python File Path:", "browse_python_file",
                                                                "Run Stateless", "stateless")
        input_layout.addLayout(python_widget)

        # Rate multiplier
        m_input_widget, self.m_input_1 = self.create_input_field("Rate Multiplier:", "Enter rate multiplier value")
        input_layout.addLayout(m_input_widget)

        # Active flows
        active_flows_widget, self.active_flows_input = self.create_input_field("Active Flows:",
                                                                               "Enter active flows value (optional)")
        input_layout.addLayout(active_flows_widget)

        # Cores
        core_widget, self.core_input = self.create_input_field("Cores:", "Enter number of cores (optional)")
        input_layout.addLayout(core_widget)

        layout.addLayout(input_layout)

        # Second row of inputs
        input_layout_2 = QHBoxLayout()
        input_layout_2.setSpacing(5)

        # TRex config
        cfg_widget, self.cfg_input = self.create_file_input("TRex Config:", "browse_file_config")
        input_layout_2.addLayout(cfg_widget)

        # Log file
        log_widget, self.log = self.create_file_input("Log File:", "browse_file_log")
        input_layout_2.addLayout(log_widget)

        # Duration
        duration_widget, self.duration = self.create_input_field("Duration:", "Enter duration (optional)")
        input_layout_2.addLayout(duration_widget)

        # Mbuf
        mbuf_widget, self.mbuf = self.create_input_field("Mbuf:", "Increase mbuf count (optional)")
        input_layout_2.addLayout(mbuf_widget)

        # Wait time
        wait_widget, self.wait = self.create_input_field("Wait:", "Wait time between startup and traffic sending")
        self.wait.setToolTip("Default: 1 second")
        input_layout_2.addLayout(wait_widget)

        layout.addLayout(input_layout_2)

        # Output
        self.output_label = QLabel("Output:")
        layout.addWidget(self.output_label)

        self.output_text = QTextBrowser()
        self.output_text.setOpenExternalLinks(True)

        # Set monospace font for terminal-like display
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        self.output_text.setFont(font)

        # Disable line wrapping to preserve table formatting
        self.output_text.setLineWrapMode(QTextBrowser.NoWrap)

        self.output_text.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
        """)

        self.output_text.clear()

        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def create_file_input(self, label_text, browse_method, button_text=None, button_method=None):
        """Create file input with browse button - returns (layout, line_edit)"""
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        label = QLabel(label_text)
        label.setStyleSheet("color: black;")

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Enter {label_text}")

        vbox.addWidget(label)
        vbox.addWidget(line_edit)
        layout.addLayout(vbox)

        # Browse button
        browse_vbox = QVBoxLayout()
        browse_vbox.setSpacing(0)
        browse_vbox.addWidget(QLabel(""))

        browse_btn = QPushButton("...")
        browse_btn.setFixedSize(30, 27)
        if browse_method:
            browse_btn.clicked.connect(getattr(self, browse_method))
        browse_vbox.addWidget(browse_btn)
        layout.addLayout(browse_vbox)

        # Optional action button
        if button_text and button_method:
            btn_vbox = QVBoxLayout()
            btn_vbox.setSpacing(0)
            btn_vbox.addWidget(QLabel(""))

            action_btn = QPushButton(button_text)
            action_btn.setStyleSheet("background-color: blue; color: white;")
            action_btn.clicked.connect(getattr(self, button_method))
            btn_vbox.addWidget(action_btn)
            layout.addLayout(btn_vbox)

        return layout, line_edit

    def create_input_field(self, label_text, placeholder):
        """Create input field - returns (layout, line_edit)"""
        layout = QVBoxLayout()
        layout.setSpacing(0)

        label = QLabel(label_text)
        label.setStyleSheet("color: black;")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        layout.addWidget(label)
        layout.addWidget(line_edit)

        return layout, line_edit

    def browse_file(self):
        """Browse PCAP file"""
        if not self.validate_connection():
            return

        try:
            initial_path = f"/root/{self.trex_version}"
            file_dialog = HostFileDialog(self.ssh_client, initial_path, self)
            if file_dialog.exec_() == QDialog.Accepted:
                selected_file = file_dialog.selected_file()
                if selected_file:
                    self.file_path_input.setText(selected_file)
        except Exception as e:
            self.append_error(str(e))

    def browse_python_file(self):
        """Browse Python file"""
        if not self.validate_connection():
            return

        try:
            initial_path = f"/root/{self.trex_version}"
            file_dialog = HostFileDialog(self.ssh_client, initial_path, self)
            if file_dialog.exec_() == QDialog.Accepted:
                selected_file = file_dialog.selected_file()
                if selected_file:
                    self.yaml_input.setText(selected_file)
        except Exception as e:
            self.append_error(str(e))

    def browse_file_config(self):
        """Browse config file"""
        if not self.validate_connection():
            return

        try:
            initial_path = f"/root/{self.trex_version}"
            file_dialog = HostFileDialog(self.ssh_client, initial_path, self)
            if file_dialog.exec_() == QDialog.Accepted:
                selected_file = file_dialog.selected_file()
                if selected_file:
                    self.cfg_input.setText(selected_file)
        except Exception as e:
            self.append_error(str(e))

    def browse_file_log(self):
        """Browse log file"""
        if not self.validate_connection():
            return

        try:
            initial_path = f"/root/{self.trex_version}"
            file_dialog = HostFileDialog(self.ssh_client, initial_path, self)
            if file_dialog.exec_() == QDialog.Accepted:
                selected_file = file_dialog.selected_file()
                if selected_file:
                    self.log.setText(selected_file)
        except Exception as e:
            self.append_error(str(e))

    def connect_and_execute(self):
        """Start TRex in Stateless mode with tmux output display"""
        if not self.validate_connection():
            return

        try:
            if self.ssh_process is None or self.ssh_process.state() == QProcess.NotRunning:
                # Build command
                cmd_parts = ['./t-rex-64 -i --stl']

                if self.soft_checkbox.isChecked():
                    cmd_parts.append('--software')

                core_value = self.sanitize_input(self.core_input.text())
                if core_value:
                    cmd_parts.append(f'-c {core_value}')

                active_flows = self.sanitize_input(self.active_flows_input.text())
                if active_flows:
                    cmd_parts.append(f'--active-flows {active_flows}')

                cfg_value = self.sanitize_input(self.cfg_input.text())
                if cfg_value:
                    cmd_parts.append(f'--cfg {cfg_value}')

                if self.sym_checkbox.isChecked():
                    cmd_parts.append('--flip')

                if self.ipv6_checkbox.isChecked():
                    cmd_parts.append('--ipv6')

                if self.unbind_checkbox.isChecked():
                    cmd_parts.append('--unbind-unused-ports')

                mbuf_value = self.sanitize_input(self.mbuf.text())
                if mbuf_value:
                    cmd_parts.append(f'--mbuf-factor {mbuf_value}')

                log_value = self.sanitize_input(self.log.text())
                if log_value:
                    cmd_parts.append(f'--rpc-log {log_value}')

                if self.information_checkbox.isChecked():
                    cmd_parts.append('-v 8')

                wait_value = self.sanitize_input(self.wait.text())
                if wait_value:
                    cmd_parts.append(f'-w {wait_value}')

                command = ' '.join(cmd_parts)

                # Improved script for tmux output with real-time display
                script = f"""#!/bin/bash
set -e

# Killing existing session if any
tmux has-session -t khosrow_trex 2>/dev/null && tmux kill-session -t khosrow_trex

# Clean up old output files
rm -f /tmp/trex_output.log
touch /tmp/trex_output.log

# Create new tmux session
echo "Creating tmux session and starting TRex..."
tmux new-session -d -s khosrow_trex

# Configure tmux for full output
tmux set -t khosrow_trex remain-on-exit on
tmux set -t khosrow_trex status off

# Connect tmux output to log file
tmux pipe-pane -t khosrow_trex -o "cat >> /tmp/trex_output.log"

# Send commands to tmux
tmux send-keys -t khosrow_trex 'cd /root/{self.trex_version}/' C-m
tmux send-keys -t khosrow_trex '{command}' C-m

echo ""
echo "═══════════════════════════════════════════"
echo "         Starting TRex...                   "
echo "═══════════════════════════════════════════"
echo ""

# Display output in real-time
while true; do
    if [ -f /tmp/trex_output.log ]; then
        cat /tmp/trex_output.log 2>/dev/null
        > /tmp/trex_output.log
    fi

    # Check tmux status
    if ! tmux has-session -t khosrow_trex 2>/dev/null; then
        echo ""
        echo "Tmux session ended"
        break
    fi

    sleep 1
done &

# Wait for finish
wait

echo ""
echo "═══════════════════════════════════════════"
echo "Tmux session 'khosrow_trex' is running"
echo "To attach to tmux: tmux attach -t khosrow_trex"
echo "To view output: tail -f /tmp/trex_output.log"
echo "═══════════════════════════════════════════"
"""

                # Create new QProcess
                self.ssh_process = QProcess()
                self.ssh_process.setProcessChannelMode(QProcess.MergedChannels)

                # Connect signals
                self.ssh_process.readyReadStandardOutput.connect(self.handle_tmux_output)
                self.ssh_process.finished.connect(self.on_process_finished)

                ssh_command = self.execute_remote_script(script)

                if ssh_command:
                    self.ssh_process.start("bash", ["-c", ssh_command])
                    self.append_success("Starting TRex session in Stateless mode...")
                    self.append_info("Tmux output will be displayed in real-time...")
                else:
                    self.append_error("Error building SSH command")
            else:
                self.append_error("A session is already running.")

        except Exception as e:
            self.append_error(str(e))

    def handle_tmux_output(self):
        """Handle tmux output in real-time"""
        try:
            if self.ssh_process is None:
                return

            # Read all available data
            data = self.ssh_process.readAllStandardOutput().data().decode()
            if data.strip():
                self.process_tmux_output(data)
        except Exception as e:
            self.append_error(f"Error receiving output: {str(e)}")

    def process_tmux_output(self, output):
        """Process and display tmux output with preserved terminal formatting"""
        # Split output into lines
        lines = output.split('\n')

        for line in lines:
            if not line.strip():
                # Preserve empty lines for proper spacing
                self.append_output(" ", special=True)
                continue

            # Clean ANSI codes but preserve formatting
            clean_line = self.clean_ansi_codes(line)

            # Remove any carriage returns
            clean_line = clean_line.replace('\r', '')


            if "cd " in clean_line or "./t-rex-64" in clean_line:
                self.append_output(f"$ {clean_line}", color="#569cd6")

            # Detect statistics table lines
            elif any(keyword in clean_line for keyword in ["opackets", "ipackets", "obytes", "ibytes",
                                                           "errors", "oerrors", "Tx Bw", "ports"]):
                self.append_output(clean_line, special=True)

            # Detect separator lines
            elif "════════" in clean_line or "────" in clean_line or "━━━━" in clean_line:
                self.append_output(clean_line, color="#888888")

            # Detect statistics lines with colon format
            elif ":" in clean_line and any(stat in clean_line for stat in ["Cpu Utilization", "Platform_factor",
                                                                           "Total-Tx", "Total-Rx", "Total-PPS",
                                                                           "Total-CPS", "Expected-PPS", "Expected-CPS",
                                                                           "Expected-BPS", "Active-flows", "Open-flows",
                                                                           "drop-rate", "current time", "test duration",
                                                                           "Socket-util", "Socket/clients"]):
                self.append_output(clean_line, color="#ce9178")

            # Detect table header
            elif clean_line.strip() == "ports" or clean_line.strip().startswith("ports "):
                self.append_output(clean_line, bold=True)

            # Detect numeric table rows
            elif re.match(r'^\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*$', clean_line) or \
                    re.match(r'^\s*\d+\s*\|\s*\d+\s*$', clean_line):
                self.append_output(clean_line, color="#b5cea8")

            # Detect important messages
            elif "Error" in clean_line or "❌" in clean_line:
                self.append_output(f"❌ {clean_line}", color="#f48771")
            elif "Warning" in clean_line or "!!!" in clean_line:
                self.append_output(f"{clean_line}", color="#dcdcaa")
            elif "success" in clean_line.lower() or "✅" in clean_line or "complete" in clean_line.lower():
                self.append_output(f"✅ {clean_line}", color="#6a9955")
            elif "tmux" in clean_line.lower() and "attach" in clean_line.lower():
                self.append_output(clean_line, color="#9cdcfe")
            elif "TRex" in clean_line and "starting" in clean_line.lower():
                self.append_output(f"{clean_line}", color="#4ec9b0")
            else:
                # Regular lines
                self.append_output(clean_line)

    def clean_ansi_codes(self, text):
        """Remove ANSI codes from text"""
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)

        # Remove other control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        return text

    def on_process_finished(self):
        """When SSH process finishes"""
        self.append_output("═══════════════════════════════════════════", color="#888888")
        self.append_output("TRex startup process completed", color="#6a9955")
        self.append_output("═══════════════════════════════════════════", color="#888888")

    def append_output(self, text, color=None, bold=False, special=False):
        """Add text to output with proper formatting"""
        if not self.output_text:
            return

        # Escape HTML characters
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Build style
        style = "font-family: 'Courier New', monospace;"
        if color:
            style += f" color: {color};"
        if bold:
            style += " font-weight: bold;"

        if special:
            # For preserving spaces, use pre tag
            formatted_text = f"<pre style='margin:0; padding:0; {style}'>{text}</pre>"
        else:
            formatted_text = f"<span style='{style}'>{text}</span>"

        self.output_text.append(formatted_text)

        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def append_success(self, text):
        """Add success message"""
        self.append_output(text, color="#6a9955")

    def append_error(self, text):
        """Add error message"""
        self.append_output(f"❌ {text}", color="#f48771")

    def append_info(self, text):
        """Add info message"""
        self.append_output(f"{text}", color="#9cdcfe")

    def stop_command(self):
        """Stop TRex completely and close tmux session"""
        if not self.validate_connection():
            return

        try:
            if self.ssh_process and self.ssh_process.state() == QProcess.Running:
                self.ssh_process.terminate()
                self.ssh_process.waitForFinished(5000)
                self.ssh_process = None

            # Stop script
            script = """#!/bin/bash
set -e

echo "═══════════════════════════════════════════"
echo "         Stopping TRex...                   "
echo "═══════════════════════════════════════════"

# kill t-rex-64 process
pkill -f ./_t-rex-64 && echo "t-rex-64 process stopped" || echo "t-rex-64 process not found"

# kill tmux session
tmux kill-session -t khosrow_trex 2>/dev/null && echo "tmux session stopped" || echo "tmux session not found"

# clean up temp files
rm -f /tmp/trex_output.log 2>/dev/null

echo ""
echo "Stop operation completed."
echo "═══════════════════════════════════════════"
"""

            process = QProcess()
            ssh_cmd = self.execute_remote_script(script)

            if ssh_cmd:
                process.start("bash", ["-c", ssh_cmd])
                process.waitForFinished(10000)

                output = process.readAllStandardOutput().data().decode()
                if output:
                    self.append_output(output, special=True)

                self.append_success("TRex process and session stopped.")

        except Exception as e:
            self.append_error(str(e))

    def push_command(self):
        """Push PCAP file"""
        if not self.validate_connection():
            return

        try:
            file_path = self.sanitize_input(self.file_path_input.text())
            if not file_path:
                file_path = "/root/defualt_trex_khosrow/onevpn-tls.pcap"
                self.append_info(f"Using default path: {file_path}")

            # Build port options
            port_options = []
            for i in range(4):
                checkbox = getattr(self, f"port{i}_checkbox")
                if checkbox.isChecked():
                    port_options.append(f"-p {i}")

            force_option = "--force" if self.force_checkbox.isChecked() else ""

            cmd_parts = ['cd', f'/root/{self.trex_version}', '&&', 'echo',
                         f"'push -f {file_path} {force_option} {' '.join(port_options)}'",
                         '|', './trex-console']

            ssh_command = ' '.join(cmd_parts)
            output = self.ssh_client.execute_command(ssh_command)

            self.append_success(f"PCAP file pushed successfully: {file_path}")
            self.append_output(output, special=True)

        except Exception as e:
            self.append_error(str(e))

    def stop(self):
        """Stop command in TRex console"""
        if not self.validate_connection():
            return

        ssh_command = f"cd /root/{self.trex_version} && echo 'stop' | ./trex-console"
        output = self.ssh_client.execute_command(ssh_command)

        self.append_success("Successfully stopped.")
        self.append_output(output, special=True)

    def stateless(self):
        if not hasattr(self, 'ssh_client') or not self.ssh_client:
            self.output_text.append(
                "<font color='red'>Error: SSH client is not initialized. Please connect first.</font>")
            return

        file_path = self.yaml_input.text().strip() or "/root/defualt_trex_khosrow/udp_1pkt.py"
        force_option = "--force" if self.force_checkbox.isChecked() else ""
        rate_multiple = self.m_input_1.text().strip() or 1
        time_value = self.duration.text().strip()
        time_option = f"-d {time_value}" if time_value else ""
        port0_option = "-p 0" if self.port0_checkbox.isChecked() else ""
        port1_option = "-p 1" if self.port1_checkbox.isChecked() else ""
        port2_option = "-p 2" if self.port2_checkbox.isChecked() else ""
        port3_option = "-p 3" if self.port3_checkbox.isChecked() else ""

        ssh_command = f"cd /root/{self.trex_version} && echo 'start -f {file_path} -m {rate_multiple} {time_option} {force_option} {port0_option} {port1_option} {port2_option} {port3_option}' | ./trex-console"

        output = self.ssh_client.execute_command(ssh_command)

        self.output_text.append(f"<font color='green'>Successfully stateless file: {file_path}</font>")
        self.output_text.append(f"<pre>{output}</pre>")