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
import os
import pkg_resources
from importlib import import_module

from sophie.utils.config import config
from sophie.utils.logging import log


def check_pip_requirement(requirement: str) -> None:

    try:
        pkg_resources.require(requirement)

    except pkg_resources.DistributionNotFound as error:
        if (application := error.requirers_str) == 'the application':
            application = 'Sophie'  # Ofc sophie
        log.critical(f'No statisfied requirement "{error.req}" required by {application}')
        exit(5)

    except pkg_resources.ContextualVersionConflict as error:
        _error_msg = f'{error.dist} is installed but require {error.req}, This req is need by {error.required_by}'
        log.critical(_error_msg)
        exit(5)

    except pkg_resources.VersionConflict as error:
        _error_msg = f'{error.dist} is installed but require {error.req}'
        log.critical(_error_msg)
        exit(5)


def check_requirements(f) -> bool:
    from sophie.components import LOADED_COMPONENTS

    for requirement in f.readlines():
        requirement = requirement.replace('\n', '')

        if not requirement:
            continue
        if requirement.startswith('#'):
            continue
        if requirement.startswith('?'):
            # TODO: Support optional requirements
            continue

        if '[' in requirement:
            requirement = requirement.split('[', 1)[0]

        if requirement.startswith('$'):
            # Component requirement
            component = requirement.replace('$', '')
            if component not in LOADED_COMPONENTS:
                # Try to load a component
                if load_component(component):
                    continue
                else:  # Looks like we don't have such component
                    log.critical(f'No such component: {component}')
                    exit(5)

        # check pip requirement
        check_pip_requirement(requirement)

    return True


def load_component(component_name: str) -> bool:
    from sophie.components import LOADED_COMPONENTS

    base_path = 'sophie/components/'
    # check if component exists
    if not os.path.exists(base_path + component_name):
        return False

    log.debug(f'Loading component: {component_name}')
    component = {
        'name': component_name,
        'path': (base_path + component_name).replace('\n', '')
    }

    # Stage 1 - check requirements and load components
    with open(f"{component['path']}/requirements.txt") as f:
        check_requirements(f)

    verion_path = f"{component['path']}/version.txt"
    version = None
    if os.path.exists(verion_path):
        with open(verion_path) as f:
            version = f.read()

    imported_component = import_module(f"sophie.components.{component_name}")

    LOADED_COMPONENTS[component_name] = {
        'name': component['name'],
        'object': imported_component,
        'path': component['path'],
        'version': version
    }

    return True


def load_module(module) -> None:
    from sophie.modules import LOADED_MODULES
    from sophie.services.aiogram import dp

    # Stage 1 - check requirements and load components
    requirements_file_path = f"{module['path']}/requirements.txt"
    if os.path.exists(requirements_file_path):
        with open(requirements_file_path) as f:
            log.debug(f"Checking requirements for {module['name']} module...")
            check_requirements(f)
            log.debug("...Passed!")

    log.debug(f"Importing <d><n>{module['name']}</></>")
    imported_module = import_module(f"sophie.modules.{module['name']}")

    path = str(imported_module.__path__[0])
    with open(f'{path}/version.txt') as f:
        version = f.read()

    new = {
        'name': module['name'],
        'object': imported_module,
        'path': path,
        'version': version
    }

    if hasattr(imported_module, 'router'):
        log.debug(f"Enabling router for {module['name']}")
        new['router'] = imported_module.router
        dp.include_router(new['router'])

    LOADED_MODULES[module['name']] = new


def load_modules(to_load: list) -> 'module':
    base_path = 'sophie/modules/'

    for module_name in to_load:
        module = {
            'name': module_name,
            'path': base_path + module_name
        }

        load_module(module)

    return module


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


async def before_srv_task(modules):
    log.debug("Running __setup__...")
    for module in [m for m in modules if hasattr(m['object'], '__setup__')]:
        log.debug(f"Running __setup__ for: {module['name']}")
        await module['object'].__setup__()

    log.debug("Running __before_serving__...")
    for module in [m for m in modules if hasattr(m['object'], '__before_serving__')]:
        log.debug(f"Running __before_serving__ for: {module['name']}")
        await module['object'].__before_serving__()


def post_init():
    from sophie.modules import LOADED_MODULES
    from sophie.components import LOADED_COMPONENTS

    # Run before_srv_task for components
    loop = asyncio.get_event_loop()
    loop.run_until_complete(before_srv_task(LOADED_COMPONENTS.values()))

    # Run before_srv_task for modules
    loop = asyncio.get_event_loop()
    loop.run_until_complete(before_srv_task(LOADED_MODULES.values()))
