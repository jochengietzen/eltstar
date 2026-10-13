### aigen_start
from collections.abc import Callable, Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from eltstar.exceptions import WrapperFunctionException
from eltstar.models.data_frame_wrapper.functions.base import WrapperArgSpec, WrapperFunctionSpec
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper

ENTRY_POINTS_PATH = "eltstar.models.data_frame_wrapper.wrapper.entry_points"


# Example ArgSpecs, FuncSpec etc. defined
class SampleArgSpec(WrapperArgSpec):
    column: str


class OtherSampleArgSpec(WrapperArgSpec):
    column: str


class EngineASampleArgSpec(SampleArgSpec):
    mode: str


class EngineBSampleArgSpec(SampleArgSpec):
    mode: str
    extra_flag: bool = False


class SampleFuncSpec[WrapperArg: WrapperArgSpec, TightWrapperArg: WrapperArgSpec](
    WrapperFunctionSpec[WrapperArg, TightWrapperArg]
):
    func_name: str = "sample_func"


# Example case for multiple engines (mocked engines, since we are in the core currently)
class MockEngineA:
    engine_identifier = "mock_engine_a"


class MockEngineB:
    engine_identifier = "mock_engine_b"


def _impl_a(self: Any, function_spec: Any) -> str:  # pylint: disable=unused-argument
    return "a"


def _impl_b(self: Any, function_spec: Any) -> str:  # pylint: disable=unused-argument
    return "b"


def _fake_entry_point(register: Callable[[], None]) -> MagicMock:
    entry_point = MagicMock()
    entry_point.value = f"fake.{register.__name__}"
    entry_point.load.side_effect = register
    return entry_point


@pytest.fixture(autouse=True)
def isolated_wrapper_registry() -> Iterator[None]:
    """Restore the global DataFrameWrapper registry and the dynamically attached methods after each test."""
    old_functions = dict(DataFrameWrapper.registered_wrapper_functions)
    old_loaded = DataFrameWrapper._loaded_plugins  # pylint: disable=protected-access
    old_attrs = set(vars(DataFrameWrapper))
    DataFrameWrapper.registered_wrapper_functions.clear()
    DataFrameWrapper._loaded_plugins = False  # pylint: disable=protected-access
    yield
    for attr in set(vars(DataFrameWrapper)) - old_attrs:
        delattr(DataFrameWrapper, attr)
    DataFrameWrapper.registered_wrapper_functions.clear()
    DataFrameWrapper.registered_wrapper_functions.update(old_functions)
    DataFrameWrapper._loaded_plugins = old_loaded  # pylint: disable=protected-access


def _register_a(
    tight: type[WrapperArgSpec] = EngineASampleArgSpec, broad: type[WrapperArgSpec] = SampleArgSpec
) -> None:
    DataFrameWrapper.register_wrapper_function(
        engine=MockEngineA,  # type: ignore[arg-type]
        func_spec=SampleFuncSpec[Any, Any](arg_spec=broad, tight_arg_spec=tight),
        func=_impl_a,  # type: ignore[arg-type]
    )


def _register_b(
    tight: type[WrapperArgSpec] = EngineBSampleArgSpec, broad: type[WrapperArgSpec] = SampleArgSpec
) -> None:
    DataFrameWrapper.register_wrapper_function(
        engine=MockEngineB,  # type: ignore[arg-type]
        func_spec=SampleFuncSpec[Any, Any](arg_spec=broad, tight_arg_spec=tight),
        func=_impl_b,  # type: ignore[arg-type]
    )


def test_make_function_of_dataframe_plugin_loading():
    # with patched importlib.metadata entry_points:
    entry_points = [_fake_entry_point(_register_a), _fake_entry_point(_register_b)]
    with patch(ENTRY_POINTS_PATH, return_value=entry_points) as patched:
        DataFrameWrapper.load_all_plugins()

    patched.assert_called_once_with(group="eltstar.wrapper_functions")
    for entry_point in entry_points:
        entry_point.load.assert_called_once()

    # Register the actual functions for both engines
    assert len(DataFrameWrapper.registered_wrapper_functions) == 2
    # The wrapper now exposes the function and dispatches by the wrapper's engine
    assert DataFrameWrapper(data_frame=None, engine=MockEngineA).sample_func(function_spec=None) == "a"  # type: ignore[arg-type]  # pylint: disable=no-member
    assert DataFrameWrapper(data_frame=None, engine=MockEngineB).sample_func(function_spec=None) == "b"  # type: ignore[arg-type]  # pylint: disable=no-member


def test_plugin_loading_is_only_done_once():
    with patch(ENTRY_POINTS_PATH, return_value=[_fake_entry_point(_register_a)]) as patched:
        DataFrameWrapper.load_all_plugins()
        DataFrameWrapper.load_all_plugins()
    patched.assert_called_once()


def test_plugin_loading_raises_if_broad_arg_specs_differ():
    # to test the raising of an error, if the arg specs differ
    def register_b_with_other_broad_spec() -> None:
        _register_b(broad=OtherSampleArgSpec)

    entry_points = [_fake_entry_point(_register_a), _fake_entry_point(register_b_with_other_broad_spec)]
    with patch(ENTRY_POINTS_PATH, return_value=entry_points):
        with pytest.raises(ExceptionGroup) as exc_info:
            DataFrameWrapper.load_all_plugins()

    assert exc_info.group_contains(WrapperFunctionException, match="different broad arg spec")


def test_plugin_loading_raises_if_tight_arg_spec_is_not_derived_from_broad_spec():
    # to test the raising of an error, if the tight arg specs differ (i.e. do not adhere to the broad spec)
    def register_b_with_unrelated_tight_spec() -> None:
        _register_b(tight=OtherSampleArgSpec)

    entry_points = [_fake_entry_point(_register_a), _fake_entry_point(register_b_with_unrelated_tight_spec)]
    with patch(ENTRY_POINTS_PATH, return_value=entry_points):
        with pytest.raises(ExceptionGroup) as exc_info:
            DataFrameWrapper.load_all_plugins()

    assert exc_info.group_contains(WrapperFunctionException, match="does not adhere to the same function arguments")


### aigen_end
