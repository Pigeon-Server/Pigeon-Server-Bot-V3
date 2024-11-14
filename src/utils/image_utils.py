from tempfile import TemporaryFile
from typing import Any, Optional

from PIL import Image, ImageDraw, ImageFont


def text_to_image(draw_content: Any, save_path: Optional[str] = None, font_family: str = "msyh.ttc",
                  font_size: int = 50, text_color: str = 'black', bg_color: str = 'white') -> str:
    if save_path is None:
        file = TemporaryFile("rb", dir="temp", suffix=".png")
        save_path = file.name
        file.close()
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
