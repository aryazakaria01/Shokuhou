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

import asyncio
from importlib import import_module
from logging import DEBUG

from sophie.utils.config import config

from sophie.modules.utils.filters import __setup__ as filters_setup
from sophie.modules.utils.middlewares import __setup__ as middlewares_setup
from sophie.services.aiogram import dp, bot
from sophie.utils.loader import load_all_modules, post_init
from sophie.utils.logging import log

if config.advanced.debug:
    log.setLevel(DEBUG)
    log.warning("! Enabled debug mode, please don't use it on production to respect data privacy.")

if config.advanced.uvloop:
    log.info("Enabling uvloop...")
    import_module('sophie.utils.uvloop')

loop = asyncio.get_event_loop()

log.debug('Loading top-level custom filters...')
filters_setup()
log.debug('...Done!')

log.debug('Loading modules...')
load_all_modules()
log.info('Modules loaded successfully!')

log.debug('Loading middlewares...')
middlewares_setup()
log.debug('...Done!')

log.debug('Running postinit stage...')
post_init()
log.debug('...Done!')

log.info('Running the bot...')
loop.run_until_complete(dp.start_polling(bot))
