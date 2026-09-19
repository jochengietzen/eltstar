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


