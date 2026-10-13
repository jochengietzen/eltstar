from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Literal

from pydantic import ConfigDict

from eltstar.base_model import BaseModel
from eltstar.engines.base import EngineType  # pylint: disable=unused-import  # noqa
from eltstar.graph import Lineage, LineageTransformationElement
from eltstar.logging import logger
from eltstar.models.table import Table
from eltstar.transformation import Transformation  # pylint: disable=unused-import  # noqa


class InfoNode(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # LineageTransformationElement holds a TransformationNode

    node: LineageTransformationElement
    node_type: Literal["transformation"] = "transformation"


class InfoTable(BaseModel):
    node: Table
    node_type: Literal["read", "write"]


InfoNode.model_rebuild()
InfoTable.model_rebuild()


### aigen_start
# --8<-- [start:runtime-system-interface]
class BaseRuntimeSystem[MySendT: BaseModel](ABC):
    @abstractmethod
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        """aigen_start
        Generate runtime system artifacts from the given lineage graph.
        aigen_end"""

    # --8<-- [end:runtime-system-interface]
    ### aigen_end

    def iter_nodes(
        self, lineage: Lineage, source_table_type: type | None = None
    ) -> Generator[InfoNode | InfoTable, MySendT]:
        # materialise the generators, otherwise the logging below would exhaust them
        source_tables = list(lineage.iter_source_tables(source_table_type=source_table_type))
        sink_tables = list(lineage.iter_sink_tables())
        transformations = list(lineage.iter_transformations())
        logger.info("Source tables: %s", [t.path.name for t in source_tables])
        logger.info("Transformations: %s", [(t.name, t.depends_on_transformations) for t in transformations])
        logger.info("Sink tables: %s", [t.path.name for t in sink_tables])
        for source_table in source_tables:
            yield InfoTable(node=source_table, node_type="read")

        for transformation in transformations:
            yield InfoNode(node=transformation)

        for sink_table in sink_tables:
            yield InfoTable(node=sink_table, node_type="write")
