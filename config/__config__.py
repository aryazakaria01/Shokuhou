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
from pydantic import BaseModel


class GeneralConfig(BaseModel):
    token: str
    owner_id: int
    operators: Optional[List[int]] = []


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


def __conf__() -> dict:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'config.toml')) as conf:
        payload = toml.load(conf)
    return payload


general_config = __conf__()
