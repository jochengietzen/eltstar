import math
import random
from typing import Any

from faker import Faker

from eltstar.engines.base import Engine
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.table import Table

# from eltstar.engines.polars_engine import PolarsEngine
# from eltstar.models.base import DataFrameWrapper, IntegerType, Schema, SchemaField, StringType
# from eltstar.testing.faker_type import FakerIDType, FakerIntType, FakerType
from eltstar.testing.faker_type import FakerType


class FakerManager:
    def __init__(self, faker: Faker | None = None) -> None:
        self.faker = Faker() if faker is None else faker
        self.primary_key_generation_registry: dict[str, set] = {}
        self.non_key_generation_registry: dict[str, set] = {}

    def register_faker_type(self, faker_type: "FakerType") -> "FakerManager":
        """aigen_start
        Register a FakerType's generation pool in the manager if it has a generation_id.
        aigen_end"""
        if faker_type.generation_id is not None and faker_type.generation_id not in self.non_key_generation_registry:
            # TODO: check proper typing! (V1)
            self.non_key_generation_registry[faker_type.generation_id] = set()  # type: ignore
        return self

    def generate(self, table: Table, engine: Engine, n_values: int = 100) -> DataFrameWrapper:
        """aigen_start
        Generate a DataFrameWrapper with fake data matching the given table's schema.
        aigen_end"""
        schema = table.columns.get_schema()
        columns = {
            key: col.generation.faker_type for key, col in table.columns.root.items() if col.generation is not None
        }
        return engine.dataframe_from_faker_columnar(
            data=self._generate_for_columns(columns=columns, n_values=n_values),
            schema=schema,
        )

    def _generate_for_columns(self, columns: dict[str, "FakerType"], n_values: int = 100) -> dict[str, list[Any]]:
        result = {}
        for column, faker_type in columns.items():
            if faker_type.generation_id is None:
                result[column] = [faker_type(faker_=self.faker) for _ in range(n_values)]
                continue

            if faker_type.generation_id not in self.non_key_generation_registry:
                self.non_key_generation_registry[faker_type.generation_id] = set()
            current_set = self.non_key_generation_registry[faker_type.generation_id]
            while len(current_set) < n_values:
                current_set.add(faker_type(faker_=self.faker.unique))

            percentage = (
                random.randint(
                    a=int(faker_type.reuse_percentage_min * 100 // 1),
                    b=int(faker_type.reuse_percentage_max * 100 // 1),
                )
                / 100
            )

            rand_func = random.choices if faker_type.allow_duplicate_values else random.sample
            result[column] = rand_func(population=list(current_set), k=math.ceil(n_values * percentage))
            result[column] += [
                faker_type(faker_=self.faker if faker_type.allow_duplicate_values else self.faker.unique)
                for _ in range(math.floor(n_values * (1 - percentage)))
            ]
            random.shuffle(result[column])

            # for _ in n_values:
        return result


# faker_manager = FakerManager()

# column_faker_instance = FakerIDType(generation_id="a")
# column_faker_instance_2 = FakerIntType(generation_id="b")
# column_faker_instance_3 = FakerIDType(
#     generation_id="a", allow_duplicate_values=False)

# # print(faker_manager.generate(n_values=10,
# #   columns={"test": column_faker_instance, "test2": column_faker_instance_2}))
# print(
#     faker_manager._generate_for_columns(
#         n_values=20,
#         columns={"test3": column_faker_instance_3,
#                  "test2": column_faker_instance_2},
#     )
# )
# data = faker_manager._generate_for_columns(
#     n_values=20,
#     columns={"test3": column_faker_instance_3,
#              "test2": column_faker_instance_2},
# )

# df = PolarsEngine.dataframe_from_faker_columnar(
#     data,
#     schema=Schema(
#         root=[
#             SchemaField(name="test3", type_=StringType(), nullable=False),
#             SchemaField(name="test2", type_=IntegerType(), nullable=False),
#         ]
#     ),
# )
