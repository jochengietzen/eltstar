from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import model_validator

from eltstar.base_model import BaseModel
from eltstar.graph import Lineage
from eltstar.runtime_system.base import BaseRuntimeSystem, RuntimeSystemConfig


class DatabricksDependsOn(BaseModel):
    task_key: str


class DatabricksNotebookTask(BaseModel):
    notebook_path: str


class DatabricksPythonWheelTask(BaseModel):
    package_name: str
    entry_point: str
    parameters: list[str] = []
    named_parameters: dict[str, Any] = {}


class DatabricksTask(BaseModel):
    task_key: str
    depends_on: list[DatabricksDependsOn] = []
    # notebook_task: DatabricksNotebookTask
    python_wheel_task: DatabricksPythonWheelTask


class DatabricksRuntimeSystemConfig(RuntimeSystemConfig):
    yaml_resource_path: Path
    tasks_path: str
    package_name: str
    entry_point: str

    @model_validator(mode="after")
    def tasks_path_correction(self) -> Self:
        self.tasks_path = self.tasks_path.rstrip(".tasks")
        return self


# --8<-- [start:databricks-rs-example]
class DatabricksAssetBundleJobRS(BaseRuntimeSystem):
    @classmethod
    def generate(
        cls, lineage: Lineage, runtime_system_config: RuntimeSystemConfig, source_table_type: type | None = None
    ) -> Any:
        source_tables = list(lineage.iter_source_tables(source_table_type=source_table_type))
        sink_tables = list(lineage.iter_sink_tables())
        transformations = list(lineage.iter_transformations())

        with open(runtime_system_config.yaml_resource_path, encoding="utf-8") as file:
            resource_file = yaml.safe_load(file)

        def task_name(name: str, node_type: Literal["read", "write", "transform"]) -> str:
            return f"{node_type}_{name}"

        output_transformation_lookup = {
            transformation.transformation.output_table_model.path.name: DatabricksDependsOn(
                task_key=task_name(name=transformation.name, node_type="transform")
            )
            for transformation in transformations
        }
        nodes = sorted(
            [
                DatabricksTask(
                    task_key=task_name(name=node.path.name, node_type="read"),
                    depends_on=[],
                    # notebook_task=DatabricksNotebookTask(),
                    python_wheel_task=DatabricksPythonWheelTask(
                        package_name=runtime_system_config.package_name,
                        entry_point=runtime_system_config.entry_point,
                        named_parameters={"table_path": node.path},
                    ),
                )
                for node in source_tables
            ]
            + [
                DatabricksTask(
                    task_key=task_name(name=node.name, node_type="transform"),
                    # notebook_task=DatabricksNotebookTask(),
                    python_wheel_task=DatabricksPythonWheelTask(
                        package_name=runtime_system_config.package_name,
                        entry_point=runtime_system_config.entry_point,
                        named_parameters={"table_path": node.name},
                    ),
                    depends_on=[
                        DatabricksDependsOn(task_key=task_name(name=dep, node_type="transform"))
                        for dep in node.depends_on_transformations
                    ],
                )
                for node in transformations
            ]
            + [
                DatabricksTask(
                    task_key=task_name(name=node.path.name, node_type="write"),
                    depends_on=[output_transformation_lookup[node.path.name]],
                    # notebook_task=DatabricksNotebookTask(),
                    python_wheel_task=DatabricksPythonWheelTask(
                        package_name=runtime_system_config.package_name,
                        entry_point=runtime_system_config.entry_point,
                        named_parameters={"table_path": node.path},
                    ),
                )
                for node in sink_tables
            ],
            key=lambda x: x.task_key,
        )
        tasks = [node.model_dump() for node in nodes]

        current = resource_file
        for key in runtime_system_config.tasks_path.split("."):
            current = current[key]

        current["tasks"] = tasks
        with open(runtime_system_config.yaml_resource_path, "w", encoding="utf-8") as file:
            yaml.dump(resource_file, file)


# --8<-- [end:databricks-rs-example]
