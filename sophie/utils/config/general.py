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
#
# Contains general/Core config model

# type: ignore

import os
import toml

from pydantic import BaseModel
from typing import List, MutableMapping

from .field import Field


class GeneralConfig(BaseModel):
    token: str = Field(None, env="TOKEN")
    owner_id: int = Field(None, env="OWNER_ID")
    operators: List[int] = Field([], env="OPERATORS")


class AdvancedConfig(BaseModel):  # Advanced settings
    debug: bool = Field(False, env="DEBUG")
    uvloop: bool = Field(False, env="UVLOOP")
    migrator: bool = Field(True, env="MIGRATOR")
    log_file: bool = Field(True, env="LOG_FILE")


class ModuleConfig(BaseModel):
    load: List[str] = Field(['owner'], env="TO_LOAD")
    dont_load: List[str] = Field([], env="DONT_LOAD")


class MongoConfig(BaseModel):  # settings for database
    url: str = Field('localhost', env="MONGO_URL")
    namespace: str = Field('sophie', env="MONGO_NAMESPACE")


def __conf__() -> MutableMapping[str, dict]:  # method to load general config.toml
    path = 'config/config.toml'

    if os.name == 'nt':
        path.replace('/', '\\')

    with open(path) as file:
        payload = toml.load(file)
    return payload


general_config = __conf__()
