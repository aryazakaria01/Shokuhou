# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
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

from pymongo import ASCENDING

from sophie.services.mongo import sync_mongo
from sophie.utils.logging import log


col_name = 'migrator'
col_validation = {
    "$jsonSchema":
        {
            "bsonType": "object",
            "required": ["name", "type", "version"],
            "properties": {
                "name": {
                    "bsonType": "string"
                },
                "type": {
                    "bsonType": "string",
                    "pattern": "^(base|module|component)$"
                },
                "version": {
                    "bsonType": "int"
                }
            }
        }
}


def get_current_version(loaded_name: str, loaded_type: str) -> (None, str):
    data = sync_mongo[col_name].find_one({'name': loaded_name, 'type': loaded_type})

    if not data:
        return None

    return data['version']


def set_version(loaded_name: str, loaded_type: str, version: int) -> int:
    sync_mongo[col_name].update_one(
        {'name': loaded_name, 'type': loaded_type},
        {'$set': {'version': version}},
        upsert=True
    )
    return version


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
