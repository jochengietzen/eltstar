# Wrapper functions

Now we get into more interesting areas.
While you can still use the original data frame functionalities, we recommend to use WrapperFunctions. Either self built or provided through plugins.

**What** is a WrapperFunction?
A WrapperFunction is a definition of a function, that can operate on DataFrameWrapper(s). A WrapperFunction Definition defines everything needed to call a specific function on a DataFrameWrapper. The DataFrameWrapper then allows you to register a WrapperFunction for the Definitions. This allows us, to have a shared Definition of how to call that function and provide different implementations for different engines.

**Why** would I want to go through this?
Granted, it is a bit more effort to first define the functions you want to use, instead of just using the probably existing function in the DataFrame API, but over the long run it will pay out.
The big benefit is, that this will allow you to switch the engine without any changes to your transformations, as long as you only utilise WrapperFunctions and no direct DataFrame APIs (only indirectly through the WrapperFunctions).

This is one of the central concepts that allow us to be extremely flexible in terms of vendor and engines.

To ensure, that your logic produces consistent results, we provide some testing functionality to compare results of a WrapperFunction across several engines.

These functions are executed on a given DataFrameWrapper, meaning you can utilise them like you would with a traditional DataFrame API.

<!---aigen_start-->
```python title="examples/eltstar_add_function_to_multiple_engines_example/tests/test_ordered_duplication.py"
from eltstar.testing.wrapper_functions import compare_wrapper_functions_accross_engines

def test_ordered_duplication_function(test_df):
    --8<-- "examples/eltstar_add_function_to_multiple_engines_example/tests/test_ordered_duplication.py:compare-across-engines"
```
<!---aigen_end-->

But how do you define a wrapper function?
Let's explore it, using the example of the provided join function.

## Join Function Example

### Parts of a Definition

The Definition of a function contains 3 Parts, the ArgSpec, the ArgSpecType and the FuncSpec.

The ArgSpec and FuncSpec are just Pydantic Models, the ArgSpecType is a TypeVar of the ArgSpec.

#### ArgSpec and ArgSpecType

The ArgSpec definition is a pydantic model/class that inherits from WrapperArgSpec (in `eltstar.models.data_frame_wrapper.functions.base`).

The naming convention is to name it starting with your function's name and then adding the suffix ArgSpec. In our example it would be `JoinArgSpec`

For the join's ArgSpec, we used the following code:

<!---aigen_start-->
```python title="src/eltstar/models/data_frame_wrapper/functions/join.py"
--8<-- "src/eltstar/models/data_frame_wrapper/functions/join.py:join-arg-spec"
```
<!---aigen_end-->

1. In our case we allowed an arbitrary type
2. Usually, when joining, you need another dataframe - in our case we need another DataFrameWrapper as DataFrame to join the existing one to
3. The left side's joining on columns
4. The right side's joining on columns
5. These operators are there to indicate, how you want to compare each pair of the left_on, right_on columns to match for the joins
6. This indicates the type of join, as we are used to from most data frame apis

<!---aigen_start-->
Right below these fields, `JoinArgSpec` also has two `model_validator`s that check `left_on`/`right_on` have matching lengths and default `operator_list` to `EQUAL` for every pair - omitted above for brevity, but worth a look if you want to see validators in practice.
<!---aigen_end-->

You can utilise Pydantic's model_validators to ensure, that the parameters are given properly, which helps a lot with debugging in advance.

From the ArgSpec, we now derive the ArgSpecType using
<!---aigen_start-->
```python title="src/eltstar/models/data_frame_wrapper/functions/join.py"
--8<-- "src/eltstar/models/data_frame_wrapper/functions/join.py:join-arg-spec-type"
```
<!---aigen_end-->

This will be used in our Func Spec to type the arg_spec.

#### FuncSpec

The actual function specification lives in the FuncSpec object.

Similar to the ArgSpec, the same naming convention applies to the FuncSpec. Just start with the function's name and finish with FuncSpec.

The FuncSpec is defined as a pydantic model, as well.
Here we provide a bit more convenience for the model through generics:

<!---aigen_start-->
```python title="src/eltstar/models/data_frame_wrapper/functions/join.py"
--8<-- "src/eltstar/models/data_frame_wrapper/functions/join.py:join-func-spec"
```
<!---aigen_end-->

