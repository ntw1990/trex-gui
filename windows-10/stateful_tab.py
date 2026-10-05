from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QSizePolicy, \
    QSpacerItem, QLabel, QTextBrowser, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from dialogs import HostFileDialog
from base_tab import BaseTRexTab
import re


class StatefulControlPanel(BaseTRexTab):
    def __init__(self):
        super().__init__()
        self.pcap_process = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        button_layout = QHBoxLayout()

        self.connect_button = QPushButton("Start TRex")
        self.connect_button.setStyleSheet("background-color: green; color: white;")
        self.connect_button.clicked.connect(self.connect_and_execute)
        button_layout.addWidget(self.connect_button)

        self.stop_button = QPushButton("Stop TRex")
        self.stop_button.setStyleSheet("background-color: red; color: white;")
        self.stop_button.clicked.connect(self.stop_command)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

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

        self.prom_checkbox = QCheckBox("Promiscuous")
        self.prom_checkbox.setStyleSheet(checkbox_style)
        self.prom_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.prom_checkbox.setToolTip("Promiscuous mode to receive all packets")
        checkbox_layout.addWidget(self.prom_checkbox)

        self.rx_check_checkbox = QCheckBox("RX Check")
        self.rx_check_checkbox.setStyleSheet(checkbox_style)
        self.rx_check_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.rx_check_checkbox.setToolTip("Check received packets")
        checkbox_layout.addWidget(self.rx_check_checkbox)

        self.queue_drop_checkbox = QCheckBox("Queue Drop")
        self.queue_drop_checkbox.setStyleSheet(checkbox_style)
        self.queue_drop_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.queue_drop_checkbox.setToolTip("Packet drop in queue")
        checkbox_layout.addWidget(self.queue_drop_checkbox)

        self.sym_checkbox = QCheckBox("Symmetric")
        self.sym_checkbox.setStyleSheet(checkbox_style)
        self.sym_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.sym_checkbox.setToolTip("Each flow is sent both client->server and server->client")
        checkbox_layout.addWidget(self.sym_checkbox)

        self.ipv6_checkbox = QCheckBox("IPv6")
        self.ipv6_checkbox.setStyleSheet(checkbox_style)
        self.ipv6_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        checkbox_layout.addWidget(self.ipv6_checkbox)

        self.unbind_checkbox = QCheckBox("Unbind")
        self.unbind_checkbox.setStyleSheet(checkbox_style)
        self.unbind_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.unbind_checkbox.setToolTip("Automatically unbind unused ports (i40e only)")
        checkbox_layout.addWidget(self.unbind_checkbox)

        self.information_checkbox = QCheckBox("Verbose")
        self.information_checkbox.setStyleSheet(checkbox_style)
        self.information_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.information_checkbox.setToolTip("Show more information for debugging")
        checkbox_layout.addWidget(self.information_checkbox)

        self.latency_checkbox = QCheckBox("Latency Test")
        self.latency_checkbox.setStyleSheet(checkbox_style)
        self.latency_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.latency_checkbox.setToolTip("Run latency test")
        checkbox_layout.addWidget(self.latency_checkbox)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        checkbox_layout.addSpacerItem(spacer)
        layout.addLayout(checkbox_layout)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        file_path_widget, self.file_path_input = self.create_file_input("YAML File Path:", "browse_file",
                                                                        "Generate PCAP",
                                                                        "push_command")
        input_layout.addLayout(file_path_widget)

        yaml_widget, self.yaml_input = self.create_file_input("Execution YAML Path:", "browse_yaml_file")
        input_layout.addLayout(yaml_widget)

        m_widget, self.m_input = self.create_input_field("Rate Multiplier:", "Enter rate multiplier value")
        input_layout.addLayout(m_widget)

        active_flows_widget, self.active_flows_input = self.create_input_field("Active Flows:",
                                                                               "Enter active flows value (optional)")
        input_layout.addLayout(active_flows_widget)

        core_widget, self.core_input = self.create_input_field("Cores:", "Enter number of cores (optional)")
        input_layout.addLayout(core_widget)

        layout.addLayout(input_layout)

        input_layout_2 = QHBoxLayout()
        input_layout_2.setSpacing(5)

        duration_widget, self.duration = self.create_input_field("Duration:", "Enter duration (optional)")
        input_layout_2.addLayout(duration_widget)

        mbuf_widget, self.mbuf = self.create_input_field("Mbuf:", "Increase mbuf count (optional)")
        input_layout_2.addLayout(mbuf_widget)

        log_widget, self.log = self.create_file_input("Log File:", "browse_file_log")
        input_layout_2.addLayout(log_widget)

        wait_widget, self.wait = self.create_input_field("Wait:", "Wait time between startup and traffic sending")
        self.wait.setToolTip("Default: 1 second")
        input_layout_2.addLayout(wait_widget)

        cfg_widget, self.cfg_input = self.create_file_input("TRex Config:", "browse_file_config")
        input_layout_2.addLayout(cfg_widget)

        layout.addLayout(input_layout_2)

        self.output_label = QLabel("Output:")
        layout.addWidget(self.output_label)

        self.output_text = QTextBrowser()
        self.output_text.setOpenExternalLinks(True)

        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        self.output_text.setFont(font)

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

        browse_vbox = QVBoxLayout()
        browse_vbox.setSpacing(0)
        browse_vbox.addWidget(QLabel(""))

        browse_btn = QPushButton("...")
        browse_btn.setFixedSize(30, 27)
        if browse_method:
            browse_btn.clicked.connect(getattr(self, browse_method))
        browse_vbox.addWidget(browse_btn)
        layout.addLayout(browse_vbox)

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

    def browse_yaml_file(self):
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
        if not self.validate_connection():
            return

        try:
            yaml_path = self.sanitize_input(self.yaml_input.text())
            if not yaml_path:
                yaml_path = "/root/defualt_trex_khosrow/multi_flow_khosrow_1.yaml"
                self.append_info(f"Using default YAML path: {yaml_path}")

            m_value = self.sanitize_input(self.m_input.text()) or "1"

            cmd_parts = ['./t-rex-64', '-f', yaml_path, '-m', m_value]

            if self.prom_checkbox.isChecked():
                cmd_parts.append('--prom')

            active_flows = self.sanitize_input(self.active_flows_input.text())
            if active_flows:
                cmd_parts.append(f'--active-flows {active_flows}')

            core_value = self.sanitize_input(self.core_input.text())
            if core_value:
                cmd_parts.append(f'-c {core_value}')

            cfg_value = self.sanitize_input(self.cfg_input.text())
            if cfg_value:
                cmd_parts.append(f'--cfg {cfg_value}')

            if self.rx_check_checkbox.isChecked():
                cmd_parts.append('--rx-check log')

            if self.queue_drop_checkbox.isChecked():
                cmd_parts.append('--queue-drop')

            if self.sym_checkbox.isChecked():
                cmd_parts.append('--flip')

            if self.ipv6_checkbox.isChecked():
                cmd_parts.append('--ipv6')

            if self.unbind_checkbox.isChecked():
                cmd_parts.append('--unbind-unused-ports')

            time_value = self.sanitize_input(self.duration.text())
            if time_value:
                cmd_parts.append(f'-d {time_value}')

            mbuf_value = self.sanitize_input(self.mbuf.text())
            if mbuf_value:
                cmd_parts.append(f'--mbuf-factor {mbuf_value}')

            if self.information_checkbox.isChecked():
                cmd_parts.append('-v 8')

            if self.latency_checkbox.isChecked():
                cmd_parts.append('--lo -l 1000')

            log_value = self.sanitize_input(self.log.text())
            if log_value:
                cmd_parts.append(f'--rpc-log {log_value}')

            wait_value = self.sanitize_input(self.wait.text())
            if wait_value:
                cmd_parts.append(f'-w {wait_value}')

            command = ' '.join(cmd_parts)

            script = f"""#!/bin/bash
tmux has-session -t khosrow_trex 2>/dev/null && tmux kill-session -t khosrow_trex

rm -f /tmp/trex_output.log
touch /tmp/trex_output.log

echo "Creating tmux session and starting TRex..."
tmux new-session -d -s khosrow_trex

tmux set -t khosrow_trex remain-on-exit on
tmux set -t khosrow_trex status off

tmux pipe-pane -t khosrow_trex -o "cat >> /tmp/trex_output.log"

tmux send-keys -t khosrow_trex 'cd /root/{self.trex_version}/' C-m
tmux send-keys -t khosrow_trex '{command}' C-m

echo ""
echo "==========================================="
echo "         Starting TRex...                   "
echo "==========================================="
echo ""

while true; do
    if [ -f /tmp/trex_output.log ]; then
        cat /tmp/trex_output.log 2>/dev/null
        > /tmp/trex_output.log
    fi

    if ! tmux has-session -t khosrow_trex 2>/dev/null; then
        echo ""
        echo "Tmux session ended"
        break
    fi

    sleep 1
done

echo ""
echo "==========================================="
echo "Tmux session 'khosrow_trex' is running"
echo "To attach to tmux: tmux attach -t khosrow_trex"
echo "To view output: tail -f /tmp/trex_output.log"
echo "==========================================="
"""

            self.append_success("Starting TRex session in Stateful mode...")
            self.append_info("Tmux output will be displayed in real-time...")

            def on_output(line):
                self.process_tmux_output(line)

            self.execute_remote_script(script, output_callback=on_output)

        except Exception as e:
            self.append_error(str(e))

    def process_tmux_output(self, output):
        lines = output.split('\n')

        for line in lines:
            if not line.strip():
                self.append_output(" ", special=True)
                continue

            clean_line = self.clean_ansi_codes(line)
            clean_line = clean_line.replace('\r', '')

            if "cd " in clean_line or "./t-rex-64" in clean_line:
                self.append_output(f"$ {clean_line}", color="#569cd6")

            elif any(keyword in clean_line for keyword in ["opackets", "ipackets", "obytes", "ibytes",
                                                           "errors", "oerrors", "Tx Bw", "ports"]):
                self.append_output(clean_line, special=True)

            elif "════════" in clean_line or "────" in clean_line or "━━━━" in clean_line:
                self.append_output(clean_line, color="#888888")

            elif ":" in clean_line and any(stat in clean_line for stat in ["Cpu Utilization", "Platform_factor",
                                                                           "Total-Tx", "Total-Rx", "Total-PPS",
                                                                           "Total-CPS", "Expected-PPS", "Expected-CPS",
                                                                           "Expected-BPS", "Active-flows", "Open-flows",
                                                                           "drop-rate", "current time", "test duration",
                                                                           "Socket-util", "Socket/clients"]):
                self.append_output(clean_line, color="#ce9178")

            elif clean_line.strip() == "ports" or clean_line.strip().startswith("ports "):
                self.append_output(clean_line, bold=True)

            elif re.match(r'^\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*$', clean_line) or \
                    re.match(r'^\s*\d+\s*\|\s*\d+\s*$', clean_line):
                self.append_output(clean_line, color="#b5cea8")

            elif "Error" in clean_line:
                self.append_output(f"{clean_line}", color="#f48771")
            elif "Warning" in clean_line or "danger!!" in clean_line:
                self.append_output(f"danger!! {clean_line}", color="#dcdcaa")
            elif "success" in clean_line.lower() or "complete" in clean_line.lower():
                self.append_output(f"{clean_line}", color="#6a9955")
            elif "tmux" in clean_line.lower() and "attach" in clean_line.lower():
                self.append_output(clean_line, color="#9cdcfe")
            elif "TRex" in clean_line and "starting" in clean_line.lower():
                self.append_output(f" {clean_line}", color="#4ec9b0")
            else:
                self.append_output(clean_line)

    def append_output(self, text, color=None, bold=False, special=False):
        if not self.output_text:
            return

        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        style = "font-family: 'Courier New', monospace;"
        if color:
            style += f" color: {color};"
        if bold:
            style += " font-weight: bold;"

        if special:
            formatted_text = f"<pre style='margin:0; padding:0; {style}'>{text}</pre>"
        else:
            formatted_text = f"<span style='{style}'>{text}</span>"

        self.output_text.append(formatted_text)

        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def append_success(self, text):
        self.append_output(text, color="#6a9955")

    def append_error(self, text):
        self.append_output(f"{text}", color="#f48771")

    def append_info(self, text):
        self.append_output(f"{text}", color="#9cdcfe")

    def stop_command(self):
        if not self.validate_connection():
            return

        try:
            script = """#!/bin/bash
echo "==========================================="
echo "         Stopping TRex...                   "
echo "==========================================="

pkill -f ./_t-rex-64 && echo "t-rex-64 process stopped" || echo "t-rex-64 process not found"

tmux kill-session -t khosrow_trex 2>/dev/null && echo "tmux session stopped" || echo "tmux session not found"

rm -f /tmp/trex_output.log 2>/dev/null

echo ""
echo "Stop operation completed."
echo "==========================================="
"""

            def on_output(line):
                self.append_output(line, special=True)

            self.execute_remote_script(script, output_callback=on_output)
            self.append_success("TRex process and session stopped.")

        except Exception as e:
            self.append_error(str(e))

    def push_command(self):
        if not self.validate_connection():
            return

        try:
            file_path = self.sanitize_input(self.file_path_input.text())
            if not file_path:
                file_path = "/root/defualt_trex_khosrow/dns.yaml"
                self.append_info(f"Using default path: {file_path}")

            script = f"""#!/bin/bash
echo "Starting PCAP generation from file: {file_path}"
echo "----------------------------------------"

cd /root/{self.trex_version}/

if [ ! -f "{file_path}" ]; then
    echo "Error: File {file_path} does not exist!"
    exit 1
fi

echo "Running bp-sim-64 ..."
./bp-sim-64 -f "{file_path}" -o Successfully_Pcap_Generated.pcap

if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo " PCAP file created successfully:"
    echo " /root/{self.trex_version}/Successfully_Pcap_Generated.pcap"
    echo ""
    echo "Generated file info:"
    ls -lh Successfully_Pcap_Generated.pcap
else
    echo "Error generating PCAP file"
    exit 1
fi
"""

            self.append_success("Generating PCAP file...")

            def on_output(line):
                self.process_tmux_output(line)

            self.execute_remote_script(script, output_callback=on_output)

        except Exception as e:
            self.append_error(str(e))