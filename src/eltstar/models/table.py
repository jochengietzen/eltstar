from abc import abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

# from pydantic import Field
from eltstar.base_model import BaseModel
from eltstar.config import (
    EnvironmentConfigType,
    RuntimeConfigType,
)
from eltstar.exceptions import SchemaVerificationError
from eltstar.models.column import Columns
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.schema import Schema
from eltstar.models.table_path import TablePath

if TYPE_CHECKING:
    from eltstar.engines.base import EngineType
# from eltstar.models.expectations import RowLevelTableExpectation

TablePathType = TypeVar("TablePathType", bound=TablePath)  # pylint: disable=invalid-name
# TableExpectationType = TypeVar("TableExpectationType", bound=RowLevelTableExpectation)  # pylint: disable=invalid-name


class Table(BaseModel):
    path: TablePathType  # type: ignore # TODO: try to find proper way to handle pydantic and mypy
    columns: Columns
    engine: type["EngineType"]  # type: ignore # TODO: try to find proper way to handle pydantic and mypy
    description: str
    # Assumption: on table-level we only have expectations,
    # there is no equivalent to constraints on column level
    # Possibliy we do not need the generic type.
    # expectations: list[TableExpectationType] = Field(default_factory=list)

    @abstractmethod
    def read(
        self,
        *args: Any,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        **kwargs: Any,
    ) -> DataFrameWrapper:
        """aigen_start
        Read data from the configured source path and return it as a DataFrameWrapper.
        aigen_end"""
        # TODO: Make sure that we set the engine to the attribute, if no engine was given (V1)

    @abstractmethod
    def write(
        self,
        *args: Any,
        runtime_config: RuntimeConfigType,
        environment_config: EnvironmentConfigType,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs: Any,
    ) -> "Table":
        """aigen_start
        Write the given DataFrameWrapper to the configured output path and return self.
        aigen_end"""
        # TODO: Make sure that we set the engine to the attribute, if no engine was given (V1)

    def get_schema(self, by_name: bool = False) -> Schema:
        """Convenience function to retrieve the Column based schema"""
        return self.columns.get_schema(by_name=by_name)

    def _verify_schema(self, data_frame_wrapper: DataFrameWrapper) -> None:
        if data_frame_wrapper.engine is None:
            raise RuntimeError("Cannot verify schema without engine on data frame wrapper!")
        expected_eltstar_schema = self.columns.get_schema()
        expected_schema = data_frame_wrapper.engine._to_engine_schema(schema=expected_eltstar_schema)  # pylint: disable=protected-access
        actual_schema = data_frame_wrapper.engine.get_engine_schema(data_frame_wrapper)

        base_msg = "of the given data frame does not comply with the expected schema for the table!"
        if not data_frame_wrapper.engine.engine_schemas_equals(actual_schema, expected_schema):
            raise SchemaVerificationError(
                f"The schema {base_msg}\nActual: {actual_schema}\nExpected: {expected_schema}"
            )

        actual_eltstar_schema = data_frame_wrapper.schema
        if actual_eltstar_schema is None:
            return

        if not expected_eltstar_schema.equals(actual_eltstar_schema, ignore_order=True):
            raise SchemaVerificationError(
                f"The eltstar schema {base_msg}\nActual: {actual_eltstar_schema}\nExpected: {expected_eltstar_schema}"
            )

    def cast(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        """Convenience function to cast the dataframe into the actual table"""
        dfw = DataFrameWrapper(
            data_frame=data_frame_wrapper.data_frame,
            schema=self.columns.get_schema(by_name=False),
            engine=data_frame_wrapper.engine,
        )
        return dfw.cast()

    def validate_table_schema(self, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        """aigen_start
        Verify the schema and cast the given DataFrameWrapper according to this table's schema.
        aigen_end"""
        self._verify_schema(data_frame_wrapper)

        return self.cast(data_frame_wrapper)
