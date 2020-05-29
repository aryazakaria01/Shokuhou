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

from sophie.utils.logging import log

LOADED_COMPONENTS = {}


def list_all_components():
    components_directory = 'sophie/components'

    all_components = []
    for dir in os.listdir(components_directory):
        path = components_directory + '/' + dir
        if not os.path.isdir(path):
            continue

        if dir == '__pycache__':
            continue

        if not os.path.isfile(path + '/version.txt'):
            continue

        if dir in all_components:
            log.critical("Components with same name can't exists!")
            exit(5)

        all_components.append(dir)
    return all_components


ALL_COMPONENTS = sorted(list_all_components())
__all__ = ALL_COMPONENTS + ["ALL_COMPONENTS"]
