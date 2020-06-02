# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2020 Jeepeo
#
# This file is part of SophieBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
import sys

from motor import motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'sophie'

# Init MongoD
motor = motor_asyncio.AsyncIOMotorClient(MONGO_URI, MONGO_PORT)
db = motor[MONGO_DB]

try:
    asyncio.ensure_future(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(logging.critical("Can't connect to mongodb! Exiting..."))
