import pandas as pd
import polars as pl
from eltstar_engine_pandas.engine import PandasEngine
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.logging import logger
from eltstar.models.base import FloatType, IntegerType
from eltstar.models.schema import Schema, SchemaField
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_pandas_implementation import (
    PandasOrderedDuplicateArgSpec,
)
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_polars_implementation import (
    PolarsOrderedDuplicateArgSpec,
)

logger.setup_stdout_handler()
from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper  # noqa: E402


def main() -> None:
    """
    Demonstrates registering the same `ordered_duplicate` wrapper function
    for both the pandas and polars engines, and running it through each.
    """
    schema = Schema(
        root=[
            SchemaField(name="foo", type_=IntegerType(), nullable=False),
            SchemaField(name="bar", type_=FloatType(), nullable=False),
        ]
    )

    pandas_wrapper = DataFrameWrapper(
        data_frame=pd.DataFrame({"foo": [1, 2, 3], "bar": [6.0, 7.0, 8.0]}),
        schema=schema,
        engine=PandasEngine,
    )
    polars_wrapper = DataFrameWrapper(
        data_frame=pl.DataFrame({"foo": [1, 2, 3], "bar": [6.0, 7.0, 8.0]}),
        schema=schema,
        engine=PolarsEngine,
    )

    pandas_result = pandas_wrapper.ordered_duplicate(
        function_spec=PandasOrderedDuplicateArgSpec(n_duplications=1, index_column_name="index_column")
    )
    polars_result = polars_wrapper.ordered_duplicate(
        function_spec=PolarsOrderedDuplicateArgSpec(n_duplications=1, index_column_name="index_column")
    )

    print(pandas_result.data_frame)
    print(polars_result.data_frame)


if __name__ == "__main__":
    main()
