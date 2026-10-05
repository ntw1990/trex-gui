import os
import re
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, \
    QDialogButtonBox, QMessageBox, QFormLayout, QComboBox
from PyQt5.QtCore import Qt
import posixpath


class HostFileDialog(QDialog):
    def __init__(self, ssh_client, initial_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select or Create File")
        self.setGeometry(200, 200, 600, 400)

        self.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                }
                QLabel {
                    color: #d4d4d4;
                }
                QListWidget {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555;
                }
                QListWidget::item:selected {
                    background-color: #264f78;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555;
                    padding: 3px;
                }
            """)

        self.ssh_client = ssh_client
        self.current_path = initial_path

        layout = QVBoxLayout(self)

        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.navigate_to_parent)
        nav_layout.addWidget(self.back_button)

        self.create_button = QPushButton("Create New File")
        self.create_button.clicked.connect(self.create_new_file)
        nav_layout.addWidget(self.create_button)

        layout.addLayout(nav_layout)

        self.file_list_widget = QListWidget(self)
        self.file_list_widget.itemDoubleClicked.connect(self.navigate_into_directory)
        layout.addWidget(self.file_list_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.load_directory_contents()

    def load_directory_contents(self):
        self.file_list_widget.clear()

        try:
            clean_path = re.sub(r'<[^>]+>', '', str(self.current_path)).strip()
            if "\n" in clean_path:
                clean_path = clean_path.split("\n")[-1].strip()

            output, error = self.ssh_client.execute_command_raw(f"ls -p '{clean_path}'")

            if error:
                QMessageBox.warning(self, "Error", f"Error listing directory: {error}")
                return

            raw_items = []
            for line in output.split("\n"):
                line_str = line.strip()
                if line_str:
                    raw_items.append(line_str)

            directories = sorted([item for item in raw_items if item.endswith("/")])
            files = sorted([item for item in raw_items if not item.endswith("/")])

            for item in directories + files:
                self.file_list_widget.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error listing directory: {str(e)}")

    def navigate_to_parent(self):
        if self.current_path != "/":
            self.current_path = posixpath.dirname(self.current_path) or "/"
            self.load_directory_contents()

    def navigate_into_directory(self, item):
        selected_item = item.text().strip()
        if selected_item.endswith("/"):
            clean_current = re.sub(r'<[^>]+>', '', str(self.current_path)).strip()
            if "\n" in clean_current:
                clean_current = clean_current.split("\n")[-1].strip()

            new_path = posixpath.join(clean_current, selected_item[:-1])
            self.current_path = new_path
            self.load_directory_contents()

    def create_new_file(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New File")

        layout = QVBoxLayout()
        label = QLabel("Enter file name:")
        self.new_filename_input = QLineEdit()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(label)
        layout.addWidget(self.new_filename_input)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted and self.new_filename_input.text():
            new_filename = self.new_filename_input.text().strip()
            full_path = posixpath.join(self.current_path, new_filename)

            try:
                self.ssh_client.execute_command(f"touch '{full_path}'")
                self.load_directory_contents()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error creating file: {str(e)}")

    def selected_file(self):
        selected_items = self.file_list_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0].text()
            if not selected_item.endswith("/"):
                return posixpath.join(self.current_path, selected_item)
        return None


class SSHLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Server Login")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.host_input = QLineEdit(self)
        self.host_input.setPlaceholderText("Example: 192.168.1.100")

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Example: root")
        self.user_input.setText("root")

        self.pass_input = QLineEdit(self)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Enter password")

        self.version_combo = QComboBox(self)
        self.version_combo.addItems(["v2.99", "v3.00", "v3.01", "v3.02", "v3.03", "v3.04", "v3.05", "v3.06"])
        self.version_combo.setCurrentText("v3.06")

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Server Address:", self.host_input)
        layout.addRow("Username:", self.user_input)
        layout.addRow("Password:", self.pass_input)
        layout.addRow("TRex Version:", self.version_combo)
        layout.addRow(self.button_box)

    def get_inputs(self):
        return (self.host_input.text().strip(),
                self.user_input.text().strip(),
                self.pass_input.text(),
                self.version_combo.currentText())