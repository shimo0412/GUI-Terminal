from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QComboBox, QTextEdit
from PySide6.QtCore import QProcess, QEvent  # QEvent を追加
import os

class TerminalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Terminal")
        self.setStyleSheet("background-color: black; color: white;")
        
        self.main_layout = QHBoxLayout()
        self.left_panel = QVBoxLayout()
        
        self.commands = {
            "dir": {"desc": "現在のディレクトリの一覧を表示", "options": ["/A", "/B"]},
            "ipconfig": {"desc": "IP設定を表示", "options": ["/all", "/renew"]}
        }
        
        self.create_command_buttons()
        
        from PySide6.QtWidgets import QPlainTextEdit  # 追加
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(False)  # 書き込み可能に設定
        self.prompt_length = 0  # プロンプト部分の長さを記憶
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        self.terminal_output.installEventFilter(self)  # キーイベント用
        
        self.terminal = QProcess(self)
        self.terminal.setProgram("cmd")
        self.terminal.setProcessChannelMode(QProcess.MergedChannels)
        self.terminal.readyReadStandardOutput.connect(self.update_terminal_output)
        self.terminal.start()
        
        self.main_layout.addLayout(self.left_panel)
        self.main_layout.addWidget(self.terminal_output)
        self.setLayout(self.main_layout)
    
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
        option_box = QComboBox()
        option_box.addItems(self.commands[command]["options"])
        
        execute_button = QPushButton("実行")
        execute_button.clicked.connect(lambda: self.run_command_with_option(command, option_box.currentText()))
        
        description = QLabel(self.commands[command]["desc"])
        
        self.left_panel.addWidget(back_button)
        self.left_panel.addWidget(cmd_label)
        self.left_panel.addWidget(option_box)
        self.left_panel.addWidget(execute_button)
        self.left_panel.addWidget(description)
    
    def reset_command_buttons(self):
        while self.left_panel.count():
            item = self.left_panel.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.create_command_buttons()
    
    def run_command_with_option(self, command, option):
        full_command = f"{command} {option}\r\n"
        self.terminal.write(full_command.encode())
        self.terminal.waitForBytesWritten()
        self.terminal.waitForReadyRead()  # 修正ポイント
    
    def update_terminal_output(self):
        output = self.terminal.readAllStandardOutput().data().decode("utf-8")
        if output:
            from PySide6.QtGui import QTextCursor
        self.terminal_output.moveCursor(QTextCursor.End)
        self.terminal_output.ensureCursorVisible()  # 常に最終行に表示
        self.terminal_output.insertPlainText(output)
        from PySide6.QtGui import QTextCursor
        self.terminal_output.moveCursor(QTextCursor.End)
        self.terminal_output.ensureCursorVisible()  # カーソルを最終行に移動
        self.prompt_length = self.terminal_output.document().blockLength(self.terminal_output.document().blockCount() - 1)
        output = self.terminal.readAllStandardOutput().data().decode("utf-8")
        if output:
            self.terminal_output.appendPlainText(output + "")

    def eventFilter(self, source, event):
        if source == self.terminal_output and event.type() == QEvent.KeyPress:
            cursor = self.terminal_output.textCursor()
            current_pos = cursor.position()
            if current_pos < self.prompt_length or cursor.blockNumber() != self.terminal_output.document().blockCount() - 1:  # プロンプト部分または最終行以外は編集不可
                return True
            if event.key() in [16777220, 16777221]:  # Enterキー判定
                command = self.terminal_output.toPlainText().splitlines()[-1][self.prompt_length:]  # プロンプト以降のコマンド取得
                self.terminal.write((command + "").encode())  # コマンド送信
                self.terminal.waitForBytesWritten()
                self.prompt_length = self.terminal_output.document().characterCount()  # 次の行のプロンプト部分を保護
                return True
            if event.key() in [16777219, 16777223]:  # バックスペース、デリートキー
                if current_pos <= self.prompt_length:  # プロンプト部分は削除不可
                    return True
        return super().eventFilter(source, event)
        
    
    def closeEvent(self, event):
        if self.terminal.state() == QProcess.Running:
            self.terminal.kill()  # 強制終了に変更
            self.terminal.waitForFinished()
        event.accept()