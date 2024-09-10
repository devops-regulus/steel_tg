import re
from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


class IsAdminFilter(BaseFilter):
    default = False

    def __init__(self, is_admin: bool = default):
        self.is_admin = is_admin

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user = await User.get(session, uid=message.from_user.id)
        admins = await User.get_admins(session)
        return (user in admins) == self.is_admin


class IsBlockedFilter(BaseFilter):
    default = False

    def __init__(self, is_blocked: bool = default):
        self.is_blocked = is_blocked

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        user = await User.get(session, uid=message.from_user.id)

        return user.is_blocked == self.is_blocked if user else True


class GetPageFilter(BaseFilter):

    async def __call__(self, call: CallbackQuery) -> Union[bool, Dict[str, Any]]:
        page = call.data.split("_p")[-1].strip().split("_")[0].strip()
        if page.isdigit():
            return {"page": int(page)}
        return True


class GetObjectIdFilter(BaseFilter):

    async def __call__(self, call: CallbackQuery) -> Union[bool, Dict[str, Any]]:
        if not isinstance(call, CallbackQuery):
            return False
        # if multiple _id in call.data return dict of obj_ids
        if len(call.data.split("_id")) > 2:
            objects = {}
            parts = call.data.split("_")
            for i in range(len(parts)):
                if re.fullmatch(r'id\d+', parts[i]):
                    key = parts[i - 1]
                    value = int(parts[i].replace("id", ""))
                    objects[key] = value
            return {"obj_ids": objects}
        obj_id = call.data.split("_id")[-1].strip().split("_")[0].strip()
        if obj_id.isdigit():
            return {"obj_id": int(obj_id)}
        return False
