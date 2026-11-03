<!---aigen_start-->
# eltstar minimal example

The smallest fully working eltstar pipeline. Every other example under `examples/`
shows a richer, more realistic setup; this one strips everything down to a single
file that still touches every core concept exactly once, so it works as a
five-minute overview of what eltstar actually does.

## Run it

```bash
uv run --package eltstar-minimal-example src/eltstar_minimal_example/main.py
```

This generates 20 fake "people" rows, writes them to `data/people.csv`, runs a
transformation that filters for age >= 30, prints and writes the result to
`data/adults.csv`, reads it back to prove the round trip, and prints the
lineage graph's edges.

## What it demonstrates

Read `src/eltstar_minimal_example/main.py` top to bottom - it's numbered:

1. **`TablePath`** - resolves a table's physical location (`LocalCsvPath`).
2. **`Table`** - engine-agnostic `read()`/`write()`, backed here by plain
   polars CSV I/O (`CsvTable`).
3. **`Columns`/`Column`** - defines the schema (`id`, `name`, `age`) and, via
   `Generation`, how to fake each column for testing.
4. **`Transformation`** - a plain function (`filter_adults`) registered
   against its input/output tables with `manager.register_transformation`.
5. **`RuntimeConfig`/`EnvironmentConfig`** - eltstar's registration-based
   config-loading pattern, used here with the base classes directly since
   this example needs no extra config fields.
6. **`FakerManager`** - generates schema-valid fake data for the input table.
7. **`Lineage`** - `manager.lineage` builds a dependency graph from every
   registered transformation, for free.

## What's deliberately left out

Joins/aggregations, multiple engines and engine conversion, custom data
types, and deployment/runtime-system generation. Those are all real eltstar
features - see `eltstar_pandas_example` and `eltstar_polars_example` for them
- just not part of a "quick overview".
<!---aigen_end-->
