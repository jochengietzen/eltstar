import datetime
import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from faker import Faker

if TYPE_CHECKING:
    from eltstar.testing.faker_manager import FakerManager


class FakerType:
    def __init__(
        self,
        generation_id: str | None = None,
        reuse_percentage_min: float = 0.3,
        reuse_percentage_max: float = 0.8,
        allow_duplicate_values: bool = False,
    ):
        self.generation_id = generation_id
        self.reuse_percentage_min = reuse_percentage_min if 0 <= reuse_percentage_min <= 1 else 0
        self.reuse_percentage_max = reuse_percentage_max if 0 <= reuse_percentage_max <= 1 else 1
        self.allow_duplicate_values = allow_duplicate_values
        self.reuse_percentage_min = min(self.reuse_percentage_min, self.reuse_percentage_max)

    def register_in_manager(self, manager: "FakerManager") -> Any:
        """aigen_start
        Register this FakerType instance in the given FakerManager.
        aigen_end"""
        manager.register_faker_type(self)

    @abstractmethod
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        pass

    @property
    def _properties(self) -> dict[str, Any]:
        return {
            k: v
            for k, v in self.__dict__.items()
            if k in ["generation_id", "reuse_percentage_min", "reuse_percentage_max", "allow_duplicate_values"]
        }

    def to_json(self) -> str:
        """aigen_start
        Serialize the FakerType properties to a JSON string.
        aigen_end"""
        return json.dumps(self._properties)

    def __hash__(self) -> int:
        return hash(self.to_json())


class FakerTextType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.text()


class FakerStringType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.word()


class FakerIntType(FakerType):
    def __init__(
        self,
        min_val: int,
        max_val: int,
        generation_id: str | None = None,
        reuse_percentage_min: float = 0.3,
        reuse_percentage_max: float = 0.8,
        allow_duplicate_values: bool = False,
    ):
        super().__init__(
            generation_id,
            reuse_percentage_min,
            reuse_percentage_max,
            allow_duplicate_values,
        )
        self.min_val = min_val
        self.max_val = max_val

    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.random_int(min=self.min_val, max=self.max_val)


class FakerIDType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.uuid4()


class FakerTimestampTypeSecondsUTC(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.date_time(tzinfo=datetime.UTC)
