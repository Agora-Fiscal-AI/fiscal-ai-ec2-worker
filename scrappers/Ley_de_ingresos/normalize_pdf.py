import unicodedata
import os



def normalize_text(pdf_text: str) -> str:
    clean_text = unicodedata.normalize("NFD", pdf_text)
    result = "" 
    for c in clean_text:
        if unicodedata.category(c) != "Mn":
            result += c
    return result