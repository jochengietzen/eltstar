from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, Optional, Protocol, TypeVar, Union

from eltstar.exceptions import ProgrammingError, SchemaVerificationError, WrapperFunctionException
from eltstar.logging import logger
from eltstar.models.data_frame_wrapper.functions.base import WrapperArgSpec, WrapperFunctionSpec

if TYPE_CHECKING:
    from eltstar.engines.base import Engine
    from eltstar.models.schema import Schema


class WrapperFunctionProtocol(Protocol):
    def __call__(self: "DataFrameWrapper", *, function_spec: WrapperArgSpec) -> "DataFrameWrapper": ...  # type: ignore


class EngineSpecificFunctionKey(NamedTuple):
    engine_identifier: str
    func_name: str


class EngineSpecificFunctionValue(NamedTuple):
    func_spec: WrapperFunctionSpec[Any]
    func_args: WrapperArgSpec
    func: WrapperFunctionProtocol


class EngineFunctionTuple(NamedTuple):
    engine_identifier: str
    function: EngineSpecificFunctionValue


class DataFrameWrapper:
    # Composition Approach
    # Registration of utilized functions
    # Plugin functionality?

    registered_wrapper_functions: ClassVar[dict[EngineSpecificFunctionKey, EngineSpecificFunctionValue]] = {}
    _loaded_plugins: ClassVar[bool] = False

    def __init__(
        self,
        data_frame: Any,
        schema: Optional["Schema"] = None,
        engine: Union["Engine", type["Engine"]] | None = None,
        auto_verify_schema_if_given: bool = False,
    ) -> None:
        self.data_frame = data_frame
        self.schema = schema
        self.engine = engine
        if auto_verify_schema_if_given and self.schema is not None and self.engine is not None:
            self.verify_schema(raise_on_mismatch=True)

    def create_with_new_data(self, data_frame: Any) -> "DataFrameWrapper":
        """aigen_start
        Return a new DataFrameWrapper with updated data but the same schema and engine.
        aigen_end"""
        return DataFrameWrapper(data_frame=data_frame, schema=self.schema, engine=self.engine)

    def verify_schema(self, raise_on_mismatch: bool = False) -> bool:
        """Verifies the given data frame against the given schema"""
        if self.engine is None:
            raise RuntimeError("Cannot verify schema if no engine is set on DataFrameWrapper!")
        if self.schema is None:
            raise RuntimeError("Cannot verify schema if no schema is set on DataFrameWrapper!")
        frame_schema = self.engine.get_engine_schema(self)
        schema_as_engine_schema = self.schema.to_engine_schema(engine_identifier=self.engine.engine_identifier)
        eqls = self.engine.engine_schemas_equals(schema_left=frame_schema, schema_right=schema_as_engine_schema)
        if raise_on_mismatch and not eqls:
            raise SchemaVerificationError(
                "The Dataframe's schema does not comply with the DataFrameWrapper's schema!"
                f"\nData Frame Schema: {frame_schema}\nGiven Schema in Wrapper: {schema_as_engine_schema}"
            )
        return eqls

    @classmethod
    def ensure_is_wrapper(
        cls, data_frame: Any, schema: Optional["Schema"] = None, engine: Union["Engine", type["Engine"]] | None = None
    ) -> "DataFrameWrapper":
        """aigen_start
        Return the input unchanged if it is already a DataFrameWrapper, otherwise wrap it.
        aigen_end"""
        if isinstance(data_frame, cls):
            return data_frame
        return cls.from_data_frame(data_frame=data_frame, schema=schema, engine=engine)

    @classmethod
    def from_data_frame(
        cls, data_frame: Any, schema: Optional["Schema"] = None, engine: Union["Engine", type["Engine"]] | None = None
    ) -> "DataFrameWrapper":
        """aigen_start
        Construct a DataFrameWrapper from a raw dataframe object.
        aigen_end"""
        return cls(data_frame=data_frame, schema=schema, engine=engine)

    def cast(self) -> "DataFrameWrapper":
        """aigen_start
        Cast the wrapped dataframe to the types defined in the schema using the registered engine.
        aigen_end"""
        if self.engine is None:
            raise ProgrammingError("Casting requires an engine to be set for the DataFrameWrapper!")
        if self.schema is None:
            raise ProgrammingError("Cannot cast dataframe, due to missing schema in wrapper.")
        return self.engine.cast(schema=self.schema, data_frame_wrapper=self)

    def convert_to(self, target_engine: type["Engine"]) -> "DataFrameWrapper":
        """aigen_start
        Convert the wrapped dataframe to a different engine's format.
        aigen_end"""
        if self.schema is None:
            raise ProgrammingError("Conversion requires a schema to be set for the DataFrameWrapper!")
        if self.engine is None:
            raise ProgrammingError("Conversion requires an engine to be set for the DataFrameWrapper!")
        return self.engine.convert_to_engine(schema=self.schema, target_engine=target_engine, data_frame_wrapper=self)

    @classmethod
    def _get_relevant_registered_wrapper_functions(
        cls, func_spec: WrapperFunctionSpec[Any] | str
    ) -> dict[str, EngineSpecificFunctionValue]:
        func_identifier = func_spec.func_name if isinstance(func_spec, WrapperFunctionSpec) else func_spec
        return {
            func_key.engine_identifier: value
            for func_key, value in cls.registered_wrapper_functions.items()
            if func_key.func_name == func_identifier
        }

    @classmethod
    def register_wrapper_function(
        cls, engine: Union["Engine", type["Engine"]], func_spec: WrapperFunctionSpec[Any], func: WrapperFunctionProtocol
    ):
        """
        Function to register a new DataFrameWrapper Function.
        This allows you to register an engine specific implementation to your given wrapper function specification.
        """
        # TODO: Ensure, that all registered functions have the same or compatible arg specs! (V1)
        # TODO: Double check, if this is still necessary or already done!
        func_key = EngineSpecificFunctionKey(engine_identifier=engine.engine_identifier, func_name=func_spec.func_name)
        if func_key in cls.registered_wrapper_functions:
            logger.info(
                f"Warning: the function {func_key.func_name} for engine {func_key.engine_identifier} "
                f"is already registered. You will overwrite it, with your own function!"
            )
        func_args = func_spec.arg_spec
        logger.info("Registering function %s for engine %s", func_spec.func_name, engine.engine_identifier)
        cls.registered_wrapper_functions[func_key] = EngineSpecificFunctionValue(
            func=func, func_spec=func_spec, func_args=func_args
        )
        exceptions: list[WrapperFunctionException] = []
        for engine_identifier, func_engine_value in cls._get_relevant_registered_wrapper_functions(
            func_spec=func_spec
        ).items():
            if not isinstance(func_engine_value.func_args, type(func_args)):
                exceptions.append(
                    WrapperFunctionException(
                        f"The function {func_spec.func_name} in the engine {engine_identifier} does "
                        "not adhere to the same function arguments, like the newly registered one!"
                        " This cannot be the case, in order to ensure compatibility between engines!"
                    )
                )
        if exceptions:
            raise ExceptionGroup(
                f"Cannot register function {func_spec.func_name} for "
                f"engine {engine.engine_identifier} due to mismatch in"
                " arg specs with existing engine/function registrations",
                exceptions,
            )

    @classmethod
    def _get_wrapper_functions_by_name(cls) -> dict[str, EngineFunctionTuple]:
        ret: dict[str, EngineFunctionTuple] = {}
        for func_key, func_value in cls.registered_wrapper_functions.items():
            ret[func_key.func_name] = EngineFunctionTuple(
                engine_identifier=func_key.engine_identifier, function=func_value
            )
        return ret

    @classmethod
    def load_all_plugins(cls) -> None:
        """
        Method to load all eltstar wrapper_function plugins
        by traversing entrypoints grouped under `eltstar.wrapper_functions`.
        """
        if cls._loaded_plugins:
            return

        for ep in entry_points(group="eltstar.wrapper_functions"):
            logger.info("Found entry point to load: %s", ep.value)
            ep.load()

        for func_name, engine_func_tuple in cls._get_wrapper_functions_by_name().items():

            def _make_func(captured_func_name, captured_engine_func_tuple):
                def _func(self, *args, **kwargs):
                    logger.info(
                        "Executing function %s for engine %s",
                        captured_func_name,
                        captured_engine_func_tuple.engine_identifier,
                    )
                    if self.engine is None:
                        raise WrapperFunctionException(
                            f"Can only execute function {captured_func_name} if wrapper is aware of its engine!"
                        )
                    func_to_execute = cls.registered_wrapper_functions[
                        EngineSpecificFunctionKey(
                            func_name=captured_func_name,
                            engine_identifier=self.engine.engine_identifier,
                        )
                    ].func
                    return func_to_execute(self, *args, **kwargs)

                return _func

            setattr(
                cls, func_name, _make_func(captured_func_name=func_name, captured_engine_func_tuple=engine_func_tuple)
            )

        cls._loaded_plugins = True


DataFrameType = TypeVar("DataFrameType")  # pylint: disable=invalid-name


# TODO: try to find proper way to handle pydantic and mypy
class TypedDataFrameWrapper[DataFrameT: DataFrameType](DataFrameWrapper):  # type: ignore
    def __init__(self, data_frame: DataFrameT, schema: Optional["Schema"] = None) -> None:
        super().__init__(data_frame=data_frame, schema=schema)
        self.data_frame: DataFrameT = data_frame
