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
from typing import Union

from sophie.utils.logging import log
from .modules import load_pkg


def load_component(component_name: str) -> Union[dict, bool]:
    from . import LOADED_COMPONENTS

    base_path = 'sophie/components/'
    # check if component exists
    if not os.path.exists(base_path + component_name):
        return False

    log.debug(f'Loading component: {component_name}')
    component = load_pkg({
        'type': 'component',
        'name': component_name,
        'path': f'sophie/components/{component_name}',
        'absolute_path': f"sophie.components.{component_name}"
    })

    LOADED_COMPONENTS[component_name] = component
    return component
