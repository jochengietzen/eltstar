from enum import StrEnum, auto
from typing import Literal

import polars as pl

from eltstar.models.data_frame_wrapper.functions.join import JoinArgSpec, JoinFuncSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_engine_polars.engine import PolarsEngine


### aigen_start
# --8<-- [start:polars-join-implementation]
class PolarsJoinComparisonOperator(StrEnum):  # (1)!
    EQUAL = auto()


class PolarsJoinArgSpec(JoinArgSpec):  # (2)!
    operator_list: list[PolarsJoinComparisonOperator]
    how: Literal["inner", "left", "right", "full", "cross", "semi", "anti"]  # (3)!


def join(self: DataFrameWrapper, function_spec: PolarsJoinArgSpec) -> DataFrameWrapper:  # (4)!
    df_in: pl.DataFrame = self.data_frame  # (5)!
    df_other: pl.DataFrame = function_spec.other.data_frame  # (6)!

    joined = df_in.join(  # (7)!
        df_other, left_on=function_spec.left_on, right_on=function_spec.right_on, how=function_spec.how
    )

    return DataFrameWrapper(data_frame=joined, engine=self.engine)  # (8)!


DataFrameWrapper.register_wrapper_function(  # (9)!
    engine=PolarsEngine,  # (10)!
    func_spec=JoinFuncSpec(arg_spec=PolarsJoinArgSpec),  # (11)!
    func=join,  # (12)!
)
# --8<-- [end:polars-join-implementation]
### aigen_end
