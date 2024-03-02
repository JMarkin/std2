from json import dumps
from typing import Iterable, Iterator, Mapping, MutableSequence


class ParseError(Exception): ...


def split(tokens: Iterable[str], sep: str, esc: str) -> Iterator[str]:
    acc: MutableSequence[str] = []
    it = iter(tokens)

    for c in it:
        if c == esc:
            nc = next(it, "")
            if nc in {sep, esc}:
                acc.append(nc)
            else:
                e, s, n = dumps(esc), dumps(sep), dumps(nc)
                msg = f"Unexpected char: {n} after {e}, expected: {e} or {s}"
                raise ParseError(msg)
        elif c == sep:
            yield "".join(acc)
            acc.clear()
        else:
            acc.append(c)

    if acc:
        yield "".join(acc)


def envsubst(tokens: Iterable[str], env: Mapping[str, str]) -> str:
    def cont() -> Iterator[str]:
        it = iter(tokens)
        for c in it:
            if c == "$":
                nc = next(it, "")
                if nc == "$":
                    yield nc
                elif nc == "{":
                    chars: MutableSequence[str] = []
                    for c in it:
                        if c == "}":
                            name = "".join(chars)
                            if name in env:
                                yield env[name]
                            else:
                                msg = f"KeyError: expected {name} in env"
                                raise ParseError(msg)
                            break
                        else:
                            chars.append(c)
                    else:
                        msg = "Unexpected EOF after ${"
                        raise ParseError(msg, tokens)
                else:
                    msg = f"Unexpected char: {c} after $, expected $, {{"
                    raise ParseError(msg, tokens)
            else:
                yield c

    return "".join(cont())
