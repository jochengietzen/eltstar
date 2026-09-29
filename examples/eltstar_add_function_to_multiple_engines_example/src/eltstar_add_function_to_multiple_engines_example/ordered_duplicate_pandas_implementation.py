import pandas as pd
from eltstar_engine_pandas.engine import PandasEngine

from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_add_function_to_multiple_engines_example.ordered_duplicate_function_spec import (
    OrderedDuplicateArgSpec,
    OrderedDuplicateFuncSpec,
)


class PandasOrderedDuplicateArgSpec(OrderedDuplicateArgSpec):
    something: str = "pandas"


def ordered_duplicate(self: DataFrameWrapper, function_spec: PandasOrderedDuplicateArgSpec) -> DataFrameWrapper:
    df: pd.DataFrame = self.data_frame
    df[function_spec.index_column_name] = range(len(df))
    result = df

    for _ in range(function_spec.n_duplications):
        result = pd.concat([result, df], axis=0, ignore_index=True)

    result = result.sort_values(by=[function_spec.index_column_name])
    return DataFrameWrapper(data_frame=result, engine=PandasEngine)


DataFrameWrapper.register_wrapper_function(
    engine=PandasEngine,
    func_spec=OrderedDuplicateFuncSpec(arg_spec=PandasOrderedDuplicateArgSpec),
    func=ordered_duplicate,
)
