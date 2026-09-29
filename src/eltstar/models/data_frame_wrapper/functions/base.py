from typing import TypeVar

from pydantic import ConfigDict

from eltstar.base_model import BaseModel


class WrapperArgSpec(BaseModel):
    model_config = ConfigDict(extra="allow")


WrapperArgSpecType = TypeVar("WrapperArgSpecType", bound=WrapperArgSpec)  # pylint: disable=invalid-name


# TODO: try to find proper way to handle pydantic and mypy
class WrapperFunctionSpec[WrapperArg: WrapperArgSpecType](BaseModel):  # type: ignore
    func_name: str
    arg_spec: WrapperArg
