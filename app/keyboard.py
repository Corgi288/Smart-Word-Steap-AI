from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

import app.database.requsts as rq

# Main menu reply keyboard
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Згенерувати слова'),
                                      KeyboardButton(text='Переглянути попередні слова')],
                                      [KeyboardButton(text='Пройти тестування'),
                                      KeyboardButton(text='Змінити рівень')]],
                            resize_keyboard=True)


async def get_topic_keyboard(new_topic: str, old_topic: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=new_topic, callback_data='words'),
        InlineKeyboardButton(text=old_topic, callback_data='words_old')],
        [InlineKeyboardButton(text='Головна', callback_data='main')]
    ])
    return keyboard