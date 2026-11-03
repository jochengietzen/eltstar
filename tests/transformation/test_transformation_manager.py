from typing import Any

import pyarrow as pa

from eltstar.config import EnvironmentConfig, EnvironmentConfigType, RuntimeConfig, RuntimeConfigType
from eltstar.engines.base import EngineType
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar.models import Column, Columns, Table, TablePath
from eltstar.models.base import StringType
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.generation import Generation
from eltstar.testing.faker_type import FakerStringType
from eltstar.transformation import TransformationManager


class MockTablePath(TablePath):
    def full_path(
        self,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        *args: Any,
        **kwargs: dict[str, Any],
    ) -> str:
        return "test"


class MockTable(Table):
    path: MockTablePath = MockTablePath()
    engine: type[EngineType] = ArrowEngine
    description: str = "A test table"

    def read(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs,
    ) -> DataFrameWrapper:
        return DataFrameWrapper(data_frame=pa.Table(), schema=None, engine=ArrowEngine)

    def write(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs,
    ) -> "MockTable":
        return self


def test_transformation_registration():
    tm = TransformationManager()

    columns = Columns(
        root={
            "test": Column(
                name="channel_id",
                data_type=StringType(),
                is_primary_key=True,
                generation=Generation(faker_type=FakerStringType()),
            )
        }
    )

    output_table_model = MockTable(columns=columns)
    input_model_1 = MockTable(columns=columns)
    input_model_2 = MockTable(columns=columns)

    def test_transformation(input_model_1: DataFrameWrapper, input_model_2: DataFrameWrapper):
        return input_model_1

    tm.register_transformation(
        output_table_model=output_table_model,
        input_model_1=input_model_1,
        input_model_2=input_model_2,
    )(test_transformation)


test_transformation_registration()
