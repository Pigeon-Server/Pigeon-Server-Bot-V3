from random import choice
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Optional


def random_string(length: int,
                  *,
                  letters: Optional[str] = None,
                  uppercase: bool = True,
                  lowercase: bool = True,
                  number: bool = True,
                  special: bool = False) -> str:
    if letters is None:
        letters = []
        if uppercase:
            letters += ascii_uppercase
        if lowercase:
            letters += ascii_lowercase
        if number:
            letters += digits
        if special:
            letters += punctuation
    return ''.join(choice(letters) for _ in range(length))
