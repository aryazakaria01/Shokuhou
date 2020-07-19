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

from typing import Any, Union


class FormatListText:
    __slots__ = ['data', 'sub_titles_bold', 'title_text', 'titles_bold', 'tuple_delimiter']

    space = ' '

    def __init__(self,
                 data: Union[list, tuple, dict],
                 sub_titles_bold=True,
                 title=None,
                 titles_bold=True,
                 tuple_delimiter='->'
                 ) -> None:
        self.data = data
        self.sub_titles_bold = sub_titles_bold
        self.title_text = title
        self.titles_bold = titles_bold
        self.tuple_delimiter = tuple_delimiter

    def get_title(self, title) -> str:
        if self.titles_bold:
            return f'<b>{title}:</b> '
        else:
            return f'{title} '

    def get_sub_title(self, sub_title) -> str:
        if self.sub_titles_bold:
            return f'<b>{sub_title}:</b> '
        else:
            return f'{sub_title} '

    def build_list_text(self, data: list, text='', space='') -> str:
        for value in data:
            text += '\n'
            text += space
            text += '- '

            text = self.loop(value, text, space)
        return text

    def build_dict_text(self, data: dict, text='', space='') -> str:
        for key, value in data.items():
            text += '\n'
            text += space
            text += self.get_sub_title(key)

            text = self.loop(value, text, space)
        return text

    def build_tuple_text(self, data: tuple, text='', space='') -> str:
        for tuple_item in data:
            text += '\n'
            text += space
            text += f"- {tuple_item[0]} {self.tuple_delimiter}"

            for num, values in enumerate(tuple_item[1].items()):
                title, value = values
                if num != 0:
                    text += ','
                text += f' {str(title)}: {str(value)}'

        return text

    def loop(self, value, text="", space=space) -> str:
        if isinstance(value, dict):
            text = self.build_dict_text(value, text, space + space)
        elif isinstance(value, list):
            text = self.build_list_text(value, text, space + space)
        elif isinstance(value, tuple):
            text = self.build_tuple_text(value, text, space + space)
        else:
            value = value.replace('\n', '\n' + space + space)
            text += str(value)

        return text

    @property
    def title(self) -> str:
        """Returns formatted title"""
        return self.get_title(self.title_text)

    @property
    def text(self) -> str:
        """Returns formatted text"""
        text = ''
        if self.title_text:
            text += self.title

        text += self.loop(self.data)
        return text

    def __getitem__(self, key) -> Any:
        """Returns data from dict"""
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        """Sets a value to data"""
        self.data[key] = value

    def __delitem__(self, key) -> None:
        """Deletes item"""
        del self.data[key]
