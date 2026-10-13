import polars as pl
import pytest
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.base import FloatType, IntegerType
from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField


@pytest.fixture
def test_df() -> pl.DataFrame:
    return DataFrameWrapper(
        data_frame=pl.DataFrame(
            {
                "foo": [1, 2, 3],
                "bar": [6.0, 7.0, 8.0],
            }
        ),
        schema=Schema(
            root=[
                SchemaField(name="foo", type_=IntegerType(), nullable=False),
                SchemaField(name="bar", type_=FloatType(), nullable=False),
            ]
        ),
        engine=PolarsEngine,
    )
