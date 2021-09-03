from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from .types import Void, VoidType

_T = TypeVar("_T")


def aiter(ait: AsyncIterable[_T]) -> AsyncIterator[_T]:
    return ait.__aiter__()


async def anext(ait: AsyncIterator[_T], default: Union[_T, VoidType] = Void) -> _T:
    if isinstance(default, VoidType):
        return await ait.__anext__()
    else:
        try:
            return await ait.__anext__()
        except StopAsyncIteration:
            return default


class SupportsLT(Protocol):
    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        ...


def clamp(
    lo: _T, n: _T, hi: _T, key: Optional[Callable[[_T], SupportsLT]] = None
) -> _T:
    if key:
        return max(lo, min(hi, n, key=key), key=key)
    else:
        return max(lo, min(hi, n))  # type: ignore
