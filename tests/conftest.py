# from typing import Any
# from unittest.mock import MagicMock

# import pytest

# from eltstar.config import EnvironmentConfigType, RuntimeConfigType
# from eltstar.engines.base import EngineType
# from eltstar.engines.eltstar_arrow_engine import ArrowEngine
# from eltstar.models.base import (
#     TablePath,
# )
# from eltstar.models.table import Table


# class MockTablePath(TablePath):
#     def full_path(
#         self,
#         runtime_config: RuntimeConfigType,
#         environment_config: EnvironmentConfigType,
#         *args: Any,
#         **kwargs: dict[str, Any],
#     ) -> str:
#         return "test"


# class MockTable(Table):
#     path: MockTablePath = MockTablePath()
#     engine: type[EngineType] = ArrowEngine

#     def read(*args, **kwargs):
#         return MagicMock()

#     def write(*args, **kwargs):
#         return MagicMock()


# @pytest.fixture(scope="session")
# def mock_table() -> Table:

#     # MockTable.model_rebuild()

#     return MockTable
