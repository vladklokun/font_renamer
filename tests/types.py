"""Type definitions and annotations for use in tests."""
import enum
import typing as typ

import font_renamer.opentype_name_constants as fr_const


# A workaround for type hints for generic literals. Obviously, this
# would match any types that are not literals (int, str etc), however, as per
# Zen of Python, practicality beats purity.
LiteralValueAtom = typ.Union[int, str, bool, enum.Enum, None]
LiteralValue = typ.Union[list[LiteralValueAtom], LiteralValueAtom]
Literal = type[LiteralValue]


class NameRecordTupleMaybe(typ.NamedTuple):
    """A named tuple with possibly valid arguments for creating `NameRecord`s."""

    string: typ.Union[str, bytes]
    name_id: int
    platform_id: int
    platform_encoding_id: int
    language_id: int


class NameRecordTupleValid(NameRecordTupleMaybe):
    """A named tuple with arguments for creating `NameRecord`s."""

    string: str
    name_id: fr_const.NameID
    platform_id: fr_const.PlatformID
    platform_encoding_id: typ.Union[
        fr_const.MacPlatformEncodingID, fr_const.WindowsPlatformEncodingID
    ]
    language_id: int
