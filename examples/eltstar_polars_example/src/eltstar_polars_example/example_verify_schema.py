from uuid import uuid4

import polars as pl
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.exceptions import SchemaVerificationError
from eltstar.models.base import StringType, UUIDType
from eltstar.models.column import Column, Columns
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.generation import Generation
from eltstar.models.schema import Schema, SchemaField
from eltstar.testing.faker_type import FakerIDType, FakerStringType
from eltstar_polars_example.models.youtube import ReadTable, YoutubeTablePath

if __name__ == "__main__":
    tbl = ReadTable(
        path=YoutubeTablePath(
            name="youtube_tech_channels",
            date="20251120",
            time="133753",
        ),
        description="Test table",
        columns=Columns(
            root=dict(
                channel_id=Column(
                    name="channel_id",
                    data_type=UUIDType(),
                    is_primary_key=True,
                    generation=Generation(faker_type=FakerIDType()),
                ),
                channel_name=Column(
                    name="channel_name",
                    data_type=StringType(),
                    generation=Generation(faker_type=FakerStringType()),
                ),
            )
        ),
    )

    print(tbl.columns.get_schema())
    print(PolarsEngine._to_engine_schema(tbl.columns.get_schema()))

    data = pl.DataFrame(
        {
            "channel_id": [str(uuid4()), str(uuid4()), str(uuid4())],
            "channel_name": ["foo", "biz", "bar"],
        },
        schema={"channel_id": str, "channel_name": str},
    )
    print(data)

    df_w = DataFrameWrapper(data_frame=data, schema=tbl.columns.get_schema(), engine=PolarsEngine)

    df_w.verify_schema(raise_on_mismatch=True)

    tbl._verify_schema(data_frame_wrapper=df_w)

    df_w2 = DataFrameWrapper(
        data_frame=data.with_columns(pl.col("channel_name").alias("duplicate_name")), engine=PolarsEngine
    )

    try:
        tbl._verify_schema(data_frame_wrapper=df_w2)
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")

    df_w3 = DataFrameWrapper(
        data_frame=data,
        schema=Schema(
            root=[
                SchemaField(name="channel_id", type_=StringType(), nullable=False),
                SchemaField(name="channel_name", type_=StringType(), nullable=False),
            ]
        ),
        engine=PolarsEngine,
    )

    try:
        tbl._verify_schema(data_frame_wrapper=df_w3)
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")

    try:
        DataFrameWrapper(
            data_frame=data.with_columns(pl.col("channel_name").alias("duplicate_name")),
            schema=tbl.columns.get_schema(),
            engine=PolarsEngine,
            auto_verify_schema_if_given=True,
        )
    except SchemaVerificationError:
        pass
    else:
        raise RuntimeError("This should have failed in the test!")
