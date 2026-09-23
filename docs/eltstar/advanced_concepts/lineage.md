<!---aigen_start-->
# Lineage

Every transformation you register already declares which tables it reads and which table it writes (see [Running a pipeline](../core_concepts/running_a_pipeline.md)). eltstar uses exactly that information to build a lineage graph across your whole pipeline - you don't declare anything extra for this to work. Here it is used to print every edge in the [minimal example](https://github.com/jochengietzen/eltstar/tree/main/examples/eltstar_minimal_example)'s pipeline:

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:lineage-edges"
```

`manager.lineage` builds a fresh [`networkx`](https://networkx.org/) `MultiDiGraph` from every currently registered transformation, each time you access it. Tables and transformations both become nodes; an edge points from an input table to the transformation that reads it, and from a transformation to the table it writes.

**Why** would you want this? A few reasons we ran into ourselves:

- Finding out which tables are "raw" sources or final sinks of your pipeline, without maintaining that list by hand.
- Generating deployment artifacts (job definitions, DAGs, ...) for a runtime system from the pipeline structure - see [Runtime systems](./runtime_systems.md).
- Simply visualising or debugging a pipeline that has grown larger than you can hold in your head.

## Walking the graph

A few convenience methods save you from having to know `networkx` to get useful answers out of the graph:

```python
list(lineage.iter_source_tables()) # (1)!
list(lineage.iter_sink_tables()) # (2)!
list(lineage.iter_transformations()) # (3)!
```

1. Tables with no incoming edges, i.e. nothing in your registered transformations writes to them - your pipeline's actual sources. Pass `source_table_type=SomeTableSubclass` to only get tables of a specific `Table` subclass.
2. Tables with no outgoing edges, i.e. nothing reads from them - your pipeline's actual sinks. Also accepts a `sink_table_type` filter.
3. Every transformation, yielded in topological order, as a `LineageTransformationElement(name, input_models, depends_on_transformations, transformation)` namedtuple. `depends_on_transformations` lists the names of the other registered transformations that write one of this transformation's inputs.

### Ordering your run

[`execute_all_transformations`](../core_concepts/running_a_pipeline.md#4-execute) is built directly on top of `iter_transformations`, so your transformations always run in dependency order, regardless of the order you happened to register them in.

If you ever need to drive execution yourself instead of calling `execute_all_transformations` (e.g. to inspect or skip individual results), you can do the exact same walk manually:

```python
for element in manager.lineage.iter_transformations(): # (1)!
    result = element.transformation.execute()
    element.transformation.save_output_table(result)
```

1. `iter_transformations` is backed by `nx.topological_sort`, so by the time a transformation is yielded, every transformation it `depends_on` has already been yielded before it. This is exactly what `execute_all_transformations` does internally.

## Grouping transformations

Every transformation has a `graph_label` (default: `"default"`), which becomes the edge key in the underlying `MultiDiGraph`. If you register several independent pipelines against the same `manager`, giving them different `graph_label`s lets you tell their edges apart later, e.g. when generating per-pipeline deployment artifacts.

You set it directly through `register_transformation`:

```python
@manager.register_transformation(
    output_table_model=tech_channels_2,
    tech_ch=tech_channels,
    graph_label="tech_channels_pipeline", # (1)!
)
def foo_name_transformation(tech_ch: DataFrameWrapper) -> pl.DataFrame:
    ...
```

1. Optional - defaults to `"default"` if you don't pass it, which is exactly right if you only ever register a single pipeline on your `manager`.

## Drawing it

For quick, throwaway debugging, `Lineage.draw()` renders the graph with `matplotlib`:

```python
manager.lineage.draw()
```

This requires `matplotlib` to be installed, which eltstar does **not** pull in as a dependency - install it yourself if you want to use `draw()`.
<!---aigen_end-->
