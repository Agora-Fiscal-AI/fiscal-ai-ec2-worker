from StructureBuilder import create_tree, RAW_TEXT
from NormNode import NormNode
from typing import List, Optional
from StructuralParser import LevelMatch

ROOTS, MATCH = create_tree()


class ContentBinder:

    def __init__(self, nodes: List[NormNode]):
        self.nodes = nodes

        # indexación REAL: start_line → NormNode
        self.node_by_line = {
            node.start_line: node
            for node in self._walk(nodes)
            if hasattr(node, "start_line")
        }

    def _walk(self, nodes):
        for n in nodes:
            yield n
            yield from self._walk(n.children)

    def bind(self, document):
        total_lines = len(document.lines)

        active_node = None

        for idx in range(total_lines):
            if idx in self.node_by_line:
                active_node = self.node_by_line[idx]
                continue

            if active_node:
                line = document.get_line(idx).strip()
                if line:
                    active_node.content.append(line)



content = ContentBinder(ROOTS)
content.bind(RAW_TEXT)

def print_tree(node, indent=0):
    spacer = " " * indent
    print(f"{spacer}- {node.level} {node.number} | children: {len(node.children)}, | contenido: {node.title}, | contenido: {node.content}")

    for child in node.children:
        print_tree(child, indent + 2)

for root in ROOTS:
    print_tree(root)
