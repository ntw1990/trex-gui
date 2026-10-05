import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser, \
    QTabWidget, QMenuBar, QMenu, QAction, QSpinBox, QDialog, QMessageBox, QDialogButtonBox
from PyQt5.QtCore import Qt
import paramiko

from dialogs import SSHLoginDialog, HostFileDialog
import stateless_tab
import stateful_tab
import advanced_stateful_tab
import generator_tab


class SSHClient:
    def __init__(self, hostname, username, password, trex_version):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.trex_version = trex_version

    def execute_command(self, command):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            output = f"<b>Connecting to {self.hostname}...</b>\n"
            client.connect(self.hostname, username=self.username, password=self.password)
            output += "<font color='green'><b>Connection established.</b></font>\n"

            output += f"<b>Executing command:</b> <pre>{command}</pre>\n"
            stdin, stdout, stderr = client.exec_command(command)

            cmd_output = stdout.read().decode()
            cmd_error = stderr.read().decode()

            if cmd_output:
                output += f"<font color='blue'><b>Output:</b></font><pre>{cmd_output}</pre>\n"
            if cmd_error:
                output += f"<font color='red'><b>Error:</b></font><pre>{cmd_error}</pre>\n"

            client.close()
            output += "<font color='green'><b>SSH connection closed.</b></font>\n"

        except paramiko.AuthenticationException:
            output = "<font color='red'><b>Error: Authentication failed. Check username and password.</b></font>\n"
        except paramiko.SSHException as e:
            output = f"<font color='red'><b>Error: SSH connection failed - {str(e)}</b></font>\n"
        except Exception as e:
            output = f"<font color='red'><b>Error: {str(e)}</b></font>\n"

        return output

    def execute_command_raw(self, command):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.hostname, username=self.username, password=self.password)
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            client.close()
            return output, error
        except Exception as e:
            return "", str(e)



class TabbedUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI - TRex")
        self.setGeometry(200, 200, 900, 650)
        self.ssh_client = None
        self.trex_version = None
        self.initUI()
        self.show_login_dialog()

    def initUI(self):
        layout = QVBoxLayout()

        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("file")

        connect_action = QAction("Connect to Server", self)
        connect_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(connect_action)

        file_menu.addSeparator()

        font_menu = file_menu.addMenu("Font Size")

        small_action = QAction("Small (12px)", self)
        medium_action = QAction("Medium (16px)", self)
        large_action = QAction("Large (20px)", self)
        xlarge_action = QAction("Extra Large (24px)", self)
        custom_action = QAction("Custom...", self)

        small_action.triggered.connect(lambda: self.set_font_size(12))
        medium_action.triggered.connect(lambda: self.set_font_size(16))
        large_action.triggered.connect(lambda: self.set_font_size(20))
        xlarge_action.triggered.connect(lambda: self.set_font_size(24))
        custom_action.triggered.connect(self.set_custom_font_size)

        font_menu.addAction(small_action)
        font_menu.addAction(medium_action)
        font_menu.addAction(large_action)
        font_menu.addAction(xlarge_action)
        font_menu.addSeparator()
        font_menu.addAction(custom_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        layout.setMenuBar(menubar)

        self.tab_widget = QTabWidget()
        self.stateless_page = stateless_tab.StatelessControlPanel()
        self.stateful_page = stateful_tab.StatefulControlPanel()
        self.advanced_stateful_page = advanced_stateful_tab.AdvancedStatefulPanel()
        self.generator_page = generator_tab.GeneratorTab()

        self.tab_widget.addTab(self.stateless_page, "stateless_tab")
        self.tab_widget.addTab(self.stateful_page, "stateful_tab")
        self.tab_widget.addTab(self.advanced_stateful_page, "advanced_statefull_tab")
        self.tab_widget.addTab(self.generator_page, "yaml_generator")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        self.set_tabs_enabled(False)

    def set_tabs_enabled(self, enabled):
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enabled)

    def set_font_size(self, size):
        style = f"font-size: {size}px; font-family: 'Courier New';"
        self.stateless_page.output_text.setStyleSheet(style)
        self.stateful_page.output_text.setStyleSheet(style)
        self.advanced_stateful_page.output_text.setStyleSheet(style)
        self.generator_page.output_text.setStyleSheet(style)

    def set_custom_font_size(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Font Size")

        layout = QVBoxLayout()
        label = QLabel("Enter font size (pixels):")
        spin_box = QSpinBox()
        spin_box.setRange(1, 100)
        spin_box.setValue(22)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(label)
        layout.addWidget(spin_box)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            self.set_font_size(spin_box.value())

    def show_login_dialog(self):
        dialog = SSHLoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            host, user, password, version = dialog.get_inputs()

            if not host or not user or not password:
                QMessageBox.warning(self, "Error", "Host, username and password are required.")
                return

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password)
                client.close()

                self.ssh_client = SSHClient(host, user, password, version)
                self.trex_version = version

                self.update_all_tabs()
                self.set_tabs_enabled(True)

                success_msg = f"Successfully connected to {host}. TRex version: {version}"
                self.stateless_page.append_success(success_msg)
                self.stateful_page.append_success(success_msg)
                self.advanced_stateful_page.append_success(success_msg)
                self.generator_page.append_success(success_msg)

            except paramiko.AuthenticationException:
                QMessageBox.critical(self, "Error", "Authentication failed. Check username and password.")
            except paramiko.SSHException as e:
                QMessageBox.critical(self, "Error", f"SSH connection failed: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def update_all_tabs(self):
        tabs = [
            self.stateless_page,
            self.stateful_page,
            self.advanced_stateful_page,
            self.generator_page
        ]

        for tab in tabs:
            tab.ssh_client = self.ssh_client
            tab.trex_version = self.trex_version


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TabbedUI()
    window.show()
    sys.exit(app.exec_())