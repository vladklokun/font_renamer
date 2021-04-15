"""Facilities for interacting with the OpenType `name` table.

fontTools uses a camelCase naming convention, which is uncharacteristic for
Python, so we adapt most of the classes to follow PEP8. Besides stylistic
choices, we adapt some of the behavior:
- Discourage returning `None` on failure (record not found etc). We prefer to
  fail early, so raise an error instead.
- Follow command-query separation: a method either executes a query and returns
  a value, or executes a command, but not both.
"""
import abc
import dataclasses as dc
import typing as typ
import font_renamer.opentype_name_constants as fr_const

import fontTools.ttLib.tables._n_a_m_e as ft_name_table
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e as NameTable
import pydantic as pyd


class PNameRecord(typ.Protocol):
    """A protocol for name record instances."""

    string: str
    name_id: int
    platform_id: int
    platform_encoding_id: int
    language_id: int

    @abc.abstractmethod
    def as_dict(self) -> typ.Dict[str, typ.Union[int, str]]:
        """Return a dictionary representation of the name record instance."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_ft_name_record(
        cls: typ.Type,
        ft_name_record: ft_name_table.NameRecord,
    ) -> "PNameRecord":
        """Create an instance from an instance of fontTools' `NameRecord`."""
        raise NotImplementedError


@dc.dataclass(frozen=True)
class NameRecord(PNameRecord):
    """A standard name record implementation."""
    string: str
    name_id: int
    platform_id: int
    platform_encoding_id: int
    language_id: int

    def as_dict(self) -> typ.Dict[str, typ.Union[int, str]]:
        """Return the name record as a dictionary."""
        return dict(self.__dict__)

    @classmethod
    def from_ft_name_record(
        cls: typ.Type["NameRecord"],
        ft_name_record: ft_name_table.NameRecord,
    ) -> "NameRecord":
        name_string = ft_name_record.toUnicode()

        if not isinstance(ft_name_record.string, str):
            raise ValueError(
                "The provided name string could not be encoded as a valid "
                "Unicode string. "
                f"Provided name string: {name_string}."
            )

        return cls(
            string=name_string,
            name_id=ft_name_record.nameID,
            platform_id=ft_name_record.platformID,
            platform_encoding_id=ft_name_record.platEncID,
            language_id=ft_name_record.langID,
        )


class PNameTable(abc.ABC):
    """Interface for a sane `name` table.

    Requires implementors to use PEP8 method names and follow command-query
    separation. Also, through type hints, suggests that implementations should
    either return a valid object of required type or raise errors instead of
    returning an option type value.
    """

    @abc.abstractmethod
    def get_name_record(
        self,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> ft_name_table.NameRecord:
        """Return a name record from a table identified by provided IDs.

        Raises a `KeyError` if a record identified by provided IDs cannot be
        found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_name_string(
        self,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> str:
        """Return a name string by IDs.

        Finds a name record in a name table that matches the provided IDs and
        returns the name string of the record. Raises a `KeyError` if a record
        identified by provided IDs cannot be found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_name_string(
        self,
        string: str,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> None:
        """Set a `name` record by string.

        "Setting" means that if no matching record exists, the method creates a
        new record. If the record exists, the method overwrites it.
        """
        raise NotImplementedError


class TTLibToNameTableAdapter(PNameTable):
    """Adapts the `fontTools.ttLib.table__n_a_m_e` to the INameTable interface.

    Needed to conform to Python code style, consistently report errors and
    return properly typed objects.
    """

    def __init__(self, table: NameTable) -> None:
        self._table = table

        # A fontTools quirk. By default, when creating a `table__n_a_m_e`,
        # fontTools does not create the `table.names` attribute, yet it might
        # try use it in other methods. This raises an `AttributeError`
        # unexpectedly. Since we expect the attribute to exist, and not raise
        # exceptions in random places, when adapting a `table__n_a_m_e`
        # instance, if the `names` attribute does not exist, initialize it to
        # an empty list to minimize unexpected exceptions and stabilize the
        # interface.
        if not hasattr(table, "names"):
            self._table.names = []

    def get_name_record(
        self,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> ft_name_table.NameRecord:
        name_record = self._table.getName(
            name_id, platform_id, platform_encoding_id, language_id
        )
        # fontTools returns `None` if a name string cannot be found in a
        # `name` table. I prefer to fail ASAP, since it allows to locate the
        # problem earlier during debugging. Therefore, raise an error if
        # fontTools returns `None` while looking up an entry in a `name` table.
        if name_record is None:
            raise KeyError(
                f"Unable to find the desired name string "
                f"(nameID: {name_id}, platformID: {platform_id}, "
                f"encodingID: {platform_encoding_id}, "
                f"languageID: {language_id})."
            )

        return name_record

    def get_name_string(
        self,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> str:
        name_record = self.get_name_record(
            name_id=name_id,
            platform_id=platform_id,
            platform_encoding_id=platform_encoding_id,
            language_id=language_id,
        )
        return name_record.string

    # pylint: disable=too-many-arguments
    def set_name_string(
        self,
        string: str,
        name_id: int,
        platform_id: int,
        platform_encoding_id: int,
        language_id: int,
    ) -> None:
        self._table.setName(
            string=string,
            nameID=name_id,
            platformID=platform_id,
            platEncID=platform_encoding_id,
            langID=language_id,
        )
