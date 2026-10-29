from pathlib import Path

from eltstar_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS, DatabricksRuntimeSystemConfig

from eltstar.logging import logger
from eltstar_polars_example.manager import manager

if __name__ == "__main__":
    logger.setup_stdout_handler()
    logger.set_level("DEBUG")
    logger.debug("Registered transformations: %s", manager._registered_transformations.keys())
    # result = manager._registered_transformations["youtube_channel_overview"].execute()
    # print(result.data_frame)
    # manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)

    config = DatabricksRuntimeSystemConfig(
        package_name="eltstar_polars_example",
        entry_point="blub",
        yaml_resource_path=Path("/workspace/examples/eltstar_polars_example/src/eltstar_polars_example/test.yaml"),
        tasks_path="foo.bar.tasks",
    )
    ### aigen_start
    # --8<-- [start:rs-usage]
    DatabricksAssetBundleJobRS.generate(lineage=manager.lineage, runtime_system_config=config)
    # --8<-- [end:rs-usage]
    ### aigen_end
