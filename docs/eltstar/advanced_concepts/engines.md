<!---aigen_start-->
# Engines

Every table you've seen so far declared an `engine`, e.g. `engine: type[EngineType] = PolarsEngine`. This page explains what an `Engine` actually is, why the core library never imports `polars` or `pandas` itself, and what's involved in writing your own.

**What** is an `Engine`? It's the one place that knows how to translate between eltstar's engine-agnostic world (`Schema`, `DataType`, `DataFrameWrapper`) and one specific dataframe library's native world (a `pl.DataFrame` and `pl.Schema`, say). Everything else in eltstar - `Table`, `Transformation`, `DataFrameWrapper` - only ever talks to the `Engine` interface, never to `polars`/`pandas` directly. That's what makes switching engines (mostly) a one-line change on your `Table` definition.

## Registering data types

An engine subclasses `Engine` (from `eltstar.engines.base`) and, at import time, registers a mapping between eltstar's [`DataType`s](../core_concepts/model_driven.md#table-instances) and its own native types via a classmethod conventionally called `setup()`:

```python title="plugins/engines/polars/src/eltstar_engine_polars/engine.py"
from eltstar.engines.base import Engine, EngineSpecificDataType
from eltstar.models.base import FloatType, IntegerType, StringType
from eltstar.models.schema import Schema
import polars as pl

--8<-- "plugins/engines/polars/src/eltstar_engine_polars/engine.py:engine-attrs"

    @classmethod
    def setup(cls):
        --8<-- "plugins/engines/polars/src/eltstar_engine_polars/engine.py:engine-setup-excerpt"
        ...  # a handful more `register_data_type` calls, one per supported `DataType`

--8<-- "plugins/engines/polars/src/eltstar_engine_polars/engine.py:engine-setup-call"
```

1. Every engine needs a unique, lowercase `engine_identifier` string - this is the key used everywhere internally (registries, `EngineSpecificFunctionKey`, ...).
2. The native schema type for this engine (`pl.Schema` for polars). Used to dispatch `Schema.from_engine_schema` to the right engine when you only have a native schema object and want the eltstar `Schema` for it.
3. The engine's native dataframe class (`pl.DataFrame` for polars). As soon as this class is defined, `Engine.__init_subclass__` registers it in a `dataframe_type -> Engine` lookup table - this is what lets `TypedDataFrameWrapper` figure out which engine a `pl.DataFrame`/`pd.DataFrame`/... belongs to without you passing `engine=` yourself. See [DataFrameWrapper](../core_concepts/data_frame_wrapper.md#typeddataframewrapper).
4. `Schema.register_from_engine_schema` wires up the two-way conversion between the eltstar `Schema` and this engine's native schema representation - see below.
5. `register_data_type` accepts a bare native type/class, like here for `FloatType`/`pl.Float64`, ...
6. ... or an `EngineSpecificDataType` for cases that need more than a plain class comparison - a `dtype_class`/`lambda_class` (a callable returning the type, useful for parametrized types like `pl.Datetime(time_unit=..., time_zone=...)`) or a `str_repr` for engines whose "type" is really just a string.
7. **This line matters.** Registration only happens when `setup()` is actually called. See [Discovery, honestly](#discovery-honestly) below for how (and when) that currently happens.

## The abstract methods

Beyond `setup()`, `Engine` declares a handful of abstract classmethods every engine has to implement:

| Method | Responsible for |
| --- | --- |
| `_from_engine_schema` / `_to_engine_schema` | Converting between the native schema type and eltstar's `Schema` |
| `get_engine_schema` | Extracting the native schema from a `DataFrameWrapper` |
| `cast` | Casting a `DataFrameWrapper`'s dataframe to a given `Schema` |
| `dataframe_from_faker_columnar` | Building a `DataFrameWrapper` from the columnar dict produced by [fake data generation](./testing_and_fake_data.md) |
| `convert_to_arrow` / `convert_from_arrow` | Converting to/from `pyarrow` - see below |

`engine_schemas_equals` has a sensible default (`==`) but can be overridden if your native schema type doesn't compare the way you'd want.

## Converting between engines: the Arrow bridge

`DataFrameWrapper.convert_to(target_engine)` (used, for example, by [`compare_wrapper_functions_accross_engines`](./wrapper_functions.md)) doesn't require every engine to know how to convert to every other engine directly. Instead, every engine only needs to implement `convert_to_arrow`/`convert_from_arrow`, and `Engine.convert_to_engine` routes any conversion through `pyarrow` as a common intermediate format:

```python
source_engine.convert_to_arrow(...) -> arrow DataFrameWrapper -> target_engine.convert_from_arrow(...)
```

If either side of the conversion already *is* the arrow engine, that leg is skipped. This means adding a new engine gets you conversions to/from every other existing engine for free, instead of an ever-growing matrix of engine-pair conversion functions.

## Discovery, honestly

`TransformationManager.load_all_plugins()` scans the `eltstar.engines` and `eltstar.runtime_systems` entry-point groups. This is meant to eventually give you zero-config auto-discovery, the same way `eltstar.wrapper_functions` already works (see [Wrapper functions](./wrapper_functions.md#entrypoint-for-us-to-find-the-function)).

As of today, no shipped engine plugin declares an `eltstar.engines` entry point yet - `PolarsEngine.setup()` is instead triggered simply by importing the module, e.g.

```python
from eltstar_engine_polars.engine import PolarsEngine # (1)!
```

1. The import itself is enough - `PolarsEngine.setup()` runs at module import time, at the bottom of `engine.py`. You don't need to (and shouldn't need to) call `.setup()` yourself.

So: make sure whatever module calls `PolarsEngine.setup()` (or your own engine's `setup()`) actually gets imported somewhere in your pipeline's entrypoint - directly, or transitively through a `Table` subclass that references the engine's type. `plugin_tactics.md` in the repo root has the full plan for closing this gap; treat `eltstar.engines` as reserved but not yet load-bearing.
<!---aigen_end-->
