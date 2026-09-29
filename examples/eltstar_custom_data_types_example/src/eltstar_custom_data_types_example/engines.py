import polars as pl
import pyarrow as pa
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.engines.base import EngineSpecificDataType
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar_custom_data_types_example.data_types import DoubleType, MissingDataType

ArrowEngine.register_data_type(
    data_type=DoubleType(),
    engine_type=EngineSpecificDataType(dtype_class=pa.float64()),
)
ArrowEngine.register_data_type(
    data_type=MissingDataType(),
    engine_type=EngineSpecificDataType(dtype_class=pa.float64()),
)
PolarsEngine.register_data_type(
    data_type=DoubleType(),
    engine_type=EngineSpecificDataType(dtype_class=pl.Float64),
)
