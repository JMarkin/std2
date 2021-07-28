from asyncio.subprocess import DEVNULL, PIPE, create_subprocess_exec
from contextlib import suppress
from dataclasses import dataclass
from os import environ, getcwd
from subprocess import CalledProcessError
from typing import AbstractSet, Mapping, Optional, Sequence, cast

from ..pathlib import AnyPath


@dataclass(frozen=True)
class ProcReturn:
    prog: str
    args: Sequence[str]
    code: int
    out: bytes
    err: str


async def call(
    prog: AnyPath,
    *args: AnyPath,
    stdin: Optional[bytes] = None,
    cwd: Optional[AnyPath] = None,
    env: Optional[Mapping[str, str]] = None,
    check_returncode: AbstractSet[int] = frozenset((0,))
) -> ProcReturn:
    p = str(prog)
    proc = await create_subprocess_exec(
        p,
        *args,
        stdin=PIPE if stdin is not None else DEVNULL,
        stdout=PIPE,
        stderr=PIPE,
        cwd=getcwd() if cwd is None else cwd,
        env=environ if env is None else {**environ, **env},
    )
    try:
        stdout, stderr = await proc.communicate(stdin)
        code = cast(int, proc.returncode)

        if check_returncode and code not in check_returncode:
            raise CalledProcessError(
                returncode=code, cmd=(p, *args), output=stdout, stderr=stderr.decode()
            )
        else:
            return ProcReturn(
                prog=p, args=args, code=code, out=stdout, err=stderr.decode()
            )
    finally:
        with suppress(ProcessLookupError):
            proc.kill()
        await proc.wait()
