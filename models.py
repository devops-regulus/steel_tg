import asyncio
import datetime
import logging
import os
from typing import List, Optional

import dotenv
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, JSON, select, ForeignKey, Text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column, selectinload
from sqlalchemy.sql import func
from sqlalchemy_utils import database_exists, create_database
dotenv.load_dotenv()
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DEBUG = str(os.environ.get("DEBUG", 0)) == "1"
SQLALCHEMY_DATABASE_URI = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    uid = Column(BigInteger, unique=True)
    username = Column(String(255))
    fullname = Column(String(255))
    is_admin = Column(Boolean, default=False)
    registered = Column(DateTime(timezone=True), default=func.now())
    phone_number = Column(String(15), unique=True, index=True)

    is_blocked = Column(Boolean, default=False)

    def __str__(self):
        return f"#{self.id} [{self.uid}] @{self.username} {self.fullname}"

    @staticmethod
    async def get_admins(session: AsyncSession):
        admins = await session.execute(select(User).filter_by(is_admin=True))
        return admins.unique().scalars().all()

    @staticmethod
    async def get(session: AsyncSession, **kwargs):
        user = await session.execute(select(User).filter_by(**kwargs))
        return user.scalars().first()

    @staticmethod
    async def get_all(session: AsyncSession):
        users = await session.execute(select(User))
        return users.unique().scalars().all()

    @staticmethod
    async def count(session: AsyncSession):
        count_query = select(func.count()).select_from(User)
        users_count = await session.execute(count_query)
        return users_count.scalar()


engine = create_async_engine(SQLALCHEMY_DATABASE_URI, echo=DEBUG)

sessionmaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_database_if_not_exists():
    logger = logging.getLogger("mylog")
    try:
        sync_engine = create_engine(SQLALCHEMY_DATABASE_URI.replace("mysql+aiomysql", "mysql+pymysql"))
        if not database_exists(sync_engine.url):
            logger.info("Creating database {DB_NAME}")
            create_database(sync_engine.url)
        else:
            logger.info(f"Found existing database {DB_NAME}")
    except Exception as e:
        logger.error(e)
        return False
    return True


async def init_models():
    logger = logging.getLogger("mylog")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Models created")
    except Exception as e:
        logger.error(e)
        exit(1)

