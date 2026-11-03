from typing import TypeVar

from pydantic import ConfigDict

from eltstar.models.data_frame_wrapper.functions.base import WrapperArgSpec, WrapperFunctionSpec


class OrderedDuplicateArgSpec(WrapperArgSpec):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    n_duplications: int = 1
    index_column_name: str = "index_column"


OrderedDuplicateSpecType = TypeVar("OrderedDuplicateSpecType", bound=OrderedDuplicateArgSpec)  # pylint: disable=invalid-name


class OrderedDuplicateFuncSpec(WrapperFunctionSpec):
    func_name: str = "ordered_duplicate"
    arg_spec: type[OrderedDuplicateSpecType]  # type: ignore # TODO: try to find proper way to handle pydantic and mypy
