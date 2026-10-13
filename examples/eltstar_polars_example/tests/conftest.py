import pytest
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.engines.base import Engine
from eltstar.testing.faker_manager import FakerManager


@pytest.fixture
def faker_manager() -> FakerManager:
    return FakerManager()


@pytest.fixture
def engine() -> Engine:
    return PolarsEngine()
