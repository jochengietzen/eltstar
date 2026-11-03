import sys
from pathlib import Path

from eltstar.logging import logger
from eltstar_rs_systemd_example.manager import manager
from eltstar_rs_systemd_example.systemd_runtime_system.runtime_system import (
    SystemDFile,
    SystemDJobRS,
    SystemDRuntimeSystemConfig,
)

__dir = Path(__file__).parent


def main():
    logger.setup_stdout_handler()
    logger.set_level("DEBUG")
    logger.debug("Registered transformations: %s", manager._registered_transformations.keys())

    config = SystemDRuntimeSystemConfig(
        SystemDFile(
            description="A wonderful systemd etl job",
            exec_path=__dir / "main.py",
            uv_path=sys.executable,
        ),
        target_path=__dir / "../../eltstar.service",
    )
    SystemDJobRS.generate(lineage=manager.lineage, runtime_system_config=config)


if __name__ == "__main__":
    main()
