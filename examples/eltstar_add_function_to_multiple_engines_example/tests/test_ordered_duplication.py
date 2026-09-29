import pytest
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_pandas_implementation import (
    PandasOrderedDuplicateArgSpec,
)
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_polars_implementation import (
    PolarsOrderedDuplicateArgSpec,
)
from eltstar_engine_pandas.engine import PandasEngine
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.base import FloatType, IntegerType
from eltstar.models.schema import Schema, SchemaField
from eltstar.testing.wrapper_functions import compare_wrapper_functions_accross_engines


def test_ordered_duplication_function(test_df):
    compare_wrapper_functions_accross_engines(
        dfw=test_df,
        engine_func_spec_lookup={
            PolarsEngine: PolarsOrderedDuplicateArgSpec(n_duplications=1, index_column_name="index_column"),
            PandasEngine: PandasOrderedDuplicateArgSpec(n_duplications=1, index_column_name="index_column"),
        },
        func_identifier="ordered_duplicate",
        expected_result_schema=Schema(
            root=[
                SchemaField(name="foo", type_=IntegerType(), nullable=False),
                SchemaField(name="bar", type_=FloatType(), nullable=False),
                SchemaField(name="index_column", type_=IntegerType(), nullable=False),
            ]
        ),
    )

    with pytest.raises(AssertionError):
        compare_wrapper_functions_accross_engines(
            dfw=test_df,
            engine_func_spec_lookup={
                PolarsEngine: PolarsOrderedDuplicateArgSpec(n_duplications=1, index_column_name="index_column"),
                PandasEngine: PandasOrderedDuplicateArgSpec(n_duplications=2, index_column_name="index_column"),
            },
            func_identifier="ordered_duplicate",
            expected_result_schema=Schema(
                root=[
                    SchemaField(name="foo", type_=IntegerType(), nullable=False),
                    SchemaField(name="bar", type_=FloatType(), nullable=False),
                    SchemaField(name="index_column", type_=IntegerType(), nullable=False),
                ]
            ),
        )
