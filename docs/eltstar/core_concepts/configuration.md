<!---aigen_start-->
# Configuration

We've now seen [Tables](./model_driven.md) and [Transformations](./transformations.md), and both of them take a `runtime_config` and an `environment_config` parameter. Time to actually explain where those come from.

**Why** two configs and not one? We found it useful to separate two different concerns:

- `EnvironmentConfig` - "where am I running?" (dev, tst, prod, a specific customer's tenant, ...). This is the config that usually ends up as part of your table's path, e.g. via `environment_config.env` as seen in the [TablePath example](./model_driven.md#tablepath).
- `RuntimeConfig` - "what do I need to actually connect to things right now?" (client ids, credentials, storage account names, ...). Things that are not necessarily tied to a specific environment, but to how/where the code currently executes (locally, in a CI job, in a specific runtime system).

You are, of course, free to only use one of them properly and leave the other one closer to empty, if your setup doesn't need the distinction.

## The registration pattern

Both configs are plain pydantic models (inheriting from `EnvironmentConfig`/`RuntimeConfig` respectively) and both use the same pattern to get instantiated: you register a "load method" for a `situation_identifier`, and later ask the config class to `load` itself for that situation.

```python
from eltstar.config import EnvironmentConfig, RuntimeConfig

class MyEnvironmentConfig(EnvironmentConfig):
    env: str

MyEnvironmentConfig.register_load_method( # (1)!
    situation_identifier="local", # (2)!
    method=lambda: MyEnvironmentConfig(env="local"), # (3)!
)

...

config = MyEnvironmentConfig.load(situation_identifier="local") # (4)!
```

1. `register_load_method` is a classmethod, so it registers the loader for `MyEnvironmentConfig` specifically (subclasses each have their own registry).
2. The `situation_identifier` is just a string you make up. Common choices are the deployment stage (`"local"`, `"dev"`, `"prod"`) or the way the code is being triggered (`"pytest"`, `"cli"`, `"databricks_job"`).
3. The load method itself can be anything callable that returns an instance of your config class - a lambda, a classmethod, a function that reads environment variables or a secrets manager, or (as here) simply the class' own constructor.
4. `load` looks up the registered method for the given `situation_identifier` and calls it. If nothing was registered for that identifier, you'll get a `NotImplementedError` telling you so.

This indirection is what allows the exact same table and transformation code to run unchanged locally, in CI and in whatever runtime system you deploy to - only the registration differs per situation, usually in your entrypoint/main file.

**Careful!** Registration only has to happen once, before the first `load` call for that `situation_identifier`. It is not undone automatically between test runs, so if you register multiple load methods for the same identifier (e.g. across several test files), the last registration wins.

## Wiring it into the transformation manager

You don't usually call `.load()` yourself. Instead, you hand the class type to the [`manager`](./running_a_pipeline.md), which loads it once and propagates it to every registered transformation. Here's the complete registration-and-wiring pattern, straight from the [minimal example](https://github.com/jochengietzen/eltstar/tree/main/examples/eltstar_minimal_example):

```python title="examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py"
from eltstar.config import EnvironmentConfig, RuntimeConfig
from eltstar.transformation import manager

--8<-- "examples/eltstar_minimal_example/src/eltstar_minimal_example/main.py:config-registration"
```

For the full picture of how this fits into actually running your pipeline, continue with [Running a pipeline](./running_a_pipeline.md).
<!---aigen_end-->
