# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo.
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
#

import glob
import toml

from os import PathLike
from typing import List, Optional

from sophie.utils.logging import log
from pydantic import BaseSettings, BaseModel, ValidationError, Field


# this class contains structures for initiating Config
class Structure:
    class General(BaseModel):
        token: str
        owner_id: int
        operators: Optional[List[int]] = []

    class Advanced(BaseModel):  # Advanced settings
        debug: bool = False
        uvloop: bool = False

    class Pyrogram(BaseModel):  # Settings for component 'Pyrogram'
        app_id: int = None
        app_hash: str = None

    class Mongo(BaseModel):  # settings for database
        url: str = 'localhost'
        namespace: str = 'sophie'

    class Cache(BaseModel):  # settings for component 'Caching'

        class Redis(BaseModel):  # redis config
            url: str = 'localhost'
            port: int = 6379

        class MemCached(BaseModel):  # memcache config
            url: str = 'localhost'
            port: int = 11211

        mode: str = 'memory'
        redis: Redis = Redis()
        memcached: MemCached = MemCached()
        plugins: Optional[List[str]] = None
        namespace: str = 'Sophie'
        serializer: str = 'pickle'

    class Localization(BaseModel):
        default_language: str = 'en-US'

    class Modules(BaseModel):
        load: List[str] = ['owner']
        dont_load: List[str] = []


class Conf(BaseSettings):

    # Some fields are required, some can follow default value
    general: Structure.General = Field(..., env='GENERAL_SETTINGS')
    advanced: Structure.Advanced = Field(Structure.Advanced().dict(), env='ADVANCED_SETTINGS')
    mongo: Structure.Mongo = Field(Structure.Mongo().dict(), env='MONGO_SETUP')
    cache: Structure.Cache = Field(Structure.Cache().dict(), env='CACHE_SETUP')
    pyrogram: Structure.Pyrogram = Field(Structure.Pyrogram().dict(), env='PYROGRAM_SETUP')
    localization: Structure.Localization = Field(Structure.Localization().dict(), env='LOCALIZATION')
    modules: Structure.Modules = Field(Structure.Modules().dict(), env='MODULES_SETUP')


# loading configuration

payload: dict = {}
confs: List[PathLike] = glob.glob('**/config.toml', recursive=True)
for conf in confs:
    with open(conf) as toml_conf:
        data = toml.load(toml_conf)
        payload.update(data)

try:
    config: Conf = Conf(**payload)
except ValidationError as error:
    log.error(f'Something went wrong when loading config \n {str(error)}')
    exit(5)
