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

from aiogram.dispatcher.handler import MessageHandler
from magic_filter import F

from .. import router

from sophie.modules.utils.strings import apply_strings_dec
from sophie.components.localization.locale import get_chat_locale


@router.message(commands=['lang'])
@apply_strings_dec('locale')
class GetLanguageMenu(MessageHandler):

    def get_locale(self, chat_id):
        return get_chat_locale(chat_id)

    async def handle(self):
        print(self.get_locale(self.chat.id))
