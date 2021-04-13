"""Tests for facilities defined to be used with constants."""
import dataclasses as dc

import hypothesis as h
import hypothesis.strategies as h_strats
import pytest

import font_renamer.platforms as fr_platforms


class TestLanguageMappedPlatform:
    """Tests instances of platforms with language mappings attached."""

    @h.given(
        # We need to check valid platform instances with language codes that
        # are supported by a given instance. Therefore, to minimize the
        # search space of supported language codes, it makes sense to use the
        # instance itself as a source of supported language codes.
        #
        # To do this, we need to share the platform instance drawn from the
        # platform generation strategy with the language code generation
        # strategy, and draw a language code from the shared platform instance.
        platform=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            # Ensure that examples from the strategy are shared by using an
            # explicit key
            key="shared_platform",
        ),
        lang_code=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            key="shared_platform",
        ).flatmap(
            lambda x: h_strats.sampled_from(sorted(x.language_ids.keys()))
        ),
    )
    def test_get_language_id_existing_lang_code_returns_valid_language_id(
        self,
        platform: fr_platforms.LanguageMappedPlatform,
        lang_code: str,
    ) -> None:
        """Test if `get_language_id()` with a supported language code returns
        a valid language ID.
        """
        language_id = platform.get_language_id(lang_code)
        assert isinstance(language_id, int)
        assert platform.language_ids[lang_code] == language_id

    @h.given(
        platform=h_strats.from_type(fr_platforms.LanguageMappedPlatform),
        lang_code=h_strats.text(),
    )
    def test_get_language_id_missing_lang_code_raises_UnsupportedLanguageCodeError(  # noqa: E501
        self,
        platform: fr_platforms.LanguageMappedPlatform,
        lang_code: str,
    ) -> None:
        """Test if `get_language_id()` with an unsupported language code raises
        an `UnsupportedLanguageCodeError`.
        """
        # Only use language codes that are not supported by the platform
        h.assume(lang_code not in platform.language_ids.keys())

        with pytest.raises(fr_platforms.UnsupportedLanguageCodeError):
            platform.get_language_id(lang_code)

    @h.given(
        # Since we need to test attributes specific to the instance of a
        # platform, we have to share it...
        instance=h_strats.shared(
            h_strats.sampled_from(
                sorted(fr_platforms.PLATFORMS, key=lambda x: x.name)
            ),
            key="test_attr_assignment",
        ),
        # ...and extract a list of attributes on which assignment will be
        # tested
        attribute_name=h_strats.shared(
            h_strats.sampled_from(
                sorted(fr_platforms.PLATFORMS, key=lambda x: x.name)
            ),
            key="test_attr_assignment",
        ).flatmap(lambda x: h_strats.sampled_from(sorted(vars(x).keys()))),
    )
    def test_constant_platform_attribute_assignment_raises_FrozenInstanceError(
        self,
        instance: fr_platforms.LanguageMappedPlatform,
        attribute_name: str,
    ) -> None:
        """Tests if assignment to a language mapped platform raises
        `FrozenInstanceError`.

        Platfroms defined as constants should not be mutable after
        instantiation. This test ensures that a user cannot mutate platform
        data.
        """
        with pytest.raises(dc.FrozenInstanceError):
            setattr(instance, attribute_name, None)


class TestGetLanguageInfo:
    """Test suite for the `get_language_info` function."""

    @h.given(
        platform=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            key="test_supported_language_code_returns_correct_language_info",
        ),
        language_code=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            key="test_supported_language_code_returns_correct_language_info",
        ).flatmap(
            lambda p: h_strats.sampled_from(sorted(p.language_ids.keys()))
        ),
    )
    def test_supported_language_code_returns_correct_language_info(
        self,
        platform: fr_platforms.LanguageMappedPlatform,
        language_code: str,
    ) -> None:
        """Test if calling with a `language_code` supported by `platform`
        returns correct `LanguageInfo`.

        Language info `li` is considered correct if:
            - `li.platform_id` matches the `platform`'s own
              `platform_id`.
            - `li.language_id` matches the value provided by the
              `platform`.
            - `li.platform_encoding_id` matches the value for `language_code`
              provided by the `platform`.
        """
        language_info = fr_platforms.get_language_info(platform, language_code)
        assert isinstance(language_info, fr_platforms.LanguageInfo)
        assert language_info.platform_id == platform.platform_id
        assert language_info.language_id == platform.get_language_id(
            language_code
        )
        assert (
            language_info.platform_encoding_id
            == platform.get_platform_encoding_id(language_code)
        )

    @h.given(
        platform=h_strats.from_type(fr_platforms.LanguageMappedPlatform),
        language_code=h_strats.text()
    )
    def test_unsupported_language_code_raises(
        self,
        platform: fr_platforms.LanguageMappedPlatform,
        language_code: str
    ) -> None:
        """Test if calling with a `language_code` NOT supported by `platform`
        raises `UnsupportedLanguageCodeError`.
        """

        h.assume(language_code not in platform.language_ids.keys())
        with pytest.raises(fr_platforms.UnsupportedLanguageCodeError):
            fr_platforms.get_language_info(platform, language_code)
