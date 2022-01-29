from functools import lru_cache
from itertools import cycle
from os import linesep
from shutil import get_terminal_size
from typing import Iterator, Optional
from unicodedata import east_asian_width

_COLS, _ = get_terminal_size()
_UNICODE_WIDTH_LOOKUP = {
    "W": 2,  # CJK
    "N": 0,  # Non printable
}


def display_width(tabsize: int, string: str) -> int:
    def cont() -> Iterator[int]:
        for char in string:
            if char == "\t":
                yield tabsize
            else:
                code = east_asian_width(char)
                yield _UNICODE_WIDTH_LOOKUP.get(code, 1)

    return sum(cont())


@lru_cache
def hr(
    thing: Optional[str] = None,
    *,
    sep: str = "-",
    end: str = linesep,
    tabsize: int = 4,
    cols: int = _COLS,
) -> str:
    def cont() -> Iterator[str]:
        source = cycle(zip(sep, (display_width(tabsize, string=char) for char in sep)))
        seen = 0
        for char, length in source:
            seen += length
            if seen < cols:
                yield char
            else:
                break

    line = "".join(cont())

    if thing is None:
        return line
    else:
        decor = f"{line}{linesep}{thing}{linesep}{line}{end}"
        return decor
