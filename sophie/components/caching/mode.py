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

from sophie.utils.config import config

conf = config('cache/mode', default='memory').lower()

if conf == 'memory':
    from aiocache import SimpleMemoryCache

    mode = SimpleMemoryCache
    mode_kwargs = {}
elif conf == 'redis':
    from aiocache import RedisCache

    mode = RedisCache
    mode_kwargs = {
        'endpoint': config('cache/redis/url', default='localhost'),
        'port': config('cache/redis/port', default=6379)
    }
elif conf == 'memcached':
    from aiocache import MemcachedCache

    mode = MemcachedCache
    mode_kwargs = {
        'endpoint': config('cache/memcached/url', default='localhost'),
        'port': config('cache/memcached/port', default=11211)
    }
else:
    raise NotImplementedError
