from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from pydantic import ConfigDict, model_validator

from eltstar.models.data_frame_wrapper.functions.base import WrapperArgSpec, WrapperFunctionSpec

if TYPE_CHECKING:
    from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper


### aigen_start
# --8<-- [start:join-arg-spec]
class JoinComparisonOperator(StrEnum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_EQUAL_THAN = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL_THAN = auto()


class JoinArgSpec(WrapperArgSpec):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # (1)!

    other: "DataFrameWrapper"  # (2)!
    left_on: list[str]  # (3)!
    right_on: list[str]  # (4)!
    operator_list: list[JoinComparisonOperator]  # (5)!
    how: Literal[  # (6)!
        "inner",
        "left",
        "right",
        "full",
        "cross",
        "semi",
        "anti",
        "outer",
        "full_outer",
        "left_outer",
        "right_outer",
        "left_semi",
        "left_anti",
    ]
    # --8<-- [end:join-arg-spec]
    ### aigen_end

    @model_validator(mode="before")
    @classmethod
    def check_left_on_with_right_on(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validator to verify correct settings of left_on and right_on for joining logic"""
        if "left_on" not in values:
            raise ValueError("left_on is not present in join arg spec! Required!")
        if "right_on" not in values:
            raise ValueError("right_on is not present in join arg spec! Required!")
        if len(values["left_on"]) != len(values["right_on"]):  # type: ignore
            raise ValueError("left_on and right_on have to have the same length!")
        return values

    @model_validator(mode="before")
    @classmethod
    def default_operator_list(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validator for the operator list. Generates a default value if no value present."""
        if "operator_list" not in values:
            values["operator_list"] = [JoinComparisonOperator.EQUAL.value] * len(values["left_on"])
        return values


### aigen_start
# --8<-- [start:join-arg-spec-type]
JoinArgSpecType = TypeVar("JoinArgSpecType", bound=JoinArgSpec)  # pylint: disable=invalid-name
# --8<-- [end:join-arg-spec-type]
### aigen_end


### aigen_start
# --8<-- [start:join-func-spec]
class JoinFuncSpec(WrapperFunctionSpec[type[JoinArgSpecType]]):  # (1)!
    func_name: str = "join"  # (2)!


# --8<-- [end:join-func-spec]
### aigen_end
