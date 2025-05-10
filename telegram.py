"""
Telegram bot helper class for sending messages and media files.
This module provides a wrapper around the telebot library for easier message sending.
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class TelegramHelper:
    """
    Helper class for sending messages and media files to Telegram.
    Provides methods for sending text messages, photos, videos, and documents.
    """
    def __init__(self, token):
        """
        Initialize the Telegram bot with the provided token.
        Args:
            token: The Telegram bot token
        """
        self.bot = telebot.TeleBot(token)

    def send_message(self, chat_id, text, buttons=None, parse_mode="Markdown"):
        """
        Send a text message to a Telegram chat.
        Args:
            chat_id: The target chat ID
            text: The message text (supports Markdown)
            buttons: Optional list of inline keyboard buttons
            parse_mode: Message parse mode (default: Markdown)
        """
        markup = None
        if buttons:
            markup = InlineKeyboardMarkup()
            for btn in buttons:
                if btn['text'] and btn['url']:
                    markup.add(InlineKeyboardButton(btn['text'], url=btn['url']))
        self.bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=markup)

    def send_photo(self, chat_id, photo_path, caption=None, buttons=None):
        """
        Send a photo to a Telegram chat.
        Args:
            chat_id: The target chat ID
            photo_path: Path to the photo file
            caption: Optional caption for the photo
            buttons: Optional list of inline keyboard buttons
        """
        markup = None
        if buttons:
            markup = InlineKeyboardMarkup()
            for btn in buttons:
                if btn['text'] and btn['url']:
                    markup.add(InlineKeyboardButton(btn['text'], url=btn['url']))
        with open(photo_path, 'rb') as f:
            self.bot.send_photo(chat_id, f, caption=caption, reply_markup=markup)

    def send_video(self, chat_id, video_path, caption=None, buttons=None):
        """
        Send a video to a Telegram chat.
        Args:
            chat_id: The target chat ID
            video_path: Path to the video file
            caption: Optional caption for the video
            buttons: Optional list of inline keyboard buttons
        """
        markup = None
        if buttons:
            markup = InlineKeyboardMarkup()
            for btn in buttons:
                if btn['text'] and btn['url']:
                    markup.add(InlineKeyboardButton(btn['text'], url=btn['url']))
        with open(video_path, 'rb') as f:
            self.bot.send_video(chat_id, f, caption=caption, reply_markup=markup)

    def send_document(self, chat_id, file_path, caption=None, buttons=None):
        """
        Send a document to a Telegram chat.
        Args:
            chat_id: The target chat ID
            file_path: Path to the document file
            caption: Optional caption for the document
            buttons: Optional list of inline keyboard buttons
        """
        markup = None
        if buttons:
            markup = InlineKeyboardMarkup()
            for btn in buttons:
                if btn['text'] and btn['url']:
                    markup.add(InlineKeyboardButton(btn['text'], url=btn['url']))
        with open(file_path, 'rb') as f:
            self.bot.send_document(chat_id, f, caption=caption, reply_markup=markup) 