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

# type: ignore

import os
import toml

from typing import Optional, List

from sophie.utils.config import Field
from pydantic.main import BaseModel


class CacheConfig(BaseModel):  # settings for component 'Caching'

    class Redis(BaseModel):  # redis config
        url: str = Field('localhost', env='REDIS_URL')
        port: int = Field(6379, env="REDIS_PORT")

    class MemCached(BaseModel):  # memcache config
        url: str = Field('localhost', env="MEMCACHE_URL")
        port: int = Field(11211, env="MEMCACHE_PORT")

    mode: str = Field("memory", env="CACHE_MODE")
    serializer: str = Field('pickle', env="CACHE_SERIALIZER")
    redis: Redis = Redis()
    memcached: MemCached = MemCached()
    plugins: Optional[List[str]] = Field(None, env="CACHE_PLUGINS")
    namespace: str = Field('Sophie', env="CACHE_NAMESPACE")


class LocalizationConfig(BaseModel):
    default_language: str = Field('en-US', env="DEFAULT_LANG")
    languages_names_in_english: bool = Field(True, env="LANG_NAMES_IN_ENG")


class PyrogramConfig(BaseModel):  # Settings for component 'Pyrogram'
    app_id: Optional[int] = Field(None, env="APP_ID")
    app_hash: Optional[str] = Field(None, env="APP_HASH")


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
