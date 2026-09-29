import os
from pathlib import Path

from eltstar.transformation import manager
from eltstar_pandas_example.config import MyEnvironmentConfig, MyRuntimeConfig

FILE_PARTS = __file__.split(os.sep)
ROOT = Path(os.sep.join(FILE_PARTS[: FILE_PARTS.index("examples")])).absolute()

manager.load_all_plugins()

manager.load_runtime_config(runtime_class_type=MyRuntimeConfig, situation_identifier="local")
manager.load_environment_config(
    environment_class_type=MyEnvironmentConfig,
    situation_identifier="local",
    path=str(ROOT / "data/tst/config.yaml"),
)


manager.load_all_transformations("eltstar_pandas_example.transformations")
