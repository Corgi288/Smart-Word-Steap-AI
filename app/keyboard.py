from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Згенерувати слова'),
                                      KeyboardButton(text='Переглянути попередні слова')]],
                            resize_keyboard=True)