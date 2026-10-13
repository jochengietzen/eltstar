# from abc import abstractmethod
# from collections import defaultdict
# from collections.abc import Callable
# from typing import TYPE_CHECKING, Any, ClassVar

# from eltstar.base_model import BaseModel

# if TYPE_CHECKING:
#     from eltstar.models.data_frame_wrapper.wrapper import DataFrameWrapper

# # We are stuck with how to bring the expectation result into a form, that can be used to
# # do quarantining and evaluation. Maybe through an extension of the dataframewrapper?


# class RowLevelExpectationResult:
#     pass


# class RowLevelExpectation(BaseModel):
#     _engine_specific_calls: ClassVar[dict[str, dict[str, Callable[[Any], RowLevelExpectationResult]]]] = defaultdict(
#         dict
#     )

#     name: str

#     @classmethod
#     @property
#     def expectation_identifier(cls) -> str:
#         """aigen_start
#         Return a unique string identifier for this expectation class.
#         aigen_end"""
#         return "_".join([cls.__name__, str(id(cls))])

#     @classmethod
#     def register_engine_call(cls, func: Callable[[Any], RowLevelExpectationResult], engine_identifier: str) -> None:
#         """aigen_start
#         Register an engine-specific implementation for this expectation.
#         aigen_end"""
#         cls._engine_specific_calls[cls.expectation_identifier][engine_identifier] = func

#     @abstractmethod
#     def __call__(self, *args: Any, data_frame: "DataFrameWrapper", **kwds: Any) -> Any:
#         pass


# class RowLevelColumnExpectation(RowLevelExpectation):
#     pass


# class RowLevelTableExpectation(RowLevelExpectation):
#     pass


# # class MinMaxExpectation(RowLevelColumnExpectation):
# #     min: int
# #     max: int

# #     def __call__(self, *args: Any, data_frame: DataFrameWrapper, **kwds: Any) -> Any:
# #         return super().__call__(*args, data_frame=data_frame, **kwds)


# # MinMaxExpectation.register_engine_call(MinMaxExpectation.__call__, engine_identifier="polars")


# # logger.info(id(RowLevelColumnExpectation), dict(RowLevelExpectation._engine_specific_calls))
