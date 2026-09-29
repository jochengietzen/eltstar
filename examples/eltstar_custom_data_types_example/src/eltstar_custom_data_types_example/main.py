import polars as pl
import pyarrow as pa

from eltstar.models.base import IntegerType
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField
from eltstar_custom_data_types_example.data_types import DoubleType, MissingDataType
from eltstar_custom_data_types_example.engines import ArrowEngine, PolarsEngine

if __name__ == "__main__":
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6.0, 7.0, 8.0],
        }
    )
    table = pa.Table.from_arrays(
        arrays=[
            pa.array([1, 2, 3]),
            pa.array([6.0, 7.0, 8.0]),
        ],
        names=["foo", "bar"],
    )

    schema = Schema(
        root=[
            SchemaField(name="bar", type_=DoubleType(), nullable=False),
            SchemaField(name="foo", type_=IntegerType(), nullable=False),
        ]
    )
    schema2 = Schema(
        root=[
            SchemaField(name="bar", type_=DoubleType(), nullable=False),
            SchemaField(name="foo", type_=MissingDataType(), nullable=False),
        ]
    )

    df_w = DataFrameWrapper(data_frame=df, schema=schema, engine=PolarsEngine).cast()

    print(df_w.data_frame)
    df_a = df_w.convert_to(target_engine=ArrowEngine)
    # df_w = PolarsEngine.convert_to_engine(schema=schema, target_engine=ArrowEngine, data_frame_wrapper=df_w)
    print(df_a.data_frame)

    df_a2 = DataFrameWrapper(data_frame=table, schema=schema2, engine=ArrowEngine)
    print(df_a2.data_frame)
    try:
        df_p = df_a2.convert_to(target_engine=PolarsEngine)
        print(df_p)
    except KeyError:
        print("Could not convert to polars, as expected!")
    else:
        raise RuntimeError(
            "The conversion from arrow to polars should have failed, "
            "since polars is not aware of the 'MissingDataType'!"
        )
