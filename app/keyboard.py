"""
This module defines the keyboards used in the Telegram bot.
It includes both reply keyboards for the main menu and inline keyboards for topic selection.
"""

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

import app.database.requsts as rq

# Main menu reply keyboard
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Згенерувати слова'),
                                      KeyboardButton(text='Переглянути попередні слова')],
                                      [KeyboardButton(text='Пройти тестування'),
                                      KeyboardButton(text='Змінити рівень')]],
                            resize_keyboard=True)


async def get_topic_keyboard(new_topic: str, old_topic: str):
    """
    Generates an inline keyboard for selecting between new and old word topics for a quiz.

    Args:
        new_topic (str): The name of the current/new topic.
        old_topic (str): The name of the previous/old topic.

    Returns:
        InlineKeyboardMarkup: The constructed inline keyboard.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=new_topic, callback_data='words'),
        InlineKeyboardButton(text=old_topic, callback_data='words_old')],
        [InlineKeyboardButton(text='Головна', callback_data='main')]
    ])
    return keyboard