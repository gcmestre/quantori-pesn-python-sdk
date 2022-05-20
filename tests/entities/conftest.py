import pytest
from pytest_factoryboy import register

from tests.entities.factories import (
    ChemicalDrawingFactory,
    EIDFactory,
    EntityFactory,
    ExcelFactory,
    ExperimentFactory,
    ImageFactory,
    NotebookFactory,
    TextFactory,
    WordFactory
)
from tests.entities.stoichiometry.factories import StoichiometryFactory
from tests.entities.tables.factories import TableFactory


register(EIDFactory)
register(NotebookFactory)
register(ExperimentFactory)
register(TextFactory)
register(ChemicalDrawingFactory)
register(ImageFactory)
register(TableFactory)
register(StoichiometryFactory)
register(EntityFactory)
register(WordFactory)
register(ExcelFactory)


@pytest.fixture()
def entity_store_mock(mocker):
    return mocker.patch('signals_notebook.entities.EntityStore')
