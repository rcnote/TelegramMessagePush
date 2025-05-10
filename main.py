"""
A Telegram message sender application built with PyQt5.
This application allows users to send messages, photos, videos, and documents to Telegram channels or chats.
"""

import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QStatusBar, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from telegram import TelegramHelper

# Configuration file path
CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration from the config file.
    Returns an empty dict if the file doesn't exist or is invalid.
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(data):
    """
    Save configuration to the config file.
    Args:
        data: Dictionary containing configuration data
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class TelegramSender(QWidget):
    """
    Main application window for sending Telegram messages.
    Provides a GUI interface for configuring bot settings and sending messages.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram 消息推送工具")
        self.setWindowIcon(QIcon("logo.png"))
        self.resize(450, 750)
        self.config = load_config()
        self.file_path = None
        self.file_type = None
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        """
        Returns the CSS stylesheet for the application.
        Defines the visual appearance of all UI elements.
        """
        return """
        QWidget {
            background: #ffffff;
            font-family: 'Microsoft YaHei UI', '微软雅黑', 'Segoe UI', sans-serif;
            font-size: 14px;
            color: #2c3e50;
        }
        
        QGroupBox {
            border: 2px solid #e8f0fe;
            border-radius: 10px;
            margin-top: 16px;
            padding: 15px;
            background: #ffffff;
            font-weight: 600;
            font-size: 15px;
            color: #1a73e8;
        }
        
        QGroupBox:title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            background: #ffffff;
        }
        
        QLabel {
            color: #5f6368;
            font-size: 14px;
            padding: 2px;
        }
        
        QLineEdit, QTextEdit {
            border: 1.5px solid #e0e3e7;
            border-radius: 8px;
            padding: 8px 12px;
            background: #ffffff;
            color: #202124;
            selection-background-color: #e8f0fe;
        }
        
        QLineEdit:hover, QTextEdit:hover {
            border-color: #d2e3fc;
            background: #fafbfc;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #1a73e8;
            background: #ffffff;
        }
        
        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            background: #f1f3f4;
            color: #1a73e8;
            font-weight: 500;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background: #e8f0fe;
        }
        
        QPushButton:pressed {
            background: #d2e3fc;
        }
        
        QPushButton:disabled {
            background: #f1f3f4;
            color: #80868b;
        }
        
        QPushButton#mainBtn {
            background: #1a73e8;
            color: #ffffff;
            font-weight: 600;
        }
        
        QPushButton#mainBtn:hover {
            background: #1557b0;
        }
        
        QPushButton#mainBtn:pressed {
            background: #174ea6;
        }
        
        QPushButton#mainBtn:disabled {
            background: #dadce0;
            color: #ffffff;
        }
        
        QStatusBar {
            background: #f8f9fa;
            border-top: 1px solid #e0e3e7;
            color: #5f6368;
            padding: 4px 10px;
            font-size: 13px;
        }
        """

    def init_ui(self):
        """
        Initialize the user interface.
        Creates and arranges all UI elements including configuration fields,
        message input, file selection, and custom buttons.
        """
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Bot配置分组
        config_group = QGroupBox("Bot 配置")
        config_layout = QGridLayout()
        config_layout.setHorizontalSpacing(4)
        config_layout.setVerticalSpacing(4)
        self.token_edit = QLineEdit(self.config.get("token", ""))
        self.token_edit.setPlaceholderText("请输入Bot Token")
        self.token_edit.textChanged.connect(self.update_send_btn_state)
        config_layout.addWidget(QLabel("Bot Token:"), 0, 0)
        config_layout.addWidget(self.token_edit, 0, 1)
        token_save_btn = QPushButton("保存")
        token_save_btn.setFixedWidth(50)
        token_save_btn.clicked.connect(self.save_token)
        config_layout.addWidget(token_save_btn, 0, 2)

        self.chatid_edit = QLineEdit(self.config.get("chat_id", ""))
        self.chatid_edit.setPlaceholderText("请输入Chat ID")
        self.chatid_edit.textChanged.connect(self.update_send_btn_state)
        config_layout.addWidget(QLabel("Chat ID:"), 1, 0)
        config_layout.addWidget(self.chatid_edit, 1, 1)
        chatid_save_btn = QPushButton("保存")
        chatid_save_btn.setFixedWidth(50)
        chatid_save_btn.clicked.connect(self.save_chatid)
        config_layout.addWidget(chatid_save_btn, 1, 2)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # 消息内容分组
        msg_group = QGroupBox("消息内容")
        msg_layout = QVBoxLayout()
        msg_layout.setContentsMargins(4, 4, 4, 4)
        self.msg_edit = QTextEdit()
        self.msg_edit.setPlaceholderText("在此输入消息内容（支持Markdown格式） ...")
        self.msg_edit.setMinimumHeight(180)
        self.msg_edit.textChanged.connect(self.update_send_btn_state)
        msg_layout.addWidget(self.msg_edit)
        msg_group.setLayout(msg_layout)
        main_layout.addWidget(msg_group)

        # 文件选择分组
        file_group = QGroupBox("文件/媒体")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(3)
        self.file_label = QLabel("未选择文件")
        self.file_label.setMinimumWidth(120)
        file_layout.addWidget(self.file_label)
        img_btn = QPushButton("图片")
        img_btn.setFixedWidth(50)
        img_btn.clicked.connect(lambda: self.choose_file("image"))
        file_layout.addWidget(img_btn)
        video_btn = QPushButton("视频")
        video_btn.setFixedWidth(50)
        video_btn.clicked.connect(lambda: self.choose_file("video"))
        file_layout.addWidget(video_btn)
        doc_btn = QPushButton("文件")
        doc_btn.setFixedWidth(50)
        doc_btn.clicked.connect(lambda: self.choose_file("file"))
        file_layout.addWidget(doc_btn)
        clear_btn = QPushButton("清除")
        clear_btn.setFixedWidth(50)
        clear_btn.clicked.connect(self.clear_file)
        file_layout.addWidget(clear_btn)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 自定义按钮分组
        btn_group = QGroupBox("自定义按钮（文本+链接，最多6个）")
        btn_layout = QGridLayout()
        btn_layout.setHorizontalSpacing(3)
        btn_layout.setVerticalSpacing(3)
        self.btn_text_edits = []
        self.btn_url_edits = []
        for i in range(6):
            text_edit = QLineEdit()
            text_edit.setPlaceholderText(f"按钮{i+1}文本")
            url_edit = QLineEdit()
            url_edit.setPlaceholderText(f"按钮{i+1}链接")
            btn_layout.addWidget(text_edit, i, 0)
            btn_layout.addWidget(url_edit, i, 1)
            self.btn_text_edits.append(text_edit)
            self.btn_url_edits.append(url_edit)
        btn_group.setLayout(btn_layout)
        main_layout.addWidget(btn_group)

        # 操作按钮
        op_layout = QHBoxLayout()
        self.send_btn = QPushButton("发送消息")
        self.send_btn.setObjectName("mainBtn")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setFixedWidth(90)
        op_layout.addStretch()
        op_layout.addWidget(self.send_btn)
        op_layout.addStretch()
        main_layout.addLayout(op_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.update_send_btn_state()

    def save_token(self):
        """
        Save the bot token to configuration.
        Validates the token format before saving.
        """
        token = self.token_edit.text().strip()
        if not self.is_token_valid(token):
            self.status_bar.showMessage("Token格式错误，必须包含冒号", 5000)
            return
        self.config["token"] = token
        save_config(self.config)
        self.status_bar.showMessage("Token已保存", 3000)

    def save_chatid(self):
        """
        Save the chat ID to configuration.
        Validates that the chat ID is not empty.
        """
        chat_id = self.chatid_edit.text().strip()
        if not chat_id:
            self.status_bar.showMessage("Chat ID不能为空", 5000)
            return
        self.config["chat_id"] = chat_id
        save_config(self.config)
        self.status_bar.showMessage("Chat ID已保存", 3000)

    def choose_file(self, filetype):
        """
        Open a file dialog to select a file.
        Args:
            filetype: Type of file to select ('image', 'video', or 'file')
        """
        if filetype == "image":
            path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        elif filetype == "video":
            path, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "视频文件 (*.mp4 *.avi *.mov *.mkv)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*.*)")
        if path:
            self.file_path = path
            self.file_type = filetype
            self.file_label.setText(f"已选择文件: {os.path.basename(path)}")
        else:
            self.clear_file()
        self.update_send_btn_state()

    def clear_file(self):
        """
        Clear the currently selected file.
        Resets file path and type to None.
        """
        self.file_path = None
        self.file_type = None
        self.file_label.setText("未选择文件")
        self.update_send_btn_state()

    def get_buttons(self):
        """
        Get the list of custom buttons from the UI.
        Returns a list of dictionaries containing button text and URLs.
        """
        buttons = []
        for text_edit, url_edit in zip(self.btn_text_edits, self.btn_url_edits):
            text = text_edit.text().strip()
            url = url_edit.text().strip()
            if text and url:
                buttons.append({"text": text, "url": url})
        return buttons

    def is_token_valid(self, token):
        """
        Validate the bot token format.
        Args:
            token: The bot token to validate
        Returns:
            bool: True if the token is valid, False otherwise
        """
        return ":" in token and len(token) > 10

    def update_send_btn_state(self):
        """
        Update the state of the send button based on input validation.
        Enables the button only when all required fields are filled.
        """
        token = self.token_edit.text().strip()
        chat_id = self.chatid_edit.text().strip()
        msg = self.msg_edit.toPlainText().strip()
        enable = bool(self.is_token_valid(token) and chat_id and (msg or self.file_path))
        self.send_btn.setEnabled(enable)

    def send_message(self):
        """
        Send the message to Telegram.
        Handles different types of messages (text, photo, video, document)
        based on the selected file type.
        """
        token = self.token_edit.text().strip()
        chat_id = self.chatid_edit.text().strip()
        msg = self.msg_edit.toPlainText().strip()
        if not self.is_token_valid(token):
            self.status_bar.showMessage("Token格式错误，必须包含冒号", 5000)
            return
        if not chat_id:
            self.status_bar.showMessage("Chat ID不能为空", 5000)
            return
        if not (msg or self.file_path):
            self.status_bar.showMessage("消息内容或文件不能为空", 5000)
            return
        try:
            helper = TelegramHelper(token)
        except Exception as e:
            self.status_bar.showMessage(f"Bot初始化失败: {str(e)}", 8000)
            return
        buttons = self.get_buttons()
        try:
            if self.file_path:
                if self.file_type == "image":
                    helper.send_photo(chat_id, self.file_path, caption=msg, buttons=buttons)
                elif self.file_type == "video":
                    helper.send_video(chat_id, self.file_path, caption=msg, buttons=buttons)
                else:
                    helper.send_document(chat_id, self.file_path, caption=msg, buttons=buttons)
                self.clear_file()
            else:
                helper.send_message(chat_id, msg, buttons=buttons)
            self.status_bar.showMessage("消息已发送", 3000)
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            self.status_bar.showMessage(f"发送失败: {str(e)}", 8000)
            print("详细错误：", err)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TelegramSender()
    win.show()
    sys.exit(app.exec_()) 