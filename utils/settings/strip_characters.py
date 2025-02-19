from typing import Callable


def strip_characters(characters: str) -> Callable:
    def core(value: str) -> str:
        return value.strip(characters)
    return core 