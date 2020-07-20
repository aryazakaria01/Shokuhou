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

import os
import logging as log
from typing import List, MutableMapping

import toml
from pydantic import BaseSettings, ValidationError, Field, BaseModel

# Inlcude config structures
from sophie.components.__config__ import CacheConfig, PyrogramConfig, LocalizationConfig, component_config


class GeneralConfig(BaseModel):
    token: str
    owner_id: int
    operators: List[int] = []


class AdvancedConfig(BaseModel):  # Advanced settings
    debug: bool = False
    uvloop: bool = False
    migrator: bool = True
    log_file: bool = True


class ModuleConfig(BaseModel):
    load: List[str] = ['owner']
    dont_load: List[str] = []


class MongoConfig(BaseModel):  # settings for database
    url: str = 'localhost'
    namespace: str = 'sophie'


def general_config() -> MutableMapping[str, dict]:  # method to load general config.toml
    __config__ = 'config/config.toml'

    if os.name == 'nt':
        __config__.replace('/', '\\')

    with open(__config__) as file:
        conf = toml.load(file)
    return conf


class Conf(BaseSettings):

    # Some fields are required, some can follow default value
    general: GeneralConfig = Field(..., env='GENERAL_SETTINGS')
    advanced: AdvancedConfig = Field(AdvancedConfig().dict(), env='ADVANCED_SETTINGS')
    modules: ModuleConfig = Field(ModuleConfig().dict(), env='MODULES_SETUP')
    mongo: MongoConfig = Field(MongoConfig().dict(), env='MONGO_SETUP')
    cache: CacheConfig = Field(CacheConfig().dict(), env='CACHE_SETUP')
    pyrogram: PyrogramConfig = Field(PyrogramConfig().dict(), env='PYROGRAM_SETUP')
    localization: LocalizationConfig = Field(LocalizationConfig().dict(), env='LOCALIZATION')


# loading configuration
payload = {**general_config(), **component_config}
try:
    config: Conf = Conf(**payload)
except ValidationError as error:
    log.error(f'Something went wrong when loading config \n {str(error)}')
    exit(5)
