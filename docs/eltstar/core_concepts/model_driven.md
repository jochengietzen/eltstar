# Model driven tables

In eltstar one defines their tables as pydantic model instances.

A table always belongs to a possible set of tables, usually belonging to a system or a groupable set of tables.
Let's take the example of our youtube tables. Youtube would be our "system" and multiple tables exist in this system.

The system defines, how we can load/read tables, but also write tables.

Additionally, a table needs to have a table path definition. A table path is required, so you can load your table in different environments and runtime environments.

Let's take a closer look into the youtube example.

## TablePath

```python
from eltstar.models.base import TablePath
from eltstar.config import EnvironmentConfig, RuntimeConfig

class YoutubeTablePath(TablePath):
    date: str
    time: str
    name: str

    def full_path(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: MyEnvironmentConfig,
        **kwargs: dict[str, Any],
    ) -> str:
        return f"/workspace/data/{environment_config.env}/{self.name}_{self.date}_{self.time}.csv"
```

Let's quickly explore what is happening here:

We inherit from the imported Class Table Path and define some attributes of this pydantic model, that are relevant to your table paths. Here we have a date, a time and a name.
As the base/parent class has the abstractmethod full_path, we need to provide an implementation for said function.
Based on the automatically passed runtime configuration, environment configuration and the model's attributes date, time and name we can now construct the table's full path. 

If you cannot imagine yet, how to use that, try to think of a postgresql or metastore, with 3 path components (e.g. db, schema and table name). You could define the db as a fixed value, the schema as part of your environment configuration and the table name depending on your table.
E.g.:
```python
...
class MyEnvironmentConfig(EnvironmentConfig):
    env: str # (1)!

class PGTable(TablePath):
    db_name: str
    table_name: str # (2)!
    
    def full_path(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: MyEnvironmentConfig,
        **kwargs: dict[str, Any],
    ) -> str:
        return f"{self.db_name}.{environment_config.env}.{self.table_name}"
```

1. :man_raising_hand: This is not necessary, as the EnvironmentConfig already defines the env attribute. 
This is only shown for clarity.
2. You can utilise any name you want, as long as you stay true to your naming.

Now that we have a table path, we can continue with the definition of our System level table behaviour, by defining the Table's class/model

## System's Table

This class has a few more necessities and has to inherit from the class Table.

```python
from eltstar.models.table import Table
from eltstar.engines.base import EngineType
from eltstar_engine_polars.engine import PolarsEngine
from eltstar.config import EnvironmentConfig, RuntimeConfig
from eltstar.models.data_frame_wrapper import DataFrameWrapper

class YoutubeTable(Table):
    path: YoutubeTablePath # (1)!
    engine: type[EngineType] = PolarsEngine # (2)!

    def read(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs,
    ) -> DataFrameWrapper:
        return DataFrameWrapper(
            data_frame=pl.read_csv(
                *args,
                source=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
                **kwargs,
            ),
            schema=self.get_schema(),
            engine=self.engine,
        )

    def write(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs,
    ) -> "YoutubeTable":
        return data_frame_wrapper.data_frame.write_csv(
            *args,
            file=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
            **kwargs,
        )
```

1. This is the table path configuration from earlier.
2. This defines the engine you use for this table. (Yes, this theoretically allows you to later mix different engines - to a certain extent.)

We now have a couple of things to unwrap in this block.

- First, the latest concept with the table path - no need to reiterate for now.
- Then we have the read and write methods defined. These depend on your engine, which is why we highly recommend to define the engine as an attribute for the class and not at instantiation. :material-information-outline:{ title="If you want the flexibility to use the same model with various engines, you could provide multiple read/write cases (if/elif/else blocks) for the desired engines. This gives you the flexibility to set the model's engine dynamically or at instantiation time." }


## Table instances

After we have the basics in definition out of the way, we can now write our actual table instances.

```python
tech_channels = YoutubeTable(
    path=YoutubeTablePath(
        name="youtube_tech_channels", # (1)!
        date="20251120",
        time="133753",
    ),
    columns=Columns( # (2)!
        root=dict(
            channel_id=Column( # (3)!
                name="channel_id", #(4)!
                data_type=StringType(), # (5)!
                is_primary_key=True, # (6)!
                generation=Generation(faker_type=FakerStringType()), # (7)!
            ),
            channel_name=Column(
                name="channel_name",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            description=Column(
                name="description",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            subscribers=Column(
                name="subscribers",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            total_views=Column(
                name="total_views",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            total_videos=Column(
                name="total_videos",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            created_date=Column(
                name="created_date",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            country=Column(
                name="country",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            scraped_at=Column(
                name="scraped_at",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
        )
    ),
    description="Youtube tech channels",
)
```

1. We remember the path definition from earlier. Here we see, how we actually use the TablePath object. The name is the actual name (prefix) of the csv we use in this example.
2. Now we get to the Column definition. Columns is a RootModel of a dictionary that builds from names (strings) to Column objects. This is the basis for all Schema related things.
3. This is the first column definition. channel_id is the key (the name we will use internally) and the Column object defines various information for later.
4. The name of the column. 
5. The data type definition is essential to the eltstar logic. We use this info for the Schemas and we cast data frames into the given type etc.
6. This attribute indicates a primary column (think of an ER Diagram) of a table. Defaulting to false, we recommend providing primary key information, as we can utilise these later on in the fake data generation etc.
7. The generation attribute requires a Generation object. This defines the type and therefore logic, how we create fake data for your smoke tests. E.g. by creating values in a certain range or other restrictions.


**Careful!** Why do we define the name twice? 
Once as a key and once as the Column's attribute `name`?<br/>
Often times we deal with external systems we need to read from, sometimes even write to. In these cases, we often encounter different naming conventions, that might even be illegal in our context :material-asterisk:{ title="e.g. an api might allow spaces in the column names, but our engine might not allow that; or we have a system with all lower case names and the source system uses PascalCasing" }. This is the reason, we define 2 names for the columns. 

Note, that the keys are the names we will use in the system running the engine.


Since the individual Column objects are instances, you can obviously reuse them in several table definitions.

<!---aigen_start-->
## Built-in data types

`data_type=StringType()` and `data_type=IntegerType()` are only two of the `DataType`s that ship with eltstar (in `eltstar.models.base`):

| Class | Example Python value |
| --- | --- |
| `StringType` | `"example"` |
| `IntegerType` | `1` |
| `FloatType` | `1.1` |
| `BooleanType` | `True` |
| `DateType` | `datetime.date(2024, 1, 1)` |
| `TimestampTypeSecondsNTZ` | `datetime.datetime(2024, 1, 1)` (no timezone) |
| `TimestampTypeSecondsUTC` | `datetime.datetime(2024, 1, 1, tzinfo=UTC)` |
| `BinaryType` | `b"example"` |
| `DecimalType28` | `decimal.Decimal(1)` (precision 28, scale 0) |
| `UUIDType` | a `uuid.UUID` |

Two `DataType`s are considered equal if their `identifier` matches, regardless of which instance you use - this is what lets `Schema.equals` compare a table's expected schema against an actual one. Whether a given type is actually usable depends on your [engine](../advanced_concepts/engines.md) having registered a mapping for it; not every engine necessarily supports every type above.
<!---aigen_end-->

