"""Domain models for interaction with the OpenType `name` table."""
import pydantic as pyd
import font_renamer.opentype_name_constants as fr_ot_const
import typing as typ


class PNameRecord(typ.Protocol):
    """Protocol for platform-specific name records."""

    string: pyd.StrictStr
    platform_id: fr_ot_const.PlatformID
    platform_encoding_id: typ.Union[
        fr_ot_const.MacPlatformEncodingID, fr_ot_const.WindowsPlatformEncodingID
    ]
    language_id: typ.Union[
        fr_ot_const.MacLanguageID, fr_ot_const.WindowsLanguageID
    ]


class MacNameRecord(pyd.BaseModel):
    """Mac-specific name record."""

    string: pyd.StrictStr
    platform_id: typ.Literal[fr_ot_const.PlatformID.MAC]
    platform_encoding_id: fr_ot_const.MacPlatformEncodingID
    language_id: fr_ot_const.MacLanguageID
