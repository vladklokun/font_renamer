"""Domain-specific type definitions.

For example, mapped language codes, platform IDs, platform encoding IDs. These
are used to abide by the "parse, don't validate" methodology, which is supposed
to vastly reduce parsing and validation bugs.
"""
import abc
import collections.abc as col_abc
import typing as typ

T = typ.TypeVar("T")

_SUPPORTED_CONTAINED_TYPES: typ.Final[col_abc.Set[type]] = frozenset(
    (int, str, float, list, dict, set, frozenset)
)


class PCustomType(typ.Protocol):
    """Protocol for custom types for use with pydantic."""

    @classmethod
    @abc.abstractmethod
    def __get_validators__(
        cls,
    ) -> typ.Generator[typ.Callable[[T], T], None, None]:
        """Return validators for the type."""


# Allow runtime checks to conveniently test the class factory
@typ.runtime_checkable
class PContainedType(PCustomType, typ.Protocol):
    """A type which has all its possible values inside of a container."""

    @classmethod
    @abc.abstractmethod
    def __get_container__(cls) -> col_abc.Container:
        """Return the container with all possible values of the contained type."""

    @classmethod
    @abc.abstractmethod
    def __get_type__(cls) -> type:
        """Return the type of supported values."""


class ContainedType(abc.ABC, PContainedType):
    """A base class for custom contained pydantic types.

    A contained type is a type that is a subclass of type `T`, for which all
    valid values are defined in a container. For example, a contained type
    `ContainedInt` that has been defined on type `int` and a container `C =
    {-2, 11, 100` is a subclass of `int` that only accepts values in the set
    `C`. All other values must be considered invalid.
    """

    _ARGUMENT_TYPE: typ.ClassVar[type]
    _CONTAINER: typ.ClassVar[col_abc.Container]

    @classmethod
    def __get_type__(cls) -> type:
        return cls._ARGUMENT_TYPE

    @classmethod
    def validate(cls, value: T) -> T:
        if not isinstance(value, cls.__get_type__()):
            raise TypeError(
                f"Value '{value}' is not of type '{cls._ARGUMENT_TYPE}'"
            )
        if value not in cls._CONTAINER:
            raise ValueError(f'Value "{value}" not found in "{cls._CONTAINER}"')
        return value

    @classmethod
    def __get_validators__(
        cls,
    ) -> typ.Generator[typ.Callable[[T], T], None, None]:
        yield cls.validate


def contained_type(
    t: type,
    container: col_abc.Container[str],
    name: typ.Optional[str] = None,
) -> PContainedType:
    """Return a new `ContainedType` for a specified contained value."""
    if t not in _SUPPORTED_CONTAINED_TYPES:
        raise ValueError(f"Type {t} is not supported for contained types.")

    namespace = {"_ARGUMENT_TYPE": t, "_CONTAINER": container}
    new_cls = type(
        "ContainedValue",
        (
            t,
            ContainedType,
        ),
        namespace,
    )
    return new_cls


class LanguageCode(str):
    """Base class for language codes that have been mapped for any platform
    supported by OpenType.
    """


class MacLanguageCode(LanguageCode):
    """Type for language codes that have been mapped for the Mac platform."""
