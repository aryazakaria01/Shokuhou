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


from .locale import get_chat_locale


def get_strings(module: str, lang: str) -> dict:
    from sophie.modules import LOADED_MODULES
    if lang not in LOADED_MODULES[module]['translations']:
        lang = 'en-US'

    return LOADED_MODULES[module]['translations'][lang]


def get_string(module: str, key: str, lang: str) -> (str, dict, list):
    strings = get_strings(module, lang)
    if key not in strings:
        # Fallback to English in case if current language don't have this strings
        strings = get_strings(module, 'en-US')

    return strings[key]


async def get_strings_by_chat_id(module: str, chat_id: int) -> dict:
    locale = await get_chat_locale(chat_id)
    strings = get_strings(module, locale)

    return strings


