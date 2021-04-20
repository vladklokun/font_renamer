"""Facilities for working with platforms supported by the OpenType standard.

Defines internal constants and dataclasses for accessing data about the
platforms supported by the OpenType standard. This data should be immutable,
therefore we freeze dataclasses and wrap dictionaries in the `MappingProxyType`
to prevent modification.
"""
import collections.abc as col_abc
import dataclasses as dc
import typing as typ

import fontTools.ttLib.tables._n_a_m_e as ft_table_name
import immutables as im

import font_renamer.opentype_name_constants as fr_const


class UnsupportedLanguageCodeError(KeyError):
    """Shows that a platform does not support the provided language code."""


# Maps IETF BCP-47 codes (e. g. "en", "ar") to platform-specific `language_id`s
# These maps need to be immutable to be truly constant, so wrap dicts provided
# by FontTools in `MappingProxyType` from here on out
_MAC_LANGUAGE_IDS: typ.Mapping[str, fr_const.LanguageID] = im.Map(
    ft_table_name._MAC_LANGUAGE_CODES
)


_WINDOWS_LANGUAGE_IDS: typ.Mapping[str, fr_const.LanguageID] = im.Map(
    ft_table_name._WINDOWS_LANGUAGE_CODES
)


# Maps language IDs to platform encoding IDs
_MAC_PLATFORM_ENCODING_IDS: typ.Mapping[
    fr_const.LanguageID, fr_const.MacPlatformEncodingID
] = im.Map(
    {
        lang: fr_const.MacPlatformEncodingID(encoding)
        for lang, encoding in ft_table_name._MAC_LANGUAGE_TO_SCRIPT.items()
    }
)


_WINDOWS_PLATFORM_ENCODING_IDS: typ.Mapping[
    fr_const.LanguageID, fr_const.WindowsPlatformEncodingID
] = im.Map(
    {
        # Every language should be encoded as Unicode, since this is the most
        # widely supported option
        lang: fr_const.WindowsPlatformEncodingID.UNICODE_BMP
        for lang in _WINDOWS_LANGUAGE_IDS.values()
    }
)


@dc.dataclass(frozen=True)
class Platform:
    """A platform supported by the OpenType specification."""

    name: str
    platform_id: fr_const.PlatformID
    valid_platform_encoding_ids: col_abc.Set[fr_const.PlatformID]
    valid_language_ids: col_abc.Set[fr_const.LanguageID]


@dc.dataclass(frozen=True)
class LanguageMappedPlatform(Platform):
    """A platform supported by OpenType with language code mapping attached.

    Allows to get it's `platform_encoding_id` and `language_id` values by a
    BCP-47 language code.
    """

    language_ids: typ.Mapping[str, fr_const.LanguageID]
    platform_encoding_ids: typ.Mapping[
        fr_const.LanguageID, fr_const.PlatformID
    ]

    def get_language_id(self, language_code: str) -> fr_const.LanguageID:
        """Return OpenType `language_id` for a given BCP-47 code.

        Raises an `UnsupportedLanguageCodeError` when a language ID cannot be
        found for a given language code.
        """
        try:
            language_id = self.language_ids[language_code]
        except KeyError:
            raise UnsupportedLanguageCodeError(
                f'Unable to find a language ID for "{language_code}". '
                f"Supported languages: {self.language_ids}"
            )
        return language_id

    def get_platform_encoding_id(
        self, language_code: str
    ) -> fr_const.PlatformID:
        """Return OpenType `platform_encoding_id` for a given BCP-47 code.

        Raises an `UnsupportedLanguageCodeError` when a platform encoding ID
        cannot be found for a given language code.
        """
        language_id = self.get_language_id(language_code)
        try:
            platform_encoding_id = self.platform_encoding_ids[language_id]
        except KeyError:
            raise UnsupportedLanguageCodeError(
                f"Unable to find a platform encoding ID "
                f'for "{language_code}". '
                f"Supported languages: {self.platform_encoding_ids}"
            )
        return platform_encoding_id


@dc.dataclass(frozen=True)
class LanguageInfo:
    """A data structure describing the platform-specific language info.

    Since language information is platform-specific, and the same language can
    map to different `language_id`s and `language_encoding_id`s on different
    platforms, we have to store a low-level platform-specific value for each
    platform.
    """

    platform_id: fr_const.PlatformID
    language_id: int
    platform_encoding_id: int


def get_language_info(platform, language_code: str) -> LanguageInfo:
    """Return `LanguageInfo` for a given platform and language code."""
    language_id = platform.get_language_id(language_code)
    platform_encoding_id = platform.get_platform_encoding_id(language_code)
    return LanguageInfo(platform.platform_id, language_id, platform_encoding_id)


WINDOWS_PLATFORM: LanguageMappedPlatform = LanguageMappedPlatform(
    name="windows",
    platform_id=fr_const.PlatformID.WINDOWS,
    valid_platform_encoding_ids=frozenset(fr_const.WindowsPlatformEncodingID),
    valid_language_ids=frozenset(_WINDOWS_LANGUAGE_IDS.values()),
    language_ids=_WINDOWS_LANGUAGE_IDS,
    platform_encoding_ids=_WINDOWS_PLATFORM_ENCODING_IDS,
)
MAC_PLATFORM: LanguageMappedPlatform = LanguageMappedPlatform(
    name="mac",
    platform_id=fr_const.PlatformID.MAC,
    valid_platform_encoding_ids=frozenset(fr_const.MacPlatformEncodingID),
    valid_language_ids=frozenset(_MAC_LANGUAGE_IDS.values()),
    language_ids=_MAC_LANGUAGE_IDS,
    platform_encoding_ids=_MAC_PLATFORM_ENCODING_IDS,
)


PLATFORMS: typ.Tuple = (WINDOWS_PLATFORM, MAC_PLATFORM)
