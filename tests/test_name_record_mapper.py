"""Tests for the name record mapper.
"""
import typing as typ

import hypothesis as h
import hypothesis.strategies as h_strats
import pytest

import font_renamer.name_record_mapper as fr_nrm
import font_renamer.opentype_name_constants as ot_const
import font_renamer.platforms as fr_platforms

from . import hypothesis_strategies as h_strats_custom


class TestPLanguageToLanguageInfoMapper:
    """Test the interface for the name record mapper."""

    def test_init_raises_type_error(self) -> None:
        """Test if init raises a `TypeError`."""
        with pytest.raises(TypeError):
            fr_nrm.PLanguageToLanguageInfoMapper()


class TestLanguageMapper:
    """Tests the language mapper."""

    def test_init_empty_args_ok_uses_default_platforms(self) -> None:
        """Test if init with empty arguments uses the default platforms."""
        mapper = fr_nrm.LanguageInfoMapper()
        assert mapper
        assert fr_platforms.WINDOWS_PLATFORM in mapper._platforms
        assert fr_platforms.MAC_PLATFORM in mapper._platforms
        assert mapper._platforms == fr_platforms.PLATFORMS

    @staticmethod
    def _test_mapping_set_properly(
        mapping: typ.Mapping[typ.Any, fr_platforms.LanguageMappedPlatform],
        mapping_key: str,
        should_contain: typ.Iterable[fr_platforms.LanguageMappedPlatform],
    ) -> None:
        """Helper static method for testing private mappings."""
        # Check if the mapping contains all expected values
        assert set(should_contain) == set(mapping.values())

        # Check if keys correspond to the proper values (platforms)
        # For example, in a {`PlatformID`: `LanguageMappedPlatform`} mapping, a
        # specific key should match the platform ID of its value. Same for
        # `name` -> `LanguageMappedPlatform`.
        for key, platform in mapping.items():
            assert key == getattr(platform, mapping_key)

    def test_nonparametrized_init_properly_inits_platforms(self) -> None:
        """Test if a non-parametrized init properly assigns platforms and
        creates private mappings such as `self._platforms_by_name`.
        """
        mapper = fr_nrm.LanguageInfoMapper()
        assert set(mapper._platforms) == set(fr_platforms.PLATFORMS)
        assert mapper._platforms_by_name
        assert mapper._platforms_by_id

        for mapping, mapping_key in zip(
            (mapper._platforms_by_id, mapper._platforms_by_name),
            ("platform_id", "name"),
        ):
            self._test_mapping_set_properly(
                mapping, mapping_key, fr_platforms.PLATFORMS
            )

    def test_get_language_info_supported_language_code_returns_proper_info(
        self,
        default_language_info_mapper: fr_nrm.LanguageInfoMapper,
    ) -> None:
        mapper = default_language_info_mapper
        # Build a set of language codes that are supported by every platform in
        # the mapper
        language_codes_supported_on_every_platform = set()
        for platform in mapper._platforms:
            language_codes_supported_on_every_platform &= set(
                platform.language_ids.keys()
            )

        # Check that every universally supported language produces a valid
        # result
        for lc in language_codes_supported_on_every_platform:
            platform_language_infos = mapper.get_language_info(lc)
            assert platform_language_infos
            assert len(platform_language_infos) == len(mapper._platforms)
            for language_info in platform_language_infos:
                platform = mapper._platforms_by_id[language_info.platform_id]
                assert language_info.language_id == platform.language_ids[lc]
                assert (
                    language_info.platform_encoding_id
                    == platform.platform_encoding_ids[lc]
                )

            assert platform_language_infos

    # TODO: test if trying to get language info by language codes that are
    # supported by some platforms, but not all, raises an exception

    @h.given(
        platform=h_strats.shared(
            h_strats_custom.supported_language_mapped_platforms,
            key="test_get_language_info_by_code_returns_proper_info",
        ),
        language_code=h_strats.shared(
            h_strats_custom.supported_language_mapped_platforms,
            key="test_get_language_info_by_code_returns_proper_info",
        ).flatmap(
            lambda x: h_strats.sampled_from(sorted(x.language_ids.keys()))
        ),
    )
    def test_get_language_info_by_code_on_supported_platform_returns_proper_info(
        self,
        default_language_info_mapper: fr_nrm.LanguageInfoMapper,
        platform: fr_platforms.LanguageMappedPlatform,
        language_code: str,
    ) -> None:
        """Test if `get_language_info` by language code with a supported
        platform returns proper corresponding language information.
        """
        mapper = default_language_info_mapper
        language_info = mapper.get_language_info(
            language_code,
            platform=platform.platform_id,
        )
        assert language_info

    @h.given(
        platform=h_strats.from_type(fr_platforms.LanguageMappedPlatform),
        language_code=h_strats.text(),
    )
    def test_get_language_info_by_code_unsupported_code_raises_UnsupportedLanguageCodeError(
        self,
        default_language_info_mapper: fr_nrm.LanguageInfoMapper,
        platform: fr_platforms.LanguageMappedPlatform,
        language_code: str,
    ) -> None:
        """Test if `get_language_info` by language code when a language code is
        unsupported raises an `UnsupportedLanguageCodeError`.
        """
        mapper = default_language_info_mapper
        target_platform = mapper._platforms_by_id[platform.platform_id]
        h.assume(language_code not in target_platform.language_ids.keys())

        mapper = default_language_info_mapper
        with pytest.raises(fr_platforms.UnsupportedLanguageCodeError):
            mapper.get_language_info(
                language_code,
                platform=platform.platform_id,
            )

    @h.given(
        platform=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            key="test_get_language_info_by_platform_name_returns_proper_info",
        ),
        language_code=h_strats.shared(
            h_strats.from_type(fr_platforms.LanguageMappedPlatform),
            key="test_get_language_info_by_platform_name_returns_proper_info",
        ).flatmap(
            lambda x: h_strats.sampled_from(sorted(x.language_ids.keys()))
        ),
    )
    def test_get_language_info_by_platform_name_returns_proper_info(
        self,
        default_language_info_mapper: fr_nrm.LanguageInfoMapper,
        platform: fr_platforms.LanguageMappedPlatform,
        language_code: str,
    ) -> None:
        """Test if `get_language_info` by language code and platform name
        returns proper information.
        """
        mapper = default_language_info_mapper
        platform_name = platform.name
        language_info = mapper.get_language_info(
            language_code=language_code,
            platform=platform_name,
        )
        assert language_info
