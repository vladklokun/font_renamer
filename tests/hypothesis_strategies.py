"""Custom Hypothesis strategies for generating test data."""
import typing as typ

import hypothesis.strategies as hyp_strats

import font_renamer.opentype_name_constants as ot_const
import font_renamer.platforms as fr_platforms

from . import types as tt


def strategy_for_type(type_: typ.Type) -> typ.Callable:
    """Register the decorated function as a strategy for a given type.

    Used as a declarative alternative to Hypothesis'
    `register_type_strategy()`.

    TODO: use `inspect.getfullargspec()` to infer the return type. Make
    arguments to decorator optional.
    """

    def decorator(strategy: typ.Callable) -> typ.Callable:
        hyp_strats.register_type_strategy(type_, strategy())
        # Since we don't modify the behavior of the decorated function, return
        # it as-is
        return strategy

    return decorator


supported_platform_ids: hyp_strats.SearchStrategy[
    ot_const.PlatformID
] = hyp_strats.sampled_from(
    # Select a supported platform
    sorted(fr_platforms.PLATFORMS, key=lambda x: x.platform_id)
).map(
    # And use its PlatformID
    lambda x: x.platform_id
)

# Generates language codes that are supported on all platforms
supported_language_codes_all_platforms: hyp_strats.SearchStrategy[
    str
] = hyp_strats.sampled_from(
    sorted(
        set(fr_platforms._WINDOWS_LANGUAGE_IDS.keys())
        & set(fr_platforms._MAC_LANGUAGE_IDS.keys())
    )
)

# Returns a supported language-mapped platform
supported_language_mapped_platforms: hyp_strats.SearchStrategy[
    fr_platforms.LanguageMappedPlatform
] = hyp_strats.sampled_from(
    sorted(fr_platforms.PLATFORMS, key=lambda x: x.platform_id)
)
hyp_strats.register_type_strategy(
    fr_platforms.LanguageMappedPlatform, supported_language_mapped_platforms
)


@hyp_strats.composite
def name_record_tuples_valid(draw) -> tt.NameRecordTupleValid:
    """Return tuples that are valid arguments for instantiating `NameRecord`s."""
    # Generate independent values
    string = draw(hyp_strats.text())
    name_id = draw(hyp_strats.sampled_from(ot_const.NameID))

    # Generate values that depend on a platform convention
    platform = draw(
        hyp_strats.sampled_from(
            sorted(fr_platforms.PLATFORMS, key=lambda x: x.name)
        )
    )
    platform_id = platform.platform_id
    platform_encoding_id = draw(
        hyp_strats.sampled_from(sorted(platform.valid_platform_encoding_ids))
    )
    language_id = draw(
        hyp_strats.sampled_from(sorted(platform.valid_language_ids))
    )
    return tt.NameRecordTupleValid(
        string=string,
        name_id=name_id,
        platform_id=platform_id,
        platform_encoding_id=platform_encoding_id,
        language_id=language_id,
    )


def everything_of_type_not_in(
    target_type: typ.Type[typ.Any], excluded_values: typ.Container[typ.Any]
) -> hyp_strats.SearchStrategy:
    """Return a strategy that provides values except those that are in
    `excluded_values`.
    """
    return hyp_strats.from_type(target_type).filter(
        lambda x: x not in excluded_values
    )


@hyp_strats.composite
def name_record_tuples_invalid(draw) -> tt.NameRecordTupleMaybe:
    """Return tuples that are NOT valid arguments for instanting `NameRecord`s."""
    # TODO: implement generation of instances where at least one parameter is
    # invalid, so we can parse name records properly

    def is_invalid_utf8(bytestr: bytes) -> bool:
        """Check if the provided byte stream cannot be decoded as a valid utf8
        string.
        """
        try:
            bytestr.decode()
        except UnicodeDecodeError:
            return True
        return False

    name_string = draw(hyp_strats.binary().filter(is_invalid_utf8))
    name_id = draw(everything_of_type_not_in(int, tuple(ot_const.NameID)))

    platform_convention = draw(
        hyp_strats.sampled_from(
            sorted(fr_platforms.PLATFORMS, key=lambda x: x.name)
        )
    )
    platform_id = platform_convention.platform_id
    platform_encoding_id = draw(
        everything_of_type_not_in(
            int, tuple(platform_convention.valid_platform_encoding_ids)
        )
    )
    language_id = draw(
        everything_of_type_not_in(
            int, tuple(platform_convention.valid_language_ids)
        )
    )

    return tt.NameRecordTupleMaybe(
        string=name_string,
        name_id=name_id,
        platform_id=platform_id,
        platform_encoding_id=platform_encoding_id,
        language_id=language_id,
    )
