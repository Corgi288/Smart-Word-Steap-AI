"""
This module contains database request functions for interacting with the database models.
It provides an abstraction layer for CRUD operations related to users, words, and tests.
"""

from app.database.models import async_session
from app.database.models import User_registration, User_words, Test
from sqlalchemy import select, update, or_
import json


async def set_user(tg_id):
    """
    Checks if a user exists in the database. If not, creates a new user entry.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        User_registration or None: Returns the User_registration object if the user already existed,
                                  otherwise returns None after creating the user.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))

        if not user:
            session.add(User_registration(tg_id=tg_id))
            await session.commit()
            return None 
        return user
    
async def add_user(tg_id, name, level):
    """
    Updates a user's profile with their name and English level.

    Args:
        tg_id (int): The Telegram user ID.
        name (str): The user's name.
        level (str): The user's English level.

    Returns:
        None
    """
    async with async_session() as session:
        await session.execute(update(User_registration).where(User_registration.tg_id == tg_id).values(user_name=name, level=level))
        await session.commit()

async def update_level(tg_id, level):
    """
    Updates the English level of an existing user.

    Args:
        tg_id (int): The Telegram user ID.
        level (str): The new English level.

    Returns:
        None
    """
    async with async_session() as session:
        await session.execute(update(User_registration).where(User_registration.tg_id == tg_id).values(level=level))
        await session.commit()

async def add_words(tg_id: int, new_words_text: str, new_topic: str):
    """
    Adds newly generated words to the database for a user.
    Moves current words to 'old_words' and current topic to 'old_topic' before updating.

    Args:
        tg_id (int): The Telegram user ID.
        new_words_text (str): The formatted text of the new words.
        new_topic (str): The topic of the new words.

    Returns:
        User_registration: The user object associated with the words.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))
        
        if not user:
            user = User_registration(tg_id=tg_id)
            session.add(user)
            await session.flush()

        word_entry = await session.scalar(
            select(User_words).where(User_words.user_tg_id == tg_id)
        )

        if word_entry:
            word_entry.words_old = word_entry.words
            word_entry.topic_old = word_entry.topic  
    
            word_entry.words = new_words_text
            word_entry.topic = new_topic
        else:
            session.add(User_words(words=new_words_text, user_tg_id=tg_id, topic=new_topic))

        await session.commit()
        return user
    
async def add_user_test(tg_id: int, quizzes_list: list):
    """
    Adds newly generated quiz tests to the database for a user.
    Saves current tests to 'tests_old' and updates 'tests' with new JSON data.

    Args:
        tg_id (int): The Telegram user ID.
        quizzes_list (list): A list of dictionaries representing quiz questions.

    Returns:
        None
    """
    async with async_session() as session:
        quizzes_json = json.dumps(quizzes_list, ensure_ascii=False)
        stmt = select(Test).where(Test.user_tg_id == tg_id)
        existing_test = await session.scalar(stmt)
        
        if existing_test:
            existing_test.tests_old = existing_test.tests
            existing_test.tests = quizzes_json
        else:
            new_entry = Test(
                tests=quizzes_json,
                user_tg_id=tg_id
            )
            session.add(new_entry)
            
        await session.commit()

async def get_user_level(tg_id):
    """
    Retrieves the English level of a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The user's English level if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))
        
        if user:
            return user.level 
        return None

async def get_user_name(tg_id):
    """
    Retrieves the name of a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The user's name if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))
        
        if user:
            return user.user_name 
        return None
    
from sqlalchemy import select

async def get_old_words(tg_id):
    """
    Retrieves the previously generated words for a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The previous words text if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.words_old
        return None
    
async def get_words(tg_id):
    """
    Retrieves the currently active generated words for a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The current words text if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.words
        return None
    
async def get_topics(tg_id):
    """
    Retrieves the topic of the currently active words for a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The current topic if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.topic
        return None
    
async def get_old_topics(tg_id):
    """
    Retrieves the topic of the previously generated words for a user.

    Args:
        tg_id (int): The Telegram user ID.

    Returns:
        str or None: The previous topic if found, otherwise None.
    """
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.topic_old
        return None
    
