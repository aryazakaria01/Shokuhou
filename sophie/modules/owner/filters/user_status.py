# Copyright (C) 2018 - 2020 MrYacha.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Sophie.

from typing import Any

from aiogram import Router
from aiogram.api.types import Message
from aiogram.dispatcher.filters import BaseFilter

from sophie.utils.config import config


class IsOwner(BaseFilter):
    is_owner: str

    async def __call__(self, message: Message) -> bool:
        owner_id = config.general.owner_id
        if message.from_user:
            if message.from_user.id != owner_id:
                return False

        return True


class IsOP(BaseFilter):
    is_op: str

    async def __call__(self, message: Message) -> bool:
        owner_id = config.general.owner_id
        operators = config.general.operators

        operators.append(owner_id)
        if message.from_user:
            if message.from_user.id not in operators:
                return False

        return True


def __setup__(dp: Router) -> Any:
    dp.message.bind_filter(IsOwner)
    dp.message.bind_filter(IsOP)
