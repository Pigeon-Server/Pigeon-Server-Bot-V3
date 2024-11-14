from os import makedirs
from os.path import exists
from pathlib import Path
from typing import Union


def check_directory(directory: Union[str, Path],
                    *,
                    create_if_not_exist: bool = False) -> bool:
    if exists(directory):
        return True
    if create_if_not_exist:
        makedirs(directory)
    return False


def check_file(file: Union[str, Path],
               *,
               create_if_not_exist: bool = False,
               file_content: Union[str, bytes] = "",
               encoding: str = "utf8") -> bool:
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file_content, str):
        file_content = file_content.encode("utf-8")
    if file.is_file():
        return True
    if create_if_not_exist:
        with open(file, "wb", encoding=encoding) as f:
            f.write(file_content)
    return False
