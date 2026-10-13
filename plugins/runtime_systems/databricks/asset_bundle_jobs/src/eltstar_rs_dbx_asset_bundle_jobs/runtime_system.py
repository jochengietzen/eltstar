from eltstar.graph import Lineage
from eltstar.runtime_system.base import BaseRuntimeSystem


# --8<-- [start:databricks-rs-example]
class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        # TODO: Write the actual asset bundle files (V1)
        for node in self.iter_nodes(lineage=lineage, source_table_type=source_table_type):
            pass


# --8<-- [end:databricks-rs-example]
