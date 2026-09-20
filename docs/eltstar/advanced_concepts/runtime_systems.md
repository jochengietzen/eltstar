<!---aigen_start-->
# Runtime systems

**What** is a runtime system, in eltstar terms? It's the thing that actually schedules and runs your transformations in production - a Databricks workspace, an Airflow instance, a plain cron job, whatever you deploy to. eltstar doesn't want to be your orchestrator, but it does want to help you generate whatever configuration your orchestrator needs, straight from the pipeline you've already defined.

That's what the `eltstar.runtime_system` module is for: a small extension point that turns your [lineage graph](./lineage.md) into deployment artifacts for a specific runtime system.

## The interface

```python
from eltstar.runtime_system.base import BaseRuntimeSystem
from eltstar.graph import Lineage

class MyRuntimeSystem(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        ...
```

`generate` is handed the full `Lineage` for your pipeline (see [Lineage](./lineage.md) for what you can pull out of it - source/sink tables, topological transformation order, dependency edges) and is expected to turn that into whatever your target system needs: job definitions, a DAG file, an asset bundle, ...

`source_table_type` is passed straight through to `lineage.iter_source_tables()`, in case your runtime system needs to treat certain kinds of source tables (e.g. ones backed by an external ingestion job) differently from tables written by your own transformations.

## Example: Databricks Asset Bundle Jobs

`plugins/runtime_systems/databricks/asset_bundle_jobs` is the reference implementation:

```python
class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    def generate(self, lineage: Lineage, source_table_type: type | None = None) -> None:
        source_tables = lineage.iter_source_tables(source_table_type=source_table_type)
        sink_tables = lineage.iter_sink_tables()
        transformations = lineage.iter_transformations()
        ...
```

**Careful!** As of now, this plugin only logs what it *would* generate - walking the lineage and printing source tables, sink tables and transformation dependency order. It does not yet write actual Databricks Asset Bundle job YAML. Treat it as a working example of how to consume a `Lineage` inside a `BaseRuntimeSystem`, not as a ready-to-deploy integration.

## Writing your own

If you want to generate artifacts for a different runtime system (Airflow, Dagster, a plain shell script, ...):

1. Subclass `BaseRuntimeSystem` and implement `generate`.
2. Use `lineage.iter_transformations()` to get transformations in dependency order, and `iter_source_tables`/`iter_sink_tables` to identify the edges of your pipeline.
3. Turn that into whatever your target system's native format is - most orchestrators have some notion of "task" and "task depends on task", which maps directly onto `LineageTransformationElement.depends_on_transformations`.

## Discovery, honestly

`TransformationManager.load_all_plugins()` scans an `eltstar.runtime_systems` entry-point group, mirroring `eltstar.engines` (see [Engines - Discovery, honestly](./engines.md#discovery-honestly)). As of now, `eltstar-rs-dbx-asset-bundle-jobs` doesn't declare that entry point either - you currently wire up a runtime system by importing and instantiating it yourself:

```python
from eltstar_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS

DatabricksAssetBundleJobRS().generate(lineage=manager.lineage)
```

This part of eltstar is intentionally minimal for now - `tbc`, in the spirit of the rest of this documentation.
<!---aigen_end-->
