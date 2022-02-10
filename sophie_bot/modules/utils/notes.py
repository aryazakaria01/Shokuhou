# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2019 Aiogram
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

import html
import re
import sys
from datetime import datetime

from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import markdown
from babel.dates import format_date, format_time, format_datetime
from telethon.errors import ButtonUrlInvalidError, MessageEmptyError,MediaEmptyError
from telethon.tl.custom import Button

import sophie_bot.modules.utils.tmarkdown as tmarkdown
from sophie_bot import BOT_USERNAME
from sophie_bot.services.telethon import tbot
from .language import get_chat_lang
from .message import get_args
from .tmarkdown import tbold, titalic, tpre, tcode, tlink, tstrikethrough, tunderline
from .user_details import get_user_link

BUTTONS = {}

ALLOWED_COLUMNS = [
    'parse_mode',
    'file',
    'text',
    'preview'
]


def tparse_ent(ent, text, as_html=True):
    if not text:
        return text

    etype = ent.type
    offset = ent.offset
    length = ent.length

    if sys.maxunicode == 0xffff:
        return text[offset:offset + length]

    entity_text = text.encode('utf-16-le') if not isinstance(text, bytes) else text
    entity_text = entity_text[offset * 2:(offset + length) * 2].decode('utf-16-le')

    if etype == 'bold':
        method = markdown.hbold if as_html else tbold
        return method(entity_text)
    if etype == 'italic':
        method = markdown.hitalic if as_html else titalic
        return method(entity_text)
    if etype == 'pre':
        method = markdown.hpre if as_html else tpre
        return method(entity_text)
    if etype == 'code':
        method = markdown.hcode if as_html else tcode
        return method(entity_text)
    if etype == 'strikethrough':
        method = markdown.hstrikethrough if as_html else tstrikethrough
        return method(entity_text)
    if etype == 'underline':
        method = markdown.hunderline if as_html else tunderline
        return method(entity_text)
    if etype == 'url':
        return entity_text
    if etype == 'text_link':
        method = markdown.hlink if as_html else tlink
        return method(entity_text, ent.url)
    if etype == 'text_mention' and ent.user:
        return ent.user.get_mention(entity_text, as_html=as_html)

    return entity_text


def get_parsed_msg(message):
    if not message.text and not message.caption:
        return '', 'md'

    text = message.caption or message.text

    mode = get_msg_parse(text)
    as_html = mode == 'html'
    entities = message.caption_entities or message.entities

    if not entities:
        return text, mode

    if sys.maxunicode != 0xFFFF:
        text = text.encode('utf-16-le')

    result = ''
    offset = 0

    for entity in sorted(entities, key=lambda item: item.offset):
        entity_text = tparse_ent(entity, text, as_html=as_html)

        if sys.maxunicode == 0xffff:
            part = text[offset:entity.offset]
        else:
            part = text[offset * 2:entity.offset * 2].decode('utf-16-le')
        result += part + entity_text
        offset = entity.offset + entity.length

    if sys.maxunicode == 0xffff:
        result += text[offset:]
    else:
        result += text[offset * 2:].decode('utf-16-le')

    result = re.sub(r'\[format:(\w+)\]', '', result)
    result = re.sub(r'%PARSEMODE_(\w+)', '', result)

    if not result:
        result = ''

    return result, mode


def get_msg_parse(text, default_md=True):
    if '[format:html]' in text or '%PARSEMODE_HTML' in text:
        return 'html'
    elif '[format:none]' in text or '%PARSEMODE_NONE' in text:
        return 'none'
    elif '[format:md]' in text or '%PARSEMODE_MD' in text:
        return 'md'
    else:
        if not default_md:
            return None
        return 'md'


def parse_button(data, name):
    raw_button = data.split('_')
    raw_btn_type = raw_button[0]

    pattern = re.match(r'btn(.+)(sm|cb|start)', raw_btn_type)
    if not pattern:
        return ''

    action = pattern.group(1)
    args = raw_button[1]

    if action in BUTTONS:
        return f"\n[{name}](btn{action}:{args}*!repl!*)"
    else:
        return (
            f'\n[{name}].(btn{action}:{args})'
            if args
            else f'\n[{name}].(btn{action})'
        )


