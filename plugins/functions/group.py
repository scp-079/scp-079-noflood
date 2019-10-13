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
from copy import deepcopy
from typing import Optional

from pyrogram import Client, Message

from .. import glovar
from .etc import code, lang, thread
from .file import save
from .telegram import delete_messages, get_messages, leave_chat

# Enable logging
logger = logging.getLogger(__name__)


def delete_flood_messages(client: Client, uid: int) -> bool:
    # Delete the user's flood messages
    try:
        flood = deepcopy(glovar.flood_ids[uid])
        need_delete = {}
        for time in flood:
            gid, mid = flood[time]
            if need_delete.get(gid) is None:
                need_delete[gid] = []

            need_delete[gid].append(mid)

        for gid in need_delete:
            thread(delete_messages, (client, gid, need_delete[gid]))

        return True
    except Exception as e:
        logger.warning(f"Delete flood messages error: {e}", exc_info=True)

    return False


def delete_message(client: Client, gid: int, mid: int) -> bool:
    # Delete a single message
    try:
        if not gid or not mid:
            return True

        mids = [mid]
        thread(delete_messages, (client, gid, mids))

        return True
    except Exception as e:
        logger.warning(f"Delete message error: {e}", exc_info=True)

    return False


def get_config_text(config: dict) -> str:
    # Get config text
    result = ""
    try:
        # Basic
        default_text = (lambda x: lang("default") if x else lang("custom"))(config.get("default"))
        delete_text = (lambda x: lang("enabled") if x else lang("disabled"))(config.get("delete"))
        restrict_text = (lambda x: lang("enabled") if x else lang("disabled"))(config.get("restrict"))
        result += (f"{lang('config')}{lang('colon')}{code(default_text)}\n"
                   f"{lang('delete')}{lang('colon')}{code(delete_text)}\n"
                   f"{lang('restrict')}{lang('colon')}{code(restrict_text)}\n")

        # Time
        result += f"{lang('noflood_time')}{lang('colon')}{code(config.get('time'))}\n"

        # Limit
        result += f"{lang('noflood_limit')}{lang('colon')}{code(config.get('limit'))}\n"

        # Purge
        result += f"{lang('noflood_purge')}{lang('colon')}{code(config.get('purge'))}\n"
    except Exception as e:
        logger.warning(f"Get config text error: {e}", exc_info=True)

    return result


def get_message(client: Client, gid: int, mid: int) -> Optional[Message]:
    # Get a single message
    result = None
    try:
        mids = [mid]
        result = get_messages(client, gid, mids)
        if result:
            result = result[0]
    except Exception as e:
        logger.warning(f"Get message error: {e}", exc_info=True)

    return result


def leave_group(client: Client, gid: int) -> bool:
    # Leave a group, clear it's data
    try:
        glovar.left_group_ids.add(gid)
        thread(leave_chat, (client, gid))

        glovar.admin_ids.pop(gid, None)
        save("admin_ids")

        glovar.configs.pop(gid, None)
        save("configs")

        return True
    except Exception as e:
        logger.warning(f"Leave group error: {e}", exc_info=True)

    return False
