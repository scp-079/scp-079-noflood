# SCP-079-NOFLOOD - Message-flooding prevention
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-NOFLOOD.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
from copy import deepcopy
from time import time
from typing import Union

from pyrogram import Filters, Message

from .. import glovar
from .etc import get_now
from .file import save
from .ids import init_flood_id, init_group_id

# Enable logging
logger = logging.getLogger(__name__)


def is_class_c(_, message: Message) -> bool:
    # Check if the message is Class C object
    try:
        if message.from_user:
            uid = message.from_user.id
            gid = message.chat.id
            if init_group_id(gid):
                if uid in glovar.admin_ids[gid] or uid in glovar.bot_ids or message.from_user.is_self:
                    return True
    except Exception as e:
        logger.warning(f"Is class c error: {e}", exc_info=True)

    return False


def is_class_d(_, message: Message) -> bool:
    # Check if the message is Class D object
    try:
        if message.from_user:
            uid = message.from_user.id
            if uid in glovar.bad_ids["users"]:
                return True
    except Exception as e:
        logger.warning(f"Is class d error: {e}", exc_info=True)

    return False


def is_class_e(_, message: Message) -> bool:
    # Check if the message is Class E object
    try:
        if message.from_user:
            # All groups' admins
            uid = message.from_user.id
            admin_ids = deepcopy(glovar.admin_ids)
            for gid in admin_ids:
                if uid in admin_ids[gid]:
                    return True
    except Exception as e:
        logger.warning(f"Is class e error: {e}", exc_info=True)

    return False


def is_declared_message(_, message: Message) -> bool:
    # Check if the message is declared by other bots
    try:
        if message.chat:
            gid = message.chat.id
            mid = message.message_id
            return is_declared_message_id(gid, mid)
    except Exception as e:
        logger.warning(f"Is declared message error: {e}", exc_info=True)

    return False


def is_exchange_channel(_, message: Message) -> bool:
    # Check if the message is sent from the exchange channel
    try:
        if message.chat:
            cid = message.chat.id
            if glovar.should_hide:
                if cid == glovar.hide_channel_id:
                    return True
            elif cid == glovar.exchange_channel_id:
                return True
    except Exception as e:
        logger.warning(f"Is exchange channel error: {e}", exc_info=True)

    return False


def is_from_user(_, message: Message) -> bool:
    # Check if the message is sent from a user
    try:
        if message.from_user:
            return True
    except Exception as e:
        logger.warning(f"Is from user error: {e}", exc_info=True)

    return False


def is_hide_channel(_, message: Message) -> bool:
    # Check if the message is sent from the hide channel
    try:
        if message.chat:
            cid = message.chat.id
            if cid == glovar.hide_channel_id:
                return True
    except Exception as e:
        logger.warning(f"Is hide channel error: {e}", exc_info=True)

    return False


def is_new_group(_, message: Message) -> bool:
    # Check if the bot joined a new group
    try:
        if message.new_chat_members:
            new_users = message.new_chat_members
            if new_users:
                for user in new_users:
                    if user.is_self:
                        return True
        elif message.group_chat_created or message.supergroup_chat_created:
            return True
    except Exception as e:
        logger.warning(f"Is new group error: {e}", exc_info=True)

    return False


def is_test_group(_, message: Message) -> bool:
    # Check if the message is sent from the test group
    try:
        if message.chat:
            cid = message.chat.id
            if cid == glovar.test_group_id:
                return True
    except Exception as e:
        logger.warning(f"Is test group error: {e}", exc_info=True)

    return False


class_c = Filters.create(
    func=is_class_c,
    name="Class C"
)

class_d = Filters.create(
    func=is_class_d,
    name="Class D"
)

class_e = Filters.create(
    func=is_class_e,
    name="Class E"
)

declared_message = Filters.create(
    func=is_declared_message,
    name="Declared message"
)

exchange_channel = Filters.create(
    func=is_exchange_channel,
    name="Exchange Channel"
)

from_user = Filters.create(
    func=is_from_user,
    name="From User"
)

hide_channel = Filters.create(
    func=is_hide_channel,
    name="Hide Channel"
)

new_group = Filters.create(
    func=is_new_group,
    name="New Group"
)

