from google import genai
import asyncio
import json

from config import GEMINI_API

from aiogram.types import Message
import app.database.requsts as rq

client = genai.Client(api_key=GEMINI_API)


async def generate_daily_words(tg_id: int, level: str, topic: str, count: str):

    used_words = await rq.get_words(tg_id)
    used_words_old = await rq.get_old_words(tg_id) 
    
    prompt = f"""
    Ти досвідчений викладач англійської мови.

    Згенеруй {count} НОВИХ англійських слів для рівня {level} на тему "{topic}".

    Вже використані слова (ЗАБОРОНЕНО використовувати знову, включно з формами):
        {used_words, used_words_old}
    
    ВІДПОВІДЬ НАДАЙ ВИКЛЮЧНО У ФОРМАТІ JSON ARRAY. 
    НЕ ПИШИ НІЯКОГО ЗАЙВОГО ТЕКСТУ, ТІЛЬКИ ЧИСТИЙ JSON.
    
    Формат:
    [
      {{
        "word": "слово",
        "translation": "переклад",
        "definition": "визначення",
        "example": "приклад"
      }}
    ]
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "LIMIT_EXCEEDED"
        raise e

def format_words_text(response: str):
    try:
        start_index = response.find('[')
        end_index = response.rfind(']') + 1
        
        if start_index == -1 or end_index == 0:
            return "❌ ШІ надіслав дані у неправильному форматі."

        json_str = response[start_index:end_index]
        words_list = json.loads(json_str)
        
        formatted_text = "<b>📚 Твої слова:</b>\n\n"
        
        for item in words_list:
            formatted_text += (
                f"🇬🇧 <b>{item['word']}</b> — {item['translation']}\n"
                f"📖 <i>{item['definition']}</i>\n"
                f"💡 Example: <u>{item['example']}</u>\n"
                f"{'—' * 20}\n"
            )
        
        return formatted_text
    
    except Exception as e:
        print(f"Помилка парсингу: {e}\nТекст від ШІ: {response}")
        return "❌ Помилка при обробці слів."
    