def get_reply_msg_btns_text(message):
    text = ''
    for column in message.reply_markup.inline_keyboard:
        for btn_num, btn in enumerate(column, start=1):
            name = btn['text']

            if 'url' in btn:
                url = btn['url']
                if '?start=' in url:
                    raw_btn = url.split('?start=')[1]
                    text += parse_button(raw_btn, name)
                else:
                    text += f"\n[{btn['text']}](btnurl:{btn['url']}*!repl!*)"
            elif 'callback_data' in btn:
                text += parse_button(btn['callback_data'], name)

            if btn_num > 1:
                text = text.replace('*!repl!*', ':same')
            else:
                text = text.replace('*!repl!*', '')
    return text


async def get_msg_file(message):
    message_id = message.message_id

    tmsg = await tbot.get_messages(message.chat.id, ids=message_id)

    if 'sticker' in message:
        return {'id': tmsg.file.id, 'type': 'sticker'}
    elif 'photo' in message:
        return {'id': tmsg.file.id, 'type': 'photo'}
    elif 'document' in message:
        return {'id': tmsg.file.id, 'type': 'document'}

    return None


async def get_parsed_note_list(message, split_args=1):
    note = {}
    if "reply_to_message" in message:
        # Get parsed reply msg text
        text, note['parse_mode'] = get_parsed_msg(message.reply_to_message)
        # Get parsed origin msg text
        text += ' '
        to_split = ''.join([f' {q}' for q in get_args(message)[:split_args]])
        if not to_split:
            to_split = ' '
        text += get_parsed_msg(message)[0].partition(message.get_command() + to_split)[2][1:]
        # Set parse_mode if origin msg override it
        if mode := get_msg_parse(message.text, default_md=False):
            note['parse_mode'] = mode

        # Get message keyboard
        if 'reply_markup' in message.reply_to_message and 'inline_keyboard' in message.reply_to_message.reply_markup:
            text += get_reply_msg_btns_text(message.reply_to_message)

        # Check on attachment
        if msg_file := await get_msg_file(message.reply_to_message):
            note['file'] = msg_file
    else:
        text, note['parse_mode'] = get_parsed_msg(message)
        text = re.sub(r'(/\w+ )([\w-]+ )', '', text, split_args)
        # Check on attachment
        if msg_file := await get_msg_file(message):
            note['file'] = msg_file

    # Preview
    if 'text' in note and '$PREVIEW' in note['text']:
        note['preview'] = True
    text = re.sub(r'%PREVIEW', '', text)

    if text.replace(' ', ''):
        note['text'] = text

    return note


async def t_unparse_note_item(message, db_item, chat_id, noformat=None, event=None):
    preview = None

    text = db_item['text'] if 'text' in db_item else ""
    file_id = db_item['file']['id'] if 'file' in db_item else None
    if noformat:
        markup = None
        if 'parse_mode' not in db_item or db_item['parse_mode'] == 'none':
            text += '\n%PARSEMODE_NONE'
        elif db_item['parse_mode'] == 'html':
            text += '\n%PARSEMODE_HTML'

        if 'preview' in db_item and db_item['preview']:
            text += '\n%PREVIEW'

        db_item['parse_mode'] = None

    else:
        pm = message.chat.type == 'private'
        text, markup = button_parser(chat_id, text, pm=pm)
        if not text and not file_id:
            text = f'#{db_item["names"][0]}'

        if 'parse_mode' not in db_item or db_item['parse_mode'] == 'none':
            db_item['parse_mode'] = None
        elif db_item['parse_mode'] == 'md':
            text = await vars_parser(text, message, chat_id, md=True, event=event)
        elif db_item['parse_mode'] == 'html':
            text = await vars_parser(text, message, chat_id, md=False, event=event)

        if 'preview' in db_item and db_item['preview']:
            preview = True

    return text, {
        'buttons': markup,
        'parse_mode': db_item['parse_mode'],
        'file': file_id,
        'link_preview': preview
    }


async def send_note(send_id, text, **kwargs):
    if 'parse_mode' in kwargs and kwargs['parse_mode'] == 'md':
        kwargs['parse_mode'] = tmarkdown
    try:
        return await tbot.send_message(send_id, text, **kwargs)
    except (ButtonUrlInvalidError, MessageEmptyError, MediaEmptyError, ValueError):
        text = 'I found this note invalid! Please update it (read Wiki).'
        return await tbot.send_message(send_id, text)


