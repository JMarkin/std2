from locale import strcoll, strxfrm
from pathlib import Path, PurePath
from sqlite3 import register_adapter, register_converter
from sqlite3.dbapi2 import Connection, Row
from typing import AbstractSet, Iterable, Mapping, Optional, Union
from unicodedata import normalize
from uuid import UUID, uuid4

SQL_TYPES = Union[int, float, str, bytes, None]
SQL_PARAM = Mapping[str, SQL_TYPES]
SQL_PARAMS = Iterable[SQL_PARAM]


def escape(nono: AbstractSet[str], escape: str, param: str) -> str:
    esc = str.maketrans({ch: f"{escape}{ch}" for ch in nono | {escape}})
    return param.translate(esc)


def _normalize(text: Optional[str]) -> Optional[str]:
    return None if text is None else normalize("NFC", text)


def _lower(text: Optional[str]) -> Optional[str]:
    return None if text is None else text.casefold()


def _uuid_bytes() -> bytes:
    return uuid4().bytes


def add_functions(conn: Connection) -> None:
    conn.row_factory = Row
    conn.create_collation("X_COLLATION", strcoll)
    conn.create_function("X_STRXFRM", 1, func=strxfrm, deterministic=True)
    conn.create_function("X_NORMALIZE", 1, func=_normalize, deterministic=True)
    conn.create_function("X_LOWER", 1, func=_lower, deterministic=True)
    conn.create_function("X_UUID_B", 0, func=_uuid_bytes, deterministic=False)


def add_conversion() -> None:
    register_adapter(UUID, lambda u: u.bytes)
    register_converter(UUID.__qualname__, lambda b: UUID(bytes=b))

    register_adapter(PurePath, str)
    register_converter(PurePath.__qualname__, lambda b: PurePath(b.decode()))
    register_converter(Path.__qualname__, lambda b: Path(b.decode()))
