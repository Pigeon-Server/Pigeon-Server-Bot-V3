from os import makedirs
from os.path import exists
from pathlib import Path
from typing import Any, Union

from PIL import Image, ImageDraw, ImageFont


def check_directory(directory: Union[str, Path], create_if_not_exist: bool = False) -> bool:
    if exists(directory):
        return True
    if create_if_not_exist:
        makedirs(directory)
    return False


def check_file(file: Union[str, Path], create_if_not_exist: bool = False, file_content: Union[str, bytes] = "") -> bool:
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file_content, str):
        file_content = file_content.encode("utf-8")
    if file.is_file():
        return True
    if create_if_not_exist:
        with open(file, "wb") as f:
            f.write(file_content)
    return False


def text_to_image(draw_content: Any, save_path: str = "image.png", font_family: str = "msyh.ttc",
                  font_size: int = 50, text_color: str = 'black', bg_color: str = 'white') -> str:
    text = str(draw_content)

    text = text.replace("\t", " " * 4)

    font = ImageFont.truetype(font_family, font_size)

    img = Image.new('RGB', (0, 0), color=bg_color)
    draw = ImageDraw.Draw(img)

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top + font_size // 2

    img = Image.new('RGB', (text_width, text_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    draw.rectangle(((0, 0), (text_width, text_height)), fill=bg_color)
    draw.multiline_text((0, 0), text, fill=text_color, font=font)

    img.save(save_path)
    return save_path
