from app.database.models import async_session
from app.database.models import User_registration
from sqlalchemy import select, update



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
