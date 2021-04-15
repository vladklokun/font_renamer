"""Tests the facilities for working with the OpenType `name` table.
"""
# Test classes do not use the self argument, but are required to accept it
# pylint: disable=no-self-use

import dataclasses as dc
import itertools as it
import typing as typ

import fontTools.ttLib.tables._n_a_m_e as tt_table_name
import hypothesis as h
import hypothesis.strategies as h_strats
import pytest

import font_renamer.table_name as fr_name

from . import conftest as cft
from . import hypothesis_strategies as h_strat_custom
from . import types as tt

NameTable = tt_table_name.table__n_a_m_e


def name_table_contains_record(
    table: NameTable,
    name_string: str,
    name_id: int,
    platform_id: int,
    platform_encoding_id: int,
    language_id: int,
) -> bool:
    """Returns `True` if a name record that matches the provided parameters was
    found in the provided `NameTable`. Returns `False` otherwise.
    """
    found = False
    for nr in table.names:
        if (
            nr.string == name_string
            and nr.nameID == name_id
            and nr.platformID == platform_id
            and nr.platEncID == platform_encoding_id
            and nr.langID == language_id
        ):
            found = True
            break

    return found


class TestINameRecord:
    """Tests the interface for name records."""

    def test_instantiation_raises_type_error(self) -> None:
        """Tests if instantiation of the interface raises a `TypeError`."""
        with pytest.raises(TypeError):
            fr_name.PNameRecord()


class TestNameRecord:
    """Tests the name records."""

    @h.given(
        # The `draw()` function is injected by the Hypothesis' internals, so
        # there is no need to provide it explicitly
        # pylint: disable=no-value-for-parameter
        name_rec_tuple=h_strat_custom.name_record_tuples_valid()
    )
    def test_init_valid_params_ok(
        self,
        name_rec_tuple: tt.NameRecordTupleValid,
    ) -> None:
        """Tests if instantiation with valid parameters proceeds ok."""
        name_record = fr_name.NameRecord(**name_rec_tuple._asdict())
        assert name_record
        assert name_rec_tuple.string == name_record.string

    @h.given(
        # pylint: disable=no-value-for-parameter
        name_record_tuple=h_strat_custom.name_record_tuples_valid()
    )
    def test_from_ft_name_record_valid_params_inits_ok(
        self,
        name_record_tuple: tt.NameRecordTupleValid,
        ft_name_record_from_name_record_tuple: typ.Callable[
            [tt.NameRecordTupleValid], tt_table_name.NameRecord
        ],
    ) -> None:
        """Tests if calling `from_ft_name_record()` on a valid fontTools
        `NameRecord` properly initializes a `NameRecord` object."""
        ft_name_record = ft_name_record_from_name_record_tuple(
            name_record_tuple
        )
        name_record = fr_name.NameRecord.from_ft_name_record(ft_name_record)
        assert name_record
        assert name_record.string == ft_name_record.string
        assert name_record.name_id == ft_name_record.nameID
        assert name_record.platform_id == ft_name_record.platformID
        assert name_record.platform_encoding_id == ft_name_record.platEncID
        assert name_record.language_id == ft_name_record.langID

    @h.given(
        # pylint: disable=no-value-for-parameter
        name_record_tuple_invalid=h_strat_custom.name_record_tuples_invalid()
    )
    def test_from_ft_name_record_invalid_params_raises_value_error(
        self,
        name_record_tuple_invalid: tt.NameRecordTupleMaybe,
        ft_name_record_from_name_record_tuple: typ.Callable[
            [tt.NameRecordTupleMaybe], tt_table_name.NameRecord
        ],
    ) -> None:
        """Tests if attempting to instantiate a `NameRecord` from a malformed
        `fontTools.NameRecord` raises a `ValueError`.
        """
        ft_name_record = ft_name_record_from_name_record_tuple(
            name_record_tuple_invalid
        )
        with pytest.raises(ValueError):
            fr_name.NameRecord.from_ft_name_record(ft_name_record)

    @h.given(name_record=h_strats.from_type(fr_name.NameRecord))
    def test_as_dict_returns_matching_dict_copy(
        self, name_record: fr_name.NameRecord
    ) -> None:
        """Test if `as_dict()` returns a valid matching dictionary.

        A dictionary matching a `NameRecord` is considered valid if it is:
            - Non-empty.
            - Not the `__dict__` of the `NameRecord` instance.
            - Its keys and values match the names and values of a
              `NameRecord`'s fields.
        """
        nr_dict = name_record.as_dict()
        assert nr_dict
        assert nr_dict is not name_record.__dict__
        assert set(nr_dict.keys()) == set(
            f.name for f in dc.fields(fr_name.NameRecord)
        )

        for (nr_dict_key, nr_dict_val), (nr_key, nr_val) in it.zip_longest(
            sorted(nr_dict.items()), sorted(name_record.__dict__.items())
        ):
            assert nr_dict_key == nr_key
            assert nr_dict_val == nr_val


class TestINameTableAdapter:
    """Tests the interface for `name` table adapters."""

    def test_instantiation_raises_type_error(self) -> None:
        """Tests if instantition of the interface raises a TypeError."""
        with pytest.raises(TypeError):
            fr_name.PNameTable()


