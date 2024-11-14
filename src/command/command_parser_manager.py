from typing import Callable, Dict, Optional, Union

from src.base.logger import logger
from src.element.message import Message
from src.element.result import Result
from src.type.types import parser_function
from src.utils.utils import random_string


class CommandParserManager:
    _command_parsers: Dict[str, parser_function] = {}

    @staticmethod
    def add_command_parser(parser_name: Optional[Union[parser_function, str]] = None):
        if parser_name is not None and isinstance(parser_name, Callable):
            name = f"{parser_name.__name__}_{random_string(8)}"
            logger.debug(f"Adding command parser: {name}")
            CommandParserManager._command_parsers[name] = parser_name
            return

        def decorator(func: parser_function):
            if parser_name is None:
                function_name = f"{func.__name__}_{random_string(8)}"
                logger.debug(f"Adding command parser: {function_name}")
                CommandParserManager._command_parsers[function_name] = func
            else:
                logger.debug(f"Adding command parser: {parser_name}")
                CommandParserManager._command_parsers[parser_name] = func

        return decorator

    @staticmethod
    async def parse_command(message: Message, command: list[str]) -> Optional[Result]:
        exception: list[Exception] = []
        for parser_name, parser in CommandParserManager._command_parsers.items():
            logger.debug(f"{parser_name} parsing {message}")
            try:
                result = await parser(message, command)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"{parser_name} parsing {message} failed: {e}")
                exception.append(e)
        if len(exception) != 0:
            return Result.of_failure(f"Parsing command failed, {len(exception)} exception(s)")
        return None
