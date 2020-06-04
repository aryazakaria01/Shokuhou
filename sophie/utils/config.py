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
#

import os

import toml

from sophie.utils.logging import log

DATA = {}
CONFIG_PATH = 'config/config.toml'

real_path = os.getcwd() + '/' + CONFIG_PATH

if os.name == 'nt':  # Windows name workaround
    real_path = real_path.replace('/', '\\')

if os.path.isfile(real_path):
    log.info(f'Using config file - {real_path}')
    with open(CONFIG_PATH) as f:
        DATA = toml.load(f)
else:
    log.warning("Using env vars")


def get_by_key(key, default=None, require=False):
    data = DATA
    keys = key.split('/')
    for x, sub_key in enumerate(keys):
        if sub_key not in data:
            break
        data = data[sub_key]
        if x == len(keys) - 1:
            return data

    if default:
        return default

    if require:
        log.critical(f'No config found by key "{key}"! Exiting!')
        exit(3)

    return None


def config(key, default=None, require=False):
    data = get_by_key(key, default=default, require=require)
    return data
