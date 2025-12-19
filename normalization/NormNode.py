from typing import List, Optional, Dict
from uuid import uuid4

class NormNode:
    """
    Atomic normative node representing a legal structural unit or node
    """

    def __init__(
        self,
        level: str,  # article, fraction, inciso...
        number: Optional[str], # 64, I, a), None (implicit)
        title: str, # this attribute is gonna store the entire content of the level by just concatenating it in ContentBuilder.py
        order: int,   # order among siblings
        parent_id: Optional[str],
        law_version: str,
        content: List[str] = None,
        start_line: int = 0
    ):
        self.id: str = str(uuid4())
        self.level: str = level
        self.number: Optional[str] = number
        self.title: str = title.strip()
        self.order: int = order
        self.parent_id: Optional[str] = parent_id
        self.law_version: str = law_version

        self.start_line:int = start_line
        self.content:List[str] = content if content is not None else []
        self.children: List["NormNode"] = []
        self.metadata: Dict = {}
    
    def add_child(self, child: "NormNode") -> None:
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def __repr__(self) -> str:
        return (
            f"<NormNode level = {self.level} "
            f"number = {self.number} "
            f"children={len(self.children)}>"
        )
    




"""  EXAMPES OF FUNCTIONALITY
article = NormNode(
    level="article",
    number="64",
    text="un articulo",
    order=1,
    parent_id=None,
    law_version="v1.0"
)



fraction = NormNode(
    level="fraction",
    number="I",
    text="una fraccion",
    order=1,
    parent_id=article.id,
    law_version="v1.0"
)

fraction1 = NormNode(
    level="fraction",
    number="I",
    text="una fraccion2",
    order=1,
    parent_id=article.id,
    law_version="v1.0"
)
incise = NormNode(
    level="incise",
    number="a)",
    text="un inciso",
    order=1,
    parent_id=article.id,
    law_version="v1.0"
)
incise1 = NormNode(
    level="incise",
    number="a)",
    text="un inciso2",
    order=1,
    parent_id=article.id,
    law_version="v1.0"
)
fraction1.add_child(incise1)
fraction.add_child(incise)
article.add_child(fraction1)
article.add_child(fraction)
print (article.text)
for child in article.children:
    print("|-",child.text)
    for child1 in child.children:
            print(" |-",child1.text)
"""
