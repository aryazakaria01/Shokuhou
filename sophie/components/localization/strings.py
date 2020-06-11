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

from functools import wraps

from babel.core import Locale

from .locale import get_chat_locale
from .lanuages import get_babel, get_language_emoji


class GetStrings:
    def __init__(self, module: str):
        from sophie.modules import LOADED_MODULES

        self.modules = LOADED_MODULES
        self.module = module

    def get_by_locale_name(self, locale_code: str):
        if locale_code not in self.modules[self.module]['translations']:
            locale_code = 'en-US'

        return self.modules[self.module]['translations'][locale_code]

    async def get_by_chat_id(self, chat_id: int):
        locale_name = await get_chat_locale(chat_id)
        return self.get_by_locale_name(locale_name)


class GetString:
    def __init__(self, module: str, key: str):
        self.module = module
        self.key = key

    def get_by_locale_name(self, locale_code: str):
        strings = GetStrings(self.module)[locale_code]
        return strings

    async def get_by_chat_id(self, chat_id: int):
        locale_code = await get_chat_locale(chat_id)
        return self.get_by_locale_name(locale_code)


class Strings:
    """
    Replacement of strings dict
    """

    def __init__(self, locale_code: str, module: str):
        self.locale_code = locale_code
        self.strings = GetStrings(module).get_by_locale_name(locale_code)

    def _get_string(self, key) -> str:
        return self.strings[key]

    def get(self, key, **kwargs) -> str:
        string = self._get_string(key)
        string = string.format(**kwargs)
        return string

    @property
    def babel(self) -> Locale:
        return get_babel(self.locale_code)

    @property
    def emoji(self) -> str:
        return get_language_emoji(self.locale_code)

    def __getitem__(self, key) -> (str, dict, str):
        return self._get_string(key)


def get_strings_dec(func):
    async def decorated(event, *args, **kwargs):
        module_name = func.__module__.split('.')[2]

        chat_id = event.chat.id
        strings = Strings(await get_chat_locale(chat_id), module_name)

        return await func(event, *args, strings=strings, **kwargs)

    return decorated
