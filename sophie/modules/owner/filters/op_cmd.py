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

import re

from typing import Any, Dict, Union

from aiogram import Router
from aiogram.api.types import Message
from aiogram.dispatcher.filters import BaseFilter


class IsOPCmd(BaseFilter):
    op_cmd: str

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        text = message.text or message.caption
        if not text:
            return False

        r_pattern = f'[/!]op {self.op_cmd} ?(.*)'
        if result := re.match(r_pattern, text):
            return {
                'arg_raw': result.group(1),
                'arg_list': result.group(1).split(' ')
            }

        return False


def __setup__(dp: Router) -> Any:
    dp.message.bind_filter(IsOPCmd)
