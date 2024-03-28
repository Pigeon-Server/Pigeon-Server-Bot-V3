from pathlib import Path
from typing import Union
from os.path import exists
from os import makedirs


def check_directory(directory: Union[str, Path], create_if_not_exist: bool = False) -> bool:
    if exists(directory):
        return True
    if create_if_not_exist:
        makedirs(directory)
    return False


def check_file(file: Union[str, Path], create_if_not_exist: bool = False, file_content: Union[str, bytes] = "") -> bool:
    if isinstance(file, str):
        file = Path(file)
    if file.is_file():
        return True
    if create_if_not_exist:
        with open(file, "wb") as f:
            f.write(file_content)
    return False
