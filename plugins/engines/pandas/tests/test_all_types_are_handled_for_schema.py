import pandas as pd
import pytest
from eltstar_engine_pandas.engine import PandasEngine

from eltstar.models.data_frame_wrapper import DataFrameWrapper


@pytest.mark.parametrize("identifier", list(PandasEngine.registered_types[PandasEngine.engine_identifier].keys()))
def test_get_engine_schema_handles_all_registered_types_correctly(identifier):

    eltstar_type, engine_type = PandasEngine.registered_types[PandasEngine.engine_identifier][identifier]
    engine = PandasEngine()

    data_frame = pd.DataFrame({identifier: pd.Series(data=[eltstar_type.example_python_value], dtype=engine_type())})
    wrapper = DataFrameWrapper.from_data_frame(data_frame=data_frame)

    engine_schema = engine.get_engine_schema(wrapper)
    resolved_eltstar_type = (
        PandasEngine.registered_types[PandasEngine.engine_identifier]
        .get_by_engine_type(engine_schema[identifier])
        .eltstar_type
    )

    assert resolved_eltstar_type == eltstar_type
