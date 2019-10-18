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
from .etc import code, get_text, lang, thread, user_mention
from .filters import is_flood_message
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def flood_test(client: Client, message: Message) -> bool:
    # Test message's flood status
    try:
        origin_text = get_text(message)
        if re.search(f"^{lang('admin')}{lang('colon')}[0-9]", origin_text):
            return True
        else:
            aid = message.from_user.id

        # Send the result
        if is_flood_message(message, True):
            text = (f"{lang('admin')}{lang('colon')}{user_mention(aid)}\n\n"
                    f"{lang('flood_message')}{lang('colon')}{code('True')}\n")
            thread(send_message, (client, glovar.test_group_id, text, message.message_id))

        return True
    except Exception as e:
        logger.warning(f"Flood test error: {e}", exc_info=True)

    return False
