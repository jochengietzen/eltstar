import polars as pl
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.base import FloatType, IntegerType
from eltstar.models.schema import Schema, SchemaField
from eltstar.models.data_frame_wrapper.functions.join import JoinArgSpec
from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper

if __name__ == "__main__":
    df = pl.DataFrame(
        {
            "id_1": [1, 2, 3],
            "id_2": [4, 5, 6],
            "bar": [6.0, 7.0, 8.0],
        }
    )
    df_2 = pl.DataFrame(
        {
            "id_1": [0, 2, 5],
            "id_2": [5, 5, 5],
            "bar": [6.0, 7.0, 8.0],
        }
    )

    schema = Schema(
        root=[
            SchemaField(name="id_1", type_=IntegerType(), nullable=False),
            SchemaField(name="id_2", type_=IntegerType(), nullable=False),
            SchemaField(name="bar", type_=FloatType(), nullable=False),
        ]
    )

    df_w1 = DataFrameWrapper(data_frame=df, schema=schema, engine=PolarsEngine())
    df_w2 = DataFrameWrapper(data_frame=df_2, schema=schema, engine=PolarsEngine())

    print(
        df_w1.join(
            function_spec=JoinArgSpec(other=df_w2, left_on=["id_1", "id_2"], right_on=["id_1", "id_2"], how="inner"),
        ).data_frame
    )
