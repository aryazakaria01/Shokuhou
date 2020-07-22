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

import os

from importlib import import_module
from typing import List

from sophie.utils.logging import log
from sophie.utils.config import config

from .requirements import check_requirements


def load_pkg(pkg: dict) -> dict:
    from sophie.services.aiogram import dp

    # Stage 1 - check requirements and load components
    requirements_file_path = f"{pkg['path']}/requirements.txt"
    if os.path.exists(requirements_file_path):
        with open(requirements_file_path) as f:
            log.debug(f"Checking requirements for {pkg['name']} {pkg['type']}...")
            check_requirements(f)
            log.debug("...Passed!")

    log.debug(f"Importing <d><n>{pkg['name']}</></> {pkg['type']}")
    imported_module = import_module(pkg['package_path'])

    path = str(imported_module.__path__[0])  # type: ignore  # mypy issue #1422
    with open(f"{path}/version.txt") as f:
        version = f.read()

    pkg['object'] = imported_module
    pkg['version'] = version

    if hasattr(imported_module, "router"):
        log.debug(f"Enabling router for {pkg['name']} {pkg['type']}")
        dp.include_router(imported_module.router)  # type: ignore
        pkg['router'] = imported_module.router  # type: ignore

    return pkg


def load_module(module_name: str) -> dict:
    from . import LOADED_MODULES

    module = load_pkg(
        {
            "type": "module",
            "name": module_name,
            "path": f"sophie/modules/{module_name}",
            "package_path": f"sophie.modules.{module_name}",
        }
    )

    LOADED_MODULES[module_name] = module
    return module


def load_modules(to_load: List[str]) -> list:
    modules = []
    for module_name in to_load:
        modules.append(load_module(module_name))

    return modules


def load_all_modules() -> list:
    from sophie.modules import ALL_MODULES

    load = config.modules.load
    dont_load = config.modules.dont_load

    if len(load) > 0:
        to_load = load
    else:
        to_load = ALL_MODULES

    to_load = [x for x in to_load if x not in dont_load]
    log.info("Modules to load: %s", str(to_load))
    load_modules(to_load)

    return to_load