class TestNameTableAdapter:
    """Tests the `name` table adapter."""

    def test_instantiation_ok(self, name_table_empty: NameTable) -> None:
        """Tests if an instance of `NameTableAdapter` can be created."""
        adapter = fr_name.TTLibToNameTableAdapter(name_table_empty)
        assert adapter
        assert adapter._table == name_table_empty
        assert hasattr(adapter._table, "names")

    def test_get_name_record_existing_returns_namerecord(
        self,
        raw_name_records: typ.Sequence[cft.NameRecordTuple],
        make_name_table: typ.Callable[
            [typ.Iterable[cft.NameRecordTuple]], NameTable
        ],
    ) -> None:
        """Tests if calling `get_name_record()` with the parameters that match
        a name record in the bound `name` table returns a corresponding name
        record.

        Inputs:
            - A list of raw name records.
            - A function for creating `NameTable` instances from raw name
              records.
        Expected result:
            - `get_name_record()` returns a `NameRecord` object.
            - Attributes of the returned `NameRecord` match the attributes of
              the raw name record.
        """
        raw_name_rec = raw_name_records[0]
        table = make_name_table(raw_name_records)
        adapter = fr_name.TTLibToNameTableAdapter(table)

        (
            name_string,
            name_id,
            platform_id,
            platform_encoding_id,
            language_id,
        ) = raw_name_rec

        name_rec = adapter.get_name_record(
            name_id,
            platform_id,
            platform_encoding_id,
            language_id,
        )
        assert name_rec
        assert isinstance(name_rec, tt_table_name.NameRecord)
        assert name_rec.string == name_string
        assert name_rec.nameID == name_id
        assert name_rec.platformID == platform_id
        assert name_rec.platEncID == platform_encoding_id
        assert name_rec.langID == language_id

    def test_get_name_record_empty_table_raises_key_error(
        self,
        name_table_empty: NameTable,
    ) -> None:
        """Tests if calling `get_name_record()` while the adapted table is
        empty raises `KeyError`.

        Inputs:
            - name_table_empty: an empty `NameTable`.
        Expected result:
            - `get_name_record()` raises a `KeyError`.
        """
        adapter = fr_name.TTLibToNameTableAdapter(name_table_empty)
        with pytest.raises(KeyError):
            adapter.get_name_record(
                name_id=0, platform_id=0, platform_encoding_id=0, language_id=0
            )

    def test_get_name_string_empty_table_raises_key_error(
        self,
        name_table_empty: NameTable,
    ) -> None:
        """Tests if calling `get_name_string()` while the adapted table is
        empty raises a `KeyError`.

        Inputs:
            - name_table_empty: an empty `NameTable`.
        Expected result:
            - `get_name_string()` raises a `KeyError`.
        """
        adapter = fr_name.TTLibToNameTableAdapter(name_table_empty)
        with pytest.raises(KeyError):
            adapter.get_name_string(
                name_id=0, platform_id=0, platform_encoding_id=0, language_id=0
            )

    def test_get_name_string_existing_returns_matching_string(
        self,
        raw_name_records: typ.Sequence[cft.NameRecordTuple],
        make_name_table: typ.Callable[
            [typ.Iterable[cft.NameRecordTuple]], NameTable
        ],
    ) -> None:
        """Tests if calling `get_name_string()` with the parameters that match
        a name record in the adapted table returns a name string of the name
        record that corresponds to the provided parameters.

        Inputs:
            - raw_name_records: raw name records to create `NameRecord`
              instances in a factory.
            - make_name_table: factory for creating a `name` table with
              provided name records.
        """
        raw_name_record = raw_name_records[0]
        (
            expected_name_string,
            name_id,
            platform_id,
            platform_encoding_id,
            language_id,
        ) = raw_name_record

        name_table = make_name_table(raw_name_records)
        adapter = fr_name.TTLibToNameTableAdapter(name_table)
        actual_name_string = adapter.get_name_string(
            name_id=name_id,
            platform_id=platform_id,
            platform_encoding_id=platform_encoding_id,
            language_id=language_id,
        )
        assert actual_name_string
        assert isinstance(actual_name_string, str)
        assert actual_name_string == expected_name_string

    def test_set_name_string_valid_name_records_contains_set_names_afterwards(
        self,
        raw_name_records: typ.Sequence[cft.NameRecordTuple],
        name_table_empty: NameTable,
    ) -> None:
        """Tests if calling `set_name_string()` with valid values for a name
        record sets the corresponding name records in the adapted `name` table.

        We consider name records to be successfully set if after calling the
        method the adapted `name` table contains the name records that match
        the name record description provided as the method call parameters
        (`name_string`, `name_id`, `platform_id`, `platform_encoding_id`,
        `language_id`).
        """
        adapter = fr_name.TTLibToNameTableAdapter(name_table_empty)
        for record in raw_name_records:
            (
                name_str,
                name_id,
                platform_id,
                platform_encoding_id,
                language_id,
            ) = record
            adapter.set_name_string(
                string=name_str,
                name_id=name_id,
                platform_id=platform_id,
                platform_encoding_id=platform_encoding_id,
                language_id=language_id,
            )

        for record in raw_name_records:
            (
                name_str,
                name_id,
                platform_id,
                platform_encoding_id,
                language_id,
            ) = record
            assert name_table_contains_record(
                adapter._table,
                name_string=name_str,
                name_id=name_id,
                platform_id=platform_id,
                platform_encoding_id=platform_encoding_id,
                language_id=language_id,
            )
