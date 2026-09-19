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

```python
from eltstar.testing.wrapper_functions import compare_wrapper_functions_accross_engines

def test_ordered_duplication_function(test_df):
    compare_wrapper_functions_accross_engines(
            dfw=test_df,
            engine_func_spec_lookup={
                PolarsEngine: Polars<SomeName>ArgSpec(<some_arguments>),
                PandasEngine: Pandas<SomeName>ArgSpec(<some_arguments>),
            },
            func_identifier="some_name_identifier",
            expected_result_schema=Schema(
                root=[
                    SchemaField(name="foo", type_=IntegerType(), nullable=False),
                    SchemaField(name="bar", type_=FloatType(), nullable=False),
                    SchemaField(name="index_column", type_=IntegerType(), nullable=False),
                ]
            ),
        )
```

But how do you define a wrapper function?
Let's explore it, using the example of the provided join function.

## Join Function Example

### Parts of a Definition

The Definition of a function contains 3 Parts, the ArgSpec, the ArgSpecType and the FuncSpec.

The ArgSpec and FuncSpec are just Pydantic Models, the ArgSpecType is a TypeVar of the ArgSpec.

#### ArgSpec and ArgSpecType

The ArgSpec definition is a pydantic model/class that inherits from WrapperArgSpec (in `eltstar.models.data_frame_wrapper.functions.base`).

The naming convention is to name it starting with your function's name and then adding the suffix ArgSpec. In our example it would be `JoinArgSpec`

For the join's ArgSpec, we used the following partial code:

```python
class JoinComparisonOperator(StrEnum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    ...

class JoinArgSpec(WrapperArgSpec):
    model_config = ConfigDict(arbitrary_types_allowed=True) # (1)!

    other: "DataFrameWrapper" # (2)!
    left_on: list[str] # (3)!
    right_on: list[str] # (4)!
    operator_list: list[JoinComparisonOperator] # (5)! 
    how: Literal[
        "inner",
        "left",
        ...
    ] # (6)!

    ...
```

1. In our case we allowed an arbitrary type
2. Usually, when joining, you need another dataframe - in our case we need another DataFrameWrapper as DataFrame to join the existing one to
3. The left side's joining on columns
4. The right side's joining on columns
5. These operators are there to indicate, how you want to compare each pair of the left_on, right_on columns to match for the joins
6. This indicates the type of join, as we are used to from most data frame apis

_We only showed some parts of the code to support the understanding here._

You can utilise Pydantic's model_validators to ensure, that the parameters are given properly, which helps a lot with debugging in advance.

From the ArgSpec, we now derive the ArgSpecType using
```python
JoinArgSpecType = TypeVar("JoinArgSpecType", bound=JoinArgSpec)  # pylint: disable=invalid-name # (1)!
```

This will be used in our Func Spec to type the arg_spec.

#### FuncSpec

The actual function specification lives in the FuncSpec object.

Similar to the ArgSpec, the same naming convention applies to the FuncSpec. Just start with the function's name and finish with FuncSpec.

The FuncSpec is defined as a pydantic model, as well.
Here we provide a bit more convenience for the model through generics:

```python
class JoinFuncSpec(WrapperFunctionSpec[type[JoinArgSpecType]]): # (1)!
    func_name: str = "join" # (2)!
```

1. We have to pass the ArgSpecType's type as the WrapperFunctionSpec's generic's instantiation. It's important to provide the TypeVar/Type, so we can later use Engine Specific ArgSpec Types
2. The func_name is required and will indicate the calling name from the DataFrameWrapper. At the same time it acts as its identifier, which allows you, to later overwrite the function definition, if you need it.

With these Spec objects, we finished the definition steps for our function.
You can think of these definitions as our interface for the actual function.

Based on these definitions, we can now provide implementations for engines.

### Implementation of a Function

For the actual implementation in polars, we can now use the following lines:

```python
...

class PolarsJoinComparisonOperator(StrEnum): # (1)!
    EQUAL = auto()


class PolarsJoinArgSpec(JoinArgSpec): # (2)!
    operator_list: list[PolarsJoinComparisonOperator]
    how: Literal["inner", "left", "right", "full", "cross", "semi", "anti"] # (3)!


def join(self: DataFrameWrapper, function_spec: PolarsJoinArgSpec) -> DataFrameWrapper: # (4)!
    df_in: pl.DataFrame = self.data_frame # (5)!
    df_other: pl.DataFrame = function_spec.other.data_frame # (6)!

    joined = df_in.join(df_other, left_on=function_spec.left_on, right_on=function_spec.right_on, how=function_spec.how) # (7)!

    return DataFrameWrapper(data_frame=joined, engine=self.engine) # (8)!


DataFrameWrapper.register_wrapper_function( # (9)!
    engine=PolarsEngine, # (10)!
    func_spec=JoinFuncSpec(arg_spec=PolarsJoinArgSpec), # (11)!
    func=join, # (12)!
)
```

1. The polars specific join comparison operators, since we only allow equals for polars for now
2. The polars specific join ArgSpec, since the how in Polars has a specific set of parameters, compared to e.g. pyspark.
3. The subset of join how's that are present in polars DataFrame API
4. We have to return a DataFrameWrapper as the return type and the only parameters can be the self (DataFrameWrapper) and the function_spec with our defined FunctionArgSpec in the Engine Specific definition.
5. First we retrieve the data frame from our own DataFrameWrapper
6. Then we retrieve the data frame from the other DataFrameWrapper
7. Now we perform the actual join logic for polars, using the parameters from our arg specs
8. Now we return the new DataFrameWrapper based on the joined DataFrame and specify our engine