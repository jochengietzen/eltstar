from eltstar.config import EnvironmentConfig, RuntimeConfig


class MyEnvironmentConfig(EnvironmentConfig):
    file_path: str


class MyRuntimeConfig(RuntimeConfig):
    foo: str = "bar"


MyEnvironmentConfig.register_load_method("local", MyEnvironmentConfig.from_yaml)

MyRuntimeConfig.register_load_method("local", lambda: MyRuntimeConfig())
