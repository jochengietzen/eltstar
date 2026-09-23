from eltstar.models.data_type import DataType


class DoubleType(DataType):
    identifier: str = "double"
    example_python_value: float = 1.2


class MissingDataType(DataType):
    identifier: str = "missing"
    example_python_value: None = None
