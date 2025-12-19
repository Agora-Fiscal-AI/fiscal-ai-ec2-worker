from typing import List, Dict, Optional

class LevelDefinition:
    """
    This class is responsible of define a juridic level (Titulo, Fraccion, Inciso, etc)
    It is complettely based on the legal_structure.conf archive
    """
    # Define the constructor by giving attributes of the level in the graph, all those are configurated from the .conf archive
    def __init__(
        self,
        level_id: str,
        name: str,
        aliases: List[str],
        optional: bool,
        numbering: Dict,
        children: List[str],
        implicit: bool = False

    ):
        self.level_id = level_id
        self.name = name
        self.aliases = aliases
        self.optional = optional
        self.numbering = numbering
        self.children = children
        self.implicit = implicit
    
    def allows_child(self, child_level_id: str) -> bool: 
        return child_level_id in self.children
    def __repr__(self) -> str:
        return f"<LevelDefinition: {self.level_id}>"
    
    
"""
article_level = LevelDefinition(
    level_id="article",
    name="Artículo",
    aliases=["Artículo", "Art.", "ARTÍCULO"],
    optional=False,
    numbering={
        "type": "numeric",
        "strict_sequence": False,
        "case_sensitive": False
    },
    children=["fraction"]
)
article_level.allows_child("chapter")
print (article_level.__repr__(), article_level.aliases)

""" 
