from itertools import islice
from typing import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
    TypeVar,
)

T = TypeVar("T")
K = TypeVar("K")


def take(it: Iterable[T], n: int) -> Sequence[T]:
    return tuple(islice(it, n))


def chunk(it: Iterable[T], n: int) -> Iterator[Sequence[T]]:
    return iter(lambda: take(it, n), ())


def group_by(it: Iterable[T], key: Callable[[T], K]) -> Mapping[K, Sequence[T]]:
    coll: MutableMapping[K, MutableSequence[T]] = {}

    for item in it:
        acc = coll.setdefault(key(item), [])
        acc.append(item)

    return coll


class deiter(Iterator[T]):
    def __init__(self, it: Iterable[T]) -> None:
        self._s: MutableSequence[T] = []
        self._it = iter(it)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self._s:
            return self._s.pop()
        else:
            return next(self._it)

    def push_back(self, *item: T) -> None:
        self._s.extend(reversed(item))

