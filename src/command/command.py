from src.base.event_bus import event_bus
from src.bus.event.event import MessageEvent
from src.command.mcsm_command import *
from src.command.other_command import *
from src.command.server_list_command import *
from src.command.server_status_command import *
from src.command.permission_command import *
from src.command.block_word_command import *

event_bus.subscribe(MessageEvent.MESSAGE_CREATED, CommandManager.message_listener)
