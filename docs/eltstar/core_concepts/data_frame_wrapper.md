# Data Frame Wrapper

Why do we introduce a wrapper for DataFrames? 
Aren't the individual DataFrame objects good enough? Well, yes they are, but there are reasons for it.

The most obvious reason is, that we need an abstraction layer, that allows us to add any arbitrary DataFrame Library later on. At least mostly arbitrarily.
Another reason for us is the possibility to extend the functionality of the "plain" DataFrames with things like schema verification, casting and very importantly [wrapper_functions](../advanced_concepts/wrapper_functions.md).

What can you do with a DataFrameWrapper?
Well, since it is a wrapper, of course you have direct access to your DataFrame instance via the `data_frame` attribute. This is also the only required attribute when instantiating the DataFrameWrapper. 
```python
...
df = DataFrame(...)

dfw = DataFrameWrapper(data_frame=df)
```

Instead of using the Constructor, we also offer the classmethod `ensure_is_wrapper`, which allows us, to accept DataFrames as return values of transformations, as well as DataFrameWrappers.
```python
dfw = DataFrameWrapper.ensure_is_wrapper(data_frame=df)
```

For all of the schema related functions, like schema verification or casting, you need to provide the schema and the engine attribute. The schema can be retrieved from the Columns instance.

If you need to create a DataFrameWrapper that has the same schema and engine, but different data, you can utilise the `create_with_new_data` function.
Referring back to the [Transformation](./transformations.md) example, we could also have returned
```python
...
    return tech_ch.create_with_new_data(
        data_frame=tech_ch.data_frame.with_columns(
            pl.concat_str(
                [
                    pl.col("channel_name"), 
                    pl.lit("foo"),
                ], 
                separator=" ",
            ).alias("channel_name")
        )
    )
```

<!---aigen_start-->
## Schema verification and casting

We mentioned schema verification and casting earlier as one of the reasons for the wrapper's existence - here's what that actually looks like.

**Careful!** In a normal pipeline, you will rarely call any of these three functions yourself. `Table.validate_table_schema` already calls `verify_schema`/`cast` for you, and the automatic input-casting during [transformation execution](./running_a_pipeline.md#4-execute) does the same for every input `DataFrameWrapper` before your function ever sees it. You mostly reach for these directly when writing a `Table.read()`/`write()` implementation yourself, debugging a schema mismatch, or working with a `DataFrameWrapper` outside of the usual table/transformation flow.

If you construct a `DataFrameWrapper` with both a `schema` and an `engine`, you can ask it whether the data frame it holds actually matches that schema:

```python title="examples/eltstar_polars_example/src/eltstar_polars_example/example_verify_schema.py"
--8<-- "examples/eltstar_polars_example/src/eltstar_polars_example/example_verify_schema.py:verify-schema"
```

1. Returns `True`/`False` by default; pass `raise_on_mismatch=True` to instead raise a `SchemaVerificationError` with both schemas printed, which tends to be more useful while debugging than a bare boolean. You can also pass `auto_verify_schema_if_given=True` to the constructor to run this check immediately on instantiation.

If you'd rather fix the mismatch than fail on it (e.g. a source system that reports `channel_id` as an `int` but your schema wants a `str`), `cast()` does that for you, using the schema already attached to the wrapper:

```python title="examples/eltstar_polars_example/src/eltstar_polars_example/casting_example.py"
--8<-- "examples/eltstar_polars_example/src/eltstar_polars_example/casting_example.py:cast"
```

1. Delegates to `engine.cast(schema=self.schema, data_frame_wrapper=self)`, so casting behaviour ultimately comes from the engine (see [Engines](../advanced_concepts/engines.md)) - polars casts differently than pandas would, but the eltstar-level call looks identical either way. This is also what `Table.validate_table_schema` and the automatic input-casting in [transformation execution](./running_a_pipeline.md#4-execute) use under the hood.

Lastly, `convert_to(target_engine)` gives you the same `DataFrameWrapper`, backed by a *different* engine's native dataframe type - handy when you need to hand data from a polars-backed table to a wrapper function that's only implemented for pandas. See [Engines](../advanced_concepts/engines.md#converting-between-engines-the-arrow-bridge) for how that conversion actually works under the hood.
<!---aigen_end-->

<!---aigen_start-->
## TypedDataFrameWrapper

Plain `DataFrameWrapper.data_frame` is typed as `Any` - correct, since a wrapper can hold any dataframe library's object, but it means no autocomplete and no type-checking on whatever you do with `.data_frame` next. `TypedDataFrameWrapper` fixes that by being generic over the concrete dataframe type:

```python
dfw = TypedDataFrameWrapper(data_frame=df)  # df: pl.DataFrame
```

Since `data_frame` is typed as the generic parameter, your type checker infers it from whatever you pass in - `dfw.data_frame` is statically known as `pl.DataFrame` here, so your IDE gives you real autocomplete on it, the same as if you'd never wrapped `df` at all.

You still don't need to pass `engine=` yourself: `TypedDataFrameWrapper.__init__` looks up `type(data_frame)` against a registry that every [`Engine`](../advanced_concepts/engines.md) subclass populates automatically (via its `dataframe_type`, as soon as the engine's module is imported), and sets `self.engine` from whatever it finds. If no engine is registered for that dataframe type - typically because the corresponding plugin was never imported - it raises a `ProgrammingError` immediately rather than leaving you with an engine-less wrapper that fails confusingly later in `cast()`/`convert_to()`.

This is mainly useful for annotating function parameters/return types where you want both the reader and the type checker to know exactly which dataframe type is involved - see `Engine.convert_to_arrow`/`convert_from_arrow` for an example of this in core, which annotate their arrow-backed inputs/outputs as `TypedDataFrameWrapper[pa.Table]`.
<!---aigen_end-->

