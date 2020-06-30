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


def get_mode():
    conf = config('cache/mode', default='memory').lower()

    if conf == 'memory':
        from aiocache import SimpleMemoryCache

        mode = SimpleMemoryCache
        kwargs = {}
    elif conf == 'redis':
        from aiocache import RedisCache

        mode = RedisCache
        kwargs = {
            'endpoint': config('cache/redis/url', default='localhost'),
            'port': config('cache/redis/port', default=6379)
        }
    elif conf == 'memcached':
        from aiocache import MemcachedCache

        mode = MemcachedCache
        kwargs = {
            'endpoint': config('cache/memcached/url', default='localhost'),
            'port': config('cache/memcached/port', default=11211)
        }
    else:
        raise NotImplementedError

    return mode, kwargs


def get_serializer():
    conf = config('cache/serializer', default='pickle').lower()
    if conf == 'pickle':
        from aiocache.serializers import PickleSerializer

        serializer = PickleSerializer
    elif conf == 'json':
        from aiocache.serializers import JsonSerializer

        serializer = JsonSerializer
    else:
        raise NotImplementedError

    return serializer


def __setup__():
    namespace = config('cache/namespace', default='sophie')

    mode, kwargs = get_mode()
    serializer = get_serializer()

    cache = Cache(
        cache_class=mode,
        namespace=namespace,
        serializer=serializer(),
        **kwargs
    )

    try:
        asyncio.ensure_future(cache.set('foo', 'bar'))
    except ConnectionRefusedError:
        log.critical("Can't connect to the cache database! Exiting...")
        exit(2)

    return cache
