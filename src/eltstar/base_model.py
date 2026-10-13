# pylint: disable=invalid-name
from collections.abc import ItemsView, KeysView, ValuesView
from os import PathLike

import yaml
from pydantic import BaseModel as _BaseModel
from pydantic import RootModel


class BaseModel(_BaseModel):
    @classmethod
    def from_yaml(cls, path: PathLike, encoding: str = "utf-8"):
        """
        Allows you to instantiate a model from a yaml file
        :param path: Path of the yaml file
        :param encoding: Encoding of the file
        returns: Model
        """
        try:
            with open(path, encoding=encoding) as f:
                data = yaml.full_load(f)
        except OSError as e:
            raise OSError(f"Could not read YAML file at '{path}': {e}") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Could not parse YAML file at '{path}': {e}") from e
        return cls(**data)

    def __hash__(self) -> int:
        return hash(str(self.model_dump()))


class DictRootModel[KeyType, ValueType](RootModel[dict[KeyType, ValueType]]):
    root: dict[KeyType, ValueType]

    def items(self) -> ItemsView[KeyType, ValueType]:
        """Root's items method"""
        return self.root.items()

    def keys(self) -> KeysView[KeyType]:
        return self.root.keys()

    def values(self) -> ValuesView[ValueType]:
        return self.root.values()


class ListRootModel[ItemType](RootModel[list[ItemType]]):
    root: list[ItemType]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)
