# eltstar
eltstar is a library, that allows you to streamline your etl development process.

# Core features
- Simple generation of schemad valid fake data for local testing purposes
- Enabling easy data quality checks
- Providing Data Lineage within your package
- Streamlining deployment information for vaious platforms


# Naming
Wording is hard, and even though we know, that we will clash with some names of other libraries, like spark, we try to keep a consistant naming within the library!

### schema
The schema is used to define the structure of your data. It contains the name of each column as well as the type of each column. It is comparable to sparks schema of a table/dataframe etc.

# TODOS
    
    - TODO: Embed example code into documentation (V1-2) to ensure example code is still valid/running.
    - TODO: Provide proper Documentation (V1)
    - TODO: Build minimal exmaple that actually touches all basic parts but with a full on structure, testing and a simple wrapper function! (V1)
    - TODO: Build minimal exmaple for asset bundles! (V1)
    - TODO: Make sure, that primary key generates the most values in the FakerManager generation! (V1)
    - TODO: Provide Tests for Core libraries
    - TODO: Release Process! (V1)
        Process:
            - Only release from main
            - Tag Based Releases
            - Commitizen
                => Remove Squash merge and always use fast-forward merges
                    - Enforce conventional commits for messages
                    - Restrict number of commits per branch
    - TODO: CoAuthor Commits

    - TODO: Add SchemaStruct Class! (V2)
        - TODO: provide implementation for to_engine_type in SchemaStruct Class! (V2)
    - TODO: Generics in new style (V2)
    - TODO: Runner object passed to function (V2)
    - TODO: Pass function name to function itself (V2)
    - TODO: Revisit topic of preloaded DataFrameWrapper vs. manual load or separate module. (V2)
    - TODO: Test all examples automatically (through entrypoints?) (V2)
    - TODO: provide standard functionalities like merge, upsert for engines (V2)
    - TODO: Commiting/Vetting Process (V2)
        - Maintainer only after vetting process/getting to know each other
        - Clear contribution rules (e.g. Size of PR if not [maintainer](https://carlos-camara.github.io/qa-hub-actions/actions/pr-size-labeler.html))
    - TODO: Find a migration mechanism (V2/3)
            Current idea: define a migration table, that needs to be given a read/write method by the user. We can then track all model versions in that table and migrate the versions.
            Discuss how and when a version will be created.
            Should the table only track a state?
    - TODO: Find implementation for expectation models (V2-V3)
    - TODO: Maybe provide a possibility to generate corrupt foreign key values within FakerManager generation (V2/3)

    - TODO: VSCode Plugin or typing extension => Full typing support for tables and dataframe wrappers (V2-V3)
    - TODO: Try to make it work with complex types (Array, Map, Variant) (V3?)
    - TODO: Create way for user to define custom parameters passed to transformations (V3?)
    - TODO: Better Orchestration possibilities (stages etc.) (V3)
    - TODO: Streaming mode through implementation/protocol? for engine (V3)
    - TODO: Staging of Transformation func steps to detatch steps from model and allow plugin capability (V3)
    - TODO: Prompt Primer -> Prompt Erzeugung für Claude etc. (V3)

# Adding examples

```
export EXAMPLE_NAME=<example_name>
cd examples
mkdir $EXAMPLE_NAME
uv init --package --name $EXAMPLE_NAME --directory /workspace/examples/$EXAMPLE_NAME
just create_missing_sub_venvs
cd $EXAMPLE_NAME
uv add --active eltstar
```