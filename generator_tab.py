# generator_tab.py
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QCheckBox, QLabel, QTextBrowser,
                             QDialog, QComboBox, QDialogButtonBox,
                             QListWidget, QListWidgetItem, QFormLayout, QApplication,
                             QGroupBox, QScrollArea, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFont, QTextOption, QColor, QPalette
from dialogs import HostFileDialog
from base_tab import BaseTRexTab
import re



QApplication.setEffectEnabled(Qt.UI_AnimateTooltip, True)
QApplication.setEffectEnabled(Qt.UI_FadeTooltip, True)


class PCAPParamsDialog(QDialog):
    """PCAP settings dialog"""

    def __init__(self, pcap_file="", parent=None, existing_params=None):
        super().__init__(parent)
        self.setWindowTitle("PCAP Settings")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)

        self.pcap_file = pcap_file
        self.params = existing_params or {}

        layout = QVBoxLayout()

        # Display file name
        if pcap_file:
            file_label = QLabel(f"<b>PCAP File:</b> {pcap_file}")
            file_label.setWordWrap(True)
            file_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
            layout.addWidget(file_label)

        # Settings form with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setVerticalSpacing(10)

        # Input fields with tooltips
        # CPS
        self.cps_input = QLineEdit(self.params.get('cps', '1.0'))
        self.cps_input.setToolTip("Connections per second - this value is multiplied by rate multiplier")
        self.cps_input.setPlaceholderText("Example: 1.0")
        form_layout.addRow("CPS (Connections/sec):", self.cps_input)

        # IPG
        self.ipg_input = QLineEdit(self.params.get('ipg', '1000'))
        self.ipg_input.setToolTip("Inter-packet gap (microseconds)")
        self.ipg_input.setPlaceholderText("Example: 1000")
        form_layout.addRow("IPG (microseconds):", self.ipg_input)

        # RTT
        self.rtt_input = QLineEdit(self.params.get('rtt', '1000'))
        self.rtt_input.setToolTip("Round trip time (microseconds) - usually equal to IPG")
        self.rtt_input.setPlaceholderText("Example: 1000")
        form_layout.addRow("RTT (microseconds):", self.rtt_input)

        # Weight
        self.w_input = QLineEdit(self.params.get('w', '1'))
        self.w_input.setToolTip("Weight - number of consecutive flows from one template")
        self.w_input.setPlaceholderText("Example: 1")
        form_layout.addRow("Weight:", self.w_input)

        # Limit
        self.limit_input = QLineEdit(self.params.get('limit', ''))
        self.limit_input.setPlaceholderText("Optional - Example: 200")
        self.limit_input.setToolTip("Number of flows (optional)")
        form_layout.addRow("Limit:", self.limit_input)

        # Separator
        line = QLabel("")
        line.setStyleSheet("border-bottom: 1px solid #ccc;")
        form_layout.addRow(line)

        # One App Server
        self.one_app_server_check = QCheckBox()
        self.one_app_server_check.setChecked(self.params.get('one_app_server', False))
        self.one_app_server_check.setToolTip("All flows use one server")
        form_layout.addRow("One App Server:", self.one_app_server_check)

        # Server Address
        self.server_addr_input = QLineEdit(self.params.get('server_addr', ''))
        self.server_addr_input.setPlaceholderText("Optional - Example: 48.0.0.7")
        self.server_addr_input.setToolTip("Server address (only if One App Server is selected)")
        self.server_addr_input.setVisible(self.one_app_server_check.isChecked())
        form_layout.addRow("Server Address:", self.server_addr_input)

        # Multi Flow Enabled
        self.multi_flow_enabled_check = QCheckBox()
        self.multi_flow_enabled_check.setChecked(self.params.get('multi_flow_enabled', False))
        self.multi_flow_enabled_check.setToolTip("Enable multiple flows in template")
        form_layout.addRow("Multi Flow:", self.multi_flow_enabled_check)

        # Flows Directions
        self.flows_dirs_input = QLineEdit(self.params.get('flows_dirs', '[0, 1]'))
        self.flows_dirs_input.setToolTip("Flow directions (0 = client to server, 1 = server to client)")
        self.flows_dirs_input.setVisible(self.multi_flow_enabled_check.isChecked())
        self.flows_dirs_input.setPlaceholderText("Example: [0, 1]")
        form_layout.addRow("Flow Directions:", self.flows_dirs_input)

        # Keep Source Port
        self.keep_src_port_check = QCheckBox()
        self.keep_src_port_check.setChecked(self.params.get('keep_src_port', False))
        self.keep_src_port_check.setToolTip("Keep original source port from PCAP file")
        form_layout.addRow("Keep Source Port:", self.keep_src_port_check)

        # IP Header Offset
        self.ip_header_offset_input = QLineEdit(str(self.params.get('ip_header_offset', '0')))
        self.ip_header_offset_input.setToolTip("New IP header offset (bytes)")
        self.ip_header_offset_input.setPlaceholderText("Example: 0")
        form_layout.addRow("IP Header Offset:", self.ip_header_offset_input)

        # Max IP Tunnels
        self.max_ip_tunnels_input = QLineEdit(str(self.params.get('max_ip_tunnels', '1000')))
        self.max_ip_tunnels_input.setToolTip("Maximum number of IP tunnels")
        self.max_ip_tunnels_input.setPlaceholderText("Example: 1000")
        form_layout.addRow("Max IP Tunnels:", self.max_ip_tunnels_input)

        # Connect signals
        self.one_app_server_check.toggled.connect(self.toggle_server_addr)
        self.multi_flow_enabled_check.toggled.connect(self.toggle_flows_dirs)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Button styles
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("OK")
        ok_button.setStyleSheet("background-color: green; color: white; padding: 5px;")

        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("Cancel")
        cancel_button.setStyleSheet("background-color: red; color: white; padding: 5px;")

        layout.addWidget(button_box)

        self.setLayout(layout)

    def toggle_server_addr(self, checked):
        """Show/hide server address field"""
        self.server_addr_input.setVisible(checked)
        if not checked:
            self.server_addr_input.clear()

    def toggle_flows_dirs(self, checked):
        """Show/hide flow directions field"""
        self.flows_dirs_input.setVisible(checked)
        if not checked:
            self.flows_dirs_input.setText('[0, 1]')

    def validate_inputs(self):
        """Validate inputs"""
        try:
            # Check numbers
            float(self.cps_input.text())
            float(self.ipg_input.text())
            float(self.rtt_input.text())
            float(self.w_input.text())

            if self.limit_input.text():
                int(self.limit_input.text())

            if self.ip_header_offset_input.text():
                int(self.ip_header_offset_input.text())

            if self.max_ip_tunnels_input.text():
                int(self.max_ip_tunnels_input.text())

            return True
        except ValueError as e:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values.")
            return False

    def get_params(self):
        """Get entered parameters"""
        if not self.validate_inputs():
            return None

        params = {
            'cps': self.cps_input.text().strip(),
            'ipg': self.ipg_input.text().strip(),
            'rtt': self.rtt_input.text().strip(),
            'w': self.w_input.text().strip(),
            'limit': self.limit_input.text().strip() if self.limit_input.text().strip() else None,
            'one_app_server': self.one_app_server_check.isChecked(),
            'server_addr': self.server_addr_input.text().strip() if self.server_addr_input.text().strip() else None,
            'multi_flow_enabled': self.multi_flow_enabled_check.isChecked(),
            'flows_dirs': self.flows_dirs_input.text().strip() if self.multi_flow_enabled_check.isChecked() else None,
            'keep_src_port': self.keep_src_port_check.isChecked(),
            'ip_header_offset': self.ip_header_offset_input.text().strip(),
            'max_ip_tunnels': self.max_ip_tunnels_input.text().strip()
        }
        return params


