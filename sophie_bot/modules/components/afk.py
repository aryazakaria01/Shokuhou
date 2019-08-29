# Copyright © 2018, 2019 MrYacha
# This file is part of SophieBot.
#
# SophieBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SophieBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

import re

from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from sophie_bot import decorator, mongodb
from sophie_bot.modules.disable import disablable_dec
from sophie_bot.modules.users import user_link


@decorator.t_command("afk ?(.*)", arg=True)
@disablable_dec("afk")
async def afk(event):
    if not event.pattern_match.group(1):
        reason = "No reason"
    else:
        reason = event.pattern_match.group(1)
    mongodb.afk.insert_one({'user': event.from_id, 'reason': reason})
    text = "{} is AFK!".format(await user_link(event.from_id))
    if reason:
        text += "\nReason: " + reason
    await event.reply(text)


async def get_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await event.client(GetFullUserRequest(previous_message.from_id))
    else:
        user = re.search('@(\w*)', event.text)
        if not user:
            return
        user = user.group(0)

        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await event.client.get_me()
            user = self_user.id

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return replied_user


@decorator.insurgent()
async def check_afk(event):
    user_afk = mongodb.afk.find_one({'user': event.from_id})
    if user_afk:
        rerere = re.findall('[!/]afk(.*)|brb ?(.*)', event.text)
        if not rerere:
            await event.reply("{} is not AFK anymore!".format(await user_link(event.from_id)))
            mongodb.afk.delete_one({'_id': user_afk['_id']})

    user = await get_user(event)
    if not user:
        return
    user_afk = mongodb.afk.find_one({'user': user.user.id})
    if user_afk:
        await event.reply("{} is AFK!\nReason: {}".format(
            await user_link(user.user.id), user_afk['reason']))
