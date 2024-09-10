import logging
from asyncio import sleep

from aiogram.types import BotCommandScopeChat
from sqlalchemy.ext.asyncio import AsyncSession

from globals import BOT_ORDINARY_COMMANDS, BOT_ADMIN_COMMANDS
from models import User

logger = logging.getLogger("mylog")


async def on_startup_notify(bot, session: AsyncSession):
    text = "Bot was started ✅"
    me = await bot.get_me()
    logger.info("Link to bot: https://t.me/{username}".format(username=me.username))
    logger.info("Admins notify...")
    admins = await User.get_admins(session)

    for admin in admins:
        try:
            await bot.send_message(admin.uid, text)
            await bot.set_my_commands(
                commands=BOT_ORDINARY_COMMANDS + BOT_ADMIN_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin.uid)
            )
            logger.info(f"Notify message send to admin: @{admin.username} [{admin.id}]")
        except Exception as ex:
            logger.error(f"Admins notify exception: {ex}")

        await sleep(0.1)


async def on_shutdown_notify(bot, session: AsyncSession):
    admins = await User.get_admins(session)
    text = "Bot was stopped 🚫"
    logger.info("Stopping Admins notify...")
    for admin in admins:
        try:
            await bot.send_message(admin.uid, text)
            logger.info(f"Notify message send to admin: @{admin.username} [{admin.id}]")
        except Exception as ex:
            logger.error(f"Admins notify exception: {ex}")
        await sleep(0.1)
