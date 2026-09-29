from abc import abstractmethod

from eltstar.graph import Lineage


class BaseRuntimeSystem:
    @abstractmethod
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        """aigen_start
        Generate runtime system artifacts from the given lineage graph.
        aigen_end"""
