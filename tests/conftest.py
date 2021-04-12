"""Defines global pytest fixtures.

To automatically resolve custom type-specific Hypothesis strategies, we need
to register them. However, usually, the module with the custom strategies is
not loaded into the test module scope. If the module is never loaded, its
instructions will never be executed. This means that the type-specific
strategies will not be registered, and Hypothesis will fall back on
`builds()` and silently use unexpected internal strategies for type-annotated
objects.

This behavior is undesired, therefore, we load the module with custom
Hypothesis strategies into the global fixture scope to ensure that pytest
loads the module at least once and registers the strategies.
"""
import typing as typ

import fontTools.ttLib.tables._n_a_m_e as ft_table_name
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e as NameTable
import pytest

from font_renamer import name_record_mapper as ft_nrm

from . import types as tt
from . import hypothesis_strategies  # Ensure custom strategies are loaded


# name string, nameID, platformID, encodingID, languageID
NameRecordTuple = typ.Tuple[str, int, int, int, int]


# Constants
PLATFORM_IDS = {
    "mac": (1, 0, 0),
    "windows": (3, 1, 0x0409),
}

NAME_IDS = {
    # Format: (family_name_id: int, subfamily_name_id: int)
    "windows": {
        "family": 1,
        "subfamily": 2,
    },
    "mac": {
        "family": 1,
        "subfamily": 2,
    },
    # "postscript": (6, 4),
}


@pytest.fixture
def name_table_empty() -> typ.Generator[NameTable, None, None]:
    """Provides an empty `name` table."""
    yield NameTable()


@pytest.fixture(scope="session")
def ft_name_record_from_name_record_tuple() -> typ.Generator[
    typ.Callable[[tt.NameRecordTupleMaybe], ft_table_name.NameRecord],
    None,
    None,
]:
    """Factory function for creating fontTools `NameRecord`s from our own
    `NameRecordTuple`s.
    """

    def _ft_name_record_from_name_record_tuple(
        name_record_tuple: tt.NameRecordTupleMaybe,
    ) -> ft_table_name.NameRecord:
        return ft_table_name.makeName(
            name_record_tuple.string,
            name_record_tuple.name_id,
            name_record_tuple.platform_id,
            name_record_tuple.platform_encoding_id,
            name_record_tuple.language_id,
        )

    yield _ft_name_record_from_name_record_tuple


@pytest.fixture
def make_name_table(
    name_table_empty: NameTable,
) -> typ.Callable[[typ.Iterable[NameRecordTuple]], NameTable]:
    """Factory as fixture that provides a function to create a non-empty `name`
    table that contains provided name records.
    """
    name_table = name_table_empty

    def _make_name_table(entries: typ.Iterable[NameRecordTuple]) -> NameTable:
        for e in entries:
            name_table.setName(*e)

        return name_table

    return _make_name_table


@pytest.fixture(
    params=[
        [
            # Windows font naming nameID range
            (
                "Test Family Win",
                NAME_IDS["windows"]["family"],
                *PLATFORM_IDS["windows"],
            ),
            (
                "BoldWin",
                NAME_IDS["windows"]["subfamily"],
                *PLATFORM_IDS["windows"],
            ),
            # Mac font naming nameID range
            (
                "Test Family Mac",
                NAME_IDS["mac"]["family"],
                *PLATFORM_IDS["mac"],
            ),
            ("BoldMax", NAME_IDS["mac"]["subfamily"], *PLATFORM_IDS["mac"]),
        ],
    ]
)
def raw_name_records(
    request,
) -> typ.Generator[typ.List[NameRecordTuple], None, None]:
    """Returns name records in "raw format". For the purposes of testing, "raw
    format" is defined as a tuple of parameters needed to add, set or create
    a name record using `addName()`, `setName()` or similar `name` table
    methods).
    """
    yield request.param


@pytest.fixture(
    params=[
        "CC Wild Words",
        "CC Victory Speech",
        "Helvetica",
    ]
)
def font_family_name(request) -> typ.Generator[str, None, None]:
    yield request.param


# Session-scoped since `LangInfoMapper` is safe to share, and Hypothesis
# requires fixtures that are used with it to be either session- or
# module-scoped
@pytest.fixture(scope="session")
def default_language_info_mapper() -> typ.Generator[
    ft_nrm.LanguageInfoMapper, None, None
]:
    """Yield the default language mapper."""
    yield ft_nrm.LanguageInfoMapper()
