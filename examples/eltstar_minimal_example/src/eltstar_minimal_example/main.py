### aigen_start
"""A minimal, fully working eltstar pipeline: one schema, one transformation.

Every other example under `examples/` shows a richer, more realistic setup
(multiple tables, joins, multiple engines, deployment generation). This one
strips everything down to the smallest thing that still touches every core
eltstar concept exactly once, so it works as a five-minute overview:

  1. TablePath   - resolve a table's physical location
  2. Table       - engine-agnostic read()/write()
  3. Columns     - the schema, plus how to fake it for testing
  4. Transformation - a plain function registered against tables
  5. RuntimeConfig/EnvironmentConfig - eltstar's config-loading pattern
  6. FakerManager    - schema-valid fake data generation
  7. Lineage (bonus) - free once transformations are registered
"""

from pathlib import Path
from typing import Any

import polars as pl
from eltstar_engine_polars.engine import PolarsEngine

from eltstar.config import EnvironmentConfig, RuntimeConfig
from eltstar.engines.base import EngineType
from eltstar.models.base import IntegerType, StringType
from eltstar.models.column import Column, Columns
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.models.generation import Generation
from eltstar.models.table import Table
from eltstar.models.table_path import TablePath
from eltstar.testing.faker_manager import FakerManager
from eltstar.testing.faker_type import FakerIDType, FakerIntType, FakerStringType
from eltstar.transformation import manager

DATA_DIR = Path(__file__).parents[2] / "data"


# 1. TablePath: tells eltstar how to resolve a table's physical location.
class LocalCsvPath(TablePath):
    name: str

    def full_path(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs: dict[str, Any],
    ) -> str:
        return str(DATA_DIR / f"{self.name}.csv")


# 2. Table: engine-agnostic read/write, backed here by plain polars CSV I/O.
class CsvTable(Table):
    path: LocalCsvPath
    engine: type[EngineType] = PolarsEngine

    def read(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs: Any,
    ) -> DataFrameWrapper:
        df = pl.read_csv(
            source=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config)
        )
        return DataFrameWrapper(data_frame=df, schema=self.get_schema(), engine=self.engine)

    def write(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs: Any,
    ) -> "CsvTable":
        data_frame_wrapper.data_frame.write_csv(
            file=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config)
        )
        return self


# 3. Columns/Schema: the shape of the data, plus how to fake it for testing.
person_columns = Columns(
    root=dict(
        id=Column(
            name="id",
            data_type=StringType(),
            is_primary_key=True,
            generation=Generation(faker_type=FakerIDType()),
        ),
        name=Column(name="name", data_type=StringType(), generation=Generation(faker_type=FakerStringType())),
        age=Column(
            name="age",
            data_type=IntegerType(),
            generation=Generation(faker_type=FakerIntType(min_val=18, max_val=90)),
        ),
    )
)

people = CsvTable(path=LocalCsvPath(name="people"), columns=person_columns, description="Raw people records")
adults = CsvTable(path=LocalCsvPath(name="adults"), columns=person_columns, description="People aged 30 or over")


# 4. Transformation: a plain function, registered against its input/output tables.
@manager.register_transformation(output_table_model=adults, people=people)
def filter_adults(people: DataFrameWrapper) -> DataFrameWrapper:
    return people.create_with_new_data(data_frame=people.data_frame.filter(pl.col("age") >= 30))


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 5. RuntimeConfig/EnvironmentConfig: eltstar's registration-based config loading.
    RuntimeConfig.register_load_method("local", RuntimeConfig)
    EnvironmentConfig.register_load_method("local", lambda: EnvironmentConfig(env="local"))
    manager.load_runtime_config(runtime_class_type=RuntimeConfig, situation_identifier="local")
    manager.load_environment_config(environment_class_type=EnvironmentConfig, situation_identifier="local")

    runtime_config = RuntimeConfig()
    environment_config = EnvironmentConfig(env="local")

    # 6. Generate schema-valid fake data and write it, standing in for a real ingestion step.
    fake_people = FakerManager().generate(table=people, engine=PolarsEngine(), n_values=20)
    people.write(runtime_config=runtime_config, environment_config=environment_config, data_frame_wrapper=fake_people)

    # 7. Execute every registered transformation and write its output: reads `people`, casts it
    #    to the schema, calls filter_adults(), then writes the result to the `adults` table.
    manager.execute_all_transformations()

    # 8. Round-trip: read the written output back from disk.
    print(adults.read(runtime_config=runtime_config, environment_config=environment_config).data_frame)

    # Bonus: eltstar tracks lineage across registered transformations for free.
    print(manager.lineage.graph.edges)
### aigen_end
