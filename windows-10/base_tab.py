from PyQt5.QtWidgets import QWidget, QTextBrowser, QMessageBox
from PyQt5.QtCore import QTimer
import paramiko
import threading
import queue
import re


class BaseTRexTab(QWidget):
    def __init__(self):
        super().__init__()
        self.ssh_process = None
        self.ssh_client = None
        self.trex_version = None
        self.output_text = None
        self.output_queue = queue.Queue()
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._check_queue)
        self.ui_timer.start(50)

    def _check_queue(self):
        try:
            count = 0
            while not self.output_queue.empty() and count < 100:
                item = self.output_queue.get()

                if isinstance(item, tuple) and len(item) == 3:
                    mode, callback, line = item
                    if mode == 'callback' and callback:
                        try:
                            callback(line)
                        except Exception:
                            pass
                    else:
                        if hasattr(self, 'process_tmux_output'):
                            self.process_tmux_output(line)
                        else:
                            self.append_output(line)
                else:
                    if hasattr(self, 'process_tmux_output'):
                        self.process_tmux_output(str(item))
                    else:
                        self.append_output(str(item))

                count += 1
        except Exception:
            pass

    def validate_connection(self):
        if not hasattr(self, 'ssh_client') or not self.ssh_client:
            self.append_error("SSH connection not established. Please connect via File > Connect to Server menu first.")
            return False
        return True

    def append_output(self, text, color=None, bold=False, special=False):
        if self.output_text:
            text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            style = ""
            if color:
                style += f"color: {color};"
            if bold:
                style += " font-weight: bold;"

            if style:
                self.output_text.append(f"<span style='{style}'>{text}</span>")
            else:
                self.output_text.append(text)

            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def append_success(self, text):
        self.append_output(f"{text}", color="#6a9955")

    def append_error(self, text):
        self.append_output(f"{text}", color="#f48771")

    def append_info(self, text):
        self.append_output(f"{text}", color="#9cdcfe")

    def sanitize_input(self, text):
        if not text:
            return ""
        dangerous = [';', '&', '|', '`', '$', '(', ')', '<', '>']
        for char in dangerous:
            text = text.replace(char, '')
        return text.strip()

    def execute_remote_script(self, script_content, output_callback=None):
        if not self.validate_connection():
            return None

        def _run():
            client = None
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    self.ssh_client.hostname,
                    username=self.ssh_client.username,
                    password=self.ssh_client.password
                )

                stdin, stdout, stderr = client.exec_command('bash -s')
                stdin.write(script_content)
                stdin.channel.shutdown_write()

                for line in iter(stdout.readline, ""):
                    if output_callback:
                        self.output_queue.put(('callback', output_callback, line))
                    else:
                        self.output_queue.put(('default', None, line))

                err = stderr.read().decode()
                if err:
                    if output_callback:
                        self.output_queue.put(('callback', output_callback, err))
                    else:
                        self.output_queue.put(('default', None, err))

            except Exception as e:
                self.output_queue.put(('default', None, f"SSH error: {str(e)}\n"))
            finally:
                if client:
                    try:
                        client.close()
                    except Exception:
                        pass

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return "started"

    def clean_ansi_codes(self, text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)