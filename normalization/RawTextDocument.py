from typing import List
from TextExtractor import get_text

class RawTextDocument:
    """
    Represents a raw, line-preserved legal document extracted from a source (PDF).
    This object is the single source of truth for all downstream parsing.
    """
    def __init__(self, text:str, source:str):
        self.source = source
        self.text = text
        self.lines : List[str] = self._split_lines()

    def _split_lines(self) -> List[str]:
        return [line.strip() for line in self.text.splitlines() if line.split()]
    
    def __len__(self) -> int:
        return len(self.lines)
    
    def get_line(self, index:int) -> str:
        return self.lines[index]
    
    def iter_lines(self):
        for i, line in enumerate(self.lines):
            yield i, line
    


"""
parser = RawTextDocument(get_text("Fiscalizacion.pdf"), "Fiscalizacion.pdf")
print(len(parser))

"""




