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

from pymongo import ASCENDING
from typing import Optional

from sophie.services.mongo import mongo, sync_mongo
from sophie.utils.logging import log

col_name = 'locale'
col_validation = {
    "$jsonSchema":
        {
            "bsonType": "object",
            "required": ["chat_id", "locale_code"],
            "properties": {
                "chat_id": {
                    "bsonType": "long"
                },
                "locale_code": {
                    "bsonType": "string",
                    "pattern": "^[a-z]{2}-[A-Z]{2}$"
                }
            }
        }
}


async def set_lang(chat_id: int, locale_code: str) -> dict:
    data = {
        'chat_id': chat_id,
        'locale_code': locale_code
    }

    await mongo[col_name].replace_one({'chat_id': chat_id}, data, upsert=True)

    return data


async def get_lang(chat_id: int) -> Optional[str]:
    data = await mongo[col_name].find_one({'chat_id': chat_id})
    if not data:
        return None

    return data['locale_code']


def __setup__():
    if col_name not in sync_mongo.list_collection_names():
        log.info(f'Created not exited column "{col_name}"')
        sync_mongo.create_collection(col_name)

    log.debug(f'Running validation cmd for "{col_name}" column')
    sync_mongo.command({
        'collMod': col_name,
        'validator': col_validation,
        'validationLevel': 'strict'
    })
    log.debug(f'Creating indexes for "{col_name}" column')
    sync_mongo[col_name].create_index(
        [('chat_id', ASCENDING)],
        name='chat_id',
        unique=True,
    )
