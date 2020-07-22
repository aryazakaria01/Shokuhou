# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo.
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
from typing import Any, ValuesView

from sophie.utils.logging import log


async def before_srv_task(modules: ValuesView[dict]) -> Any:
    log.debug("Running __setup__...")
    for module in [m for m in modules if hasattr(m['object'], '__setup__')]:
        log.debug(f"Running __setup__ for: {module['name']}")
        await module['object'].__setup__()

    log.debug("Running __before_serving__...")
    for module in [m for m in modules if hasattr(m['object'], '__before_serving__')]:
        log.debug(f"Running __before_serving__ for: {module['name']}")
        await module['object'].__before_serving__()


def post_init() -> Any:
    from . import LOADED_MODULES
    from . import LOADED_COMPONENTS

    # Run before_srv_task for components
    loop = asyncio.get_event_loop()
    loop.run_until_complete(before_srv_task(LOADED_COMPONENTS.values()))

    # Run before_srv_task for modules
    loop = asyncio.get_event_loop()
    loop.run_until_complete(before_srv_task(LOADED_MODULES.values()))
