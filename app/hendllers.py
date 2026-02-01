"""
This module contains the Telegram message and callback query handlers for the bot.
It defines the bot's conversation flow using Finite State Machine (FSM).
"""

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import asyncio

import app.keyboard as kb
import app.database.requsts as rq
import app.ai as ai

router = Router()

class Reg(StatesGroup):
    """FSM states for the user registration process."""
    name = State()
    levl = State()

class ChangeLevel(StatesGroup):
    """FSM states for changing the user's English level."""
    level = State()

class GWords(StatesGroup):
    """FSM states for generating new vocabulary words."""
    topic = State()
    quantity = State()

class Reg_words(StatesGroup):
    """FSM states for registering specific words (currently unused in handlers)."""
    words = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handles the /start command.
    Checks if the user is registered. If yes, shows the main menu;
    if no, starts the registration process.

    Args:
        message (Message): The Telegram message object.
        state (FSMContext): The FSM context for managing states.

    Returns:
        None
    """
    user = await rq.set_user(message.from_user.id)
    user_name = await rq.get_user_name(message.from_user.id)
    if user:
        await message.answer(f"З поверненням {user_name}! Готовий до нових слів?", reply_markup=kb.main)
    else:
        await message.answer(f"Привіт Ти ще не зареєстрований. Давай пройдемо кортку реєстрацію")
        await state.set_state(Reg.name)
        await message.answer('Ведіть ваше імя')

@router.message(Command('menu'))
async def menu(message: Message):
    """
    Handles the /menu command.
    Displays the main menu keyboard.

    Args:
        message (Message): The Telegram message object.

    Returns:
        None
    """
    await message.answer('Що будемо робити дальше?', reply_markup= kb.main)

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    """
    Handles the user's name input during registration.
    Updates the FSM data and asks for the English level.

    Args:
        message (Message): The Telegram message object containing the name.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await state.update_data(name=message.text)
    await state.set_state(Reg.levl)
    await message.answer('Введіть ваш рівень (наприклад: A1-2, B1-2, C1):')

@router.message(Reg.levl)
async def two_theree(message: Message, state: FSMContext):
    """
    Handles the user's level input during registration.
    Saves the user to the database and completes registration.

    Args:
        message (Message): The Telegram message object containing the level.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await state.update_data(levl = message.text)
    data = await state.get_data()
    await rq.add_user(message.from_user.id, data["name"], data["levl"])
    await message.answer(f'Дякую реєстрацію завершено.\nІмя: {data["name"]}, Рівень англійської: {data["levl"]}')
    await state.clear()
    await cmd_start(message, state)

@router.message(F.text == 'Змінити рівень')
async def change_level_start(message: Message, state: FSMContext):
    """
    Handles the "Змінити рівень" (Change level) button.
    Prompts the user to enter a new English level.

    Args:
        message (Message): The Telegram message object.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await message.answer('Введіть ваш новий рівень (наприклад: A1-2, B1-2, C1):')
    await state.set_state(ChangeLevel.level)

@router.message(ChangeLevel.level)
async def process_level_input(message: Message, state: FSMContext):
    """
    Handles the new level input.
    Updates the user's level in the database.

    Args:
        message (Message): The Telegram message object containing the new level.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    new_level = message.text
    await rq.update_level(message.from_user.id, new_level)
    await message.answer(f'Рівень успішно змінено на: {new_level}')
    await state.clear()


@router.message(F.text == 'Згенерувати слова')
async def generate_words(message: Message, state: FSMContext):
    """
    Handles the "Згенерувати слова" (Generate words) button.
    Prompts the user to enter a topic for word generation.

    Args:
        message (Message): The Telegram message object.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await state.set_state(GWords.topic)
    await message.answer('Ведіть тему яку ви хочете:')

