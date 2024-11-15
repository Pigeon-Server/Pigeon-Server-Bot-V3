from typing import Optional, Union

from src.element.message import Message
from src.exception.exception import QuotationUnmatchedError


def is_command(command: str) -> bool:
    return command.startswith("/")


def command_split(command: Union[Message, str]) -> Optional[list[str]]:
    if isinstance(command, Message):
        if not command.is_command or command.message == "":
            return None
        message = command.message
    else:
        if not is_command(command) or command == "":
            return None
        message = command
    res = []
    msg = message[1:]
    temp = ""
    is_quoted = False
    quote_char = None
    for i in msg:
        if i in ['"', "'"]:
            if not is_quoted:
                is_quoted = True
                quote_char = i
            elif quote_char == i:
                is_quoted = False
                quote_char = None
            continue
        if is_quoted:
            temp += i
        else:
            if i.isspace():
                if len(temp) != 0:
                    res.append(temp)
                    temp = ""
            else:
                temp += i
    if is_quoted:
        raise QuotationUnmatchedError
    if temp != "":
        res.append(temp)
    return res
