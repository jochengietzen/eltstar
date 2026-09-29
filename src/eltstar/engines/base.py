from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Protocol, Self, TypeVar

from pydantic import model_validator

from eltstar.base_model import BaseModel, DictRootModel
from eltstar.exceptions import ProgrammingError
from eltstar.models.data_type import DataType
from eltstar.models.schema import Schema
from eltstar.utils import coalesce

if TYPE_CHECKING:
    from eltstar.engines.eltstar_arrow_engine import ArrowEngine
    from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper, TypedDataFrameWrapper

ARROW_ENGINE_IDENTIFIER = "arrow"


class ReadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> "DataFrameWrapper": ...


class WriteMethod(Protocol):
    def __call__(self, *args: Any, data_frame: "DataFrameWrapper", **kwargs: Any) -> None: ...


# class ConversionMethod(Protocol):
#     def __call__(
#         self, *args: Any, data_frame: "DataFrameWrapper", schema: Schema, **kwargs: Any
#     ) -> "DataFrameWrapper": ...


# class ConversionEngineTuple(NamedTuple):
#     source_engine_identifier: str
#     target_engine_identifier: str


class EngineSpecificDataType(BaseModel):
    str_repr: str | None = None
    dtype_class: type[Any] | Any | None = None
    lambda_class: Callable[[], type[Any]] | None = None

    @model_validator(mode="after")
    def require_one_of(self) -> Self:
        if self.str_repr is None and self.dtype_class is None and self.lambda_class is None:
            raise ValueError("At least one of str_repr and dtype_class and lambda_class is required!")

        return self

    def __call__(self, *args: Any, **kwds: Any) -> str | Any:
        value = coalesce(self.dtype_class, self.lambda_class, self.str_repr)
        if value is None:
            raise ProgrammingError(
                f"This should never happen! None of the EngineSpecificDataTypes had any value set! {str(self)}"
            )
        if callable(value):
            return value(*args, **kwds)
        return value


class RegisteredTypeTuple(NamedTuple):
    eltstar_type: DataType
    engine_type: EngineSpecificDataType


class RegisteredTypeLookup(DictRootModel[str, RegisteredTypeTuple]):
    root: dict[str, RegisteredTypeTuple]

    @property
    def _by_eltstar_type(self) -> dict[DataType, RegisteredTypeTuple]:
        return {x.eltstar_type: x for x in self.root.values()}

    def get_by_eltstar_type(self, eltstar_obj: str | DataType) -> RegisteredTypeTuple:
        if isinstance(eltstar_obj, str):
            return self.root[eltstar_obj]
        return self._by_eltstar_type[eltstar_obj]

    def get_by_engine_type(self, engine_type: Any) -> RegisteredTypeTuple:
        for rtt in self.root.values():
            if engine_type == rtt.engine_type():
                return rtt
        raise KeyError(
            f"Engine type {type(engine_type)}: {str(engine_type)} was not found in the registered data types"
        )

    def __getitem__(self, key):
        return self.root[key]


class Engine(BaseModel):
    # Defines
    # - Schema
    # - DatenTypen
    # - DataFrame (DataFrameWrapper)
    # - read
    # - write
    engine_identifier: ClassVar[str]
    internal_schema_type: ClassVar[type[Any]]
    registered_types: ClassVar[dict[str, RegisteredTypeLookup]] = {}
    # TODO: Switch other registragtion variables to use the named tuple, as well (V3?)
    # registered_conversion_methods: ClassVar[dict[ConversionEngineTuple, ConversionMethod]] = {}

    @classmethod
    def register_data_type(cls, data_type: DataType, engine_type: EngineSpecificDataType | type[Any]):
        """aigen_start
        Register a DataType by mapping its engine-native type to the DataType class for this engine.
        aigen_end"""
        if not isinstance(engine_type, EngineSpecificDataType):
            engine_type = EngineSpecificDataType(dtype_class=engine_type)
        if cls.engine_identifier not in cls.registered_types:
            cls.registered_types[cls.engine_identifier] = RegisteredTypeLookup(root={})
        cls.registered_types[cls.engine_identifier].root[data_type.identifier] = (  # pylint: disable=protected-access
            RegisteredTypeTuple(
                eltstar_type=data_type,
                engine_type=engine_type,
            )
        )

    @classmethod
    @abstractmethod
    def _from_engine_schema(cls, schema: Any) -> Schema:
        pass

    @classmethod
    @abstractmethod
    def _to_engine_schema(cls, schema: Schema) -> Any:
        pass

    @classmethod
    @abstractmethod
    def cast(cls, schema: Schema, data_frame_wrapper: "DataFrameWrapper") -> "DataFrameWrapper":
        """aigen_start
        Cast the dataframe in the wrapper to the types defined by the given schema.
        aigen_end"""

    @classmethod
    @abstractmethod
    def dataframe_from_faker_columnar(cls, data: dict[str, list[Any]], schema: Schema) -> "DataFrameWrapper":
        """aigen_start
        Build a DataFrameWrapper from a columnar dict of fake data with the given schema.
        aigen_end"""

    @classmethod
    @abstractmethod
    def convert_to_arrow(
        cls, schema: Schema, data_frame_wrapper: "DataFrameWrapper"
    ) -> "TypedDataFrameWrapper[ArrowEngine]":
        """Converts the engine specific dataframe wrapper to an arrow object"""

    @classmethod
    @abstractmethod
    def get_engine_schema(cls, data_frame_wrapper: "DataFrameWrapper") -> Any:
        """Extracts the engine specific dataframe schema of a given data_frame_wrapper"""

    @classmethod
    def engine_schemas_equals(cls, schema_left: Any, schema_right: Any) -> bool:
        """Returns true iff schemas are equal"""
        return schema_left == schema_right

    @classmethod
    @abstractmethod
    def convert_from_arrow(
        cls, schema: Schema, data_frame_wrapper: "TypedDataFrameWrapper[ArrowEngine]"
    ) -> "DataFrameWrapper":
        """Converts the engine specific dataframe wrapper from an arrow dataframe wrapper"""

    @classmethod
    def convert_to_engine(
        cls, schema: Schema, target_engine: type["Engine"], data_frame_wrapper: "DataFrameWrapper"
    ) -> "DataFrameWrapper":
        """aigen_start
        Convert the given DataFrameWrapper to a different engine using a registered conversion function.
        aigen_end"""
        source_engine = data_frame_wrapper.engine
        if source_engine is None:
            raise ProgrammingError("Can only convert dataframes that are engine aware!")
        if source_engine.engine_identifier == target_engine.engine_identifier:
            return data_frame_wrapper
        if source_engine.engine_identifier == ARROW_ENGINE_IDENTIFIER:
            arrow_wrapper = data_frame_wrapper
        else:
            arrow_wrapper = source_engine.convert_to_arrow(schema=schema, data_frame_wrapper=data_frame_wrapper)
        if target_engine.engine_identifier == ARROW_ENGINE_IDENTIFIER:
            return arrow_wrapper
        return target_engine.convert_from_arrow(schema=schema, data_frame_wrapper=arrow_wrapper)  # type: ignore


EngineType = TypeVar("EngineType", bound=Engine)  # pylint: disable=invalid-name
