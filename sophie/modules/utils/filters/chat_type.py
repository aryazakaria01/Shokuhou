# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
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

from aiogram.dispatcher.filters import BaseFilter
from sophie.modules.connections import router


class OnlyGroups(BaseFilter):
    only_groups: bool

    async def __call__(self, message):
        if message.chat.type in ('group', 'supergroup'):
            return True
        return False


class OnlyPM(BaseFilter):
    only_pm: bool

    async def __call__(self, message):
        if message.chat.type == 'private':
            return True
        return False


def __setup__(dp):

    dp.message.bind_filter(OnlyGroups)
    dp.message.bind_filter(OnlyPM)
