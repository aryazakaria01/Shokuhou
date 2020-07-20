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

from aiogram import Router
from typing import Any

from sophie.modules.owner.handlers.owners_functions import OwnersFunctions  # type: ignore


router = Router()


async def __setup__() -> Any:
    from .filters import __setup__ as filters
    from .handlers import __setup__ as handlers
    from .loader import __setup__ as loader

    filters(router)
    handlers()
    await loader()


__all__ = [
    "OwnersFunctions",
    "router"
]
