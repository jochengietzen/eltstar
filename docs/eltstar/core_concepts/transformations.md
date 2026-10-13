# Transformations

Another core concept of eltstar are transformations. Transformations use the previously defined tables as inputs and generate another table as output.
Each transformation needs to be registered by the transformation manager "singleton".

## The simplest transformation

The simplest transformation can be shown as follows using the previously defined tech_channels Table definition

```python
from eltstar.models.data_frame_wrapper import DataFrameWrapper
from eltstar.transformation import manager
import polars as pl

tech_channels
tech_channels_2 = tech_channels.model_copy() # (1)!
tech_channels_2.path = YoutubeTablePath(name="youtube_tech_channels_2", date="1", time="2") # (2)!


@manager.register_transformation(
    output_table_model=tech_channels_2, # (3)!
    tech_ch=tech_channels, # (4)!
)
def foo_name_transformation( # (5)!
    tech_ch: DataFrameWrapper, # (6)!
) -> pl.DataFrame: # (7)!
    return tech_ch.data_frame.with_columns(
        pl.concat_str(
            [
                pl.col("channel_name"), 
                pl.lit("foo"),
            ], 
            separator=" ",
        ).alias("channel_name")
    )

```

1. At first we copy the tech_channels model, since we are not going to change any column definitions.
2. We need to update the output table's path, otherwise we would overwrite the original input table.
3. Every register_transformation decorator requires an output_table_model receiving a Table descendant instance.
4. We now pass our input table instances. Please note, that the key (tech_ch) has to be the same as the later parameter in the function definition.
5. The transformation name needs to be unique, as this name will be this transformation's identifier.
6. This is the DataFrameWrapper passed into the function (aka. transformation) that upholds your table definitions. Remember 3 lines ago? This key has to be the same as the above, so we can feed the correct parameter, when calling this transformation.
7. You have to return a DataFrame of your engine, or a DataFrameWrapper.

This is the simplest possible transformation, with an actual change. You could also just do
```python
...
    return tech_ch
```
which of course is even simpler, but rarely has a point, unless you keep various copies of your tables in different places.

We have briefly seen another important concept in eltstar - the [DataFrameWrapper](./data_frame_wrapper.md). For more details on that, follow the link.

<!---aigen_start-->
Registering a transformation doesn't run it, though. For how to actually load configuration and execute your registered transformations, continue with [Running a pipeline](./running_a_pipeline.md).
<!---aigen_end-->

