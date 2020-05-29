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

# This file should be overwriten by custom localization component/module
# This contains only dumb returns


def get_strings(module: str, lang: str) -> dict:
    return [module]


def get_string(module: str, key: str, lang: str) -> str:
    return key


def get_strings_by_chat_id(module: str, chat_id: int) -> dict:
    return [module]


def apply_strings_dec(arg):
    def wrapped(func):
        async def wrapped_1(message, *args, **kwargs):
            class Strings:
                def __getitem__(self, key):
                    return key

            message.__config__.allow_mutation = True  # TODO: Remove this
            setattr(message, 'strings', Strings())

            return await func(message, *args, **kwargs)

        return wrapped_1

    return wrapped
