"""Custom Hypothesis strategies for generating test data."""
import collections.abc as col_abc
import typing as typ
import logging

import hypothesis.strategies as h_strats

import font_renamer.opentype_name_constants as ot_const
import font_renamer.platforms as fr_platforms

from . import types as tt
from . import utils


T = typ.TypeVar("T")


@h_strats.composite
def same_type_but_not(
    draw,
    excluded_values: typ.Sequence[T],
) -> T:
    """Return values of the same type as `excluded_values`, but not values in
    `excluded_values`.
    """
    try:
        example_value = excluded_values[0]
    except IndexError:
        raise ValueError(
            f"Excluded values cannot be empty. Got: {excluded_values}"
        )

    matching_type_strategy = h_strats.from_type(type(example_value))
    strategy_except_values = matching_type_strategy.filter(
        lambda x: x not in excluded_values
    )
    return draw(strategy_except_values)


def everything_except_value(*excluded_values) -> h_strats.SearchStrategy:
    """Return a strategy that returns valid values of every type except values
    in `excluded_values`.
    """
    return (
        h_strats.from_type(type)
        .flatmap(h_strats.from_type)
        .filter(lambda x: x not in excluded_values)
    )


def everything_except(
    *excluded_types: type, exclude_superclasses=False
) -> h_strats.SearchStrategy:
    """Return a strategy that returns valid values of every type except those
    in `excluded_types`.

    Args:
        *excluded_types: types, instances of which will be excluded from
        output.
        exclude_superclasses: exclude instances of superclasses of excluded
        types?
    """

    def tmp(x):
        print(
            f'Texting object "{x}" of type {type(x)} against {excluded_types}'
        )
        return (
            exclude_superclasses
            and not utils.issubclass_(type(x), excluded_types)
        ) or not utils.isinstance(x, excluded_types)

    return (
        h_strats.from_type(type).flatmap(h_strats.from_type)
        # .filter(lambda x: not _isinstance(x, excluded_types))
        .filter(tmp)
    )


@h_strats.composite
def valid_init_args_for(draw, cls: type) -> col_abc.Mapping[str, typ.Any]:
    """Return arguments that are considered valid for initializing an instance
    of `cls`.
    """
    return {
        arg_name: draw(h_strats.from_type(arg_type))
        for arg_name, arg_type in _get_type_hints_or_raise(cls).items()
    }


@h_strats.composite
def invalid_init_args_for(
    draw, cls: type, exclude_superclasses=False
) -> col_abc.Mapping[str, typ.Any]:
    """Return arguments that are considered invalid for initializing an
    instance of `cls`.

    Class `cls` must be type-annotated.
    """
    type_hints = _get_type_hints_or_raise(cls)
    if not type_hints:
        raise ValueError(f"Class {cls} is not type-annotated.")

    # At least one generated argument has to be invalid
    target_invalid_args_count = draw(
        h_strats.integers(min_value=1, max_value=len(type_hints))
    )

    final_args = {}
    added_invalid_args_count = 0
    invalid_args = {}
    for arg_name, arg_type in type_hints.items():
        if added_invalid_args_count < target_invalid_args_count:
            val = draw(
                everything_except(
                    arg_type, exclude_superclasses=exclude_superclasses
                )
            )
            added_invalid_args_count += 1
            invalid_args[arg_name] = val
        else:
            val = draw(h_strats.from_type(arg_type))
        final_args[arg_name] = val

    logging.warn(f"Invalid args: {invalid_args}")
    return final_args
