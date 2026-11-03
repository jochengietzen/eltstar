from collections.abc import Generator
from typing import NamedTuple

from eltstar.engines.base import Engine
from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper
from eltstar.models.table import Table
from eltstar.testing.faker_manager import FakerManager
from eltstar.transformation import Transformation, TransformationManager


class GenerateFixture:
    def __init__(self, name: str, model: Table):
        self.name = name
        self.model = model

    def __call__(self, faker_manager: FakerManager, engine: Engine, n_values: int = 100) -> DataFrameWrapper:
        return faker_manager.generate(engine=engine, n_values=n_values, table=self.model)


class ParameterizedTest(NamedTuple):
    name: str
    transformation: Transformation
    input_models: dict[str, GenerateFixture]


def parametrize_for_tests(manager: TransformationManager) -> Generator[ParameterizedTest]:
    """aigen_start
    Yield ParameterizedTest instances for each registered transformation in the manager.
    aigen_end"""
    for name, transformation in manager._registered_transformations.items():  # pylint: disable=protected-access
        input_models = {}
        for model_name, input_table_model in transformation.input_table_models.items():
            input_models[model_name] = GenerateFixture(name=model_name, model=input_table_model.table)
        yield ParameterizedTest(name=name, transformation=transformation, input_models=input_models)
