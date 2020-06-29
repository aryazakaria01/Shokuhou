# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
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

import asyncio

from aiocache import Cache

from sophie.utils.config import config
from sophie.utils.logging import log
from .mode import mode_kwargs, mode
from .plugins import plugins
from .serializer import serializer

namespace = config.cache.namespace

cache = Cache(
    cache_class=mode,
    namespace=namespace,
    serializer=serializer(),
    plugins=plugins,
    **mode_kwargs
)

try:
    asyncio.ensure_future(cache.set('foo', 'bar'))
except ConnectionRefusedError:
    log.critical("Can't connect to the cache database! Exiting...")
    exit(2)
