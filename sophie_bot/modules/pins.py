# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2019 Aiogram

#
# This file is part of SophieBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from aiogram.utils.exceptions import BadRequest

from sophie_bot import bot
from sophie_bot.decorator import register
from .utils.connections import chat_connection
from .utils.language import get_strings_dec
from .utils.message import get_arg


@register(cmds="unpin", user_can_pin_messages=True, bot_can_pin_messages=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec('pins')
async def unpin_message(message, chat, strings):
    try:
        await bot.unpin_chat_message(chat['chat_id'])
    except BadRequest:
        await message.reply(strings['chat_not_modified_unpin'])
        return


@register(cmds="pin", user_can_pin_messages=True, bot_can_pin_messages=True)
@get_strings_dec('pins')
async def pin_message(message, strings):
    if 'reply_to_message' not in message:
        await message.reply(strings['no_reply_msg'])
        return
    msg = message.reply_to_message.message_id
    arg = get_arg(message).lower()

    loud = ['loud', 'notify']
    notify = arg in loud
    try:
        await bot.pin_chat_message(message.chat.id, msg, disable_notification=notify)
    except BadRequest:
        await message.reply(strings['chat_not_modified_pin'])
