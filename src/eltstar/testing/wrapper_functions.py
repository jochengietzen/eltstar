from eltstar.engines.base import Engine
from eltstar.engines.eltstar_arrow_engine import ArrowEngine
from eltstar.models.data_frame_wrapper.functions.base import WrapperArgSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.schema import Schema


# pylint: disable=too-many-locals
def compare_wrapper_functions_accross_engines(
    dfw: DataFrameWrapper,
    engine_func_spec_lookup: dict[type[Engine], WrapperArgSpec],
    func_identifier: str,
    expected_result_schema: Schema,
) -> dict[str, DataFrameWrapper]:
    base_df_arrow = dfw.convert_to(target_engine=ArrowEngine)

    results = {}
    engine_lookup = {key.engine_identifier: key for key in engine_func_spec_lookup.keys()}
    engine_func_lookup = {key.engine_identifier: value for key, value in engine_func_spec_lookup.items()}
    for engine_specific_function_key in DataFrameWrapper.registered_wrapper_functions:
        if (
            engine_specific_function_key.func_name != func_identifier
            or engine_specific_function_key.engine_identifier not in engine_lookup
        ):
            continue
        results[engine_specific_function_key.engine_identifier] = getattr(
            base_df_arrow.convert_to(target_engine=engine_lookup[engine_specific_function_key.engine_identifier]),
            func_identifier,
        )(function_spec=engine_func_lookup[engine_specific_function_key.engine_identifier])

    res_it = iter(results.items())
    first_engine, first_res = next(res_it)
    first_res.schema = expected_result_schema
    first_res_frame = first_res.convert_to(target_engine=ArrowEngine).data_frame
    first_res_frame = first_res_frame.select(sorted(first_res_frame.column_names))
    for n in res_it:
        other_engine, other_res = n
        other_res.schema = expected_result_schema
        other_res_frame = other_res.convert_to(target_engine=ArrowEngine).data_frame
        other_res_frame = other_res_frame.select(sorted(other_res_frame.column_names))
        assert first_res_frame.column_names == other_res_frame.column_names
        for column in first_res_frame.column_names:
            first_col_list, other_col_list = (
                first_res_frame.column(column).to_pylist(),
                other_res_frame.column(column).to_pylist(),
            )
            assert first_col_list == other_col_list, (
                f"Mismatch in column {column} found for engines:"
                f"\n{first_engine}: {first_col_list}\n{other_engine}: {other_col_list}"
            )

    return results
