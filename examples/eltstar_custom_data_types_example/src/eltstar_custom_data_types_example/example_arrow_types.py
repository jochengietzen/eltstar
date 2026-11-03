from uuid import uuid4

import pyarrow as pa

from eltstar.models.base import DecimalType28, TimestampTypeSecondsNTZ, UUIDType
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField
from eltstar_custom_data_types_example.engines import ArrowEngine

if __name__ == "__main__":
    table = pa.Table.from_arrays(
        arrays=[
            pa.array([1, 2, 3]),
            pa.array([6.0, 7.0, 8.0]),
            pa.array([uuid4(), uuid4(), uuid4()]),
        ],
        names=["ts", "d", "uuid"],
    )

    schema = Schema(
        root=[
            SchemaField(name="ts", type_=TimestampTypeSecondsNTZ(), nullable=False),
            SchemaField(name="d", type_=DecimalType28(), nullable=False),
            SchemaField(name="uuid", type_=UUIDType(), nullable=False),
        ]
    )

    df_w = DataFrameWrapper(data_frame=table, schema=schema, engine=ArrowEngine).cast()

    print(df_w.data_frame)

    print(ArrowEngine._from_engine_schema(schema=table.schema))
    print(ArrowEngine._to_engine_schema(schema=schema))
