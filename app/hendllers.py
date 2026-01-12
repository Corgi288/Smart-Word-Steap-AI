from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboard as kb
import app.database.requsts as rq
import app.ai as ai

router = Router()

class Reg(StatesGroup):
    name = State()
    levl = State()

class GWords(StatesGroup):
    topic = State()
    quantity = State()

class Reg_words(StatesGroup):
    words = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.set_user(message.from_user.id)
    user_name = await rq.get_user_name(message.from_user.id)
    if user:
        await message.answer(f"З поверненням {user_name}! Готовий до нових слів?", reply_markup=kb.main)
    else:
        await message.answer(f"Привіт Ти ще не зареєстрований. Давай пройдемо кортку реєстрацію")
        await state.set_state(Reg.name)
        await message.answer('Ведіть ваше імя')

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.levl)
    await message.answer('Ведіть рівень англійської')

@router.message(Reg.levl)
async def two_theree(message: Message, state: FSMContext):
    await state.update_data(levl = message.text)
    data = await state.get_data()
    await rq.add_user(message.from_user.id, data["name"], data["levl"])
    await message.answer(f'Дякую реєстрацію завершено.\nІмя: {data["name"]}, Рівень англійської: {data["levl"]}')
    await state.clear()
    await cmd_start(message, state)

@router.message(F.text == 'Згенерувати слова')
async def generate_words(message: Message, state: FSMContext):
    await state.set_state(GWords.topic)
    await message.answer('Ведіть тему яку ви хочете:')

@router.message(F.text == 'Згенерувати слова')
async def generate_words(message: Message, state: FSMContext):
    await state.set_state(GWords.topic)
    await message.answer('Введіть тему, яку ви хочете:')

@router.message(GWords.topic)
async def ai_four(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(GWords.quantity)
    await message.answer('Введіть кількість слів від 5 до 15:')

@router.message(GWords.quantity)
async def ai_fife(message: Message, state: FSMContext):
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
        await status_msg.edit_text("⏳ Ліміт запитів. Спробуй пізніше.")
    else:
        final_text = ai.format_words_text(raw_response)
        
        await status_msg.delete()
        await rq.add_words(message.from_user.id, final_text)
        await message.answer(final_text, parse_mode="HTML")
    
    await state.clear()
    await cmd_start(message, state)

@router.message(F.text == 'Переглянути попередні слова')
async def old_words(message: Message):
    words = await rq.get_old_words(message.from_user.id)
    if words:
        await message.answer(f"Ваші попеедні слова: {words}")
    else:
        await message.answer("Історія порожня")
