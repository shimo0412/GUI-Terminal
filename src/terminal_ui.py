from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QComboBox, QTextEdit, QFileDialog
from PySide6.QtCore import QProcess, QEvent
import os

class TerminalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Terminal")
        self.setStyleSheet("background-color: black; color: white;")
        
        self.main_layout = QHBoxLayout()
        self.left_panel = QVBoxLayout()
        
        self.commands = {
            "dir": {"desc": "現在のディレクトリの一覧を表示", "options": ["", "/A", "/B"], "path_count": 0},
            "ipconfig": {"desc": "IP設定を表示", "options": ["", "/all", "/renew"], "path_count": 0},
            "cd": {"desc": "ディレクトリを変更", "options": ["", "/D"], "path_count": 1},
            "mkdir": {"desc": "新しいディレクトリを作成", "options": [""], "path_count": 1},
            "rmdir": {"desc": "ディレクトリを削除", "options": ["", "/S", "/Q"], "path_count": 1},
            "del": {"desc": "ファイルを削除", "options": ["", "/F", "/Q", "/S", "/A"], "path_count": 1},
            "copy": {"desc": "ファイルをコピー", "options": ["", "/Y", "/-Y", "/V"], "path_count": 2},
            "move": {"desc": "ファイルまたはディレクトリを移動", "options": ["", "/Y", "/-Y"], "path_count": 2},
            "xcopy": {"desc": "ファイルとディレクトリをコピー", "options": ["", "/E", "/C", "/H", "/K", "/Y"], "path_count": 2},
            "robocopy": {"desc": "ファイルとディレクトリをコピー（高度なオプションあり）", "options": ["", "/E", "/MIR", "/Z", "/R"], "path_count": 2},
            "echo": {"desc": "テキストを表示", "options": [""], "path_count": 0},
            "type": {"desc": "ファイルの内容を表示", "options": [""], "path_count": 1},
            "find": {"desc": "ファイル内の文字列を検索", "options": ["", "/V", "/C", "/N"], "path_count": 1},
            "tasklist": {"desc": "実行中のタスク一覧を表示", "options": ["", "/S", "/U", "/FI"], "path_count": 0},
            "taskkill": {"desc": "実行中のタスクを終了", "options": ["", "/PID", "/IM", "/F"], "path_count": 0},
            "shutdown": {"desc": "コンピューターをシャットダウンまたは再起動", "options": ["", "/s", "/r", "/t", "/a"], "path_count": 0},
            "ping": {"desc": "ネットワーク接続を確認", "options": ["", "/n", "/l", "/t"], "path_count": 1},
            "tracert": {"desc": "パケットの経路を追跡", "options": ["", "/d", "/h", "/w"], "path_count": 1},
            "netstat": {"desc": "ネットワーク接続の情報を表示", "options": ["", "-a", "-n", "-o"], "path_count": 0},
            "systeminfo": {"desc": "システム情報を表示", "options": [""], "path_count": 0},
            "set": {"desc": "環境変数を設定または表示", "options": [""], "path_count": 0},
            "chkdsk": {"desc": "ディスクのエラーチェックを実行", "options": ["", "/F", "/R", "/X"], "path_count": 1},
            "diskpart": {"desc": "ディスクパーティションを管理", "options": [""], "path_count": 0},
            "format": {"desc": "ディスクをフォーマット", "options": ["", "/FS", "/Q", "/X"], "path_count": 1},
            "attrib": {"desc": "ファイルやディレクトリの属性を変更", "options": ["", "+R", "-R", "+H", "-H"], "path_count": 1},
            "git clone": {"desc": "リポジトリをクローン", "options": ["", "--depth", "--branch"], "path_count": 1},
            "git commit": {"desc": "変更をコミット", "options": ["", "-m", "--amend"], "path_count": 0},
            "git push": {"desc": "リモートリポジトリにプッシュ", "options": ["", "--force", "--tags"], "path_count": 0},
            "git pull": {"desc": "リモートリポジトリからプル", "options": ["", "--rebase"], "path_count": 0},
            "python": {"desc": "Pythonを実行", "options": ["", "-m", "-c"], "path_count": 0},
            "python -m": {"desc": "モジュールを実行", "options": [""], "path_count": 1},
            "pip install": {"desc": "パッケージをインストール", "options": ["", "--upgrade", "--user"], "path_count": 1},
            "pip uninstall": {"desc": "パッケージをアンインストール", "options": ["", "-y"], "path_count": 1}
        }
        
        self.create_command_buttons()
        
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(False)
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        self.terminal_output.installEventFilter(self)
        
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_terminal)
        
        self.current_directory = os.getcwd()
        self.start_terminal()
        
        terminal_layout = QVBoxLayout()
        terminal_layout.addWidget(self.terminal_output)
        terminal_layout.addWidget(self.clear_button)
        
        self.main_layout.addLayout(self.left_panel)
        self.main_layout.addLayout(terminal_layout)
        self.setLayout(self.main_layout)
    
    def start_terminal(self):
        self.terminal = QProcess(self)
        self.terminal.setProgram("cmd")
        self.terminal.setProcessChannelMode(QProcess.MergedChannels)
        self.terminal.readyReadStandardOutput.connect(self.update_terminal_output)
        self.terminal.start()
    
    def create_command_buttons(self):
        for cmd in self.commands:
            btn = QPushButton(cmd)
            btn.clicked.connect(lambda _, c=cmd: self.show_command_options(c))
            self.left_panel.addWidget(btn)
    
    def show_command_options(self, command):
        while self.left_panel.count():
            item = self.left_panel.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        back_button = QPushButton("戻る")
        back_button.clicked.connect(self.reset_command_buttons)
        
        cmd_label = QLabel(command)
        option_label = QLabel("オプション")
        option_box = QComboBox()
        option_box.addItems(self.commands[command]["options"])
        
        self.left_panel.addWidget(back_button)
        self.left_panel.addWidget(cmd_label)
        self.left_panel.addWidget(option_label)
        self.left_panel.addWidget(option_box)
        
        if self.commands[command]["path_count"] > 0:
            path_label = QLabel("パス")
            self.left_panel.addWidget(path_label)
        
        folder_buttons = []
        for _ in range(self.commands[command]["path_count"]):
            btn = QPushButton("フォルダーを開く")
            btn.clicked.connect(lambda _, b=btn: self.select_folder(b))
            folder_buttons.append(btn)
            self.left_panel.addWidget(btn)
        
        execute_button = QPushButton("実行")
        execute_button.clicked.connect(lambda: self.run_command_with_option(command, option_box.currentText(), folder_buttons))
        
        description = QLabel(self.commands[command]["desc"])
        
        self.left_panel.addWidget(execute_button)
        self.left_panel.addWidget(description)
    
    def reset_command_buttons(self):
        while self.left_panel.count():
            item = self.left_panel.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.create_command_buttons()
    
    def select_folder(self, button):
        folder_path = QFileDialog.getExistingDirectory(self, "フォルダーを選択")
        if folder_path:
            button.setText(folder_path)
    
    def run_command_with_option(self, command, option, folder_buttons):
        paths = [btn.text() for btn in folder_buttons if btn.text() != "フォルダーを開く"]
        full_command = f"{command} {option} {' '.join(paths)}\n"
        self.terminal.write(full_command.encode())
        self.terminal.waitForBytesWritten()
    
    def update_terminal_output(self):
        output = self.terminal.readAllStandardOutput().data().decode("utf-8")
        self.terminal_output.append(output)
    
    def clear_terminal(self):
        self.terminal_output.clear()
        self.terminal_output.append(f"{self.current_directory}> ")
    
    def closeEvent(self, event):
        if self.terminal.state() == QProcess.Running:
            self.terminal.kill()
            self.terminal.waitForFinished()
        event.accept()