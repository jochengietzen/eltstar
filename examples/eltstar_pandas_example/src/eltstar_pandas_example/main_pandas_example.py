from eltstar_rs_dbx_asset_bundle_jobs.runtime_system import DatabricksAssetBundleJobRS

from eltstar.logging import logger
from eltstar_pandas_example.manager import manager

if __name__ == "__main__":
    logger.debug("Registered transformations: %s", manager._registered_transformations.keys())
    result = manager._registered_transformations["youtube_channel_overview"].execute()
    print(result.data_frame)
    manager._registered_transformations["youtube_channel_overview"].save_output_table(result=result)

    DatabricksAssetBundleJobRS().generate(lineage=manager.lineage)