def button_parser(chat_id, texts, pm=False, aio=False, row_width=None):
    buttons = InlineKeyboardMarkup(row_width=row_width) if aio else []
    pattern = r'\[(.+?)\]\((button|btn)(.+?)(:.+?|)(:same|)\)(\n|)'
    raw_buttons = re.findall(pattern, texts)
    text = re.sub(pattern, '', texts)
    for raw_button in raw_buttons:
        name = raw_button[0]
        action = raw_button[2]
        argument = raw_button[3][1:].lower().replace('`', '') if raw_button[3] else ''

        if action in BUTTONS:
            cb = BUTTONS[action]
            string = f'{cb}_{argument}_{chat_id}' if argument else f'{cb}_{chat_id}'
            if aio:
                start_btn = InlineKeyboardButton(
                    name, url=f'https://t.me/{BOT_USERNAME}?start={string}'
                )

                cb_btn = InlineKeyboardButton(name, callback_data=string)
            else:
                start_btn = Button.url(name, f'https://t.me/{BOT_USERNAME}?start={string}')
                cb_btn = Button.inline(name, string)

            if cb.endswith('sm'):
                btn = cb_btn if pm else start_btn
            elif cb.endswith('cb'):
                btn = cb_btn
            elif cb.endswith('start'):
                btn = start_btn
            elif cb.startswith('url'):
                # Workaround to make URLs case-sensitive TODO: make better
                argument = raw_button[3][1:].replace('`', '') if raw_button[3] else ''
                btn = Button.url(name, argument)
        elif action == 'url':
            argument = raw_button[3][1:].replace('`', '') if raw_button[3] else ''
            if argument[0] == '/' and argument[1] == '/':
                argument = argument[2:]
            btn = InlineKeyboardButton(name, url=argument) if aio else Button.url(name, argument)
        else:
            # If btn not registred
            btn = None
            if argument:
                text += f'\n[{name}].(btn{action}:{argument})'
            else:
                text += f'\n[{name}].(btn{action})'
                continue

        if aio:
            buttons.insert(btn) if raw_button[4] else buttons.add(btn)
        elif len(buttons) < 1 and raw_button[4]:
            buttons.add(btn) if aio else buttons.append([btn])
        else:
            buttons[-1].append(btn) if raw_button[4] else buttons.append([btn])

    if not aio and len(buttons) == 0:
        buttons = None

    if not text or text == ' ' or text.isspace():  # TODO: Sometimes we can return text == ' '
        text = None

    return text, buttons


async def vars_parser(text, message, chat_id, md=False, event=None):
    if event is None:
        event = message

    if not text:
        return text

    language_code = await get_chat_lang(chat_id)
    current_datetime = datetime.now()

    first_name = html.escape(event.from_user.first_name)
    last_name = html.escape(event.from_user.last_name or "")
    user_id = ([user.id for user in event.new_chat_members][0]
               if 'new_chat_members' in event and event.new_chat_members != [] else event.from_user.id)
    mention = await get_user_link(user_id, md=md)
    username = ('@' + str(event.new_chat_members[0].username)
                if 'new_chat_members' in event and event.new_chat_members != [] and event.new_chat_members[0].username
                   is not None
                else '@' + event.from_user.username
                if event.from_user.username is not None else mention)
    chat_id = message.chat.id
    chat_name = html.escape(message.chat.title or 'Local')
    chat_nick = message.chat.username or chat_name

    current_date = html.escape(format_date(date=current_datetime, locale=language_code))
    current_time = html.escape(format_time(time=current_datetime, locale=language_code))
    current_timedate = html.escape(format_datetime(datetime=current_datetime, locale=language_code))

    text = text.replace('{first}', first_name) \
        .replace('{last}', last_name) \
        .replace('{fullname}', first_name + " " + last_name) \
        .replace('{id}', str(user_id).replace('{userid}', str(user_id))) \
        .replace('{mention}', mention) \
        .replace('{username}', username) \
        .replace('{chatid}', str(chat_id)) \
        .replace('{chatname}', str(chat_name)) \
        .replace('{chatnick}', str(chat_nick)) \
        .replace('{date}', str(current_date)) \
        .replace('{time}', str(current_time)) \
        .replace('{timedate}', str(current_timedate))
    return text
