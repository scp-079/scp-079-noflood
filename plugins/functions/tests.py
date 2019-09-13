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

from pyrogram import Client, Message

from .. import glovar
from .etc import code, get_text, thread, user_mention
from .filters import is_flood_message
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def flood_test(client: Client, message: Message) -> bool:
    # Test message's flood status
    try:
        message_text = get_text(message)
        if message_text:
            if re.search("^管理员：[0-9]", message_text):
                return True

        aid = message.from_user.id
        if is_flood_message(message, True):
            text = (f"管理员：{user_mention(aid)}\n\n"
                    f"洪水消息：{code('True')}\n")
            thread(send_message, (client, glovar.test_group_id, text, message.message_id))

        return True
    except Exception as e:
        logger.warning(f"Flood test error: {e}", exc_info=True)

    return False
