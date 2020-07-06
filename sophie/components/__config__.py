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
# Includes config structure

import os
import toml

from typing import Optional, List
from pydantic.main import BaseModel


class CacheConfig(BaseModel):  # settings for component 'Caching'

    class Redis(BaseModel):  # redis config
        url: str = 'localhost'
        port: int = 6379

    class MemCached(BaseModel):  # memcache config
        url: str = 'localhost'
        port: int = 11211

    mode: str = 'memory'
    serializer: str = 'pickle'
    redis: Redis = Redis()
    memcached: MemCached = MemCached()
    plugins: Optional[List[str]] = None
    namespace: str = 'Sophie'


class LocalizationConfig(BaseModel):
    default_language: str = 'en-US'
    languages_names_in_english: bool = True


class PyrogramConfig(BaseModel):  # Settings for component 'Pyrogram'
    app_id: int = None
    app_hash: str = None


def __conf__() -> dict:
    payload: dict = {}
    base_path: str = 'sophie/components'
    for component in os.listdir(base_path):
        path = base_path + '/' + component
        if not os.path.isfile(path + '/config.toml'):
            continue

        with open(path + '/config.toml') as conf:
            payload.update(toml.load(conf))
    return payload


component_config = __conf__()
