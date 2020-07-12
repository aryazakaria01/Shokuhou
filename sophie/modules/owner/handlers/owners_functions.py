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

from sophie.modules.utils.text import FormatListText
from sophie.modules.utils.term import term


class OwnersFunctions:
    async def __setup__(self, router):
        # self.echo.only_owner = True
        pass

    async def stats(self):
        from sophie.version import version
        from sophie.modules import LOADED_MODULES

        text_list = FormatListText({
            'General': {
                'Version': version
            }
        }, title='Stats')

        for module in LOADED_MODULES:
            if getattr(module['object'], '__stats__', None):
                text_list = module['object'].__stats__(text_list)

        await self.reply(text_list.text)

    async def modules(self):
        from sophie.utils.loader import LOADED_MODULES

        text_list = FormatListText([], title='Loaded modules')
        for module in LOADED_MODULES.values():
            text_list.data.append((module['name'], {'ver': module['version']}))

        # Convert list to tuple, to make FormatListText understand this as typed list
        text_list.data = tuple(text_list.data)

        await self.reply(text_list.text)

    async def term(self, arg_raw=None):
        cmd = arg_raw
        text_list = FormatListText({'$': '\n' + arg_raw}, title='Shell')
        stdout, stderr = await term(cmd)
        text_list['stdout'] = '\n' + stdout
        text_list['stderr'] = '\n' + stderr
        await self.reply(text_list.text)
