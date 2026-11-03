from uuid import uuid4

import polars as pl
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.base import DecimalType28, StringType, TimestampTypeSecondsNTZ
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField

if __name__ == "__main__":
    table = pl.DataFrame(
        {
            "ts": [1, 2, 3],
            "d": [6.0, 7.0, 8.0],
            "uuid": [str(uuid4()), str(uuid4()), str(uuid4())],
        }
    )

    schema = Schema(
        root=[
            SchemaField(name="ts", type_=TimestampTypeSecondsNTZ(), nullable=False),
            SchemaField(name="d", type_=DecimalType28(), nullable=False),
            SchemaField(name="uuid", type_=StringType(), nullable=False),
        ]
    )

    df_w = DataFrameWrapper(data_frame=table, schema=schema, engine=PolarsEngine).cast()

    print(df_w.data_frame)

    print(PolarsEngine._from_engine_schema(schema=table.schema))
    print(PolarsEngine._to_engine_schema(schema=schema))
