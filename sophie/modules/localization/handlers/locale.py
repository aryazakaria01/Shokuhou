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

from aiogram.dispatcher.handler import MessageHandler
from aiogram.api.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import router

from sophie.components.localization.locale import get_chat_locale, set_chat_locale, get_languages_list


@router.message(commands=['lang'])
class GetLanguageMenu(MessageHandler):
    async def handle(self):
        chat_id = self.chat.id
        language = await get_chat_locale(chat_id)
        await self.event.reply(language)

