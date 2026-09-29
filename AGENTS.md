# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) or other coding agents when working with code in this repository.

## Commands

This project uses `uv` as the package manager and `just` as the task runner.

**Setup:**
```bash
just init          # Full setup: creates venv, syncs deps, installs pre-commit hooks
just create_sub_venvs  # Create venvs for all plugin/example subdirectories
```

**Development:**
```bash
uv run pytest                          # Run all tests
uv run pytest tests/path/to/test.py    # Run a single test file
uv run pytest -k "test_name"           # Run a specific test by name
uv run ruff check .                    # Lint
uv run ruff format .                   # Format
uv run mypy src/                       # Type check
uv run pylint src/                     # Lint with pylint (must score 10/10)
```

Each plugin/example under `plugins/` and `examples/` has its own isolated `.venv` and `pyproject.toml`.

## Architecture

eltstar is a uv workspace monorepo. The core library lives in `src/eltstar/`. Engine support, engine conversions, and runtime system integrations are separate plugin packages under `plugins/`. Examples live under `examples/`.

### Core library (`src/eltstar/`)

The central concept is the **registration pattern**: engines, data types, read/write methods, schema converters, and config loaders are all registered at runtime rather than hardcoded. The core library has no hard dependency on any dataframe library (pandas/polars).

Key classes and how they connect:

- **`Engine`** (`engines/base.py`): Abstract base with `ClassVar` registries for read methods, write methods, and conversion methods. Each engine subclass defines a unique `engine_identifier`. Engines register themselves via `setup()`.
- **`DataType`** (`models/base.py`): Abstract base for column types (`IntegerType`, `FloatType`, `StringType`). Each engine registers mappings between its native types and eltstar types via `DataType.register_from_and_to_methods()`.
- **`Schema`** (`models/base.py`): A `RootModel[list[SchemaField | SchemaStruct]]` with class-level registries for converting to/from engine-native schemas. Registered by each engine's `setup()`.
- **`DataFrameWrapper`** (`models/data_frame_wrapper.py`): Engine-agnostic wrapper around any dataframe object. Holds a reference to `engine` and `schema`. Provides `.cast()`, `.write()`, and `.convert_to(target_engine)`.
- **`Table`** (`models/table.py`): Defines a data table with `Columns`, `EngineReadSettings`, and `EngineWriteSettings`. Has `.read()` and `.write()` methods that delegate to the registered engine.
- **`Columns`** (`models/base.py`): A `RootModel[dict[str, Column]]` that maps column keys to `Column` instances (which include `DataType`, constraints, expectations, and `Generation` for fake data).
- **`Transformation`** / **`TransformationManager`** (`transformation.py`): Decorates Python functions as named transformations with input/output `Table` references. The global `manager` singleton is imported and used throughout. `manager.load_all_plugins()` discovers plugins via entry points (`eltstar.engines`, `eltstar.conversions`, `eltstar.runtime_systems`).
- **`Lineage`** (`graph.py`): Builds a `networkx.MultiDiGraph` from registered transformations to track data lineage. Used by runtime systems to generate deployment artifacts.
- **`RuntimeConfig` / `EnvironmentConfig`** (`config.py`): Base Pydantic models for runtime and environment configuration, both using the same registration pattern (register a load method by `situation_identifier`, then call `.load(situation_identifier=...)`).
- **`FakerManager`** (`testing/faker_manager.py`): Generates schema-valid fake data for testing using `faker`. Calls `engine.dataframe_from_faker_columnar()`.

### Plugin packages

Each plugin is a standalone Python package in the uv workspace that depends on `eltstar` (resolved from workspace) plus its engine library. Plugins register themselves by calling `setup()` at module import time (currently), which wires types and methods into the core registries.

- `plugins/engines/polars/` → `eltstar-engine-polars` / `eltstar_engine_polars.engine.PolarsEngine`
- `plugins/engines/pandas/` → `eltstar-engine-pandas` / `eltstar_engine_pandas.engine.PandasEngine`
- `plugins/engine_conversions/pandas_to_polars/` → `eltstar_pandas_to_polars` — registers bidirectional conversion functions on both engines
- `plugins/runtime_systems/databricks/asset_bundle_jobs/` → `eltstar_rs_dbx_asset_bundle_jobs` — implements `BaseRuntimeSystem.generate()` for Databricks Asset Bundle Jobs

### Plugin direction (in progress)

The codebase is transitioning toward the **hybrid entry points + explicit registration** model described in `plugin_tactics.md`. The goal is auto-discovery via Python entry points groups (`eltstar.engines`, `eltstar.conversions`, `eltstar.runtime_systems`) while retaining explicit `setup()` as a fallback. `TransformationManager.load_all_plugins()` already implements the entry point discovery side; engine plugins need their `pyproject.toml` updated to declare entry points.

### Naming conventions

- `engine_identifier`: lowercase string, e.g. `"polars"`, `"pandas"` — used as the key in all registration dicts
- Column keys in `Columns` must match `^[a-zA-Z0-9-_]+$` and cannot contain commas
- Pylint enforces `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants; `bad-names` list bans `foo`, `bar`, `baz`, etc.
- Line length: 120 characters (ruff)

### AI Transparancy

This repository allows for usage of AI in certain ways, especially with documentation and tests. However, in order to make it absolutely transparent, what was written by AI, every edit must be clearly labeled.

Some examples are:
- If AI adds a docstring to the function, the docstring needs to start with `"""aidocs`, e.g. generating:
```
def foo(bar: str) -> str:
    """aigen_start
    The function foo will transform the input bar into the output baz.

    Args:
        bar (str): The parameter bar
    
    Returns:
        The string baz
    
    aigen_end"""
```
- In Readmes, which are not AI specific (e.g. not in CLAUDE.md), we use HTML comments `<!---aigen_start-->` and `<!---aigen_end-->` to surround the generated blocks.
- If whole code blocks in python are edited or generated, we surround them with `### aigen_start` and `### aigen_end` blocks

These are just examples to make the general idea of ai transparancy marking clear.
