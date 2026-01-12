from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User_registration(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger) 
    level: Mapped[str] = mapped_column(String(3), nullable=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=True)

    words: Mapped[list["User_words"]] = relationship(back_populates="user")

class User_words(Base):
    __tablename__ = 'words'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    words: Mapped[str] = mapped_column()
    words_old: Mapped[str] = mapped_column(nullable=True)
    
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    user: Mapped["User_registration"] = relationship(back_populates="words")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)