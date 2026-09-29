# from eltstar.models.expectations import RowLevelColumnExpectation


import datetime
import decimal
import uuid

from eltstar.models.data_type import DataType


class IntegerType(DataType):
    identifier: str = "integer"
    example_python_value: int = 1


class FloatType(DataType):
    identifier: str = "float"
    example_python_value: float = 1.1


class StringType(DataType):
    identifier: str = "string"
    example_python_value: str = "example"


class BooleanType(DataType):
    identifier: str = "boolean"
    example_python_value: bool = True


class TimestampTypeBase(DataType):
    unit: str
    time_zone: str | None


class TimestampTypeSecondsNTZ(TimestampTypeBase):
    identifier: str = "timestamp_ntz_ns"
    example_python_value: datetime.datetime = datetime.datetime(2024, 1, 1, tzinfo=None)
    unit: str = "ns"
    time_zone: str | None = None


class TimestampTypeSecondsUTC(TimestampTypeBase):
    identifier: str = "timestamp_utc_ns"
    example_python_value: datetime.datetime = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)
    unit: str = "ns"
    time_zone: str = "UTC"


class DateType(DataType):
    identifier: str = "date"
    example_python_value: datetime.date = datetime.date(2024, 1, 1)


class BinaryType(DataType):
    identifier: str = "binary"
    example_python_value: bytes = b"example"
    length: int = -1


class DecimalType28(DataType):
    identifier: str = "decimal_28"
    example_python_value: decimal.Decimal = decimal.Decimal(1)
    precision: int = 28
    scale: int = 0


class UUIDType(DataType):
    identifier: str = "uuid"
    example_python_value: uuid.UUID = uuid.uuid4()
