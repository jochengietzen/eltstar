import polars as pl
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_function_spec import (
    OrderedDuplicateArgSpec,
    OrderedDuplicateFuncSpec,
)


class PolarsOrderedDuplicateArgSpec(OrderedDuplicateArgSpec):
    something: str = "polars"


def ordered_duplicate(self: DataFrameWrapper, function_spec: PolarsOrderedDuplicateArgSpec) -> DataFrameWrapper:
    df: pl.DataFrame = self.data_frame
    df = df.with_row_index(function_spec.index_column_name)
    result = df

    for _ in range(function_spec.n_duplications):
        result = pl.union([result, df])

    result = result.sort(function_spec.index_column_name)
    return DataFrameWrapper(data_frame=result, engine=PolarsEngine)


DataFrameWrapper.register_wrapper_function(
    engine=PolarsEngine,
    func_spec=OrderedDuplicateFuncSpec(arg_spec=PolarsOrderedDuplicateArgSpec),
    func=ordered_duplicate,
)
