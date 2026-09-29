from enum import StrEnum, auto
from typing import Literal

import pandas as pd

from eltstar.models.data_frame_wrapper.functions.join import JoinArgSpec, JoinFuncSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_engine_pandas.engine import PandasEngine


class PandasJoinComparisonOperator(StrEnum):
    EQUAL = auto()


class PandasJoinArgSpec(JoinArgSpec):
    operator_list: list[PandasJoinComparisonOperator]
    how: Literal["left", "right", "outer", "inner", "cross", "left_anti", "right_anti"]


def join(self: DataFrameWrapper, function_spec: PandasJoinArgSpec) -> DataFrameWrapper:
    df_in: pd.DataFrame = self.data_frame
    df_other: pd.DataFrame = function_spec.other.data_frame
    assert function_spec.left_on == function_spec.right_on, "PAndas can only handle same left/right on values"
    joined = df_in.set_index(function_spec.left_on).join(
        other=df_other.set_index(function_spec.right_on), how=function_spec.how, lsuffix="_l", rsuffix="_r"
    )

    return DataFrameWrapper(data_frame=joined, engine=self.engine)


DataFrameWrapper.register_wrapper_function(
    engine=PandasEngine, func_spec=JoinFuncSpec(arg_spec=PandasJoinArgSpec), func=join
)
