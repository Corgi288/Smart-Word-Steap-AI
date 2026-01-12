from app.database.models import async_session
from app.database.models import User_registration, User_words
from sqlalchemy import select, update, delete



async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))

        if not user:
            session.add(User_registration(tg_id=tg_id))
            await session.commit()
            return None 
        return user
    
async def add_user(tg_id, name, level):
    async with async_session() as session:
        await session.execute(update(User_registration).where(User_registration.tg_id == tg_id).values(user_name=name, level=level))
        await session.commit()

async def add_words(tg_id: int, new_words_text: str):
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
            word_entry.words = new_words_text
        else:
            session.add(User_words(words=new_words_text, user_tg_id=tg_id))

        await session.commit()
        return user

async def get_user_level(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))
        
        if user:
            return user.level 
        return None

async def get_user_name(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User_registration).where(User_registration.tg_id == tg_id))
        
        if user:
            return user.user_name 
        return None
    
from sqlalchemy import select

async def get_old_words(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.words_old
        return None
    
async def get_words(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User_words).where(User_words.user_tg_id == tg_id))
        
        if user:
            return  user.words
        return None