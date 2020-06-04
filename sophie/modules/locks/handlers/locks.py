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

import re
from contextlib import suppress

from aiogram.api import types
from aiogram.dispatcher.handler import MessageHandler
from aiogram.utils.exceptions import TelegramAPIError
from pyrogram import ChatPermissions
from pyrogram.errors import BadRequest, ChatNotModified
from rejson import Path
from sophie.modules.utils.strings import apply_strings_dec

from sophie.components.caching import redis
from sophie.components.pyrogram import pbot
from sophie.modules.utils.message import get_args_list
from sophie.services.mongo import mongo
from .. import router, background_router


# TODO: Use admin filter, Use arg filter


class LocksModule:

    def locks(self):
        api_list = list(self.api_list().keys())
        non_api_list = self.nonapi_list()
        return ['all'] + api_list + non_api_list

    @staticmethod
    def api_list():
        locktypes = {
            'text': 'can_send_messages',
            'media': 'can_send_media_messages',
            'stickers': 'can_send_stickers',
            'gif': 'can_send_animations',
            'games': 'can_send_games',
            'bot': 'can_use_inline_bots',
            'polls': 'can_send_polls',
            'preview': 'can_add_web_page_previews'
        }
        return locktypes

    @staticmethod
    def nonapi_list():
        locktypes = [
            'audio', 'button',
            'command', 'contact',
            'document', 'email',
            'forward', 'invitelink',
            'location', 'photo',
            'url', 'video',
            'emojigames', 'voice'
        ]
        return locktypes

    def handle_input(self, inputs):
        args_list: list = []
        failed_list: list = []
        for args in inputs:
            if args in self.locks():
                args_list.append(args)
            else:
                failed_list.append(args)

        return args_list, failed_list

    async def create_output(self, args, action, chat_id):
        output = dict()
        duplicate = list()
        for locktype in self.api_list().items():
            if locktype[0] in (arg for arg in args):
                args.remove(locktype[0])
                if await self.check_duplicate(locktype[1], action, chat_id):
                    duplicate.append(locktype[0])
                    continue
                output[locktype[1]] = action

        for arg in args:
            if arg in self.nonapi_list():
                if not await self.check_duplicate(arg, action, chat_id, api=False):
                    await self.db_lock(arg, action, chat_id)
                else:
                    duplicate.append(arg)
        return output, duplicate

    shorts = {
        'emojigames': 'dice',
    }

    async def db_lock(self, locktype, action, chat_id):
        if isinstance(locktype, list):
            new = dict()
            new['chat_id'] = chat_id
            for lock in locktype:
                if lock in self.shorts.keys():
                    lock = self.shorts.get(lock)
                new[lock] = action
        else:
            if locktype in self.shorts.keys():
                locktype = self.shorts.get(locktype)
            new = {'chat_id': chat_id, locktype: action}
        await mongo.locks.update_one(
            {'chat_id': chat_id},
            {'$set': new},
            upsert=True
        )
        await self.update_cache(chat_id)

    async def set_permission(self, locktypes, action, chat_id):
        output, duplicate = await self.create_output(locktypes, action, chat_id)
        if output:
            new_permissions = await self.parse_output(output, chat_id)
            data = await pbot.set_chat_permissions(chat_id, new_permissions)
            key = f'api_locks_{chat_id}'
            redis.jsonset(key, Path.rootPath(), vars(data.permissions))
            redis.expire(key, 1000)
        return duplicate

    @staticmethod
    async def get_current_permissions(chat_id):
        return (await pbot.get_chat(chat_id)).permissions

    async def check_duplicate(self, locktype, action, chat_id, api=True):
        if api:
            permissions = await self.get_current_permissions(chat_id)
            if permissions[locktype] == action:
                return True
            else:
                return False
        else:
            if locktype in self.shorts:
                locktype = self.shorts.get(locktype)
            current_settings = await mongo.locks.find_one({'chat_id': chat_id})
            if current_settings is not None and locktype in current_settings:
                return current_settings[locktype] == action
            return False

    async def parse_output(self, output, chat_id):
        permissions = await self.get_current_permissions(chat_id)
        for new_permission in output.items():
            permissions[new_permission[0]] = new_permission[1]
        return permissions

    @staticmethod
    async def update_cache(chat_id):
        data = await mongo.locks.find_one({'chat_id': chat_id})
        if data is not None:
            del data['chat_id'], data['_id']
            redis.jsonset(f'locks_{chat_id}', Path.rootPath(), data)
            return data


