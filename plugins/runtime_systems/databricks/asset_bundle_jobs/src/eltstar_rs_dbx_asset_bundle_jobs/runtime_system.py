from eltstar.graph import Lineage
from eltstar.logging import logger
from eltstar.runtime_system.base import BaseRuntimeSystem


### aigen_start
# --8<-- [start:databricks-rs-example]
class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        source_tables = lineage.iter_source_tables(source_table_type=source_table_type)
        sink_tables = lineage.iter_sink_tables()
        transformations = lineage.iter_transformations()
        logger.debug("Source tables: %s", [t.path.name for t in source_tables])
        logger.debug("Sink tables: %s", [t.path.name for t in sink_tables])
        logger.debug("Transformations: %s", [(t.name, t.depends_on_transformations) for t in transformations])
        # TODO: Write the actual asset bundle files (V1)
# --8<-- [end:databricks-rs-example]
### aigen_end
