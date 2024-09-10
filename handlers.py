import datetime
import logging
import os
from typing import Union

from aiogram import Dispatcher, types, Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ErrorEvent
from sqlalchemy.ext.asyncio import AsyncSession

from filters import GetPageFilter, GetObjectIdFilter, IsBlockedFilter
from keyboard import main_user_keyboard, loading_keyboard, cancel_keyboard
from models import User

logger = logging.getLogger("mylog")

router = Router()


async def cancel(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Canceled")


async def empty_handler(call: types.CallbackQuery):
    await call.answer()


async def start(message: Union[types.Message, types.CallbackQuery], session: AsyncSession):
    try:
        user = await User.get(session, uid=message.from_user.id)
        if user is None:
            user = User(uid=message.from_user.id, username=message.from_user.username, fullname=message.from_user.full_name)
            session.add(user)
        else:
            if user.username != message.from_user.username:
                user.username = message.from_user.username
            if user.fullname != message.from_user.full_name:
                user.fullname = message.from_user.full_name
        await session.commit()
        if isinstance(message, types.CallbackQuery):
            await session.refresh(user)
            await message.message.edit_text(f"Hello, {user.username}!", reply_markup=main_user_keyboard(user))
        else:
            await message.reply(f"Hello, {user.username}!", reply_markup=main_user_keyboard(user))
    except Exception as e:
        await session.rollback()
        logger.error(e)
        await message.answer("An error occurred while processing your request")


async def update_start_page(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_text("Loading...", reply_markup=loading_keyboard())
    await start(call, session)


async def error_handler(event: ErrorEvent, session: AsyncSession = None):
    logger.error(f"Error: {event.exception}", exc_info=True)


async def contact(message: types.Message, session: AsyncSession):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id

    user = await User.get(session,uid=user_id)
    user.phone_number = phone_number

    await session.commit()
    await message.answer("Phone number saved!")


def register_handlers(dp: Dispatcher):
    router.message.filter(IsBlockedFilter(False))
    router.callback_query.filter(IsBlockedFilter(False))
    router.message.register(start, Command("start"))
    router.callback_query.register(start, F.data == "start")
    router.callback_query.register(update_start_page, F.data == "update_start_page")
    router.callback_query.register(cancel, F.data == "cancel")
    dp.message.register(contact, F.content_type == ContentType.CONTACT)

    router.callback_query.register(empty_handler, F.data == "empty")

    router.error.register(error_handler)

    dp.include_router(router)
