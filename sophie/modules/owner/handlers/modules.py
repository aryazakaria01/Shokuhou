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

from aiogram.api.types import BufferedInputFile
from aiogram.dispatcher.handler import MessageHandler

from sophie.modules.utils.message import get_args_list
from .. import router


@router.message(commands=['modules'], is_op=True)
class ModulesListHandler(MessageHandler):
    @staticmethod
    def loaded_modules():
        from sophie.modules import LOADED_MODULES
        return LOADED_MODULES

    def list_modules_text(self):
        text = "<b>Loaded modules:</b>"
        modules = self.loaded_modules().values()
        for num, module in enumerate(modules, start=1):
            text += f"\n{num}: {module['name']} (<code>{module['version']}</code>)"

        return text

    async def list_modules(self):
        text = self.list_modules_text()
        await self.event.answer(text)

    async def dump_modules(self):
        text = str(self.loaded_modules())
        f = BufferedInputFile(text.encode(), filename='test.txt')
        await self.event.answer_document(f)

    async def handle(self):
        message = self.event

        args = get_args_list(message)
        if 'dump' in args:
            await self.dump_modules()
            return

        await self.list_modules()
