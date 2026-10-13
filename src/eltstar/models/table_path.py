from abc import ABC, abstractmethod
from typing import Any

from eltstar.base_model import BaseModel
from eltstar.config import EnvironmentConfigType, RuntimeConfigType


class TablePath(BaseModel, ABC):
    @abstractmethod
    def full_path(
        self,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        *args: Any,
        **kwargs: dict[str, Any],
    ) -> str:
        """aigen_start
        Return the fully resolved path string for the table given the runtime and environment configuration.
        aigen_end"""
