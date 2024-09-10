import datetime
import os

import humanize
import paramiko
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


def format_timedelta(td):
    return humanize.naturaldelta(td)


def timedelta_to_sentence(td):
    return humanize.precisedelta(td, format="%.0f")


async def create_default_admin(session: AsyncSession):
    admin_id = os.getenv("DEFAULT_ADMIN")
    if not admin_id or not admin_id.isdigit():
        return False
    admin = await User.get(session, uid=int(admin_id))
    if not admin:
        admin = User(uid=int(admin_id), username="admin", fullname="admin", is_admin=True)
        session.add(admin)
        await session.commit()


def generate_progress_bar(percent):
    # Задаємо максимальну довжину шкали прогресу (20 символів для 100%)
    max_length = 20
    # Розраховуємо кількість дефісів та пробілів в шкалі
    num_dashes = int(max_length * (percent / 100))
    num_spaces = int(max_length - num_dashes)
    # num_spaces += int(num_spaces * 0.35)
    # Генеруємо рядок з дефісів та пробілів
    progress_bar = f'|{"█" * num_dashes + "░" * num_spaces}|'
    return progress_bar
