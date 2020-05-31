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
import logging

from pyrogram import Client
from sophie.config import config
from sophie.utils.logging import log

TOKEN = config('general/token', require=True)
session_name = TOKEN.split(':')[0]
API_ID = config('general/api_id', require=True)
API_HASH = config('general/api_hash', require=True)

pyrogram = Client(
    session_name,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

log.debug('Starting 🔥 Pyrogram...')
# disable logging for pyrogram [not for ERROR logging]
logging.getLogger('pyrogram').setLevel(level=logging.ERROR)
asyncio.ensure_future(pyrogram.start())
