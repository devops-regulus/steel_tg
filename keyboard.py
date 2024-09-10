from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from helper import format_timedelta
from models import User


def main_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="👨‍💻 Users", callback_data="users"))
    # add all stats button

    builder.adjust(1, repeat=True)
    return builder.as_markup()


def loading_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Loading data...", callback_data="empty"))

    return builder.as_markup()


def cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))

    return builder.as_markup()


def admin_users_keyboard(users, page=1):
    builder = InlineKeyboardBuilder()
    users_buttons = []
    row = []
    if len(users) < 1:
        builder.add(InlineKeyboardButton(text="Users not found", callback_data="empty"))
    else:
        users_per_page = 5
        start = (page - 1) * users_per_page
        end = start + users_per_page
        for user in users[start:end]:
            users_buttons.append(InlineKeyboardButton(text=f"{user.fullname} (@{user.username})", callback_data=f"user_id{user.id}"))
            row.append(1)
        if len(users) > users_per_page:
            buttons = 0
            if page > 1:
                users_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"users_p{page - 1}"))
                buttons += 1
            if page > 1 or end < len(users):
                users_buttons.append(InlineKeyboardButton(text=f"{page}/{(len(users) - 1) // users_per_page + 1}", callback_data='empty'))
                buttons += 1
            if end < len(users):
                users_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"users_p{page + 1}"))
                buttons += 1
            row.append(buttons)
        builder.add(*users_buttons)
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="admin"))
    row.append(1)
    builder.adjust(*row, repeat=False)
    return builder.as_markup()


def admin_user_keyboard(user: User):
    builder = InlineKeyboardBuilder()
    # make user admin button
    builder.add(InlineKeyboardButton(text="🟢 Make admin" if not user.is_admin else "🔴 Remove admin", callback_data=f"toggle_admin_id{user.id}"))
    builder.add(InlineKeyboardButton(text="🟢 Unblock user" if user.is_blocked else "🟥 Block user", callback_data=f"block_user_id{user.id}"))
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="users"))
    builder.adjust(1, repeat=True)
    return builder.as_markup()


def main_user_keyboard(user: User):
    builder = ReplyKeyboardBuilder()
    builder.resize_keyboard=True
    row = []

    builder.add(KeyboardButton(text="Поділитись номером", request_contact = True))
    row.append(1)
    builder.adjust(*row, repeat=False)

    return builder.as_markup(resize_keyboard=True)
