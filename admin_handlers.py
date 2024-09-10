import asyncio
import logging
import sys
from typing import Union

from aiogram import Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ErrorEvent
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import handlers
from filters import IsAdminFilter, GetPageFilter, GetObjectIdFilter
from keyboard import main_admin_keyboard, admin_users_keyboard, admin_user_keyboard

from models import User

logger = logging.getLogger("mylog")
router = Router()


async def admin(message: Union[types.Message, types.CallbackQuery], session: AsyncSession):
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text("Hello, admin!", reply_markup=main_admin_keyboard())
    else:
        await message.reply("Hello, admin!", reply_markup=main_admin_keyboard())


async def users_handler(call: types.CallbackQuery, session: AsyncSession, page: int = 1):
    users = await User.get_all(session)
    await call.message.edit_text(f"Users count: {len(users)}\n\nUsers list:", reply_markup=admin_users_keyboard(users, page))


async def check_user_details_handler(call: types.CallbackQuery, session: AsyncSession, obj_id: int = None):
    user = await User.get(session, id=obj_id)
    await session.refresh(user)
    message = (f"User details:\n\n"
               f"ID: {user.id}\n"
               f"UID: <a href='tg://user?id={user.uid}'>{user.uid}</a>\n"
               f"Username: @{user.username}\n"
               f"Fullname: {user.fullname}\n"
               f"Registered: {user.registered.strftime('%d.%m.%Y %H:%M:%S')}\n"
               f"Is admin: {'🟢' if user.is_admin else '🔴'}\n")

    await call.message.edit_text(message, reply_markup=admin_user_keyboard(user))


async def toggle_admin(call: types.CallbackQuery, session: AsyncSession, obj_id: int = None):
    user = await User.get(session, id=obj_id)
    user.is_admin = not user.is_admin
    await session.commit()
    await check_user_details_handler(call, session, obj_id)


async def block_user(call: types.CallbackQuery, session: AsyncSession, obj_id: int = None):
    user = await User.get(session, id=obj_id)
    user.is_blocked = not user.is_blocked
    await session.commit()
    await check_user_details_handler(call, session, obj_id)


async def error_handler(event: ErrorEvent, session: AsyncSession = None):
    logger.error(f"Error: {event.exception}", exc_info=True)


def register_admin_handlers(dp: Dispatcher):
    router.message.filter(IsAdminFilter(True))
    router.callback_query.filter(IsAdminFilter(True))
    router.message.register(admin, Command("admin"))
    router.callback_query.register(admin, F.data == "admin")

    router.callback_query.register(users_handler, GetPageFilter(), F.data.startswith("users"))
    router.callback_query.register(check_user_details_handler, GetPageFilter(), GetObjectIdFilter(), F.data.regexp(r"user_id\d+"))

    router.callback_query.register(toggle_admin, GetObjectIdFilter(), F.data.regexp(r"toggle_admin_id\d+"))
    router.callback_query.register(block_user, GetObjectIdFilter(), F.data.regexp(r"block_user_id\d+"))

    router.error.register(error_handler)

    dp.include_router(router)
