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

from aiogram.dispatcher.handler import MessageHandler
from aiogram.utils.exceptions import TelegramAPIError

from sophie.components.connections import set_connected_chat, chat_connection
from sophie.components.localization.strings import get_strings_dec
from .. import router


async def connect_chat(message, user, chat, strings):
    await set_connected_chat(user.id, chat)
    text = strings.get('pm_connected', chat=chat.title)
    try:
        await message.reply(text)
    except TelegramAPIError:
        await message.answer(text)


@router.message(commands=['connect'], only_groups=True)
@get_strings_dec
class ChatConnectionGroup(MessageHandler):
    async def handle(self):
        await self.bot.send_message(self.from_user.id, self.data['strings'].get('pm_connected', chat=self.chat.title))
        await connect_chat(self.event, self.from_user, self.chat, self.data['strings'])


@router.message(commands=['disconnect'], only_pm=True)
@chat_connection()
@get_strings_dec
class DisconnectChat(MessageHandler):
    async def handle(self):
        if self.from_user.id != self.chat.chat_id:
            await set_connected_chat(self.from_user.id)
            return await self.event.reply(self.data['strings'].get('disconnected_successfully', chat=self.chat.title))
        return await self.event.reply(self.data['strings'].get('nothing_connected'))