@background_router.message(content_types=types.message.ContentType.ANY)
class LocksHandler(MessageHandler, LocksModule):

    async def get_cache(self):
        if data := redis.jsonget(f'locks_{self.chat.id}'):
            return data
        else:
            return await self.update_cache(self.chat.id)

    async def check_message(self):
        data = await self.get_cache()
        if data is not None:
            for lock in data:
                if data.get(lock) is False and hasattr(self.event, lock) and getattr(self.event, lock) is not None:
                    return True

            if self.event.entities is not None:
                for entity in self.event.entities:
                    if entity.type in data and data[entity.type] is False:
                        return True

            if self.event.text:
                if 'invitelink' in data and data['invitelink'] is False:
                    invitelink = r'(https://|)(t.me/)(\w+)(/.+|)'
                    if data := re.search(invitelink, self.event.text):
                        if (match := data.group(3)) != 'joinchat':
                            try:
                                chat = (await pbot.get_chat('@' + match)).type
                            except BadRequest:
                                pass
                            else:
                                return chat in ('supergroup', 'group')
                        else:
                            return True

            if 'forward' in data and data['forward'] is False:
                if self.event.forward_from_chat or self.event.forward_from is not None:
                    return True

    async def handle(self):
        if await self.check_message():
            await self.bot.delete_message(self.chat.id, self.event.message_id)


@router.message(commands=['locks', 'locktypes', 'locked'], user_admin=True)
@apply_strings_dec('locks')
class Locks(MessageHandler, LocksModule):
    async def locktypes(self):
        if self.data['command'].command == 'locked':
            text = '<b>Currently locked types:</b>\n'
            count = 0
            for lock in self.locks():
                if not await self.get_status(lock):
                    count += 1
                    text += f'- <code>{lock}</code>\n'
            if count < 1:
                text = 'Nothing is locked here!'
            return text
        text = '<b>Current lock settings:</b>\n'
        for lock in self.locks():
            text += f'- <code>{lock}</code> : {not await self.get_status(lock)}\n'
        return text

    async def get_status(self, lock):
        if lock in self.api_list().keys():
            lock = self.api_list().get(lock)
            if data := redis.jsonget(f'api_locks_{self.chat.id}'):
                return data[lock]
            else:
                data = (await pbot.get_chat(self.chat.id)).permissions
                key = f'api_locks_{self.chat.id}'
                redis.jsonset(key, Path.rootPath(), vars(data))
                redis.expire(key, 1000)
                return data[lock]

        if lock in self.nonapi_list():
            data = redis.jsonget(f'locks_{self.chat.id}')
            if data is not None and lock in data:
                return data[lock]
            return True

        if lock == 'all':
            api = redis.jsonget(f'api_locks_{self.chat.id}')
            if api is None:
                api = (await pbot.get_chat(self.chat.id)).permissions
                key = f'api_locks_{self.chat.id}'
                redis.jsonset(key, Path.rootPath(), vars(api))
                redis.expire(key, 1000)
            for lock in self.api_list().values():
                if api[lock] is True:
                    return True
            for lock in self.nonapi_list():
                if lock not in (data := await mongo.locks.find_one({'chat_id': self.chat.id})):
                    return True
                if data[lock] is not False:
                    return True
            return False

    async def handle(self):
        try:
            message = await self.event.reply('Fetching...')
        except TelegramAPIError:
            message = await self.event.answer('Fetching...')
        await self.bot.edit_message_text(await self.locktypes(), self.chat.id, message.message_id, parse_mode='HTML')


