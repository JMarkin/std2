from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from ipaddress import IPv4Address, IPv4Interface
from typing import (
    Any,
    ClassVar,
    Generic,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)
from unittest import TestCase
from uuid import UUID, uuid4

from ..std2.pickle import DecodeError, decode, encode
from ..std2.pickle.coders import (
    BUILTIN_DECODERS,
    BUILTIN_ENCODERS,
    datetime_float_decoder,
    datetime_float_encoder,
    datetime_str_decoder,
    datetime_str_encoder,
    uuid_decoder,
    uuid_encoder,
)
from ..std2.pickle.decoder2 import new_parser

T = TypeVar("T")


class Encode(TestCase):
    def test_1(self) -> None:
        thing = encode([1, 2, 3])
        self.assertEqual(thing, (1, 2, 3))

    def test_2(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: Sequence[str]
            c: Mapping[str, int]

        thing = encode(C(a=1, b=["a", "b"], c={"a": 2}))
        self.assertEqual(thing, {"a": 1, "b": ("a", "b"), "c": {"a": 2}})

    def test_3(self) -> None:
        class C(Enum):
            a = b"a"

        thing = encode(C.a)
        self.assertEqual(thing, C.a.name)


class Decode(TestCase):
    def test_1(self) -> None:
        p = new_parser(None)
        thing: None = p(None)
        self.assertEqual(thing, None)

    def test_2(self) -> None:
        p = new_parser(None)
        with self.assertRaises(DecodeError):
            p(())

    def test_3(self) -> None:
        p = new_parser(int)
        thing: int = p(2)
        self.assertEqual(thing, 2)

    def test_4(self) -> None:
        with self.assertRaises(DecodeError):
            decode(int, "a")

    def test_5(self) -> None:
        p = new_parser(str)
        thing: str = p("a")
        self.assertEqual(thing, "a")

    def test_6(self) -> None:
        p = new_parser(Optional[str])
        thing: Optional[str] = p("a")
        self.assertEqual(thing, "a")

    def test_7(self) -> None:
        p = new_parser(Optional[str])
        thing: Optional[str] = p(None)
        self.assertEqual(thing, None)

    def test_8(self) -> None:
        p = new_parser(Union[int, str])
        thing: int = p(2)
        self.assertEqual(thing, 2)

    def test_9(self) -> None:
        p = new_parser(Union[int, str])
        thing: int = p("a")
        self.assertEqual(thing, "a")

    def test_10(self) -> None:
        p = new_parser(Union[int, str])
        with self.assertRaises(DecodeError):
            p(b"a")

    def test_11(self) -> None:
        p = new_parser(Tuple[int, str])
        thing: Tuple[int, str] = p((1, "a"))
        self.assertEqual(thing, [1, "a"])

    def test_12(self) -> None:
        p = new_parser(Tuple[int, str])
        with self.assertRaises(DecodeError):
            p(("a",))

    def test_13(self) -> None:
        p = new_parser(Tuple[int, str])
        with self.assertRaises(DecodeError):
            p(("a", 1))

    def test_14(self) -> None:
        p = new_parser(Any)
        thing: None = p(None)
        self.assertEqual(thing, None)

    def test_15(self) -> None:
        p = new_parser(Tuple[int, ...])
        thing: Tuple[int, ...] = p([1, 2, 3])
        self.assertEqual(thing, [1, 2, 3])

    def test_16(self) -> None:
        p = new_parser(Tuple[int, ...])
        with self.assertRaises(DecodeError):
            p((1, "a"))

    def test_17(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: List[str]
            c: bool = False

        p = new_parser(C)
        thing: C = p({"a": 1, "b": []})
        self.assertEqual(thing, C(a=1, b=[], c=False))

    def test_18(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: List[str]
            c: bool = False
            z: ClassVar[bool] = True

        p = new_parser(C, strict=False)
        thing: C = p({"a": 1, "b": []})
        self.assertEqual(thing, C(a=1, b=[], c=False))

    def test_19(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: List[str]
            c: bool = False

        p = new_parser(C)
        thing: C = p({"a": 1, "b": [], "d": "d"})
        self.assertEqual(thing, C(a=1, b=[], c=False))

    def test_20(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: List[str]
            c: bool = False

        p = new_parser(C, strict=True)
        with self.assertRaises(DecodeError) as e:
            p({"a": 1, "b": [], "d": "d"})
        self.assertEqual(e.exception.extra_keys, {"d"})

    def test_21(self) -> None:
        @dataclass(frozen=True)
        class C:
            a: int
            b: List[str]
            c: bool = False

        p = new_parser(C)
        with self.assertRaises(DecodeError) as e:
            p({"a": 1})
        self.assertEqual(e.exception.missing_keys, {"b"})

    def test_22(self) -> None:
        uuid = uuid4()
        thing: UUID = decode(UUID, uuid.hex, decoders=(uuid_decoder,))
        self.assertEqual(uuid, thing)

    def test_23(self) -> None:
        class E(Enum):
            a = "b"
            b = "a"

        thing: Sequence[E] = decode(Sequence[E], ("a", "b"))
        self.assertEqual(thing, (E.a, E.b))

    def test_24(self) -> None:
        thing: Tuple[Literal[5], Literal[2]] = decode(
            Tuple[Literal[5], Literal[2]], [5, 2]
        )
        self.assertEqual(thing, (5, 2))

    def test_25(self) -> None:
        with self.assertRaises(DecodeError):
            decode(Literal[b"a"], "a")

    def test_26(self) -> None:
        @dataclass(frozen=True)
        class C(Generic[T]):
            t: T

        with self.assertRaises(DecodeError):
            decode(C[int], {"t": True})

    def test_27(self) -> None:
        a: float = decode(float, 0)
        self.assertEqual(a, 0.0)

    def test_28(self) -> None:
        class E(Enum):
            a = "b"
            b = "a"

        with self.assertRaises(DecodeError):
            decode(Sequence[E], ("name", "b"))

    def test_29(self) -> None:
        addr = IPv4Address("1.1.1.1")
        inf = IPv4Interface("1.1.1.1/24")

        d_addr = decode(IPv4Address, str(addr), decoders=BUILTIN_DECODERS)
        d_inf = decode(IPv4Interface, str(inf), decoders=BUILTIN_DECODERS)
        self.assertNotEqual(addr, inf)
        self.assertEqual(d_addr, addr)
        self.assertEqual(d_inf, inf)

    def test_30(self) -> None:
        addr = IPv4Address("1.1.1.1")
        inf = IPv4Interface("1.1.1.1/24")

        a_addr = encode(addr, encoders=BUILTIN_ENCODERS)
        inf_addr = encode(inf, encoders=BUILTIN_ENCODERS)
        self.assertNotEqual(addr, inf)
        self.assertEqual(a_addr, str(addr))
        self.assertEqual(inf_addr, str(inf))


class RoundTrip(TestCase):
    def test_1(self) -> None:
        before = uuid4()
        thing = encode(before, encoders=(uuid_encoder,))
        after: UUID = decode(UUID, thing, decoders=(uuid_decoder,))
        self.assertEqual(after, before)

    def test_2(self) -> None:
        before = datetime.now(tz=timezone.utc)
        thing = encode(before, encoders=(datetime_str_encoder,))
        after: datetime = decode(datetime, thing, decoders=(datetime_str_decoder,))
        self.assertEqual(after, before)

    def test_3(self) -> None:
        before = datetime.now(tz=timezone.utc)
        thing = encode(before, encoders=(datetime_float_encoder,))
        after: datetime = decode(datetime, thing, decoders=(datetime_float_decoder,))
        self.assertEqual(after, before)