1. We have to pass the ArgSpecType's type as the WrapperFunctionSpec's generic's instantiation. It's important to provide the TypeVar/Type, so we can later use Engine Specific ArgSpec Types
2. The func_name is required and will indicate the calling name from the DataFrameWrapper. At the same time it acts as its identifier, which allows you, to later overwrite the function definition, if you need it.

With these Spec objects, we finished the definition steps for our function.
You can think of these definitions as our interface for the actual function.

Based on these definitions, we can now provide implementations for engines.

### Implementation of a Function

For the actual implementation in polars, we can now use the following lines:

<!---aigen_start-->
```python title="plugins/engines/polars/src/eltstar_engine_polars/functions/join.py"
from enum import StrEnum, auto
from typing import Literal

import polars as pl

from eltstar.models.data_frame_wrapper.functions.join import JoinArgSpec, JoinFuncSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar_engine_polars.engine import PolarsEngine

--8<-- "plugins/engines/polars/src/eltstar_engine_polars/functions/join.py:polars-join-implementation"
```
<!---aigen_end-->

1. The polars specific join comparison operators, since we only allow equals for polars for now
2. The polars specific join ArgSpec, since the how in Polars has a specific set of parameters, compared to e.g. pyspark.
3. The subset of join how's that are present in polars DataFrame API
4. We have to return a DataFrameWrapper as the return type and the only parameters can be the self (DataFrameWrapper) and the function_spec with our defined FunctionArgSpec in the Engine Specific definition.
5. First we retrieve the data frame from our own DataFrameWrapper
6. Then we retrieve the data frame from the other DataFrameWrapper
7. Now we perform the actual join logic for polars, using the parameters from our arg specs
8. Now we return the new DataFrameWrapper based on the joined DataFrame and specify our engine
9. Now we register the function to our DataFrameWrapper
10. We have to indicate, the Engine this function is registered for
11. We have to pass the func spec. Careful, we use the JoinFuncSpec from the general definition, but the PolarsJoinArgSpec from our specific ArgSpec definition
12. Lastly, we need to pass the actual function

### Entrypoint for us to find the function

If you define these functions, it is very important to give us a hint, where we can find this registration, or it won't be loaded.
You can do this in your pyproject.toml using the entrypoint group `"eltstar.wrapper_functions"`.
Every registration of a wrapper_function, that you list in your entry-points group with this name, will be automatically found by eltstar.

<!---aigen_start-->
```toml title="plugins/engines/polars/pyproject.toml"
--8<-- "plugins/engines/polars/pyproject.toml:join-entrypoint"
```
<!---aigen_end-->
1. The join key on the left side is irrelevant for us. We like to name it the same as our function and module, but the key is not used by us.

### Usage

Now that you have defined the functions, or installed a plugin that provides these definitions and/or implementations, you can use them, as you would usually with a DataFrame, just on the DataFrameWrapper.

One last thing to mention, before we actually use this.
We provide 2 DataFrameWrappers in 2 modules.
1. `from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper`
    - This is the plain DataFrameWrapper class definition.
    - If you only use this one, you will need to call the classfunction `DataFrameWrapper.load_all_plugins()` before any wrapper_function usage.
2. `from eltstar.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper`
    - This convenience class is the exact same as in case 1 but the plugins are already loaded for you.
    - Important: This should not be the Wrapper you use for your own registrations and entrypoints, since the registration itself does not load/apply the function. Only the load step will apply the function to the DataFrameWrapper class.


Using the wrapper function is as simple as calling:

<!---aigen_start-->
```python title="examples/eltstar_polars_example/src/eltstar_polars_example/wrapper_function_example.py"
from eltstar_engine_polars.functions.join import PolarsJoinArgSpec

--8<-- "examples/eltstar_polars_example/src/eltstar_polars_example/wrapper_function_example.py:join-usage-import"
df_w1: DataFrameWrapper = ...
df_w2: DataFrameWrapper = ...
--8<-- "examples/eltstar_polars_example/src/eltstar_polars_example/wrapper_function_example.py:join-usage"
```
<!---aigen_end-->
1. As mentioned above, we should use the preloaded DataFrameWrapper for usage here - especially if this is a transformation
2. We use the engine specific Arg Spec in this case, but if you specified the specific ArgSpec as recommended to only be a subset of the general ArgSpec, you should use the general ArgSpec, so that you don't have to change anything to switch between engines
3. The second DataFrameWrapper to join to the first one
4. The left side on columnse
5. The right side on columnse
6. The type of our join

And all our arguments are automatically typed and type checked when calling the function. All thanks to the utilisation of pydantic for our args.