@router.message(commands=['lock'])
@apply_strings_dec('locks')
class Lock(MessageHandler, LocksModule):

    async def parse(self):
        chat = self.chat.id
        args, unknown_types = self.handle_input(get_args_list(self.event))
        if 'all' in args:
            return await self.lock_all()

        already_locked = await self.set_permission(list(args), False, chat)
        await self.update_cache(self.chat.id)
        return args, unknown_types, already_locked

    async def lock(self):
        text = str()
        args, utypes, already_locked = await self.parse()
        for lock in already_locked:
            if lock in args:
                args.remove(lock)
        if (count := len(args)) > 0:
            text += f'Successfully locked {count} locktypes \n'
            for arg in args:
                text += f'- <code>{arg}</code>\n'

        if (count := len(utypes + already_locked)) > 0:
            text += f'\n Unable to lock {count} given types - '
            if len(already_locked) > 0:
                modified_list = []
                for i in already_locked:
                    modified_list.append(f'<code>{i}</code>')
                text += f'locktype(s) {", ".join(modified_list)} was already locked!'
                if len(utypes) > 0:
                    text += 'and '

            if (count := len(utypes)) > 0:
                text += f'found {count} unknown locktypes (use <code>/locks</code> to see valid locktypes)'
        return text

    async def lock_all(self):
        with suppress(ChatNotModified):
            data = await pbot.set_chat_permissions(self.chat.id, ChatPermissions())
            key = f'api_locks_{self.chat.id}'
            redis.jsonset(key, Path.rootPath(), vars(data.permissions))
            redis.expire(key, 1000)
        await self.db_lock(self.nonapi_list(), False, self.chat.id)
        await self.update_cache(self.chat.id)
        await self.bot.edit_message_text(f'Locked everything in <b>{self.chat.title}</b>',
                                         self.chat.id, self.message.message_id, parse_mode="HTML")
        return [], [], []

    async def handle(self):
        try:
            self.message = await self.event.reply('Locking...')
        except TelegramAPIError:
            self.message = await self.event.answer('Locking...')
        if get_args_list(self.event) == ['']:
            return
        text = await self.lock()
        if text:
            await self.bot.edit_message_text(text, self.chat.id, self.message.message_id, parse_mode='HTML')


@router.message(commands=['unlock'])
@apply_strings_dec('locks')
class Unlock(MessageHandler, LocksModule):

    async def parse(self):
        chat = self.chat.id
        args, unknown_types = self.handle_input(get_args_list(self.event))
        if 'all' in args:
            return await self.unlock_all()

        already_unlocked = await self.set_permission(list(args), True, chat)
        await self.update_cache(self.chat.id)
        return args, unknown_types, already_unlocked

    async def unlock(self):
        text = str()
        args, utypes, already_unlocked = await self.parse()
        for lock in already_unlocked:
            if lock in args:
                args.remove(lock)
        if (count := len(args)) > 0:
            text += f'Successfully unlocked {count} locktype(s) \n'
            for arg in args:
                text += f'- <code>{arg}</code>\n'

        if (count := len(utypes + already_unlocked)) > 0:
            text += f'\n Unable to unlock {count} given types - '
            if len(already_unlocked) > 0:
                modified_list = []
                for i in already_unlocked:
                    modified_list.append(f'<code>{i}</code>')
                text += f'\nlocktype(s) {", ".join(modified_list)} was already unlocked!'
                if len(utypes) > 0:
                    text += 'and '

            if (count := len(utypes)) > 0:
                text += f'found {count} unknown locktype(s) (use <code>/locks</code> to see valid locktypes)'
        return text

    async def unlock_all(self):
        locks = {
            'can_send_messages': True,
            'can_send_media_messages': True,
            'can_send_stickers': True,
            'can_send_animations': True,
            'can_send_games': True,
            'can_use_inline_bots': True,
            'can_send_polls': True,
            'can_add_web_page_previews': True
        }
        permissions = ChatPermissions(**locks)
        with suppress(ChatNotModified):
            data = await pbot.set_chat_permissions(self.chat.id, permissions)
            key = f'api_locks_{self.chat.id}'
            redis.jsonset(key, Path.rootPath(), vars(data.permissions))
            redis.expire(key, 1000)
        await self.db_lock(self.nonapi_list(), True, self.chat.id)
        await self.update_cache(self.chat.id)
        await self.bot.edit_message_text(f'Unlocked everything in <b>{self.chat.title}</b>!',
                                         self.chat.id, self.message.message_id, parse_mode='HTML')
        return [], [], []

    async def handle(self):
        try:
            self.message = await self.event.reply('Unlocking...')
        except TelegramAPIError:
            self.message = await self.event.answer('Unlocking...')
        if get_args_list(self.event) == ['']:
            return
        text = await self.unlock()
        if text:
            await self.bot.edit_message_text(text, self.chat.id, self.message.message_id, parse_mode='HTML')
