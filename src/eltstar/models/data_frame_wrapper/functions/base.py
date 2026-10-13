from pydantic import ConfigDict

from eltstar.base_model import BaseModel


class WrapperArgSpec(BaseModel):
    model_config = ConfigDict(extra="allow")


class WrapperFunctionSpec[WrapperArg: WrapperArgSpec, TightWrapperArg: WrapperArgSpec](BaseModel):
    func_name: str
    arg_spec: type[WrapperArg]
    tight_arg_spec: type[TightWrapperArg]