test_group = Filters.create(
    func=is_test_group,
    name="Test Group"
)


def is_declared_message_id(gid: int, mid: int) -> bool:
    # Check if the message's ID is declared by other bots
    try:
        if mid in glovar.declared_message_ids.get(gid, set()):
            return True
    except Exception as e:
        logger.warning(f"Is declared message id error: {e}", exc_info=True)

    return False


def is_detected_user(message: Message) -> bool:
    # Check if the message is sent by a detected user
    try:
        if message.from_user:
            gid = message.chat.id
            uid = message.from_user.id
            return is_detected_user_id(gid, uid)
    except Exception as e:
        logger.warning(f"Is detected user error: {e}", exc_info=True)

    return False


def is_detected_user_id(gid: int, uid: int) -> bool:
    # Check if the user_id is detected in the group
    try:
        user = glovar.user_ids.get(uid, {})
        if user:
            status = user["detected"].get(gid, 0)
            now = get_now()
            if now - status < glovar.punish_time:
                return True
    except Exception as e:
        logger.warning(f"Is detected user id error: {e}", exc_info=True)

    return False


def is_flood_message(message: Message, test: bool = False) -> Union[bool, str]:
    # Check if the message is flooding message
    try:
        gid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id
        if init_flood_id(uid):
            # Check if the media group message has been counted
            if not message.media_group_id or message.media_group_id not in glovar.media_group_ids:
                if message.media_group_id:
                    glovar.media_group_ids.add(message.media_group_id)

                now = time()
                the_time = (message.date and message.date + now - int(now)) or now
                glovar.flood_ids[uid][the_time] = (gid, mid)
                for t in list(glovar.flood_ids[uid]):
                    if now - t > 60:
                        glovar.flood_ids[uid].pop(t, (0, 0))

                # Check declare status
                if is_declared_message(None, message):
                    return False

                if test:
                    flood_limit = 5
                    flood_time = 10
                else:
                    flood_limit = glovar.configs[gid]["limit"]
                    flood_time = glovar.configs[gid]["time"]

                user_flood = deepcopy(glovar.flood_ids[uid])
                for t in deepcopy(user_flood):
                    if now - t > flood_time:
                        user_flood.pop(t, (0, 0))

                user_count = len(user_flood)
                if len(user_flood) >= flood_limit:
                    return f"{flood_time} {user_count}"

        # If the user is being punished
        if is_detected_user(message):
            return f"UNKNOWN UNKNOWN"
    except Exception as e:
        logger.warning(f"Is flood message error: {e}", exc_info=True)

    return False


def is_high_score_user(message: Message) -> Union[bool, float]:
    # Check if the message is sent by a high score user
    try:
        if message.from_user:
            uid = message.from_user.id
            user = glovar.user_ids.get(uid, {})
            if user:
                score = sum(user["score"].values())
                if score >= 3.0:
                    return score
    except Exception as e:
        logger.warning(f"Is high score user error: {e}", exc_info=True)

    return False


def is_regex_text(word_type: str, text: str, again: bool = False) -> bool:
    # Check if the text hit the regex rules
    result = False
    try:
        if text:
            if not again:
                text = re.sub(r"\s{2,}", " ", text)
            elif " " in text:
                text = re.sub(r"\s", "", text)
            else:
                return False
        else:
            return False

        for word in list(eval(f"glovar.{word_type}_words")):
            if re.search(word, text, re.I | re.S | re.M):
                result = True

            # Match, count and return
            if result:
                count = eval(f"glovar.{word_type}_words").get(word, 0)
                count += 1
                eval(f"glovar.{word_type}_words")[word] = count
                save(f"{word_type}_words")
                return result

        # Try again
        return is_regex_text(word_type, text, True)
    except Exception as e:
        logger.warning(f"Is regex text error: {e}", exc_info=True)

    return result


def is_watch_user(message: Message, the_type: str) -> bool:
    # Check if the message is sent by a watch user
    try:
        if message.from_user:
            uid = message.from_user.id
            now = get_now()
            until = glovar.watch_ids[the_type].get(uid, 0)
            if now < until:
                return True
    except Exception as e:
        logger.warning(f"Is watch user error: {e}", exc_info=True)

    return False
