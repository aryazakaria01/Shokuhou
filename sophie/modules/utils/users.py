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

from rejson import Path

from sophie.components.caching import redis
from sophie.services.aiogram import bot


async def get_admins_rights(chat_id, force_update=False):
    key = 'admin_cache:' + str(chat_id)
    if (alist := redis.jsonget(key)) and not force_update:
        return alist
    else:
        alist = {}
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            user_id = admin.user.id
            alist[user_id] = {
                'status': admin.status,
                'admin': True,
                'can_change_info': admin.can_change_info,
                'can_delete_messages': admin.can_delete_messages,
                'can_invite_users': admin.can_invite_users,
                'can_restrict_members': admin.can_restrict_members,
                'can_pin_messages': admin.can_pin_messages,
                'can_promote_members': admin.can_promote_members
            }

        redis.jsonset(key, Path.rootPath(), alist)
        redis.expire(key, 900)
    return alist
