from uuid import uuid4

import pandas as pd
from eltstar_engine_pandas.engine import PandasEngine

from eltstar.models.base import FloatType, StringType, TimestampTypeSecondsUTC
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField

if __name__ == "__main__":
    table = pd.DataFrame(
        {
            "ts": [1, 2, 3],
            "d": [pd.Timestamp("2026-01-01 01:01:01+00:00")] * 3,
            # "d": [6.0, 7.0, 8.0],
            "uuid": [str(uuid4()), str(uuid4()), str(uuid4())],
        },
    )
    print(table)

    schema = Schema(
        root=[
            SchemaField(name="ts", type_=FloatType(), nullable=False),
            SchemaField(name="d", type_=TimestampTypeSecondsUTC(), nullable=False),
            SchemaField(name="uuid", type_=StringType(), nullable=False),
        ]
    )

    df_w = DataFrameWrapper(data_frame=table, schema=schema, engine=PandasEngine).cast()

    print(df_w.data_frame)

    print(PandasEngine._to_engine_schema(schema=schema))
    print(PandasEngine._from_engine_schema(schema=table.dtypes))
