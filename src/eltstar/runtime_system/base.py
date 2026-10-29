from abc import ABC, abstractmethod
from typing import Any

from eltstar.base_model import BaseModel
from eltstar.engines.base import EngineType  # pylint: disable=unused-import  # noqa
from eltstar.graph import Lineage
from eltstar.transformation import Transformation  # pylint: disable=unused-import  # noqa


class RuntimeSystemConfig(BaseModel):
    """
    Configuration object for the runtime systems
    """


### aigen_start
# --8<-- [start:runtime-system-interface]
class BaseRuntimeSystem[MySendT: BaseModel](ABC):
    @classmethod
    @abstractmethod
    def generate(
        cls, lineage: Lineage, runtime_system_config: RuntimeSystemConfig, source_table_type: type | None = None
    ) -> Any:
        """aigen_start
        Generate runtime system artifacts from the given lineage graph.
        aigen_end"""

    # --8<-- [end:runtime-system-interface]
    ### aigen_end
