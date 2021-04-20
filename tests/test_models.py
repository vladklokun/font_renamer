"""Tests for domain models."""
import collections.abc as col_abc
import typing as typ

import hypothesis as h
import hypothesis.strategies as h_strats
import pytest
import pydantic as pyd

import font_renamer.models as fr_models
import font_renamer.opentype_name_constants as fr_ot_const

from . import hypothesis_strategies as h_strats_custom


class TestNameRecord:
    """Test the base protocol class."""

    def test_name_record_init_raises_TypeError(self) -> None:
        """Test if attempts to init a protocol class raise."""
        with pytest.raises(TypeError) as exc_info:
            fr_models.PNameRecord()
            assert "Protocols cannot be instantiated" in exc_info.exconly(
                tryshort=True
            )


class TestMacNameRecord:
    """Test the Mac name record."""

    @h.given(
        init_args=h_strats_custom.valid_init_args_for(fr_models.MacNameRecord)
    )
    def test_name_record_valid_data_init_ok(
        self,
        init_args: col_abc.Mapping[str, typ.Any],
    ) -> None:
        """Test if init with valid arguments is ok."""
        nr = fr_models.MacNameRecord(**init_args)
        assert nr
        assert isinstance(nr.string, str)
        assert isinstance(nr.platform_id, fr_ot_const.PlatformID)
        assert isinstance(
            nr.platform_encoding_id, fr_ot_const.MacPlatformEncodingID
        )
        assert isinstance(nr.language_id, fr_ot_const.MacLanguageID)

    @h.given(
        invalid_init_args=h_strats_custom.invalid_init_args_for(
            fr_models.MacNameRecord,
            exclude_superclasses=True,
        ),
    )
    def test_invalid_name_record_raises_any_exception(
        self,
        invalid_init_args: col_abc.Mapping[str, typ.Any],
    ) -> None:
        """Test if init with invalid arguments raises an Exception.

        Since invalid data types can produce unexpected exceptions, such as
        `decimal.InvalidOperation`, we need to catch a base for user-defined
        --- `Exception`.
        """
        with pytest.raises(Exception):
            fr_models.MacNameRecord(**invalid_init_args)
