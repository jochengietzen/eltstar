import pytest
from eltstar_polars_example.manager import manager

from eltstar.testing.utils import parametrize_for_tests


@pytest.mark.parametrize("parameter", parametrize_for_tests(manager=manager))
def test_all_transformations(faker_manager, engine, parameter):
    print(parameter.name)
    input_models = {}
    for name, generate in parameter.input_models.items():
        input_models[name] = generate(faker_manager=faker_manager, engine=engine, n_values=100)
        print(name)
        print(input_models[name].data_frame)
    result = parameter.transformation.func(**input_models)
    assert result is not None
