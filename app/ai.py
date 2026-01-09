from google import genai
import asyncio
import json

from config import GEMINI_API

client = genai.Client(api_key=GEMINI_API)


async def generate_daily_words(level: str, topic: str, count: str):
    prompt = f"""
    Ти професійний вчитель англійської. 
    Підбери {count} слів для рівня {level} на тему {topic}.
    
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
        print(f"Помилка парсингу: {e}\nТекст від ШІ: {response}") # Щоб ти бачив помилку в консолі
        return "❌ Помилка при обробці слів."