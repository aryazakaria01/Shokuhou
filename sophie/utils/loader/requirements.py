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

import pkg_resources

from typing import TextIO
from sophie.utils.logging import log


def check_pip_requirement(requirement: str) -> bool:
    try:
        pkg_resources.require(requirement)

    except pkg_resources.DistributionNotFound as error:

        if (application := error.requirers_str) == "the application":  # type: ignore
            application = "Sophie"  # Ofc sophie
        log.warning(f'No satisfied requirement "{error.req}" required by {application}')  # type: ignore
        return False

    except pkg_resources.ContextualVersionConflict as error:
        log.critical(f'{error.dist} is installed but require {error.req}, This req is need by {error.required_by}')
        return False

    except pkg_resources.VersionConflict as error:
        log.critical(f"{error.dist} is installed but require {error.req}")
        return False

    return True


def check_requirements(f: TextIO) -> bool:
    from .components import load_component
    from . import LOADED_COMPONENTS

    optional = False

    for requirement in f.readlines():
        requirement = requirement.replace('\n', '')

        if not requirement:
            continue
        if requirement.startswith('#'):
            continue
        if requirement.startswith('?'):
            requirement = requirement[1:]
            optional = True

        if '[' in requirement:
            # TODO: ability to install optional sub-requirements
            requirement = requirement.split('[', 1)[0]

        if requirement.startswith('$'):
            # Component requirement
            component = requirement.replace('$', '')
            if component not in LOADED_COMPONENTS:
                # Try to load a component
                if load_component(component):
                    continue
                # Looks like we don't have such component
                else:
                    if optional:
                        log.warning(f'Optional component {component}, skipping')
                        continue
                    else:
                        log.critical(f'No such component: {component}')
                        exit(5)
            continue

        # check pip requirement
        if not check_pip_requirement(requirement):
            if optional:
                log.warning('Optional requirement, skipping')
                continue
            else:
                log.critical('Requirement error! Read the warning above!')
                exit(5)

    return True
