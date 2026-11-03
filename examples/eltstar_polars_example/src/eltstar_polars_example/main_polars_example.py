from pathlib import Path

from eltstar_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS, DatabricksRuntimeSystemConfig

from eltstar.logging import logger
from eltstar_polars_example.manager import manager

__dir = Path(__file__).parent


def main():
    logger.setup_stdout_handler()
    logger.set_level("DEBUG")
    logger.debug("Registered transformations: %s", manager._registered_transformations.keys())
    result = manager._registered_transformations["youtube_channel_overview"].execute()

    manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)

    config = DatabricksRuntimeSystemConfig(
        package_name="eltstar_polars_example",
        entry_point="blub",
        yaml_resource_path=__dir / "test.yaml",
        tasks_path="foo.bar.tasks",
    )
    ### aigen_start
    # --8<-- [start:rs-usage]
    DatabricksAssetBundleJobRS.generate(lineage=manager.lineage, runtime_system_config=config)
    # --8<-- [end:rs-usage]
    ### aigen_end


if __name__ == "__main__":
    main()