@router.message(GWords.topic)
async def ai_four(message: Message, state: FSMContext):
    """
    Handles the topic input for word generation.
    Prompts the user to enter the quantity of words.

    Args:
        message (Message): The Telegram message object containing the topic.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await state.update_data(topic=message.text)
    await state.set_state(GWords.quantity)
    await message.answer('Введіть кількість слів від 5 до 15:')

@router.message(F.text == 'Переглянути попередні слова')
async def old_words(message: Message):
    """
    Handles the "Переглянути попередні слова" (View previous words) button.
    Retrieves and displays the user's previously generated words from the database.

    Args:
        message (Message): The Telegram message object.

    Returns:
        None
    """
    words = await rq.get_old_words(message.from_user.id)
    if words:
        await message.answer(f"Ваші попеедні слова: {words}")
    else:
        await message.answer("Історія порожня")

@router.message(F.text == 'Пройти тестування')
async def generate_words(message: Message):
    """
    Handles the "Пройти тестування" (Take a test) button.
    Prompts the user to select a topic for the quiz using an inline keyboard.

    Args:
        message (Message): The Telegram message object.

    Returns:
        None
    """
    user_id = message.from_user.id
    words = await rq.get_topics(user_id)
    old_words = await rq.get_old_topics(user_id) or ''
    await message.answer('Веберіть по якій теми мають бути тести', reply_markup= await kb.get_topic_keyboard(words, old_words))

@router.message(GWords.quantity)
async def ai_fife(message: Message, state: FSMContext):
    """
    Handles the quantity input for word generation.
    Triggers the AI to generate words and saves them to the database.

    Args:
        message (Message): The Telegram message object containing the quantity.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    await state.update_data(quantity=message.text)
    data_ai = await state.get_data()
    user_level = await rq.get_user_level(message.from_user.id)
    
    status_msg = await message.answer("🧠 Генерую список...")
    
    raw_response = await ai.generate_daily_words(
        tg_id=message.from_user.id,
        level=user_level,
        topic=data_ai["topic"],
        count=data_ai["quantity"]
    )
    
    if raw_response == "LIMIT_EXCEEDED":
        await status_msg.edit_text("⏳ Ліміт запитів. Спробуй пізніше")
    else:
        final_text = ai.format_words_text(raw_response)
        
        await status_msg.delete()
        await rq.add_words(message.from_user.id, final_text, data_ai["topic"])
        await message.answer(final_text, parse_mode="HTML")
    
    await state.clear()
    await menu(message)



@router.callback_query(F.data.in_(['words', 'words_old']))
async def ai_question(callback: CallbackQuery):
    """
    Handles callback queries for selecting a topic for the quiz.
    Triggers AI to generate quiz questions and sends them as polls.

    Args:
        callback (CallbackQuery): The Telegram callback query object.

    Returns:
        None
    """
    await callback.message.delete()
    user_level = await rq.get_user_level(callback.from_user.id)
    user_id = callback.from_user.id
    if callback.data == 'words':
        words = await rq.get_words(user_id)
    else:
        words = await rq.get_old_words(user_id)
    
    await callback.message.answer(f"⏳ Герую тести по твоїм словам...")

    quizzes = await ai.generate_quiz_questions(
        tg_id=callback.from_user.id,
        level=user_level, 
        words=words,
        count=15
    )

    if quizzes == "LIMIT_EXCEEDED":
        return await callback.message.answer("⏳ Ліміт запитів. Спробуй пізніше")
    
    if not quizzes or not isinstance(quizzes, list):
        return await callback.message.answer("❌ Помилка при створенні тесту")

    await rq.add_user_test(callback.from_user.id, quizzes)
    
    for q in quizzes:
        await callback.message.answer_poll(
            question=q['question'],
            options=q['options'],
            type='quiz',
            correct_option_id=int(q['correct_id']),
            explanation=q.get('explanation', ""),
            is_anonymous=False
        )
        await asyncio.sleep(0.5)


@router.callback_query(F.data == 'main')
async def main(callback: CallbackQuery):
    """
    Handles the "Головна" (Main) callback button.
    Returns the user to the main menu.

    Args:
        callback (CallbackQuery): The Telegram callback query object.

    Returns:
        None
    """
    await callback.message.delete()
    await menu(callback.message)
    await callback.answer()
