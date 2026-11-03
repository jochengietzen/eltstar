from pathlib import Path
from typing import Any

from eltstar.graph import Lineage
from eltstar.runtime_system.base import BaseRuntimeSystem, RuntimeSystemConfig

# [Unit]
# Description=My Simple Daemon

# [Service]
# Type=forking
# ExecStart=/usr/sbin/my-simple-daemon -d

# [Install]
# WantedBy=multi-user.target


class SystemDFile(RuntimeSystemConfig):
    description: str

    service_type: str = "oneshot"
    uv_path: str
    exec_path: str

    def to_file(self, pth: Path):
        with open(pth, "w", encoding="utf-8") as file:
            file.write(f"""
[Unit]
Description={self.description}

[Service]
Type={self.service_type}
ExecStart={self.uv_path} run python {self.exec_path}

[Install]
WantedBy=multi-user.target
""")


class SystemDRuntimeSystemConfig(RuntimeSystemConfig):
    system_d: SystemDFile
    target_path: Path


class SystemDJobRS(BaseRuntimeSystem[SystemDRuntimeSystemConfig]):
    @classmethod
    def generate(
        cls,
        lineage: Lineage,
        runtime_system_config: SystemDRuntimeSystemConfig,
        source_table_type: type | None = None,
    ) -> Any:
        runtime_system_config.system_d.to_file(runtime_system_config.target_path)
