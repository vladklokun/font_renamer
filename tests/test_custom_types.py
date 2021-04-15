"""Tests for custom types defined for domain models."""
import typing as typ

import hypothesis as h
import hypothesis.strategies as h_strats
import pydantic as pyd
import pytest

import font_renamer.types as fr_types


class TestContainedType:
    @h.given(
        type_=h_strats.sampled_from(
            sorted(fr_types._SUPPORTED_CONTAINED_TYPES, key=lambda x: str(x))
        ),
    )
    def test_class_factory_supported_types_returns_subclasses_implementors_of_pcontainedtype(
        self,
        type_: type,
        # container: col_abc.Container,
    ) -> None:
        cls = fr_types.contained_type(type_, tuple())

        # pyright complains that `PContainedType` is incompatible with `type`,
        # but any implementor of the interface is guaranteed to be a subclass
        # of `type`
        assert issubclass(typ.cast(type, cls), type_)
        assert isinstance(cls, fr_types.PContainedType)

    @h.given(container=h_strats.sets(h_strats.text()))
    def test_validator_of_class_factory_created_class_accepts_valid_values(
        self,
        container: typ.Collection[str],
    ) -> None:
        """Test if the validator of a contained class created by a class
        factory accepts valid values.
        """
        contained_cls = fr_types.contained_type(str, container)
        validators = tuple(v for v in contained_cls.__get_validators__())
        for e in container:
            for v in validators:
                v(e)

    @h.given(
        container=h_strats.sets(h_strats.text()),
        invalid_value=h_strats.text(),
    )
    def test_class_factory_raises_on_noncontained_values(
        self,
        container: typ.Collection[str],
        invalid_value: str,
    ) -> None:
        h.assume(invalid_value not in container)
        contained_cls = fr_types.contained_type(str, container)
        validators = tuple(v for v in contained_cls.__get_validators__())
        with pytest.raises(ValueError):
            for v in validators:
                v(invalid_value)

    @h.given(container=h_strats.sets(h_strats.text()))
    def test_pydantic_model_class_accepts_valid_contained_values(
        self,
        container: typ.Collection[str],
    ) -> None:
        class Model(pyd.BaseModel):
            # pyright complains about `illegal call expression in type
            # annotation`, however, this is a conventional API for constrained
            # types in pydantic
            contained_field: fr_types.contained_type(str, container)  # type: ignore # noqa: line-too-long

        for value in container:
            Model(contained_field=value)

    @h.given(
        container=h_strats.sets(h_strats.text()), invalid_value=h_strats.text()
    )
    def test_pydantic_model_class_invalid_contained_value_raises_value_error(
        self,
        container: typ.Collection[str],
        invalid_value: str,
    ) -> None:
        h.assume(invalid_value not in container)

        class Model(pyd.BaseModel):
            contained_field: fr_types.contained_type(str, container)  # type: ignore # noqa: line-too-long

        with pytest.raises(pyd.ValidationError):
            Model(contained_field=invalid_value)
