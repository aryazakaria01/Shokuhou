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

import logging as log
from pydantic import BaseSettings, ValidationError

# configs
from sophie.components.__config__ import (CacheConfig, PyrogramConfig,  # type: ignore
                                          LocalizationConfig, component_config)  # type: ignore
from .general import GeneralConfig, AdvancedConfig, ModuleConfig, MongoConfig, general_config  # type: ignore


class Conf(BaseSettings):

    # Some fields are required, some can follow default value
    general: GeneralConfig = GeneralConfig()
    advanced: AdvancedConfig = AdvancedConfig()
    modules: ModuleConfig = ModuleConfig()
    mongo: MongoConfig = MongoConfig()
    cache: CacheConfig = CacheConfig()
    pyrogram: PyrogramConfig = PyrogramConfig()
    localization: LocalizationConfig = LocalizationConfig()


payload = {**general_config, **component_config}
try:
    config: Conf = Conf(**payload)
except ValidationError as error:
    log.error(f'Something went wrong when loading config \n {str(error)}')
    exit(5)

__all__ = ["config"]
