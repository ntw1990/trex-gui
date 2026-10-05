# base_tab.py
from PyQt5.QtWidgets import QWidget, QTextBrowser
from PyQt5.QtCore import QProcess
import base64
import re


class BaseTRexTab(QWidget):
    def __init__(self):
        super().__init__()
        self.ssh_process = None
        self.ssh_client = None
        self.trex_version = None
        self.output_text = None

    def validate_connection(self):
        """Check SSH connection"""
        if not hasattr(self, 'ssh_client') or not self.ssh_client:
            self.append_error("SSH connection not established. Please connect via File > Connect to Server menu first.")
            return False
        return True

    def append_output(self, text, color=None, bold=False, special=False):
        """Add text to output with proper formatting - should be overridden by child class"""
        if self.output_text:
            # Escape HTML characters
            text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # Build style
            style = ""
            if color:
                style += f"color: {color};"
            if bold:
                style += " font-weight: bold;"

            if style:
                self.output_text.append(f"<span style='{style}'>{text}</span>")
            else:
                self.output_text.append(text)

            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
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

    def sanitize_input(self, text):
        """Sanitize input to prevent command injection"""
        if not text:
            return ""
        # Remove dangerous characters
        dangerous = [';', '&', '|', '`', '$', '(', ')', '<', '>']
        for char in dangerous:
            text = text.replace(char, '')
        return text.strip()

    def build_ssh_command(self, remote_command):
        """Build SSH command with stored information - modified method"""
        if not self.validate_connection():
            return None

        return (f"sshpass -p '{self.ssh_client.password}' "
                f"ssh -o StrictHostKeyChecking=no "
                f"{self.ssh_client.username}@{self.ssh_client.hostname} "
                f"'{remote_command}'")

    def execute_remote_script(self, script_content):
        """Execute script on remote server using base64"""
        if not self.validate_connection():
            return None

        # Encode script with base64 to avoid quoting issues
        script_base64 = base64.b64encode(script_content.encode()).decode()

        # Command: decode base64 and execute with bash
        cmd = f"echo '{script_base64}' | base64 -d | bash"

        return (f"sshpass -p '{self.ssh_client.password}' "
                f"ssh -o StrictHostKeyChecking=no "
                f"{self.ssh_client.username}@{self.ssh_client.hostname} "
                f"'{cmd}'")

    def handle_stdout(self):
        """Handle process output with better buffering and real-time display"""
        try:
            if self.ssh_process is None:
                return

            while self.ssh_process.bytesAvailable() > 0:
                data = self.ssh_process.readAllStandardOutput().data().decode()

                if data.strip():
                    clean_data = self.clean_ansi_codes(data)
                    lines = clean_data.split('\n')
                    for line in lines:
                        if line.strip():
                            if "Error" in line or "❌" in line:
                                self.append_error(line)
                            elif "✅" in line or "success" in line.lower():
                                self.append_success(line)
                            elif "!!!" in line or "Warning" in line:
                                self.append_info(f"!!!{line}")
                            elif "tmux" in line.lower() and ("attach" in line.lower() or "session" in line.lower()):
                                self.append_info(f"{line}")
                            else:
                                self.append_output(line)

            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

        except Exception as e:
            self.append_error(f"Error receiving output: {str(e)}")

    def clean_ansi_codes(self, text):
        """Remove ANSI codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)