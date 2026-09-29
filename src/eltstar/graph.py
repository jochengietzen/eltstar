import json
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, NamedTuple

import networkx as nx

if TYPE_CHECKING:
    from eltstar.models.table import Table
    from eltstar.transformation import Transformation


class Node:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __hash__(self) -> int:
        return hash(self.data)

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.label}>"

    @property
    def data(self) -> str:
        """aigen_start
        Return a stable JSON serialization of the node's data dictionary.
        aigen_end"""
        return json.dumps(self._data, sort_keys=True)

    @property
    def label(self) -> str:
        """aigen_start
        Return a human-readable label built from the node's data key-value pairs.
        aigen_end"""
        return "_".join(["-".join(kv) for kv in self._data.items()])


class TransformationNode(Node):
    def __init__(self, transformation: "Transformation"):
        super().__init__({"name": transformation.name})
        self.transformation = transformation


class TableNode(Node):
    def __init__(self, table: "Table"):
        super().__init__({"path": table.path.model_dump_json()})  # type: ignore
        self.table = table


class LineageTransformationElement(NamedTuple):
    name: str
    input_models: dict[str, "Table"]
    depends_on_transformations: list[str]
    transformation: "Transformation"


class Lineage:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_transformations(self, transformations: dict[str, "Transformation"]) -> "Lineage":
        """aigen_start
        Add all given transformations and their table edges to the lineage graph.
        aigen_end"""
        for transformation in transformations.values():
            t = TransformationNode(transformation=transformation)
            output_node = TableNode(table=transformation.output_table_model)
            self.graph.add_edge(t, output_node, key=t.transformation.graph_label)
            for input_model_instruction in transformation.input_table_models.values():
                input_node = TableNode(table=input_model_instruction.table)
                self.graph.add_edge(input_node, t, key=t.transformation.graph_label)
        return self

    def iter_source_tables(self, source_table_type: type | None = None) -> Generator["Table"]:
        """aigen_start
        Yield all source tables (nodes with no incoming edges), optionally filtered by type.
        aigen_end"""
        for node in nx.topological_sort(self.graph):
            if isinstance(node, TableNode) and self.graph.in_degree(node) == 0:
                if source_table_type is not None and not isinstance(node.table, source_table_type):
                    continue
                yield node.table

    def iter_sink_tables(self, sink_table_type: type | None = None) -> Generator["Table"]:
        """aigen_start
        Yield all sink tables (nodes with no outgoing edges), optionally filtered by type.
        aigen_end"""
        for node in nx.topological_sort(self.graph):
            if isinstance(node, TableNode) and self.graph.out_degree(node) == 0:
                if sink_table_type is not None and not isinstance(node.table, sink_table_type):
                    continue
                yield node.table

    @property
    def transformations_graph(self) -> nx.MultiDiGraph:
        """aigen_start
        Return a derived graph with table nodes removed, leaving only transformation-to-transformation edges.
        aigen_end"""
        g = self.graph.copy()

        nodes = list(g.nodes)

        for node in nodes:
            if not isinstance(node, TableNode):
                continue
            in_edges = g.in_edges(node, keys=True)
            out_edges = g.out_edges(node, keys=True)
            if in_edges and out_edges:
                for in_edge in in_edges:
                    for out_edge in out_edges:
                        g.add_edge(in_edge[0], out_edge[1], key=in_edge[2])
            g.remove_node(node)
        return g

    def iter_transformations(self) -> Generator[LineageTransformationElement]:
        """aigen_start
        Yield all transformations in topological order with their dependencies.
        aigen_end"""
        g = self.transformations_graph
        for node in nx.topological_sort(g):
            if isinstance(node, TransformationNode):
                yield LineageTransformationElement(
                    name=node.transformation.name,
                    input_models={
                        key: table_model.table for key, table_model in node.transformation.input_table_models.items()
                    },
                    depends_on_transformations=sorted(
                        [n.transformation.name for n, _ in g.in_edges(node) if isinstance(n, TransformationNode)]
                    ),
                    transformation=node.transformation,
                )

    def draw(self, graph: nx.MultiDiGraph | None = None):
        """aigen_start
        Render the lineage graph visually using matplotlib and networkx layout algorithms.
        aigen_end"""
        # pylint: disable=import-outside-toplevel
        import itertools as it

        import matplotlib.pyplot as plt  # type: ignore # pylint: disable=import-error

        g = self.graph if graph is None else graph

        for layer, nodes in enumerate(nx.topological_generations(g)):
            for node in nodes:
                g.nodes[node]["layer"] = layer
        pos = nx.multipartite_layout(g, subset_key="layer")
        fig, ax = plt.subplots()
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.1] * 4)]
        nx.draw_networkx_nodes(g, pos=pos, ax=ax)
        labels = nx.draw_networkx_labels(g, pos=pos, ax=ax, labels={node: node.label for node in g.nodes})
        for _, label in labels.items():
            label.set_rotation(5)
        nx.draw_networkx_edges(g, pos=pos, ax=ax, connectionstyle=connectionstyle)

        fig.tight_layout()
        fig.set_figheight(15)
        fig.set_figwidth(30)
        plt.show()
