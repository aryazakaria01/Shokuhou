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
from pyrogram import ChatPermissions

from .. import router
from sophie.components.pyrogram import pyrogram
from sophie.modules.utils.strings import apply_strings_dec
from sophie.modules.utils.message import get_args_list

# TODO: Add more locktypes, Use admin filter, Use arg filter


class LocksModule:

    @staticmethod
    def list_locktypes():
        types: dict = {
            'can_send_messages': 'all',
            'can_send_media_messages': 'media',
            'can_send_stickers': 'stickers',
            'can_send_animations': 'gif',
            'can_send_games': 'games',
            'can_use_inline_bots': 'bot',
            'can_send_polls': 'polls'
        }
        return types

    def handle_input(self, inputs: list):
        args_list: list = []
        failed_list: list = []
        for args in inputs:
            if args in (self.list_locktypes()).values():
                args_list.append(args)
            else:
                failed_list.append(args)
        return args_list, failed_list

    async def create_output(self, args: list, action: bool, chat_id):
        output = dict()
        duplicate = list()
        for locktype in self.list_locktypes().items():
            if locktype[1] in (arg for arg in args):
                if await self.check_duplicate(locktype[0], action, chat_id):
                    duplicate.append(locktype[1])
                    continue
                output[locktype[0]] = action
        return output, duplicate

    async def set_permission(self, locktypes: list, action: bool, chat_id):
        output, duplicate = await self.create_output(locktypes, action, chat_id)
        if output:
            new_permissions = await self.parse_output(output, chat_id)
            await pyrogram.set_chat_permissions(chat_id, new_permissions)
        return duplicate

    @staticmethod
    async def get_current_permissions(chat_id):
        return (await pyrogram.get_chat(chat_id)).permissions

    async def check_duplicate(self, locktype, action, chat_id):
        permissions = await self.get_current_permissions(chat_id)
        if permissions[locktype] == action:
            return True
        else:
            return False

    async def parse_output(self, output, chat_id):
        permissions = await self.get_current_permissions(chat_id)
        for new_permission in output.items():
            permissions[new_permission[0]] = new_permission[1]
        return permissions


@router.message(commands=['locks', 'locktypes'])
@apply_strings_dec('locks')
class Locks(MessageHandler, LocksModule):
    async def locktypes(self):
        text = '<b>Available locktypes</b>\n'
        for lockype in self.list_locktypes().items():
            current_permission = await self.get_current_permissions(self.chat.id)
            status = not current_permission[lockype[0]]
            text += f'- <code>{lockype[1]}</code> : {status}\n'
        return text

    async def handle(self):
        await self.event.answer(await self.locktypes())


@router.message(commands=['lock'])
@apply_strings_dec('locks')
class Lock(MessageHandler, LocksModule):

    async def parse(self):
        chat = self.chat.id
        args, unknown_types = self.handle_input(get_args_list(self.event))
        if 'all' in args:
            return await self.lock_all()

        already_locked = await self.set_permission(args, False, chat)
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
        if not await self.check_duplicate('can_send_messages', False, self.chat.id):
            await pyrogram.set_chat_permissions(self.chat.id, ChatPermissions())
            return ['all'], [], []
        return [], [], ['all']

    async def handle(self):
        if get_args_list(self.event) == ['']:
            return
        text = await self.lock()
        await self.event.answer(text)


@router.message(commands=['unlock'])
@apply_strings_dec('locks')
class Unlock(MessageHandler, LocksModule):

    async def parse(self):
        chat = self.chat.id
        args, unknown_types = self.handle_input(get_args_list(self.event))
        if 'all' in args:
            return await self.unlock_all()

        already_unlocked = await self.set_permission(args, True, chat)
        return args, unknown_types, already_unlocked

    async def lock(self):
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
        locks = dict()
        for locktype in self.list_locktypes().keys():
            if not await self.check_duplicate(locktype, True, self.chat.id):
                locks.update({locktype: True})
        permissions = ChatPermissions(**locks)
        await pyrogram.set_chat_permissions(self.chat.id, permissions)
        return ['all'], [], []

    async def handle(self):
        if get_args_list(self.event) == ['']:
            return
        text = await self.lock()
        await self.event.answer(text)