class GeneratorTab(BaseTRexTab):
    """YAML Generator Tab"""

    def __init__(self):
        super().__init__()
        self.pcap_files = []
        self.output_timer = None
        self.last_output_size = 0
        self.initUI()

    def initUI(self):
        # Use Scroll Area for small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)

        # Main buttons
        button_layout = QHBoxLayout()

        self.generate_button = QPushButton("Generate YAML")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_button.clicked.connect(self.generate_yaml)
        button_layout.addWidget(self.generate_button)

        self.save_button = QPushButton("Save to File")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.save_button.clicked.connect(self.save_to_file)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        # Main settings group
        main_group = QGroupBox("Main Settings")
        main_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        main_form = QVBoxLayout()

        # Duration
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration (seconds):")
        duration_label.setMinimumWidth(120)
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Example: 10.0")
        self.duration_input.setToolTip("Test duration")
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_input)
        main_form.addLayout(duration_layout)

        # Distribution
        distribution_layout = QHBoxLayout()
        distribution_label = QLabel("Distribution:")
        distribution_label.setMinimumWidth(120)
        self.distribution_combo = QComboBox()
        self.distribution_combo.addItems(["Sequential (seq)", "Random (random)"])
        self.distribution_combo.setToolTip("Flow distribution type")
        distribution_layout.addWidget(distribution_label)
        distribution_layout.addWidget(self.distribution_combo)
        main_form.addLayout(distribution_layout)

        main_group.setLayout(main_form)
        layout.addWidget(main_group)

        # IP range group
        ip_group = QGroupBox("IP Range")
        ip_group.setStyleSheet(main_group.styleSheet())
        ip_form = QVBoxLayout()

        # Client IP range
        client_ip_layout = QHBoxLayout()
        client_start_label = QLabel("Client Start IP:")
        client_start_label.setMinimumWidth(120)
        self.client_start_input = QLineEdit()
        self.client_start_input.setPlaceholderText("Example: 16.0.0.1")
        self.client_start_input.setToolTip("Start IP address for clients")
        client_ip_layout.addWidget(client_start_label)
        client_ip_layout.addWidget(self.client_start_input)


        client_end_label = QLabel("Client End IP:")
        client_end_label.setMinimumWidth(120)
        self.client_end_input = QLineEdit()
        self.client_end_input.setPlaceholderText("Example: 16.0.1.255")
        self.client_end_input.setToolTip("End IP address for clients")
        client_ip_layout.addWidget(client_end_label)
        client_ip_layout.addWidget(self.client_end_input)
        ip_form.addLayout(client_ip_layout)

        # Server IP range
        server_ip_layout = QHBoxLayout()
        server_start_label = QLabel("Server Start IP:")
        server_start_label.setMinimumWidth(120)
        self.server_start_input = QLineEdit()
        self.server_start_input.setPlaceholderText("Example: 48.0.0.1")
        self.server_start_input.setToolTip("Start IP address for servers")
        server_ip_layout.addWidget(server_start_label)
        server_ip_layout.addWidget(self.server_start_input)

        server_end_label = QLabel("Server End IP:")
        server_end_label.setMinimumWidth(120)
        self.server_end_input = QLineEdit()
        self.server_end_input.setPlaceholderText("Example: 48.0.0.255")
        self.server_end_input.setToolTip("End IP address for servers")
        server_ip_layout.addWidget(server_end_label)
        server_ip_layout.addWidget(self.server_end_input)
        ip_form.addLayout(server_ip_layout)

        ip_group.setLayout(ip_form)
        layout.addWidget(ip_group)

        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_group.setStyleSheet(main_group.styleSheet())
        advanced_form = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()

        clients_per_gb_layout = QHBoxLayout()
        clients_per_gb_label = QLabel("Clients per GB:")
        clients_per_gb_label.setMinimumWidth(120)
        self.clients_per_gb_input = QLineEdit()
        self.clients_per_gb_input.setPlaceholderText("Example: 201")
        self.clients_per_gb_input.setToolTip("Number of clients per GB of memory")
        clients_per_gb_layout.addWidget(clients_per_gb_label)
        clients_per_gb_layout.addWidget(self.clients_per_gb_input)
        left_column.addLayout(clients_per_gb_layout)

        min_clients_layout = QHBoxLayout()
        min_clients_label = QLabel("Minimum Clients:")
        min_clients_label.setMinimumWidth(120)
        self.min_clients_input = QLineEdit()
        self.min_clients_input.setPlaceholderText("Example: 101")
        self.min_clients_input.setToolTip("Minimum number of clients")
        min_clients_layout.addWidget(min_clients_label)
        min_clients_layout.addWidget(self.min_clients_input)
        left_column.addLayout(min_clients_layout)

        advanced_form.addLayout(left_column)

        # Right column
        right_column = QVBoxLayout()

        dual_port_layout = QHBoxLayout()
        dual_port_label = QLabel("Dual Port Mask:")
        dual_port_label.setMinimumWidth(120)
        self.dual_port_input = QLineEdit()
        self.dual_port_input.setPlaceholderText("Example: 1.0.0.0")
        self.dual_port_input.setToolTip("Mask for dual ports")
        dual_port_layout.addWidget(dual_port_label)
        dual_port_layout.addWidget(self.dual_port_input)
        right_column.addLayout(dual_port_layout)

        tcp_aging_layout = QHBoxLayout()
        tcp_aging_label = QLabel("TCP Aging:")
        tcp_aging_label.setMinimumWidth(120)
        self.tcp_aging_input = QLineEdit()
        self.tcp_aging_input.setPlaceholderText("Example: 1")
        self.tcp_aging_input.setToolTip("TCP connection aging time")
        tcp_aging_layout.addWidget(tcp_aging_label)
        tcp_aging_layout.addWidget(self.tcp_aging_input)
        right_column.addLayout(tcp_aging_layout)

        advanced_form.addLayout(right_column)

        advanced_group.setLayout(advanced_form)
        layout.addWidget(advanced_group)

        # PCAP files group
        pcap_group = QGroupBox("PCAP Files")
        pcap_group.setStyleSheet(main_group.styleSheet())
        pcap_form = QVBoxLayout()

        # PCAP file list
        self.pcap_list_widget = QListWidget()
        self.pcap_list_widget.setStyleSheet("""
            QListWidget {
                font-family: 'Courier New';
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 150px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:selected {
                background-color: #264f78;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        pcap_form.addWidget(self.pcap_list_widget)

        # PCAP management buttons
        pcap_buttons_layout = QHBoxLayout()

        self.add_pcap_button = QPushButton("Add PCAP")
        self.add_pcap_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_pcap_button.clicked.connect(self.add_pcap_file)
        pcap_buttons_layout.addWidget(self.add_pcap_button)

        self.remove_pcap_button = QPushButton("Remove Selected")
        self.remove_pcap_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.remove_pcap_button.clicked.connect(self.remove_selected_pcap)
        pcap_buttons_layout.addWidget(self.remove_pcap_button)

        self.edit_pcap_button = QPushButton("Edit Selected")
        self.edit_pcap_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
        """)
        self.edit_pcap_button.clicked.connect(self.edit_selected_pcap)
        pcap_buttons_layout.addWidget(self.edit_pcap_button)

        pcap_form.addLayout(pcap_buttons_layout)

        pcap_group.setLayout(pcap_form)
        layout.addWidget(pcap_group)

        # Output
        self.output_label = QLabel("Generated YAML:")
        self.output_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #d4d4d4;")
        layout.addWidget(self.output_label)

        self.output_text = QTextBrowser()
        self.output_text.setOpenExternalLinks(True)

        # Set monospace font for terminal-like display
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        self.output_text.setFont(font)

        # Disable line wrapping to preserve formatting
        self.output_text.setLineWrapMode(QTextBrowser.NoWrap)

        # Terminal-like dark theme
        self.output_text.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                min-height: 200px;
            }
        """)

        # Clear any existing content
        self.output_text.clear()

        layout.addWidget(self.output_text)

        scroll.setWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def add_pcap_file(self):
        """Add new PCAP file"""
        if not self.validate_connection():
            return

        try:
            initial_path = f"/root/{self.trex_version}"
            file_dialog = HostFileDialog(self.ssh_client, initial_path, self)

            if file_dialog.exec_() == QDialog.Accepted:
                selected_file = file_dialog.selected_file()
                if selected_file:
                    # Show settings dialog
                    dialog = PCAPParamsDialog(selected_file, self)

                    if dialog.exec_() == QDialog.Accepted:
                        params = dialog.get_params()
                        if params:
                            params['name'] = selected_file
                            self.pcap_files.append(params)
                            self.update_pcap_list()
                            self.append_success(f"File {selected_file} added successfully")

        except Exception as e:
            self.append_error(f"Error adding file: {str(e)}")

    def remove_selected_pcap(self):
        """Remove selected PCAP file"""
        selected_items = self.pcap_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No file selected for removal.")
            return

        # Confirm removal
        reply = QMessageBox.question(self, 'Confirm Removal',
                                     'Are you sure you want to remove the selected file(s)?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Remove in reverse order to avoid index issues
            for item in reversed(selected_items):
                index = self.pcap_list_widget.row(item)
                if 0 <= index < len(self.pcap_files):
                    del self.pcap_files[index]

            self.update_pcap_list()
            self.append_success("Selected file(s) removed successfully")

    def edit_selected_pcap(self):
        """Edit selected PCAP file settings"""
        selected_items = self.pcap_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No file selected for editing.")
            return

        if len(selected_items) > 1:
            QMessageBox.warning(self, "Warning", "Please select only one file to edit.")
            return

        index = self.pcap_list_widget.row(selected_items[0])
        if not (0 <= index < len(self.pcap_files)):
            self.append_error("Error: Invalid selection")
            return

        pcap_info = self.pcap_files[index]

        dialog = PCAPParamsDialog(pcap_info['name'], self, pcap_info)

        if dialog.exec_() == QDialog.Accepted:
            params = dialog.get_params()
            if params:
                params['name'] = pcap_info['name']
                self.pcap_files[index] = params
                self.update_pcap_list()
                self.append_success("Settings updated successfully")

    def update_pcap_list(self):
        """Update PCAP list display"""
        self.pcap_list_widget.clear()
        for i, pcap in enumerate(self.pcap_files, 1):
            # Build summary text
            summary = f"{i}. {pcap['name']}\n"
            summary += f"    CPS: {pcap['cps']} |  IPG: {pcap['ipg']} | RTT: {pcap['rtt']} | W: {pcap['w']}"

            # Add extra info if available
            extra_info = []
            if pcap.get('limit'):
                extra_info.append(f"Limit: {pcap['limit']}")
            if pcap.get('server_addr'):
                extra_info.append(f"Server: {pcap['server_addr']}")
            if pcap.get('one_app_server'):
                extra_info.append("OneApp")
            if pcap.get('multi_flow_enabled'):
                extra_info.append("MultiFlow")
            if pcap.get('keep_src_port'):
                extra_info.append("KeepSrc")

            if extra_info:
                summary += f"\n   {', '.join(extra_info)}"

            item = QListWidgetItem(summary)
            self.pcap_list_widget.addItem(item)

    def generate_yaml(self):
        """Generate YAML content"""
        try:
            yaml_content = self._build_yaml_content()
            self.output_text.clear()
            self.append_output(yaml_content, special=True)
            self.append_success("YAML generated successfully")
        except Exception as e:
            self.append_error(f"Error generating YAML: {str(e)}")

    def save_to_file(self):
        """Save YAML to file on server"""
        if not self.validate_connection():
            return

        try:
            yaml_content = self._build_yaml_content()

            # Get filename from user
            dialog = QDialog(self)
            dialog.setWindowTitle("Save YAML File")
            dialog.setModal(True)

            layout = QVBoxLayout()
            layout.setSpacing(10)

            label = QLabel("Enter filename:")
            label.setStyleSheet("font-weight: bold; color: black;")

            filename_input = QLineEdit()
            filename_input.setPlaceholderText("Example: my_config.yaml")
            filename_input.setToolTip("Filename to save on server")

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

            # Button styles
            ok_button = buttons.button(QDialogButtonBox.Ok)
            ok_button.setText("Save")
            ok_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")

            cancel_button = buttons.button(QDialogButtonBox.Cancel)
            cancel_button.setText("Cancel")
            cancel_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)

            layout.addWidget(label)
            layout.addWidget(filename_input)
            layout.addWidget(buttons)

            dialog.setLayout(layout)

            if dialog.exec_() == QDialog.Accepted and filename_input.text():
                filename = filename_input.text().strip()
                if not filename.endswith('.yaml') and not filename.endswith('.yml'):
                    filename += '.yaml'

                full_path = f"/root/{self.trex_version}/{filename}"

                # Save on server (escape special characters)
                yaml_escaped = yaml_content.replace("'", "'\\''")
                ssh_command = f"echo '{yaml_escaped}' > '{full_path}'"
                output = self.ssh_client.execute_command(ssh_command)

                self.append_success(f"YAML file saved to: {full_path}")
                if output and "error" not in output.lower():
                    self.append_output(output, special=True)

        except Exception as e:
            self.append_error(f"Error saving file: {str(e)}")

    def _build_yaml_content(self):
        """Build YAML content from parameters"""
        # Main parameters with defaults
        duration = self.sanitize_input(self.duration_input.text()) or "10.0"

        # Convert combo box text to value
        distribution_text = self.distribution_combo.currentText()
        distribution = "seq" if "Sequential" in distribution_text else "random"

        client_start = self.sanitize_input(self.client_start_input.text()) or "16.0.0.1"
        client_end = self.sanitize_input(self.client_end_input.text()) or "16.0.1.255"
        server_start = self.sanitize_input(self.server_start_input.text()) or "48.0.0.1"
        server_end = self.sanitize_input(self.server_end_input.text()) or "48.0.0.255"

        clients_per_gb = self.sanitize_input(self.clients_per_gb_input.text()) or "201"
        min_clients = self.sanitize_input(self.min_clients_input.text()) or "101"
        dual_port_mask = self.sanitize_input(self.dual_port_input.text()) or "1.0.0.0"
        tcp_aging = self.sanitize_input(self.tcp_aging_input.text()) or "1"
        udp_aging = tcp_aging  # Assume same as TCP

        # Build YAML
        yaml_lines = [
            f"- duration : {duration}",
            "  generator :",
            f'          distribution : "{distribution}"',
            f'          clients_start : "{client_start}"',
            f'          clients_end   : "{client_end}"',
            f'          servers_start : "{server_start}"',
            f'          servers_end   : "{server_end}"',
            f'          clients_per_gb : {clients_per_gb}',
            f'          min_clients    : {min_clients}',
            f'          dual_port_mask : "{dual_port_mask}"',
            f'          tcp_aging      : {tcp_aging}',
            f'          udp_aging      : {udp_aging}',
            "  cap_info :"
        ]

        # Add PCAP files
        if not self.pcap_files:
            # Use default sample if no files added
            yaml_lines.extend([
                "    - name: /root/cap2/dns.pcap",
                "      cps : 1.0",
                "      ipg : 1000",
                "      rtt : 1000",
                "      w   : 1"
            ])
            self.append_info("No PCAP files added. Using default sample.")
        else:
            for pcap in self.pcap_files:
                yaml_lines.append(f"    - name: {pcap['name']}")
                yaml_lines.append(f"      cps : {pcap['cps']}")
                yaml_lines.append(f"      ipg : {pcap['ipg']}")
                yaml_lines.append(f"      rtt : {pcap['rtt']}")
                yaml_lines.append(f"      w   : {pcap['w']}")

                if pcap.get('limit'):
                    yaml_lines.append(f"      limit : {pcap['limit']}")
                if pcap.get('server_addr'):
                    yaml_lines.append(f'      server_addr : "{pcap["server_addr"]}"')
                if pcap.get('one_app_server'):
                    yaml_lines.append("      one_app_server : true")
                if pcap.get('multi_flow_enabled'):
                    yaml_lines.append("      multi_flow_enabled : true")
                    if pcap.get('flows_dirs'):
                        yaml_lines.append(f"      flows_dirs : {pcap['flows_dirs']}")
                if pcap.get('keep_src_port'):
                    yaml_lines.append("      keep_src_port : true")
                if pcap.get('ip_header_offset') and pcap['ip_header_offset'] != '0':
                    yaml_lines.append(f"      ip_header_offset : {pcap['ip_header_offset']}")
                if pcap.get('max_ip_tunnels') and pcap['max_ip_tunnels'] != '1000':
                    yaml_lines.append(f"      max_ip_tunnels : {pcap['max_ip_tunnels']}")

        return "\n".join(yaml_lines)

    def validate_connection(self):
        """Check SSH connection"""
        if not hasattr(self, 'ssh_client') or not self.ssh_client:
            QMessageBox.warning(self, "Error",
                                "SSH connection not established.\n"
                                "Please connect via File > Connect to Server first.")
            return False
        return True

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
            # For preserving spaces (like YAML), use pre tag
            formatted_text = f"<pre style='margin:0; padding:0; {style}'>{text}</pre>"
        else:
            formatted_text = f"<span style='{style}'>{text}</span>"

        self.output_text.append(formatted_text)

        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def append_success(self, text):
        """Add success message"""
        self.append_output(f"✅ {text}", color="#6a9955")

    def append_error(self, text):
        """Add error message"""
        self.append_output(f"❌ {text}", color="#f48771")

    def append_info(self, text):
        """Add info message"""
        self.append_output(f"ℹ️ {text}", color="#9cdcfe")

    def clean_ansi_codes(self, text):
        """Remove ANSI codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        return text
