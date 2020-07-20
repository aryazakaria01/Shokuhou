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

from typing import Any, Dict, Union

from aiogram import Router
from aiogram.dispatcher.filters import BaseFilter, Command


class CmdFilter(BaseFilter):
    cmds: list

    commands_prefix: str = "/"
    commands_ignore_case: bool = False
    commands_ignore_mention: bool = False

    async def __call__(self, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        self.commands = self.cmds
        return await Command.__call__(*args, **kwargs)

    parse_command = Command.parse_command


def __setup__(dp: Router) -> Any:
    # dp.message.bind_filter(CmdFilter)
    pass
