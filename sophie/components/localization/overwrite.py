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
    print(LOADED_MODULES[module])
    if lang not in LOADED_MODULES[module]['translations']:
        lang = 'en_US'

    return LOADED_MODULES[module]['translations'][lang]


def get_string(module: str, key: str, lang: str) -> (str, dict, list):
    strings = get_strings(module, lang)
    if key not in strings:
        # Fallback to English in case if current language don't have this strings
        strings = get_strings(module, 'en_US')

    return strings[key]


def get_strings_by_chat_id(module: str, chat_id: int) -> dict:
    locale = get_chat_locale(chat_id)
    strings = get_strings(module, locale)

    return strings


def apply_strings_dec(arg):
    def wrapped(func):
        async def wrapped_1(message, *args, **kwargs):
            chat_id = message.chat.id

            class Strings:
                module = arg
                lang = get_chat_locale(chat_id)

                def get_string(self, key):
                    string = get_string(self.module, key, self.lang)
                    return string

                def __getitem__(self, key):
                    return self.get_string(key)

            message.d['strings'] = Strings()

            return await func(message, *args, **kwargs)

        return wrapped_1

    return wrapped


def __setup__():
    import sophie.modules.utils.strings as old

    old.get_strings = get_strings
    old.get_string = get_string
    old.get_strings_by_chat_id = get_strings_by_chat_id
    old.apply_strings_dec = apply_strings_dec
