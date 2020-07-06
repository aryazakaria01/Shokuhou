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

from pydantic import BaseSettings, BaseModel, ValidationError, Field
from sophie.utils.logging import log

# Inlcude config structures
from config.__config__ import GeneralConfig, AdvancedConfig, ModuleConfig, MongoConfig, general_config
from sophie.components.__config__ import CacheConfig, PyrogramConfig, LocalizationConfig, component_config


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
payload = {**general_config, **component_config}
try:
    config: Conf = Conf(**payload)
except ValidationError as error:
    log.error(f'Something went wrong when loading config \n {str(error)}')
    exit(5)
