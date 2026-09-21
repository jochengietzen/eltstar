<!---aigen_start-->
# Running a pipeline

We've now defined [Tables](./model_driven.md), [Transformations](./transformations.md) and [Configuration](./configuration.md). None of that does anything on its own though - transformations are only *registered* by `manager.register_transformation`, not executed. This page closes that loop.

Everything here happens through the same `manager` singleton you already imported to register your transformations.

```python
from eltstar.transformation import manager
```

## 1. Load your configs

As explained in [Configuration](./configuration.md), register a load method and then load both configs onto the manager. This has to happen before you execute anything, otherwise you'll run into an `InitiliazationMissingError`.

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:config-registration"
```

## 2. Make sure your transformations are actually registered

The `@manager.register_transformation` decorator only runs when the module it lives in gets imported. If your entrypoint script never imports your transformation modules, they simply won't exist as far as the manager is concerned.

For a handful of transformations in one file, a plain `import my_transformations` at the top of your entrypoint is enough. Once you have transformations spread across a package, you can let eltstar find them for you instead, as the [pandas example](https://github.com/jochengietzen/eltstar/tree/main/examples/eltstar_pandas_example) does:

```python title="examples/eltstar_pandas_example/src/eltstar_pandas_example/manager.py"
--8<-- "examples/eltstar_pandas_example/src/eltstar_pandas_example/manager.py:load-all-transformations"
```

This walks every submodule of the given package (using `pkgutil.walk_packages`) and imports it, which triggers every `@manager.register_transformation` decorator inside.

## 3. Load engine/wrapper-function plugins

If you rely on plugins for your engines (e.g. `eltstar-engine-polars`) or on third-party [wrapper functions](../advanced_concepts/wrapper_functions.md), load them once, too:

```python title="examples/eltstar_pandas_example/src/eltstar_pandas_example/manager.py"
--8<-- "examples/eltstar_pandas_example/src/eltstar_pandas_example/manager.py:load-plugins"
```

This discovers everything registered under the `eltstar.engines` and `eltstar.runtime_systems` entry-point groups (see [Engines](../advanced_concepts/engines.md)). Wrapper functions are loaded separately via `DataFrameWrapper.load_all_plugins()` - see [Wrapper functions](../advanced_concepts/wrapper_functions.md#usage) for why that's a separate step.

## 4. Execute

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:execute"
```

For every registered transformation, in **dependency order**, this:

1. Reads every input table via `table.read(...)`, using the configs loaded in step 1.
2. Casts each input to its table's schema (unless you opted out - see below).
3. Calls your transformation function with the resulting `DataFrameWrapper`(s).
4. Writes the result to the transformation's `output_table_model` via `table.write(...)`.

"Dependency order" here means: if transformation B reads a table that transformation A writes, A is guaranteed to run (and be written) before B. This is derived from the [lineage graph](../advanced_concepts/lineage.md) under the hood - `execute_all_transformations` is really just `for element in manager.lineage.iter_transformations(): ...`, so it doesn't matter which order your transformation modules happened to get imported/registered in.

### Skipping the automatic cast

By default, every input table is cast to its declared schema right before your function receives it. If you'd rather deal with the raw data yourself (e.g. to validate it before casting), pass an `InputTableInstruction` instead of the bare `Table` when registering:

```python
from eltstar.transformation import InputTableInstruction

@manager.register_transformation(
    output_table_model=tech_channels_2,
    tech_ch=InputTableInstruction(table=tech_channels, cast_before_injection=False), # (1)!
)
def foo_name_transformation(tech_ch: DataFrameWrapper) -> pl.DataFrame:
    ...
```

1. Everything else about registration stays the same - the key still has to match the function parameter name.

## Putting it together

A minimal, runnable entrypoint therefore looks like this (wrap it in `if __name__ == "__main__":` when turning it into a script):

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:config-registration"

--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:execute"
```

## Bonus: lineage, for free

Since every registered transformation already declares its input and output tables, eltstar can build a dependency graph across your whole pipeline without any extra work from you:

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:lineage-edges"
```

This is useful enough on its own that it gets [its own page](../advanced_concepts/lineage.md).
<!---aigen_end-->
