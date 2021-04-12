"""Facilities for mapping name records."""
import abc
import dataclasses as dc
import functools
import types
import typing as typ

import immutables as im
import font_renamer.opentype_name_constants as fr_const
import font_renamer.platforms as fr_platforms


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


class PLanguageToLanguageInfoMapper(typ.Protocol):
    """Interface for language to language information mappers."""

    @functools.singledispatchmethod
    @abc.abstractmethod
    def get_language_info(
        self,
        language_code: str,
        *,
        platform: typ.Optional[typ.Union[fr_const.PlatformID, str]],
    ) -> typ.Union[LanguageInfo, typ.Sequence[LanguageInfo]]:
        """Return platform-specific name records.

        Accepts a keyword-only argument `platform` either as an ID or a string
        name that returns a single platform-specific name record.
        """
        raise NotImplementedError

    @get_language_info.register
    @abc.abstractmethod
    def _(  # type: ignore
        self,
        language_code: str,
        *,
        platform: typ.Literal[None],
    ) -> typ.Sequence[LanguageInfo]:
        raise NotImplementedError

    @get_language_info.register
    def _(  # type:ignore
        self,
        language_code: str,
        *,
        platform: fr_const.PlatformID,
    ) -> LanguageInfo:
        raise NotImplementedError

    @get_language_info.register
    def _(  # type: ignore
        self,
        language_code: str,
        *,
        platform: str,
    ) -> LanguageInfo:
        raise NotImplementedError


class LanguageInfoMapper(PLanguageToLanguageInfoMapper):
    """Concrete language to language information mapper."""

    def __init__(
        self,
        platforms: typ.Sequence[fr_platforms.LanguageMappedPlatform] = None,
    ) -> None:
        self._platforms = platforms if platforms else fr_platforms.PLATFORMS

    @functools.cached_property
    def _platforms_by_id(
        self,
    ) -> typ.Mapping[fr_const.PlatformID, fr_platforms.LanguageMappedPlatform]:
        """Return a read-only mapping of platform names to instances."""
        return im.Map({p.platform_id: p for p in self._platforms})

    @functools.cached_property
    def _platforms_by_name(
        self,
    ) -> typ.Mapping[str, fr_platforms.LanguageMappedPlatform]:
        """Return a read-only mapping of platform names to instances."""
        return im.Map({p.name: p for p in self._platforms})

    @functools.singledispatchmethod
    def get_language_info(self, language_code, *, platform):
        """Entry point for single dispatch."""
        raise NotImplementedError("Unrecognized argument types.")

    @get_language_info.register
    def _(  # type: ignore
        self,
        language_code: str,
        *,
        platform: typ.Literal[None] = None,
    ) -> typ.Sequence[LanguageInfo]:
        language_info = tuple(
            LanguageInfo(
                p.platform_id,
                p.get_language_id(language_code),
                p.get_platform_encoding_id(language_code),
            )
            for p in self._platforms.values()
        )

        return language_info

    @get_language_info.register
    def _(
        self,
        language_code: str,
        *,
        platform: fr_const.PlatformID,
    ) -> LanguageInfo:
        target_platform = self._platforms_by_id[platform]
        return LanguageInfo(
            target_platform.platform_id,
            target_platform.get_language_id(language_code),
            target_platform.get_platform_encoding_id(language_code),
        )
