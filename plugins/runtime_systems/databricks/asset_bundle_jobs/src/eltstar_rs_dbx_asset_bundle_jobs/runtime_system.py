from eltstar.graph import Lineage
from eltstar.logging import logger
from eltstar.runtime_system.base import BaseRuntimeSystem


class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        logger.debug("Source tables: %s", [t.path.name for t in lineage.iter_source_tables(source_table_type=source_table_type)])
        logger.debug("Sink tables: %s", [t.path.name for t in lineage.iter_sink_tables()])
        logger.debug("Transformations: %s", [(t.name, t.depends_on_transformations) for t in lineage.iter_transformations()])
        # TODO: Write the actual asset bundle files (V1)
