from abc import ABC, abstractmethod

from eltstar.graph import Lineage


### aigen_start
# --8<-- [start:runtime-system-interface]
class BaseRuntimeSystem(ABC):
    @abstractmethod
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        """aigen_start
        Generate runtime system artifacts from the given lineage graph.
        aigen_end"""


# --8<-- [end:runtime-system-interface]
### aigen_end
