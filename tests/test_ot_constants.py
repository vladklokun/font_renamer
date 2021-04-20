"""Tests for defined OpenType constants."""
import collections.abc as col_abc
import enum
import typing as typ

import fontTools.ttLib.tables._n_a_m_e as ft_table_name
import immutables as im
import pytest

import font_renamer.opentype_name_constants as fr_ot_const

LanguageCodeMapping = col_abc.Mapping[str, int]


@pytest.fixture(scope="session")
def mac_language_code_mapping() -> typ.Generator[
    LanguageCodeMapping, None, None
]:
    """Yield language code mapping for the Mac platform."""
    # Session-scoped fixture is shared among tests, so to avoid side effects
    # it's better to return a copy rather than a reference to the original data
    #
    # Immutables correctly implements the `Mapping` protocol, but pyright
    # doesn't recognize it (mypy does). Therefore, we need a cast.
    yield typ.cast(
        LanguageCodeMapping, im.Map(ft_table_name._MAC_LANGUAGE_CODES)
    )


@pytest.fixture(scope="session")
def windows_language_code_mapping() -> typ.Generator[
    LanguageCodeMapping, None, None
]:
    """Yield language code mapping for the Windows platform."""
    yield typ.cast(
        LanguageCodeMapping, im.Map(ft_table_name._WINDOWS_LANGUAGE_CODES)
    )


class TestLanguageIDs:
    """Test language ID enums."""

    @staticmethod
    def _enum_members_match_mapping(
        enum: type[enum.Enum], mapping: LanguageCodeMapping
    ) -> bool:
        """Return `True` if members of `enum` match the items in `mapping`,
        `False` otherwise.
        """
        ft_language_mappings = set(mapping.items())
        enum_language_mappings = set(
            # Despite being a dunder attribute, `__members__` is a part of the
            # public API as per https://docs.python.org/3/library/enum.html
            enum.__members__.items()
        )
        return ft_language_mappings == enum_language_mappings

    def test_mac_language_id_enum_mappings_match_fonttools(
        self,
        mac_language_code_mapping: LanguageCodeMapping,
    ) -> None:
        """Test if the `MacLanguageID` enum has the same mappings as those
        provided by fontTools.
        """
        assert self._enum_members_match_mapping(
            fr_ot_const.MacLanguageID, mac_language_code_mapping
        )

    def test_windows_language_id_enum_mappings_match_fonttools(
        self,
        windows_language_code_mapping: LanguageCodeMapping,
    ) -> None:
        """Test if the `MacLanguageID` enum has the same mappings as those
        provided by fontTools.
        """
        assert self._enum_members_match_mapping(
            fr_ot_const.WindowsLanguageID, windows_language_code_mapping
        )
