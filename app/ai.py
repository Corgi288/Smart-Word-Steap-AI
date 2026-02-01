"""
This module provides functions for interacting with the Google Gemini AI API.
It handles generating vocabulary words, formatting them, and creating quiz questions.
"""

from google import genai
import logging
import json

from config import GEMINI_API

from aiogram.types import Message
import app.database.requsts as rq

# Initialize the Gemini AI client
client = genai.Client(api_key=GEMINI_API)


async def generate_daily_words(tg_id: int, level: str, topic: str, count: str):
    """
    Generates a list of new vocabulary words using the Gemini AI.

    This function retrieves previously used words for the user to ensure new words are unique.
    It constructs a prompt for the AI specifying the role, level, topic, and constraints.

    Args:
        tg_id (int): The Telegram user ID.
        level (str): The English level of the student (e.g., A1, B2).
        topic (str): The thematic topic for the words.
        count (str): The number of words to generate.

    Returns:
        str: The raw text response from the AI, or "LIMIT_EXCEEDED" if a 429 error occurs.
    """
    used_words = await rq.get_words(tg_id)
    used_words_old = await rq.get_old_words(tg_id) 
    
    prompt = f"""
    Role: Professional English Language Teacher.
    Task: Generate {count} NEW vocabulary words for a student at the {level} level.

    THEMATIC TOPIC: 
    "{topic}"

    CONSTRAINTS:
    1. Level Accuracy: Words must strictly correspond to the {level} level (CEFR).
    2. Exclusivity: DO NOT use any of the following words (including their different forms): 
    {used_words}, {used_words_old}
    3. Quality: Choose words that are practical and commonly used within the topic "{topic}".

    OUTPUT FORMAT:
    Return ONLY a JSON ARRAY. No introductory or closing text.
    Each object in the array must follow this structure:
    [
    {{
        "word": "English word",
        "translation": "Ukrainian translation",
        "definition": "Simple definition in English",
        "example": "An example sentence using the word"
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
    """
    Parses and formats the AI's JSON response into a human-readable Telegram message.

    Args:
        response (str): The raw JSON string from the AI.

    Returns:
        str: A formatted HTML string containing words, translations, definitions, and examples,
             or an error message if parsing fails.
    """
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
    
async def generate_quiz_questions(tg_id: int, level: str, words: str, count: int):
    """
    Generates vocabulary-focused quiz questions using Gemini AI.

    This function takes a list of words and generates multiple-choice questions
    based on them, ensuring they match the user's English level.

    Args:
        tg_id (int): The Telegram user ID.
        level (str): The English level for the questions.
        words (str): The list of words to base the quiz on.
        count (int): The number of questions to generate.

    Returns:
        list or None: A list of quiz question objects (dictionaries), or None if an error occurs.
                      Each object contains "question", "options", "correct_id", and "explanation".
    """
    prompt = f"""
    Role: Senior English Language Examiner.
    Task: Create {count} vocabulary-focused questions for level {level}.

    STRICT VOCABULARY LIST (Correct answers MUST come from here):
    {words}


    RULES:
    1. TARGET WORD: Each question must focus on EXACTLY ONE word from the "STRICT VOCABULARY LIST".
    2. CORRECT ID: The target word from the list MUST be the correct answer.
    3. DISTRACTORS: Options must be complex words of the same part of speech. 
       PROHIBITED: Do not use pronouns like 'it', 'him', 'them', 'her', 'us' as options.
    4. SENTENCE: Create a sophisticated sentence where the word is missing (___). 
    5. EXPLANATION: Provide a short explanation in UKRAINIAN.

    OUTPUT: Return ONLY a JSON ARRAY. No talk, no markdown.
    Example: [{{ "question": "...", "options": ["...", "..."], "correct_id": 0, "explanation": "..." }}]
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        
        if not response or not response.text:
            logging.error("Gemini returned empty response")
            return None

        content = response.text
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        
        if json_start == -1 or json_end <= 0:
            logging.error(f"JSON not found in response. Raw text: {content}")
            return None
            
        clean_json = content[json_start:json_end]
        quizzes = json.loads(clean_json)
        
        if isinstance(quizzes, list):
            return quizzes
        return [quizzes]
        
    except Exception as e:
        logging.error(f"Error in generate_quiz_questions: {e}")
        return None

