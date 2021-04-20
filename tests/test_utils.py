import collections.abc as col_abc
import functools as ft
import typing as typ

import hypothesis as h
import hypothesis.strategies as h_strats
import pytest

from . import utils
from . import hypothesis_strategies as h_strats_custom
from . import types as test_types


T = typ.TypeVar("T")


IgnoredIterables = typ.Union[str, bytes]
RecursivePrimitives = typ.Union[bool, IgnoredIterables]
IterablePrimitives = typ.Union[RecursivePrimitives, list["IterablePrimitives"]]

recursive_iterables = h_strats.recursive(
    # Use booleans, binary or text to test excluded iterables
    h_strats.one_of(h_strats.booleans(), h_strats.binary(), h_strats.text()),
    ft.partial(h_strats.lists),
)


class TestFlatten:
    """Test the flatten function."""

    @h.given(iterables=recursive_iterables)
    def test_flat_iterable_contains_noniterables_except_excluded(
        self,
        iterables: typ.Collection[IterablePrimitives],
    ) -> None:
        # An iterable is considered flat if it doesn't have any iterables
        # inside of it, except iterables that have been ignored
        for item in utils.flat(iterables):
            assert not (
                isinstance(item, col_abc.Iterable)
                and not isinstance(
                    item, tuple(utils.FLAT_DEFAULT_ATOMIC_ITERABLES)
                )
            )


def _make_literal(x):
    return typ.Literal[x]


