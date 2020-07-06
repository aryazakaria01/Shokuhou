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

from motor.motor_asyncio import AsyncIOMotorClient

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

from sophie.utils.config import config
from sophie.utils.logging import log

MONGO_URI = config.mongo.url
MONGO_DB = config.mongo.namespace

# Init MongoDB
mongo_client = MongoClient(MONGO_URI)
sync_mongo: Database = mongo_client[MONGO_DB]

# Async mongo
motor = AsyncIOMotorClient(MONGO_URI)
mongo: Database = motor[MONGO_DB]

try:
    mongo_client.server_info()
except ServerSelectionTimeoutError:
    log.critical("Can't connect to the MongoDB! Exiting...")
    exit(2)
