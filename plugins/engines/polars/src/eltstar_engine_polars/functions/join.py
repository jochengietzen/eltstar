from enum import StrEnum, auto
from typing import Literal

import polars as pl

from eltstar.models.data_frame_wrapper.functions.join import JoinArgSpec, JoinFuncSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_engine_polars.engine import PolarsEngine


class PolarsJoinComparisonOperator(StrEnum):
    EQUAL = auto()


class PolarsJoinArgSpec(JoinArgSpec):
    operator_list: list[PolarsJoinComparisonOperator]
    how: Literal["inner", "left", "right", "full", "cross", "semi", "anti"]


def join(self: DataFrameWrapper, function_spec: PolarsJoinArgSpec) -> DataFrameWrapper:
    df_in: pl.DataFrame = self.data_frame
    df_other: pl.DataFrame = function_spec.other.data_frame

    joined = df_in.join(df_other, left_on=function_spec.left_on, right_on=function_spec.right_on, how=function_spec.how)

    return DataFrameWrapper(data_frame=joined, engine=self.engine)


DataFrameWrapper.register_wrapper_function(
    engine=PolarsEngine, func_spec=JoinFuncSpec(arg_spec=PolarsJoinArgSpec), func=join
)
