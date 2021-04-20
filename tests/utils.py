"""Miscellaneous utilities for testing.

Used either in writing tests or defining Hypothesis strategies.
"""
import collections.abc as col_abc
import enum
import typing as typ

from . import types as test_types


FLAT_DEFAULT_ATOMIC_ITERABLES: typ.List[type] = [str, bytes, enum.EnumMeta]


def flat(
    *inputs: typ.Union[col_abc.Iterable, typ.Any],
    atomic_types: typ.Optional[col_abc.Collection[type]] = None,
) -> typ.Generator[typ.Any, None, None]:
    """Yield elements of flattened `iterables`.

    Primitive iterables, such as `str` and `bytes` are not flattened and
    yielded as-is.

    Raises:
        RecursionError: if `iterables` are too nested.
    """
    atomic_types = (
        atomic_types
        if atomic_types is not None
        else FLAT_DEFAULT_ATOMIC_ITERABLES
    )
    for item in inputs:
        if isinstance(item, col_abc.Iterable) and not isinstance(
            item, tuple(atomic_types)
        ):
            yield from flat(*item)
        else:
            yield item


def is_typing_literal(obj: typ.Any) -> bool:
    """Return `True` if `obj` is a `typing.Literal`, otherwise False."""
    return typ.get_origin(obj) == typ.Literal


def get_literal_value(literal: test_types.Literal) -> test_types.LiteralValue:
    """Return the actual value wrapped in a `literal`.

    Raises:
        ValueError: if `literal` is not actually a `typing.Literal`.
    """
    if not is_typing_literal(literal):
        raise ValueError(
            f"Only literals are supported. Got <{literal}> instead."
        )
    args = typ.get_args(literal)
    if len(args) > 1:
        return list(args)
    else:
        return args[0]


def is_value_of_literal(obj: object, literal: test_types.Literal) -> bool:
    """Return `True` if `obj` is a value of `literal`, `False` otherwise."""
    literal_value = get_literal_value(literal)
    return type(obj) == type(literal_value) and obj == literal_value


def is_literal(obj: object, literal: test_types.Literal) -> bool:
    """Return `True` if `obj` is the typing literal `literal`.

    Raises:
        ValueError: if `literal` is not a `typing.Literal`.
    """
    if not is_typing_literal(literal):
        raise ValueError(f"Argument {literal} is not a Literal.")

    return is_typing_literal(obj) and get_literal_value(
        # After the first conditional `obj` is established to be a
        # `typing.Literal`, and is suitable to be an argument of
        # `get_literal_value()`
        typ.cast(test_types.Literal, obj)
    ) == get_literal_value(literal)


def isinstance_literal(obj: object, literal: test_types.Literal) -> bool:
    """Return `True` if `obj` is an instance of `literal`.

    Where `literal` is any `Literal` type hint. This is needed, since
    `isinstance` does not work with `Literal` types.

    An object is considered to be an instance of a literal if IS the `literal`
    itself or if `obj` is the inner value of a literal.
    """
    return is_value_of_literal(obj, literal) or is_literal(obj, literal)


def isinstance_(
    obj: object,
    type_spec: typ.Union[
        type,
        tuple[typ.Union[type, tuple[typ.Any, ...]], ...],
        test_types.Literal,
    ],
) -> bool:
    """Check if `obj` is an instance of `type_spec`.

    Argument `type` can be a `typing.Literal`.
    """
    if is_typing_literal(type_spec):
        # Since the built-in `isinstance` does not support checking `obj`
        # against a `typing.Literal`, dispatch a special function to handle
        # them.
        # TODO: since `type_spec` can be recursive, and one of the leaves can
        # contain a literal, check for literals recursively
        return isinstance_literal(
            obj,
            # if condition ensures `type` is a literal
            typ.cast(test_types.Literal, type_spec),
        )
    else:
        # Fall back on the built-in in all other cases
        return isinstance(obj, type_spec)


def get_type_hints_or_raise(cls: type) -> typ.Mapping[str, type]:
    """Return type hints for `cls` or raise `ValueError`."""
    hints = typ.get_type_hints(cls)
    if not hints:
        raise ValueError(f"Class {cls} does not provide type hints.")
    return hints
