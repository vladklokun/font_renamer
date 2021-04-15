"""Values used with OpenType `name` tables that have been mapped for use with
the tool.

The actual values are provided by fontTools. These include:
    - IETF BCP-47 language codes ("en", "ar" etc) — to conveniently set the
      name for a language instead of relying on whatever the language ID is for
      any given platform.
    - LanguageIDs - to get an idea of which language IDs have been mapped.
    - PlatformEncodingID - same as above.
"""
import collections.abc as col_abc
import typing as typ

import fontTools.ttLib.tables._n_a_m_e as ft_table_name

import font_renamer.opentype_name_constants as fr_ot_const


# Platform-specific language codes and IDs that have been mapped.
# For example, if a language code `"en"` is mapped to language ID `1`, it is
# considered mapped. And if a language code `"ar"` is not mapped to any
# language ID, it is considered unmapped.
_MAPPED_MAC_LANGUAGE_CODES: typ.Final[col_abc.Set[str]] = frozenset(
    ft_table_name._MAC_LANGUAGE_CODES.keys()
)
_MAPPED_MAC_LANGUAGE_IDS: typ.Final[col_abc.Set[int]] = frozenset(
    ft_table_name._MAC_LANGUAGE_CODES.values()
)
_MAPPED_MAC_PLATFORM_ENCODING_IDS: typ.Final[col_abc.Set[int]] = frozenset(
    ft_table_name._MAC_LANGUAGE_TO_SCRIPT.values()
)


_MAPPED_WINDOWS_LANGUAGE_CODES: typ.Final[col_abc.Set[str]] = frozenset(
    ft_table_name._WINDOWS_LANGUAGE_CODES.keys()
)
_MAPPED_WINDOWS_LANGUAGE_IDS: typ.Final[col_abc.Set[int]] = frozenset(
    ft_table_name._WINDOWS_LANGUAGE_CODES.values()
)

# Microsoft encourages using `WindowsEncodingID.UNICODE_BMP` as the default
# platform encoding as per:
# https://docs.microsoft.com/en-us/typography/opentype/spec/name#windows-encoding-ids
_MAPPED_WINDOWS_PLATFORM_ENCODING_IDS: typ.Final[col_abc.Set[int]] = frozenset(
    {fr_ot_const.WindowsEncodingID.UNICODE_BMP}
)
