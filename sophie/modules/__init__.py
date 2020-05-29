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

LOADED_MODULES = {}
NOT_LOADED_MODULES = []


def list_all_modules():
    modules_directory = 'sophie/modules'

    all_modules = []
    for dir in os.listdir(modules_directory):
        path = modules_directory + '/' + dir
        if not os.path.isdir(path):
            continue

        if dir == '__pycache__':
            continue

        if not os.path.isfile(path + '/version.txt'):
            continue

        if dir in all_modules:
            log.critical("Modules with same name can't exists!")
            exit(5)

        all_modules.append(dir)
    return all_modules


ALL_MODULES = sorted(list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]
