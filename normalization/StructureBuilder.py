from typing import List, Dict, Optional, Tuple
from NormNode import NormNode
from StructuralParser import  LevelMatch, LevelDetector
from LegalStructureConfig import LegalStrctureConfig
from RawTextDocument import RawTextDocument
from TextExtractor import get_text

CONFIGURATION: LegalStrctureConfig = LegalStrctureConfig()  # Configuration instance
RAW_TEXT: str = RawTextDocument(get_text("Fiscalizacion.pdf"), "Fiscalizacion.pdf") # Raw text instance already splitted in lines

class StructureBuilder:
    """
    Builds a hierarchical normatie structure from detected LevelMatch objects.
    """

    def __init__(self, law_version: str):
        self.config: LegalStrctureConfig = CONFIGURATION
        self.law_version: str =  law_version

        self.stack: List[NormNode] = []

        self.roots: List[NormNode] = []

        self.order_counter: Dict[str,int] = {}

    def build(self, matches: List[LevelMatch]) -> List[NormNode]:
        for match in matches:
            self._process_match(match)
        return self.roots
    
    def _process_match(self, match: LevelMatch) -> None:
        level_id = match.level_id
        level_def = self.config.get_level(level_id)

        self.order_counter.setdefault(level_id, 0)
        self.order_counter[level_id] += 1

        number = match.match_data.get("number")
        text = match.raw_text

        parent = self._find_parent(level_id)

        node = NormNode(
            level=level_id,
            number=number,
            title=text,
            order=self.order_counter[level_id],
            parent_id=parent.id if parent else None,
            law_version=self.law_version,
            
        )
        node.start_line = match.line_index
        print(f"ESTE NODO INICIA EN LA LINEA: {node.start_line}\n")
        if parent:
            parent.add_child(node)
        else:
            self.roots.append(node)

        self.stack.append(node)

    def _find_parent(self, level_id: str) -> Optional[NormNode]:
        """
        finds the nearest valid parent for the given level.
        Pops invalid stack nodes if necessary
        """
        allowed_parents = self._allowed_parents(level_id)
        while self.stack:
            candidate = self.stack[-1]
            if candidate.level in allowed_parents:
                return candidate
            self.stack.pop()

        return None
    def _allowed_parents(self, level_id: str) -> List[str]:
        """
        make the query to the .yaml to see what are its level parents
        """
        for level in self.config.levels.values():
            if level_id in level.children:
                return [level.level_id]
        return []


def create_tree() -> Tuple[List[NormNode], List[LevelMatch]]:
    tree = StructureBuilder("2025-01-1")
    detector = LevelDetector(CONFIGURATION)
    parser = detector.detect(RAW_TEXT)
    roots = tree.build(matches=parser)
    return roots, parser



"""
for root in roots:
    print(f"{root}\n")
    for child in root.children:
        print(f" |-{child}, parent_id: {child.text}\n")
        for fract_child in child.children:
            print(f"  |-{fract_child},  parnet_id {fract_child.text}\n")
"""
