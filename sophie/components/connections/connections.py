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

from aiogram.api.types.message import Message
from aiogram.utils.exceptions import TelegramAPIError

from sophie.components.caching import cache
from sophie.modules.utils.users import is_user_admin
from sophie.services.aiogram import bot
from sophie.services.mongo import mongo


async def get_connected_chat(message: Message, only_admin=False, only_groups=False):

    message.chat.__config__.allow_mutation = True
    # initialise another field 'chat_id' (we don't wanna edit actual id)
    message.chat.chat_id = message.chat.id

    key = f'connection_cache_{message.from_user.id}'

    if not message.chat.type == 'private':
        return True

    # check if user is banned/kicked from group
    if (cached := await cache.get(key)) and 'member_status' in cached:
        status = cached
    else:
        status = (await bot.get_chat_member(message.chat.id, message.from_user.id)).status
        await cache.set(key, {'member_status': status}, 900)

    if status in ('left', 'kicked'):
        raise ChatConnectionError('You are not in the group! Please <code>/disconnect</code> to avoid this.')

    # check for cache
    if (cached := await cache.get(key)) is not None and 'member_status' not in cached:
        message.chat.chat_id = cached['chat_id']
        message.chat.title = cached['chat_title']

        if only_admin:
            if not await is_user_admin(message.chat.chat_id, message.from_user.id):
                raise ChatConnectionError('You are not admin to use this command')
        return True

    if not (conn := await mongo.connections.find_one({'user_id': message.from_user.id})) or 'chat_id' not in conn:
        if only_groups:
            raise ChatConnectionError('This command can be only used in groups!')
        else:
            message.chat.title = 'Local Chat'
            return True

    message.chat.chat_id = conn['chat_id']
    message.chat.title = conn['chat_title']  # TODO: get this from chatlist

    if only_admin:
        if not await is_user_admin(message.chat.chat_id, message.from_user.id):
            raise ChatConnectionError('You are not admin to use this command')

    await cache.set(key, conn, 900)
    return True


def chat_connection(only_admin=False, only_groups=False):
    def wrapped(func):
        async def decorated(message, *args, **kwargs):
            try:
                if await get_connected_chat(message, only_admin, only_groups):
                    return await func(message, *args, **kwargs)
            except ChatConnectionError as error:
                try:
                    await message.reply(error.args[0])
                except TelegramAPIError:  # Reply message not found
                    await message.answer(error.args[0])
        return decorated
    return wrapped


async def set_connected_chat(user_id, chat=None):
    key = f'connection_cache_{user_id}'
    await cache.delete(key)
    if not chat:
        await mongo.connections.update_one({'user_id': user_id}, {"$unset": {'chat_id': 1}}, upsert=True)
        return

    return await mongo.connections.update_one(
        {'user_id': user_id},
        {
            "$set": {'user_id': user_id, 'chat_id': chat.id, 'chat_title': chat.title},
            "$addToSet": {'history': {'$each': [chat.id]}}
        },
        upsert=True
    )


class ChatConnectionError(BaseException):
    pass
