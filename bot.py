import asyncio
import logging
import logging.handlers
import os
from functools import partial

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from admin_handlers import register_admin_handlers
from globals import BOT_ORDINARY_COMMANDS
from handlers import register_handlers
from dotenv import load_dotenv

from helper import create_default_admin
from middlewares import DbSessionMiddleware
from models import sessionmaker, init_models, create_database_if_not_exists
from notify import on_startup_notify, on_shutdown_notify

handler = logging.handlers.TimedRotatingFileHandler('logfile.log', when='Midnight', backupCount=6)
handler.setFormatter(logging.Formatter("%(levelname)s %(asctime)s %(message)s"))
logger = logging.getLogger("mylog")
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger = logging.getLogger("mylog")


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_my_commands(
        commands=BOT_ORDINARY_COMMANDS,
    )
    session = sessionmaker()
    await create_default_admin(session)
    dispatcher.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    register_admin_handlers(dispatcher)
    register_handlers(dispatcher)
    shutdown_partial = partial(on_shutdown, session=session)
    dispatcher.shutdown.register(shutdown_partial)
    await on_startup_notify(bot, session)


async def on_shutdown(bot, session: sessionmaker):
    await on_shutdown_notify(bot, session)


async def main():
    load_dotenv()
    db_exist = await create_database_if_not_exists()
    if not db_exist:
        logger.error("Database does not exist and cannot be created")
        exit(1)
    asyncio.create_task(init_models())
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("You forgot to set BOT_TOKEN in .env file")
        exit(1)
    dp = Dispatcher(storage=MemoryStorage())
    try:
        default_properties = DefaultBotProperties(parse_mode="HTML")
        bot = Bot(token=token, default=default_properties)
    except Exception as e:
        logger.error("Bot token is invalid")
        exit(1)
    await on_startup(dp, bot)
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
