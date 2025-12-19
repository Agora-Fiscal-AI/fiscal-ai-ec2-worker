from typing import List, Optional, Dict
from LevelDefinition import LevelDefinition
import yaml

def load_yaml(ruta_archivo):

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            
            config_dict = yaml.safe_load(archivo)
            return config_dict
            
    except yaml.YAMLError as exc:
        print(f"Error al parsear el archivo YAML: {exc}")
        return None
    except Exception as e:
        print(f"Error inesperado al leer el archivo: {e}")
        return None

    return config_dict

#CONFIG_DICT = load_yaml("../utils/legal_structure.yaml")


            
class LegalStrctureConfig:
    """
    This class is responsable of the main juridic structural configuration loaded from .yaml archive
    """
    def __init__(self, conf_dict = load_yaml("../utils/legal_structure.yaml")):
        self.meta = conf_dict.get("meta", {}) # Load general metadata from conf
        self.validation = conf_dict.get("validation", {})
        self.preprocessing = conf_dict.get("preprocessing", {})
        self.versioning = conf_dict.get("versioning", {})

        self.levels: Dict[str, LevelDefinition] = {} # Diccionario que guarda el id del nivel como key y la instancia LevelDefinition como valor
        self._load_levels(conf_dict.get("levels",[])) #cargamos en esta funcion los niveles en forma de lista sacados del .yaml

    def _load_levels(self, levels_config: List[Dict]) -> None: # En este metodo le pasamos una lisa de diccionarios que esta etiquetado en conf
        for level in levels_config:
            definition = LevelDefinition( # Creamos una instancia para cada nivel jerarquico del grafo
                level_id=level["id"],
                name=level["name"],
                aliases= level.get("aliases", []),
                optional= level.get("optional", False),
                numbering=level.get("numbering", {}),
                children=level.get("children",[]),
                implicit=level.get("implicit", False)
            )
            self.levels[definition.level_id] = definition  #ejemplo [{'title': <LevelDefinition: title>}, {...}]

    def get_level(self, level_id: str) -> LevelDefinition:
        return self.levels[level_id]
    


"""

conf = LegalStrctureConfig()
for level_id, level in conf.levels.items():
    numbering = level.numbering
    regex = numbering.get("regex")
    if isinstance(regex, Dict):
        for key, val in regex.items():
            print(f"{level_id}: \n {key}: {val}")
    else:
        print(regex)

"""


"""


level = conf.get_level("fraction")
patterns = level.numbering.get("regex", {})
roman_pattern = patterns["arabic"]
print(roman_pattern)

"""



"""  

ruta_config = '../utils/legal_structure.yaml'

conf = LegalStrctureConfig(conf_dict=configuracion)
level = conf.get_level("inciso")
regex_list = [reg for key, reg in level.numbering["regex"].items()]
print(regex_list)

#print (new_settings.get_level("article").children)
"""
