"""Constants used in the OpenType `name` table specification.

https://docs.microsoft.com/en-us/typography/opentype/spec/name
"""
import enum


# We rely on fontTools to provide `languageID`s. It provides `languageID`s as
# ints, instead of an explicit type, like an Enum. Therefore, to improve
# clarity in the following code, alias `int` as `LanguageID` and use it
# where appropriate.
LanguageID = int
PlatformEncodingID = int


# Since OpenType tables use integers to store numeric field values, use
# `IntEnum`s to allow using `Enum.MEMBER` as integer values for backwards
# compatibility in comparisons.
class NameID(enum.IntEnum):
    """`nameID` values allowed in name records their purpose.

    https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids
    """

    COPYRIGHT_NOTICE = 0
    FONT_FAMILY_NAME = 1
    FONT_SUBFAMILY_NAME = 2
    UNIQUE_FONT_ID = 3
    FULL_FONT_NAME = 4
    VERSION_STRING = 5
    POSTSCRIPT_NAME = 6
    TRADEMARK = 7
    MANUFACTURER_NAME = 8
    DESIGNER = 9
    DESCRIPTION = 10
    URL_VENDOR = 11
    URL_DESIGNER = 12
    LICENSE_DESCRIPTION = 13
    LICENSE_INFO_URL = 14
    TYPOGRAPHIC_NAME = 16
    TYPOGRAPHIC_SUBFAMILY_NAME = 17
    COMPATIBLE_FULL_NAME = 18
    SAMPLE_TEXT = 19
    POSTSCRIPT_CID_FINDFONT_NAME = 20
    WWS_FAMILY_NAME = 21
    WWS_SUBFAMILY_NAME = 22
    LIGHT_BACKGROUND_PALETTE = 23
    DARK_BACKGROUND_PALETTE = 24
    VARIATIONS_POSTSCRIPT_NAME_PREFIX = 25


class PlatformID(int, enum.Enum):
    """`platformID` values allowed in name records by platform.

    https://docs.microsoft.com/en-us/typography/opentype/spec/name#platform-ids
    """

    UNICODE = 0
    MAC = 1
    WINDOWS = 3


class MacEncodingID(PlatformEncodingID, enum.Enum):
    """`encodingID` values defined for use with the Mac platform.

    https://docs.microsoft.com/en-us/typography/opentype/spec/name#macintosh-encoding-ids-script-manager-codes
    """

    ROMAN = 0
    JAPANESE = 1
    CHINESE_TRADITIONAL = 2
    KOREAN = 3
    ARABIC = 4
    HEBREW = 5
    GREEK = 6
    RUSSIAN = 7
    RSYMBOL = 8
    DEVANAGARI = 9
    GURMUKHI = 10
    GUJARATI = 11
    ORIYA = 12
    BENGALI = 13
    TAMIL = 14
    TELUGU = 15
    KANNADA = 16
    MALAYALAM = 17
    SINHALESE = 18
    BURMESE = 19
    KHMER = 20
    THAI = 21
    LAOTIAN = 22
    GEORGIAN = 23
    ARMENIAN = 24
    CHINESE_SIMPLIFIED = 25
    TIBETAN = 26
    MONGOLIAN = 27
    GEEZ = 28
    SLAVIC = 29
    VIETNAMESE = 30
    SINDHI = 31
    UNINTERPRETED = 32


class WindowsEncodingID(PlatformEncodingID, enum.Enum):
    """`encodingID` values defined for use with the Windows platform.

    https://docs.microsoft.com/en-us/typography/opentype/spec/name#windows-encoding-ids
    """

    SYMBOL = 0
    UNICODE_BMP = 1
    SHIFTJIS = 2
    PRC = 3
    BIG5 = 4
    WANSUNG = 5
    JOHAB = 6
    UNICODE_FULL_REPERTOIRE = 10
