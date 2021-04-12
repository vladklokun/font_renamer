"""Type definitions and annotations for use in tests."""
import typing as typ

import font_renamer.opentype_name_constants as fr_const


class NameRecordTupleMaybe(typ.NamedTuple):
    """A named tuple with possibly valid arguments for creating `NameRecord`s.
    """

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
        fr_const.MacEncodingID, fr_const.WindowsEncodingID
    ]
    language_id: int
