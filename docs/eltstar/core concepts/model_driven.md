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

We inherit from the imported Class Table Path and define some attributes of this pydantic model, that are relevant to your table paths. Here we have a data, a time and a name.
As the base/parent class has the abstractmehtod full_path, we need to provide an implementation for said funciton.
Based on the automatically passed runtime configuration, environment configuration and the model's attributes date, time and name we can now construct the table's full path. 

If you cannot imagine yet, how to use that, try to think of a postgresql or metastore, with 3 path components (e.g. db, schema and table name). You could define the db as a fixed value, the schema as part of your environemnt configuration and the table name depending on your table.
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
from eltstar.models.table import EngineReadSettings, EngineWriteSettings, Table

class YoutubeTable(Table):
    path: YoutubeTablePath # (3)!
    engine_read_settings: EngineReadSettings = EngineReadSettings(
        engine=PolarsEngine,
        read_type=EngineFileType.CSV,
    )
    engine_write_settings: EngineWriteSettings = EngineWriteSettings(
        engine=PolarsEngine,
        write_type=EngineFileType.CSV,
    )

    def read(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs,
    ) -> DataFrameWrapper:
        return super().read(
            *args,
            runtime_config=runtime_config,
            environment_config=environment_config,
            source=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
            **kwargs,
        )

    def write(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs,
    ) -> "YoutubeTable":
        return super().write(
            *args,
            runtime_config=runtime_config,
            environment_config=environment_config,
            data_frame_wrapper=data_frame_wrapper,
            file=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
            **kwargs,
        )
```
3. This is the table path configuration from earlier.

We now have a couple of things to unwrap in this block.

- First, the latest concept with the table path - no need to reiterate for now.
- Then we have the engine_read_settings and the engine_write_settings. These are relatively simple settings, that link to an engine and an engine file type. This is used/passed onto the engine, when calling the super().read/write methods.
- Then we have the read and write methods defined. Please notice, how we call the read with source and the write with file parameter containing the full_path passed to the super's write method. These refer to the methods of your engine (e.g. the read csv method or write csv method in polars).
Theoretically, you can completely overwrite these methods to load data from e.g. postgres and write to that. This makes the usage extremely versatile. # TODO: Fix to remove the engine style if still present

## Table instances

After we have the basics in definition out of the way, we can now write our actual table instances.

```python
tech_channels = YoutubeTable(
    path=YoutubeTablePath(
        name="youtube_tech_channels", # (4)!
        date="20251120",
        time="133753",
    ),
    columns=Columns( # (5)!
        root=dict(
            channel_id=Column(# (6)!
                name="channel_id",
                data_type=StringType(), # (7)!
                is_primary_key=True, # (8)!
                generation=Generation(faker_type=FakerStringType()),
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
