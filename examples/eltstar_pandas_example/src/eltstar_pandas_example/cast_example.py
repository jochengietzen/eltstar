import pandas as pd
from eltstar_engine_pandas.engine import PandasEngine
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.models.base import FloatType, IntegerType
from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper
from eltstar.models.schema import Schema, SchemaField
from eltstar_pandas_example.manager import manager

if __name__ == "__main__":
    manager.load_all_plugins()

    df = pd.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6.0, 7.0, 8.0],
        }
    )

    schema = Schema(
        root=[
            SchemaField(name="bar", type_=IntegerType(), nullable=False),
            SchemaField(name="foo", type_=FloatType(), nullable=False),
        ]
    )

    df_w = DataFrameWrapper(data_frame=df, schema=schema, engine=PandasEngine)

    print(df)
    df_2 = PandasEngine.cast(schema=schema, data_frame_wrapper=DataFrameWrapper(data_frame=df))
    print(df_2.data_frame.dtypes)

    print(df_w.data_frame)
    df_w = df_w.cast()
    print(df_w.data_frame)

    # df_w_polars = PandasEngine.convert_to_engine(schema=schema, engine_identifier="polars", data_frame_wrapper=df_w)
    df_w_polars = df_w.convert_to(target_engine=PolarsEngine)
    print(df_w_polars.data_frame)

    df_w_pandas = PolarsEngine.convert_to_engine(
        schema=schema, target_engine=PandasEngine, data_frame_wrapper=df_w_polars
    )
    print(df_w_pandas.data_frame)
