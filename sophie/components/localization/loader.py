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

import os

import yaml

from sophie.utils.logging import log

LANGUAGES = []


def load_all_languages():
    from sophie.modules import LOADED_MODULES

    for module in LOADED_MODULES.values():
        log.debug(f"Loading localizations from {module['name']} module")

        path = f"{module['path']}/translations"
        if not os.path.exists(path):
            log.debug(f"No translations directory found for module {module['name']}")
            continue

        for file_name in os.listdir(path):
            lang_name = file_name.split('.')[0]
            with open(f"{path}/{file_name}") as f:
                lang = yaml.load(f, Loader=yaml.SafeLoader)

                if 'translations' not in LOADED_MODULES[module['name']]:
                    LOADED_MODULES[module['name']]['translations'] = {}

                if lang_name not in LANGUAGES:
                    LANGUAGES.append(lang_name)

                LOADED_MODULES[module['name']]['translations'][lang_name] = lang
