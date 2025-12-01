import pdfplumber
import re
from normalize_pdf import normalize_text


class detect_indents:
    def __init__(self, pdf):
        self.pdf_path =pdf

    def detect_article_indentations(self, min_range, max_range):
        """
        Detecta la indentación (x0) típica de los encabezados 'Artículo XX.'
        usando las primeras páginas del PDF.
        Devuelve el promedio de indentaciones encontradas.
        """

        try:
            pdf = pdfplumber.open(self.pdf_path)
        except Exception as e:
            print(f"Error abriendo PDF: {e}")
            return None

        indents = []

        for page in pdf.pages[min_range:max_range]:
            words = page.extract_words(extra_attrs=["fontname", "size"])

            # Agrupar por línea (coordenada top)
            lines = {}
            for w in words:
                lines.setdefault(round(w["top"], 1), []).append(w)

            # Procesar líneas
            for top, line_words in lines.items():
                line_text = " ".join(w["text"] for w in line_words)
                norm = normalize_text(line_text).lower()

                # Detectar encabezado Artículo XX.
                if re.search(r'art[ií]culo\s+\d+\s*\.', norm):

                    # Buscar token exacto "Artículo"
                    for w in line_words:
                        if normalize_text(w["text"]).lower() == "articulo":
                            print(f"Detectado encabezado en PAGE {page.page_number}: x0={w['x0']} texto='{w['text']}'")
                            indents.append(w["x0"])

        pdf.close()

        if not indents:
            print("No se detectaron encabezados de artículos en las primeras páginas.")
            return None

        indent_avg = sum(indents) / len(indents)
        print(f"\nIndentaciones detectadas: {indents}")
        print(f"Indentación promedio: {indent_avg:.2f}px")

        return indent_avg
    
    def detect_rom_sub_indent(self,min_range, max_range):
        try:
            pdf = pdfplumber.open(self.pdf_path)
        except Exception as e:
            print(f"Error abriendo PDF: {e}")
            return None

        indents = []

        for page in pdf.pages[min_range:max_range]:
            words = page.extract_words(extra_attrs=["fontname", "size"])

            # Agrupar por línea (coordenada top)
            lines = {}
            for w in words:
                lines.setdefault(round(w["top"], 1), []).append(w)

            for top, line_words in lines.items():

                # Texto normalizado SOLO para buscar regex
                line_text = " ".join(w["text"] for w in line_words)
                
                # 👇 No lo convierto a lower, porque destruye romanos en mayúsculas
                line_norm = normalize_text(line_text)

                # Detectar subtema en romano: I. II. III. IV. …
                if re.search(r'\b[IVXLCDM]+\s*\.', line_norm):

                    # Ahora buscamos el token exacto romano dentro de la línea
                    for w in line_words:
                        tok = normalize_text(w["text"]).replace(" ", "")
                        
                        # Coincide algo como "IV." o "XII."
                        if re.fullmatch(r'[IVXLCDM]+\.', tok):
                            print(f"Detectado subtema en page {page.page_number}: x0={w['x0']} texto='{w['text']}'")
                            indents.append(w["x0"])
                            break  # salir, solo necesitamos el romano


        pdf.close()

        if not indents:
            print("No se detectaron subtemas en romano.")
            return None

        ranges = {
            "min": min(indents),
            "max": max(indents)
        }
        print(f"\nIndentaciones detectadas: {indents}")
        print(f"rengo de indentacion: min {min(indents):.2f}, max: {max(indents):.2f}px")

        return ranges