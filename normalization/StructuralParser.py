from typing import List, Dict
import re
import unicodedata
#from DetectedElement import DetectedElement

#CONFIGURATION = LegalStrctureConfig()  Configuration instance
#RAW_TEXT = RawTextDocument(get_text("Fiscalizacion.pdf"), "Fiscalizacion.pdf") # Raw text instance already splitted in lines




class LevelMatch:
    """
    Represents a detected structural level candidate in the text.
    """    
    def __init__(self, level_id: str, line_index: int, raw_text: str, match_data: Dict):
        self.level_id = level_id
        self.line_index = line_index
        self.raw_text = raw_text
        self.match_data = match_data

class LevelDetector:
    """
    Detects structural level candidates in a RawTextDocument.
    """
    def __init__(self, config):
       self.config = config

    def detect(self, document) -> List[LevelMatch]:
        matches: List[LevelMatch] = []

        for idx, line in document.iter_lines():
            for level in self.config.levels.values():
                result = self._match_level(level, line)
                if result:
                    matches.append(
                        LevelMatch(
                            level_id = level.level_id,
                            line_index = idx,
                            raw_text = line,
                            match_data = result
                        )
                    )
        return matches
    
    def _match_level(self, level, line: str):
        """
        Returns match_data if the line matches the level definition.
        Otherwise returns None.
        """


        # Implicit levels are never explicitly detected
        if getattr(level, "implicit", False):
            return None

        regex = level.numbering.get("regex")

        if not regex:
            return None

        aliases = getattr(level, "aliases", [])


        if aliases:
            alias_pattern = "|".join(re.escape(a) for a in aliases)
            base_pattern = rf"^(?P<alias>{alias_pattern})\s+"
        else:
            base_pattern = ""

        line = line.strip()

        # simple regex
        if isinstance(regex, str):
            pattern = base_pattern + regex
            
            m = re.match(pattern, line, re.IGNORECASE)
            if not m:
                return None
            groups = m.groupdict()
            return {
                "alias": m.group("alias") if aliases else None,
                "number":groups["num"] if "num" in groups else m.group(1),
                "number_type": level.numbering.get("type"),
                "raw": m.group(0)
            }

        # multiple regex types (roman, arabic, alpha...)
        if isinstance(regex, dict):
            for num_type, num_pattern in regex.items():
                pattern = base_pattern + num_pattern
                
                m = re.match(pattern, line, re.IGNORECASE)
                if not m:
                    continue
                #print(f"patron dic: {pattern} \n")
                groups = m.groupdict()
                #number = groups["num"] if "num" in groups else m.group(1)
           

                return {
                    "alias": m.group("alias") if aliases else None,
                    "number": groups["num"] if "num" in groups else m.group(1),
                    "number_type": num_type,
                    "raw": m.group(0)
                }

        return None


"""
parser =  LevelDetector(CONFIGURATION)
matches =  parser.detect(RAW_TEXT)
for i,match in enumerate(matches):
    print(f"{i}:{match.level_id},idx:{match.line_index} ,Raw:{match.raw_text}\n")


"""
#