class TestIsinstance:
    """Test utilities for patched `isinstance`.

    Since it's impossible to annotate generic `typing.Literal` objects, we
    annotate them as `typing.Literal`, which means any `typing.Literal` object.
    """

    LiteralSupportedTypes = typ.Union[
        None, bool, int, str, list[typ.Union[None, bool, int, str]]
    ]
    _literal_supported_values = h_strats.one_of(
        h_strats.none(),
        h_strats.booleans(),
        h_strats.integers(),
        h_strats.text(),
        h_strats.lists(
            h_strats.booleans() | h_strats.integers() | h_strats.text()
        ),
    )

    # Since static methods cannot be used unbound from the class context, yet
    # `_make_literal` is used often, and is local to the class, bind it to a
    # lambda
    _literals = _literal_supported_values.map(_make_literal)

    @h.given(obj=_literals)
    def test_is_typing_literal_on_literal_returns_true(
        self, obj: test_types.Literal
    ) -> None:
        """Test if calling `is_typing_literal()` on `Literal[val]` returns
        `True`.
        """
        assert utils.is_typing_literal(obj)

    @h.given(
        # Literals are not subclasses of `type`, so this strategy will not
        # generate `Literal`s.
        obj=h_strats.from_type(object)
    )
    def test_is_typing_literal_on_everything_except_literal_returns_false(
        self, obj: object
    ) -> None:
        """Test if calling `is_typing_literal()` on everything except
        `Literal[val]` or `val` returns False.
        """
        assert not utils.is_typing_literal(obj)

    @h.given(
        value=h_strats.shared(
            _literal_supported_values,
            key="test_get_literal_value_equals_original_value",
        ),
    )
    def test_get_literal_value_with_original_value_equal(
        self,
        value: LiteralSupportedTypes,
    ) -> None:
        """Test if `get_literal_value()` returns a value that is equal to the
        value, from which the `literal` has been created.
        """
        literal = _make_literal(value)
        assert utils.get_literal_value(literal) == value

    @h.given(
        value=h_strats.shared(
            _literal_supported_values,
            key="test_get_literal_value_does_not_equal_values_except_original",
        ),
        other_value=h_strats.shared(
            _literal_supported_values,
            key="test_get_literal_value_does_not_equal_values_except_original",
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_get_literal_value_with_values_other_than_original_not_equal(
        self, value: LiteralSupportedTypes, other_value: LiteralSupportedTypes
    ) -> None:
        literal = _make_literal(value)
        assert utils.get_literal_value(literal) != other_value

    @h.given(obj=h_strats.from_type(object))
    def test_get_literal_value_on_non_literals_raises_value_error(
        self, obj: object
    ) -> None:
        with pytest.raises(ValueError):
            # Since we're testing invalid function usage, ignore type checker
            # warnings
            utils.get_literal_value(obj)  # type: ignore

    @h.given(value=_literal_supported_values)
    @h.example(value=None)
    def test_is_value_of_literal_for_matching_value_returns_true(
        self, value: LiteralSupportedTypes
    ) -> None:
        """Test if `is_value_of_literal()` for a literal created from value
        `val` and the value `val` itself return `True`.
        """
        literal = _make_literal(value)
        assert utils.is_value_of_literal(value, literal)

    @h.given(value=_literal_supported_values)
    def test_is_value_of_literal_for_literal_wrapped_in_matching_value_returns_false(  # noqa: line-too-long
        self,
        value: LiteralSupportedTypes,
    ) -> None:
        """Test if `is_value_of_literal()` on two identical literals returns
        `False`.

        Should be `False`, because a literal is not a value of itself.
        """
        literal = _make_literal(value)
        other_literal = _make_literal(value)
        assert not utils.is_value_of_literal(other_literal, literal)

    @h.given(
        val=h_strats.shared(
            _literal_supported_values,
            key="test_get_literal_value_does_not_equal_values_except_original",
        ),
        other_val=h_strats.shared(
            _literal_supported_values,
            key="test_get_literal_value_does_not_equal_values_except_original",
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_is_value_of_literal_does_not_equal_values_except_original(
        self, val: LiteralSupportedTypes, other_val: LiteralSupportedTypes
    ) -> None:
        literal = _make_literal(val)
        assert not utils.is_value_of_literal(other_val, literal)

    @h.given(value=_literal_supported_values)
    def test_is_literal_on_matching_literal_returns_true(
        self,
        value: LiteralSupportedTypes,
    ) -> None:
        """Test if `is_literal()` on matching literals returns `True`."""
        literal1 = _make_literal(value)
        literal2 = _make_literal(value)
        assert utils.is_literal(literal1, literal2) is True

    @h.given(
        reference_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_is_literal_on_literals_with_mismatching_value_returns_"
                "false"
            ),
        ),
        mismatching_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_is_literal_on_literals_with_mismatching_value_returns_"
                "false"
            ),
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_is_literal_on_literals_with_mismatching_value_returns_false(
        self,
        reference_value: LiteralSupportedTypes,
        mismatching_value: LiteralSupportedTypes,
    ) -> None:
        """Test if `is_literal()` on literals with different inner values
        returns `False`."""
        literal1 = _make_literal(reference_value)
        literal2 = _make_literal(mismatching_value)
        assert utils.is_literal(literal1, literal2) is False

    @h.given(literal=_literals, nonliteral=h_strats.from_type(object))
    def test_is_literal_on_literal_and_nonliteral_returns_false(
        self, literal: test_types.Literal, nonliteral: object
    ) -> None:
        """Test if `is_literal()` on literal and a nonliteral returns `False`."""
        assert utils.is_literal(nonliteral, literal) is False

    @h.given(original_value=_literal_supported_values)
    def test_isinstance_literal_on_original_value_returns_true(
        self,
        original_value: LiteralSupportedTypes,
    ) -> None:
        literal = _make_literal(original_value)
        assert utils.isinstance_literal(original_value, literal) is True

    @h.given(
        original_value=h_strats.shared(
            _literal_supported_values,
            key="test_isinstance_literal_on_mismatching_values_returns_false",
        ),
        mismatching_value=h_strats.shared(
            _literal_supported_values,
            key="test_isinstance_literal_on_mismatching_values_returns_false",
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_isinstance_literal_on_literal_and_mismatching_value_returns_false(
        self,
        original_value: LiteralSupportedTypes,
        mismatching_value: LiteralSupportedTypes,
    ) -> None:
        """Test if `isinstance_literal()` on a literal and a value that does
        not match the value that is wrapped in a literal returns `False`.
        """
        literal = _make_literal(original_value)
        assert utils.isinstance_literal(mismatching_value, literal) is False

    @h.given(
        original_value=h_strats.shared(
            _literal_supported_values,
            key="test_isinstance_literal_on_mismatching_values_returns_false",
        ),
        mismatching_value=h_strats.shared(
            _literal_supported_values,
            key="test_isinstance_literal_on_mismatching_values_returns_false",
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_isinstance_literal_on_literals_with_mismatching_values_returns_false(  # noqa: line-too-long
        self,
        original_value: LiteralSupportedTypes,
        mismatching_value: LiteralSupportedTypes,
    ) -> None:
        """Test if `isinstance_literal()` on value that does not match the
        value that is wrapped in a literal returns `False`.
        """
        literal1 = _make_literal(original_value)
        literal2 = _make_literal(mismatching_value)
        assert utils.isinstance_literal(literal2, literal1) is False

    @h.given(
        value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance_literal_on_literal_and_nonliteral_returns_"
                "false"
            ),
        ),
        nonliteral=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance_literal_on_literal_and_nonliteral_returns_"
                "false"
            ),
        ).flatmap(h_strats_custom.everything_except_value),
    )
    def test_isinstance_literal_on_literal_and_nonliteral_returns_false(
        self,
        value: LiteralSupportedTypes,
        nonliteral: object,
    ) -> None:
        """Test if `isinstance_literal()` on a literal and a non-literal object
        returns `False`.
        """
        literal = _make_literal(value)
        assert utils.isinstance_literal(nonliteral, literal) is False

    @h.given(value=_literal_supported_values)
    def test_isinstance__on_literal_and_matching_value_returns_true(
        self,
        value: LiteralSupportedTypes,
    ) -> None:
        """Test if `isinstance_()` when checking if `value` is an instance of a
        literal that wraps `value` returns `True`.
        """
        literal = _make_literal(value)
        assert utils.isinstance_(value, literal) is True

    @h.given(value=_literal_supported_values)
    def test_isinstance__on_literals_with_matching_values_returns_true(
        self,
        value: test_types.LiteralValue,
    ) -> None:
        """Test if `isinstance_()` on two literals with the same inner value
        returns `True`.
        """
        literal1 = _make_literal(value)
        literal2 = _make_literal(value)
        assert utils.isinstance_(literal1, literal2) is True

    @h.given(
        value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_value_and_literal_with_other_value_"
                "returns_false"
            ),
        ),
        other_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_value_and_literal_with_other_value_"
                "returns_false"
            ),
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_isinstance__on_value_and_literal_with_other_value_returns_false(
        self,
        value: test_types.LiteralValue,
        other_value: test_types.LiteralValue,
    ) -> None:
        """Test if `isinstance_(value, Literal[other_value])` returns `False`."""
        literal = _make_literal(other_value)
        assert utils.isinstance_(value, literal) is False

    @h.given(
        value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_literals_with_mismatching_values_"
                "returns_false"
            ),
        ),
        other_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_literals_with_mismatching_values_"
                "returns_false"
            ),
        ).flatmap(lambda x: h_strats_custom.same_type_but_not([x])),
    )
    def test_isinstance__on_literals_with_mismatching_values_returns_false(
        self,
        value: test_types.LiteralValue,
        other_value: test_types.LiteralValue,
    ) -> None:
        """Test if `isinstance_()` on literals with mismatching values returns
        `False`.
        """
        literal1 = _make_literal(value)
        literal2 = _make_literal(other_value)
        assert utils.isinstance_(literal1, literal2) is False

    @h.given(
        reference_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_everything_except_reference_returns_false"
            ),
        ),
        other_value=h_strats.shared(
            _literal_supported_values,
            key=(
                "test_isinstance__on_everything_except_reference_returns_false"
            ),
        ).flatmap(h_strats_custom.everything_except_value),
    )
    def test_isinstance__on_everything_except_reference_returns_false(
        self,
        reference_value: test_types.LiteralValue,
        other_value: typ.Any,
    ) -> None:
        """Test if `isinstance_(other_value, Literal[reference_value])` is
        `False`, where `other_value != reference_value` and can be of any type.
        """
        literal = _make_literal(reference_value)
        assert utils.isinstance_(other_value, literal) is False

    @h.given(
        # Generate a type
        obj_type=h_strats.shared(
            h_strats.from_type(type),
            key=(
                "test_isinstance__on_nonliteral_type_and_matching_object_"
                "returns_true"
            ),
        ),
        # And instantiate an object of this type
        obj=h_strats.shared(
            h_strats.from_type(type),
            key=(
                "test_isinstance__on_nonliteral_type_and_matching_object_"
                "returns_true"
            ),
        ).flatmap(h_strats.from_type),
    )
    def test_isinstance__on_nonliteral_type_and_matching_object_returns_true(
        self,
        obj_type: type[T],
        obj: T,
    ) -> None:
        assert utils.isinstance_(obj, obj_type) is True

    @h.given(
        # Generate a shared type `T`
        obj_type=h_strats.shared(
            h_strats.from_type(type),
            key=(
                "test_isinstance__on_nonliteral_type_and_object_of_"
                "mismatching_type_returns_false"
            ),
        ),
        # Consume the same shared type `T`
        obj_of_mismatched_type=h_strats.shared(
            h_strats.from_type(type),
            key=(
                "test_isinstance__on_nonliteral_type_and_object_of_"
                "mismatching_type_returns_false"
            ),
        )
        # Generate type `S` that is not the shared type `T`
        .flatmap(lambda x: h_strats.from_type(type).filter(lambda y: x != y))
        # Create an object from type `S`
        .flatmap(h_strats.from_type),
    )
    def test_isinstance__on_nonliteral_type_and_object_of_mismatching_type_returns_false(  # noqa: line-too-long
        self,
        obj_type: type,
        obj_of_mismatched_type: object,
    ) -> None:
        """Test if `isinstance_()` on non-literal type and an object of
        mismatching type returns `False`.

        Intended to check if the instance check for non-literal types is
        dispatched to the built-in `isinstance()`.
        """
        assert utils.isinstance_(obj_of_mismatched_type, obj_type) is False
