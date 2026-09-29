from collections.abc import Callable
from typing import Any, ClassVar, Self

from eltstar.base_model import BaseModel, ListRootModel
from eltstar.models.data_type import DataType


class SchemaField(BaseModel):
    name: str
    type_: DataType
    nullable: bool

    def __lt__(self, other: Self) -> bool:
        return self.name < other.name


# class SchemaStruct(BaseModel):
#     name: str
#     fields: list[Union["SchemaStruct", SchemaField]]
#     nullable: bool


# class Schema(RootModel[list[SchemaStruct | SchemaField]]):
class Schema(ListRootModel[SchemaField]):
    _from_engine_methods: ClassVar[dict[str, tuple[type[Any], Callable[[Any], "Schema"]]]] = {}
    _to_engine_methods: ClassVar[dict[str, Callable[["Schema"], Any]]] = {}
    # provides schema for a given instance of Columns
    # Compostition Approach

    @classmethod
    def register_from_engine_schema(
        cls,
        engine_identifier: str,
        engine_schema_type: type[Any],
        from_method: Callable[[Any], "Schema"],
        to_method: Callable[["Schema"], Any],
    ):
        """aigen_start
        Register conversion functions between the engine's native schema format and the eltstar Schema.
        aigen_end"""
        if cls._from_engine_methods is None:
            cls._from_engine_methods = {}
        cls._from_engine_methods[engine_identifier] = (engine_schema_type, from_method)
        cls._to_engine_methods[engine_identifier] = to_method

    @classmethod
    def from_engine_schema(cls, schema: Any) -> "Schema":
        """aigen_start
        Convert an engine-native schema object into a eltstar Schema by dispatching on its type.
        aigen_end"""
        for schema_type, func in cls._from_engine_methods.values():
            if isinstance(schema, schema_type):
                return func(schema=schema)  # type: ignore
        raise RuntimeError(f"Engine for type {type(schema)} not defined!")

    def to_engine_schema(self, engine_identifier: str) -> Any:
        """aigen_start
        Convert this eltstar Schema to the engine-native schema format for the given engine identifier.
        aigen_end"""
        func = self._to_engine_methods.get(engine_identifier, None)
        if func is None:
            raise RuntimeError(f"Engine {engine_identifier} has no to engine schema defined!")
        return func(schema=self)  # type: ignore

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.equals(other, ignore_order=True)

    def equals(self, other: Self, ignore_order: bool) -> bool:
        """Returns True iff all of the schemafields are equal"""
        self_fields = sorted(self.root) if ignore_order else self.root
        other_fields = sorted(other.root) if ignore_order else other.root

        return self_fields == other_fields
