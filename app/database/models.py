"""
This module defines the database models using SQLAlchemy.
It includes models for users, their generated words, and quiz tests.
"""

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Create an asynchronous engine for SQLite
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# Create an async session factory
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""
    pass


class User_registration(Base):
    """
    Model representing a registered user.
    Stores the user's Telegram ID, English level, and name.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger) 
    level: Mapped[str] = mapped_column(String(3), nullable=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=True)

    words: Mapped[list["User_words"]] = relationship(back_populates="user")
    tests: Mapped[list["Test"]] = relationship(back_populates="user")

class User_words(Base):
    """
    Model representing words generated for a user.
    Stores both current and previous words and topics.
    """
    __tablename__ = 'words'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    words: Mapped[str] = mapped_column()
    topic: Mapped[str] = mapped_column()
    words_old: Mapped[str] = mapped_column(nullable=True)
    topic_old: Mapped[str] = mapped_column(nullable=True)
    
    
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    user: Mapped["User_registration"] = relationship(back_populates="words")

class Test(Base):
    """
    Model representing quiz tests generated for a user.
    Stores current and previous tests in JSON format.
    """
    __tablename__ = 'tests'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tests: Mapped[str] = mapped_column()
    tests_old: Mapped[str] = mapped_column(nullable=True)
    
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    user: Mapped["User_registration"] = relationship(back_populates="tests")


async def async_main():
    """
    Initializes the database by creating all defined tables.

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)