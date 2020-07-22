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
from typing import Any, TypeVar, Callable, Union, Optional, cast

from sophie.utils.logging import log
from . import cache

T = TypeVar("T", bound=Callable[..., Any])


def cached(ttl: Union[int, float] = None, key: Optional[str] = None, noself: bool = False) -> Callable[[T], T]:
    def wrapped(func: T) -> T:
        async def wrapped0(*args: Any, **kwargs: Any) -> Any:
            ordered_kwargs = sorted(kwargs.items())

            new_key = key if key else (func.__module__ or "") + func.__name__
            new_key += str(args[1:] if noself else args)

            if ordered_kwargs:
                new_key += str(ordered_kwargs)

            value = await cache.get(new_key)
            if value is not None:
                return value

            result = await func(*args, **kwargs)
            asyncio.ensure_future(cache.set(new_key, result, ttl=ttl))
            log.debug(f'Cached: writing new data for key - {new_key}')
            return result

        return cast(T, wrapped0)
    return cast(Callable[[T], T], wrapped)
