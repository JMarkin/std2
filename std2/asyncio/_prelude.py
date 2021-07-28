from asyncio import get_running_loop, sleep
from asyncio.futures import Future
from asyncio.tasks import FIRST_EXCEPTION, wait
from functools import partial
from typing import AbstractSet, Any, Callable, MutableSet, Tuple, TypeVar, cast

T = TypeVar("T")
_T2 = TypeVar("_T2", bound=Future)


async def pure(x: T) -> T:
    return x


async def cancel(f: Future) -> None:
    f.cancel()
    while not f.done():
        await sleep(0)


async def race(aw: _T2, *aws: _T2) -> Tuple[_T2, AbstractSet[_T2], AbstractSet[_T2]]:
    r: Any = await wait((aw, *aws), return_when=FIRST_EXCEPTION)
    done, pending = cast(Tuple[MutableSet[_T2], MutableSet[_T2]], r)
    ret = done.pop()
    return ret, done, pending


async def run_in_executor(f: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = get_running_loop()
    cont = partial(f, *args, **kwargs)
    return await loop.run_in_executor(None, cont)
