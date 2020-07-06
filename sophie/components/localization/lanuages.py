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

from typing import List
from babel.core import Locale
from flag import flag

from sophie.utils.config import config

from .loader import LANGUAGES


def get_languages_list() -> List[str]:
    languages = LANGUAGES
    return languages


def get_babel(locale_code: str) -> Locale:
    return Locale.parse(locale_code, sep='-')


def get_language_name(locale_code: str) -> str:
    babel = get_babel(locale_code)

    if config.localization.languages_names_in_english:
        return babel.english_name
    else:
        return babel.display_name


def get_language_emoji(locale_code: str) -> str:
    territory = Locale.parse(locale_code, sep='-').territory
    return flag(territory)
