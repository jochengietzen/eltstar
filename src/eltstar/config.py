from typing import Any, ClassVar, Protocol, TypeVar

from eltstar.base_model import BaseModel


class LoadMethod(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> "BaseModel": ...


class EnvironmentConfig(BaseModel):
    """Information to staging environment: connection, settings"""

    registered_load_methods: ClassVar[dict[str, LoadMethod]] = {}

    @classmethod
    def register_load_method(cls, situation_identifier: str, method: LoadMethod) -> None:
        """aigen_start
        Register a load method for the given situation identifier.
        aigen_end"""
        cls.registered_load_methods[situation_identifier] = method

    @classmethod
    def load(cls, *args: Any, situation_identifier: str, **kwargs: Any) -> "EnvironmentConfig":
        """aigen_start
        Load and return an EnvironmentConfig using the registered method for the given situation.
        aigen_end"""
        if situation_identifier not in cls.registered_load_methods:
            raise NotImplementedError(
                f"The configuration {cls.__name__} does not have a load function for "
                f"situation {situation_identifier} implemented."
            )
        return cls.registered_load_methods[situation_identifier](
            *args,
            **kwargs,
        )  # type: ignore # TODO: proper typing for configuration call

    env: str


class RuntimeConfig(BaseModel):
    """Possibility to pass runtime specific: storage environments, client Ids"""

    registered_load_methods: ClassVar[dict[str, LoadMethod]] = {}

    @classmethod
    def register_load_method(cls, situation_identifier: str, method: LoadMethod) -> None:
        """aigen_start
        Register a load method for the given situation identifier.
        aigen_end"""
        cls.registered_load_methods[situation_identifier] = method

    @classmethod
    def load(cls, *args: Any, situation_identifier: str, **kwargs: Any) -> "RuntimeConfig":
        """aigen_start
        Load and return a RuntimeConfig using the registered method for the given situation.
        aigen_end"""
        if situation_identifier not in cls.registered_load_methods:
            raise NotImplementedError(
                f"The configuration {cls.__name__} does not have a load function for "
                f"situation {situation_identifier} implemented."
            )
        return cls.registered_load_methods[situation_identifier](
            *args,
            **kwargs,
        )  # type: ignore # TODO: proper typing for configuration call


EnvironmentConfigType = TypeVar("EnvironmentConfigType", bound=EnvironmentConfig)  # pylint: disable=invalid-name
RuntimeConfigType = TypeVar("RuntimeConfigType", bound=RuntimeConfig)  # pylint: disable=invalid-name
