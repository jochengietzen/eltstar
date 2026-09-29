from typing import Any, ClassVar, TypeGuard

import pandas as pd
import pyarrow as pa
from pandas.io.json._table_schema import build_table_schema

from eltstar.engines.base import Engine, EngineSpecificDataType
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar.models.base import (
    BooleanType,
    DateType,
    FloatType,
    IntegerType,
    StringType,
    TimestampTypeSecondsUTC,
)
from eltstar.models.data_frame_wrapper import DataFrameWrapper, TypedDataFrameWrapper
from eltstar.models.schema import Schema, SchemaField


def pandas_frame(frame: Any) -> TypeGuard[pd.DataFrame]:
    return isinstance(frame, pd.DataFrame)


class PandasEngine(Engine):
    engine_identifier: ClassVar[str] = "pandas"
    internal_schema_type: ClassVar[type[dict[Any, Any]]] = dict

    @classmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:

        return Schema(
            [
                SchemaField(
                    name=key,
                    type_=cls.registered_types[cls.engine_identifier]
                    .get_by_engine_type(engine_type=value)
                    .eltstar_type,
                    nullable=True,
                )
                for key, value in schema.items()
            ]
        )

    @classmethod
    def _to_engine_schema(cls, schema: Schema) -> dict[Any, Any]:
        return {
            schema_field.name: cls.registered_types[cls.engine_identifier]
            .get_by_eltstar_type(eltstar_obj=schema_field.type_)
            .engine_type()
            for schema_field in schema.root
        }

    @classmethod
    def get_engine_schema(cls, data_frame_wrapper: DataFrameWrapper) -> dict[Any, Any]:
        value_mappings = {
            "integer": "int",
            "string": "str",
            "boolean": "bool",
            "number": "float",
        }
        data_frame = data_frame_wrapper.data_frame
        schema = {}
        for field in build_table_schema(data_frame)["fields"]:
            if field["name"] == "index":
                continue
            if field["type"] == "datetime":
                schema[field["name"]] = str(data_frame[field["name"]].dtype)
            else:
                schema[field["name"]] = value_mappings.get(field["type"], field["type"])
        return schema

    @classmethod
    def cast(cls, schema: Schema, data_frame_wrapper: DataFrameWrapper) -> DataFrameWrapper:
        data_frame: pd.DataFrame = data_frame_wrapper.data_frame
        return data_frame_wrapper.create_with_new_data(
            data_frame=data_frame.astype(cls._to_engine_schema(schema=schema))
        )

    @classmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> DataFrameWrapper:

        engine_schema = cls._to_engine_schema(schema=schema)

        if set(engine_schema.keys()) != set(data.keys()):
            raise ValueError(
                f"Incosistent column names - data columns: {list(data.keys())} - schema keys: {list(schema.keys())}"
            )

        return DataFrameWrapper.from_data_frame(
            pd.DataFrame({key: pd.Series(data=column, dtype=engine_schema[key]) for key, column in data.items()})
        )

    @classmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: DataFrameWrapper
    ) -> TypedDataFrameWrapper[ArrowEngine]:
        """Converts the engine specific dataframe wrapper to an arrow object"""
        data_frame: pd.DataFrame = data_frame_wrapper.data_frame
        return DataFrameWrapper(
            data_frame=pa.Table.from_pandas(data_frame, schema=ArrowEngine._to_engine_schema(schema)),
            schema=schema,
            engine=ArrowEngine,
        )

    @classmethod
    def convert_from_arrow(
        cls, schema: Schema, data_frame_wrapper: TypedDataFrameWrapper[ArrowEngine]
    ) -> DataFrameWrapper:
        """Converts the engine specific dataframe wrapper to an arrow object"""
        data_frame: pa.Table = data_frame_wrapper.data_frame
        return DataFrameWrapper(
            data_frame=data_frame.to_pandas(),
            schema=schema,
            engine=cls,
        )

    @classmethod
    def setup(cls):
        Schema.register_from_engine_schema(
            engine_identifier=cls.engine_identifier,
            engine_schema_type=cls.internal_schema_type,
            from_method=cls._from_engine_schema,
            to_method=cls._to_engine_schema,
        )
        # We are using the string representation here as we couldn't manage to get it working with the actual dtype
        cls.register_data_type(
            data_type=IntegerType(),
            engine_type=EngineSpecificDataType(str_repr="int"),
        )
        cls.register_data_type(
            data_type=FloatType(),
            engine_type=EngineSpecificDataType(
                str_repr="float",
            ),
        )
        cls.register_data_type(
            data_type=StringType(),
            engine_type=EngineSpecificDataType(
                str_repr="str",
            ),
        )
        cls.register_data_type(
            data_type=BooleanType(),
            engine_type=EngineSpecificDataType(
                str_repr="bool",
            ),
        )
        # cls.register_data_type(
        #     data_type=TimestampTypeSecondsNTZ(),
        #         engine_type=EngineSpecificDataType(dtype_class=pd.DatetimeTZDtype(
        #             unit=TimestampTypeSecondsNTZ.unit,
        #             tz=TimestampTypeSecondsNTZ.time_zone,
        #         ),
        #     )
        # )
        for base in ["ns", "us"]:
            timestamp_type_seconds_utc = TimestampTypeSecondsUTC(unit=base)
            timestamp_type_seconds_utc.identifier = timestamp_type_seconds_utc.identifier.replace("_ns", "_" + base)
            cls.register_data_type(
                data_type=timestamp_type_seconds_utc,
                engine_type=EngineSpecificDataType(str_repr=f"datetime64[{base}, UTC]"),
            )
        cls.register_data_type(
            data_type=DateType(),
            engine_type=EngineSpecificDataType(
                str_repr="datetime64[us]",
            ),
        )
        # cls.register_data_type(
        #     data_type=BinaryType(),
        #         engine_type=EngineSpecificDataType(dtype_class=pd.Bin,
        #     )
        # )
        # cls.register_data_type(
        #     data_type=DecimalType28(),
        #         # engine_type=EngineSpecificDataType(dtype_class=pd.Decimal,
        #         engine_type=EngineSpecificDataType(dtype_class=lambda: pd.Decimal(precision=DecimalType28.precision, scale=DecimalType28.scale),
        #     )
        # )
        # cls.register_data_type(
        #     data_type=UUIDType(),
        #         engine_type=EngineSpecificDataType(dtype_class=pd.String,
        #     )
        # )


PandasEngine.setup()
