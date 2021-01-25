from asyncio.subprocess import DEVNULL, PIPE, create_subprocess_exec
from dataclasses import dataclass
from os import PathLike, environ, getcwd
from typing import Any, AsyncContextManager, Mapping, Optional, Sequence, Union, cast

from ..contextlib import nullacontext

AnyPath = Union[PathLike, str, bytes]


@dataclass(frozen=True)
class ProcReturn:
    prog: str
    args: Sequence[str]
    code: int
    out: bytes
    err: str


async def call(
    prog: str,
    *args: str,
    stdin: Optional[bytes] = None,
    cwd: Optional[AnyPath] = None,
    env: Optional[Mapping[str, str]] = None,
    ctx_mgr: Optional[AsyncContextManager[Any]] = None,
) -> ProcReturn:
    async with ctx_mgr or nullacontext():
        proc = await create_subprocess_exec(
            prog,
            *args,
            stdin=PIPE if stdin else DEVNULL,
            stdout=PIPE,
            stderr=PIPE,
            cwd=getcwd() if cwd is None else cwd,
            env=environ if env is None else {**environ, **env},
        )
        stdout, stderr = await proc.communicate(stdin)
        code = cast(int, proc.returncode)

        return ProcReturn(
            prog=prog, args=args, code=code, out=stdout, err=stderr.decode()
        )
