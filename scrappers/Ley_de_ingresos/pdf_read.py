import pdfplumber
import pandas as pd
import os
import re
from normalize_pdf import normalize_text
from indents import detect_indents


new_indent = detect_indents(pdf = "test_archives/Ley_amealco.pdf")
ARTICLE_INDENT = new_indent.detect_article_indentations(14,40)  #selección de rango de páginas para la detección de un promedio de indentación de los artículos
ROMAN_INDENT = new_indent.detect_rom_sub_indent(10,60)


SECCIONES = {
    "LEY DE INGRESOS DEL MUNICIPIO DE": "LEY DE INGRESOS",
    "SECCION PRIMERA": "IMPUESTOS",
    "SECCION SEGUNDA": "CONTRIBUCIONES DE MEJORAS", 
    "SECCION TERCERA": "DERECHOS",
    "SECCION CUARTA": "PRODUCTOS",
    "SECCION QUINTA": "APROVECHAMIENTOS",
    "SECCION SEXTA": "INGRESOS POR LA VENTA DE BIENES Y PRESTACION DE SERVICIOS",
    "SECCION SEPTIMA": "PARTICIPACIONES Y APORTACIONES, CONVENIOS, INCENTIVOS DERIVADOS DE LA COLABORACION FISCAL Y FONDDOS DISTINTOS DE APORTACIONES",
    "SECCION OCTAVA": "TRANSFERENCIAS, ASIGNACIONES, SUBSIDIOS Y OTRAS AYUDAS",
    "SECCION NOVENA": "INGRESOS DERIVADOS DE FINANCIAMIENTO",
    "SECCION DECIMA": "DISPOSICIONES GENERALES Y ESTIMULOS FISCALES"
}

def is_bold_word(word, page, avg_size=None):
    """Detecta si una palabra está en negritas"""
    try:
        font_name = word.get("fontname", "").lower()
        font_size = word.get("size", 0)
        
     
        if "bold" in font_name:
            return True
            
        # Variantes de negritas
        bold_indicators = ["black", "heavy", "demi", "boldmt", "bd", "bld"]
        if any(indicator in font_name for indicator in bold_indicators):
            return True
            
        # Comparación por tamaño
        if avg_size and font_size > avg_size * 1.12:
            return True
            
        # Tamaño por default
        if font_size > 11:
            return True
            
    except Exception:
        pass
    
    return False




def extract_pdf_and_tables(pdf_path: str, output_path=None, csv_folder="../../standar-transformers/CSVs/amealco_csv/") -> str:
    full_text_parts = []
    current_section = None
    current_article = None
    current_roman = None
    section_content = []
    article_content = []
    roman_content = []

    os.makedirs(csv_folder, exist_ok=True)
 
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"Procesando página {page_num}...")

            # Extraer tablas
            tables = page.find_tables()
            table_boxes = [t.bbox for t in tables]
            
            for i, table in enumerate(tables, start=1):
                try:
                    df = pd.DataFrame(table.extract())
                    csv_path = os.path.join(csv_folder, f"pagina_{page_num}_tabla_{i}.csv")
                    df.to_csv(csv_path, index=False, encoding="utf-8")
                except Exception as e:
                    print(f"Error procesando tabla {i} en página {page_num}: {e}")

            # Extraer palabras
            words = page.extract_words(
                x_tolerance=3, 
                y_tolerance=3, 
                keep_blank_chars=False,
                extra_attrs=["fontname", "size"]
            )
            
            # Calcular tamaño promedio
            all_sizes = [w.get("size", 0) for w in words if w.get("size")]
            avg_font_size = sum(all_sizes) / len(all_sizes) if all_sizes else 10

            # Agrupar por líneas
            lines = {}
            for w in words:
                top = round(w["top"], 1)
                if top <= 40:
                    continue
                lines.setdefault(top, []).append(w)

            # Procesar cada línea
            for top in sorted(lines.keys()):
                line_words = sorted(lines[top], key=lambda w: w["x0"])
                original_text = " ".join(w["text"] for w in line_words).strip()
                
                if not original_text:
                    continue

                # Normalizar para comparación
                normalized_text = normalize_text(original_text).upper().strip()

                # ============================
                #   DETECCIÓN DE ARTÍCULOS (regex permisivo + fallback)
                # ============================
                is_article = False
                article_name = None

                # Regex muy permisivo:
                # - acepta "ARTICULO" o "ARTÍCULO" (mayúsculas/minúsculas)
                # - admite espacios, puntos, dos puntos, guiones entre la palabra y el número
                # - acepta número con o sin punto, con o sin espacio antes del punto
                # - captura el número en el primer grupo
                article_pattern = r'\bART[IÍ]CULO[\s\.\:\-–—]*([0-9]{1,2})\s*(?:[\.\)\:])?'

                # Primera búsqueda sobre el texto ORIGINAL tal cual
                article_match = re.search(article_pattern, original_text, re.IGNORECASE)

                # Si no se encontró, hacemos un "colapso" que elimina espacios indeseados entre número y punto
                # (ej: "20 ." -> "20.")
                if not article_match:
                    # Normalizamos espacios múltiples y luego colapsamos "digit [espacio] ." -> "digit."
                    tmp = re.sub(r'\s+', ' ', original_text)
                    tmp = re.sub(r'(\d)\s+\.', r'\1.', tmp)
                    article_match = re.search(article_pattern, tmp, re.IGNORECASE)



                # -------- BLOQUE CORREGIDO Y ROBUSTO --------
                if article_match:
                    # 1) número detectado por el regex (solo dígitos)
                    article_num = article_match.group(1).strip()

                    # 2) normalizar tokens de la línea
                    lines_tokens_norm = [normalize_text(w["text"]).lower().strip() for w in line_words]

                    # 3) buscar índice del token "articulo"
                    indexes = [i for i, t in enumerate(lines_tokens_norm) if t == "articulo"]
                    if not indexes:
                        # no hay token "articulo" en la línea (posible tokenización extraña)
                        continue
                    start = indexes[0]

                    # 4) asegurar que exista al menos tok_art y tok_num (tok_num puede contener "32." o "32")
                    if start + 1 >= len(line_words):
                        continue

                    tok_art = line_words[start]
                    tok_num = line_words[start + 1]

                    # 5) extraer dígitos del token num (maneja "32" y "32." y "32 )" etc.)
                    num_match = re.search(r'(\d+)', tok_num["text"])
                    if not num_match or num_match.group(1) != article_num:
                        # Si no coincide, intentar ver si el número está en el token anterior/siguiente (fallback)
                        # (pero en general si falla aquí, no es el encabezado esperado)
                        continue

                    # 6) Verificar NEGRITAS: exigir que TODOS los tokens del encabezado estén en bold
                    #    (aquí solo tomamos tok_art y tok_num, porque tok_num trae el punto pegado)
                    header_tokens = [tok_art, tok_num]
                    all_bold = all(is_bold_word(w, page, avg_font_size) for w in header_tokens)

                    if not all_bold:
                        # Debug detallado para ver por qué falla la negrita
                        print("Falla bold en encabezado (se requiere TODOS en negritas):")
                        for w in header_tokens:
                            try:
                                bold_flag = is_bold_word(w, page, avg_font_size)
                            except Exception:
                                bold_flag = False
                            print(f"    '{w['text']}' -> bold? {bold_flag}   (x0={w.get('x0')}, font={w.get('fontname')}, size={w.get('size')})")
                        continue

                    # 7) Validar INDENTACIÓN (ARTICLE_INDENT debe calcularse una vez ANTES del bucle)
                    #    Asegúrate de que ARTICLE_INDENT es float y no None
                    try:
                        indent_reference = float(ARTICLE_INDENT) if ARTICLE_INDENT is not None else None
                    except Exception:
                        indent_reference = None

                    if indent_reference:
                        tolerance = 1.5  # píxeles, ajustar si es necesario
                        if abs(tok_art["x0"] - indent_reference) > tolerance:
                            print("Falla indentación:", tok_art["x0"], "vs", indent_reference)
                            continue

                    # -------- SI TODO OK --------
                    is_article = True
                    article_name = f"Artículo {article_num}."
                    print("Artículo detectado (bold + indentación OK):", article_name)
                # -------- FIN BLOQUE --------


                # -------------------------------
                # DETECCIÓN DE SUBTEMAS EN ROMANO
                # -------------------------------
                is_roman = False
                roman_name = None

                # Buscar patrón romano en toda la línea
                # (search, NO match)
                roman_pattern = r'\b[IVXLCDM]+\s*\.'
                roman_match = re.search(roman_pattern, original_text)

                if roman_match:

                    # Buscamos token romano: puede venir como "I.", "II." o separado "II" + "."
                    tok_roman = None

                    for i, w in enumerate(line_words):
                        tok_norm = normalize_text(w["text"]).upper().strip()

                        # Caso 1: token completo "II."
                        if re.fullmatch(r'[IVXLCDM]+\.', tok_norm):
                            tok_roman = w
                            break

                        # Caso 2: separado "II" y siguiente token "."
                        if re.fullmatch(r'[IVXLCDM]+', tok_norm):
                            if i + 1 < len(line_words):
                                next_tok = normalize_text(line_words[i+1]["text"]).strip()
                                if next_tok == ".":
                                    tok_roman = line_words[i]
                                    break

                    if not tok_roman:
                        # No se detectó token romano real, solo coincidió el regex de línea
                        pass
                    else:
                        # Verificar NEGRITAS
                        if not is_bold_word(tok_roman, page, avg_font_size):
                            print("Romano rechazado (no está en bold):", tok_roman["text"])
                        else:
                            # Validar indentación
                            if ROMAN_INDENT:
                                x = tok_roman["x0"]
                                if not (ROMAN_INDENT["min"] <= x <= ROMAN_INDENT["max"]):
                                    print("Romano rechazado por indentación:", x)
                                else:
                                    # TODO OK
                                    is_roman = True
                                    roman_name = normalize_text(tok_roman["text"])
                                    print("Romano DETECTADO:", roman_name)


                #------------------------------------------
                #detectar secciones-------
                #------------------------------------------

                is_section = False
                detected_section = None
                
                for section_key, section_value in SECCIONES.items():
                    section_key_norm = normalize_text(section_key).upper()
                    
                    # Coincidencia exacta o parcial
                    if (section_key_norm in normalized_text or 
                        normalized_text in section_key_norm):
                        
                        bold_count = sum(1 for w in line_words if is_bold_word(w, page, avg_font_size))
                        total_words = len(line_words)
                        
                        if total_words > 0 and bold_count / total_words >= 0.7:
                            is_section = True
                            detected_section = section_value
                            break

                # Procesar secciones
                if is_section and detected_section:
                    print(f"Sección detectada: {detected_section}")
                    
                    if current_article and article_content:
                        section_content.append(f"<article name='{current_article}'>")
                        section_content.extend(article_content)
                        section_content.append("</article>")
                        article_content = []
                    
                    if current_section and section_content:
                        full_text_parts.append(f"<section name='{current_section}'>")
                        full_text_parts.extend(section_content)
                        full_text_parts.append("</section>\n")
                    
                    current_section = detected_section
                    section_content = [original_text]
                    current_article = None

                # Procesar artículos
                elif is_article and article_name:

                    # Si hay un romano abierto → cerrarlo ANTES de cerrar el artículo
                    if current_roman and roman_content:
                        article_content.append(f"<roman name='{current_roman}'>")
                        article_content.extend(roman_content)
                        article_content.append("</roman>")
                        current_roman = None
                        roman_content = []

                    # Si hay un artículo abierto → guardarlo en la sección
                    if current_article and article_content:
                        section_content.append(f"<article name='{current_article}'>")
                        section_content.extend(article_content)
                        section_content.append("</article>")

                    # Iniciar nuevo artículo
                    current_article = article_name
                    article_content = [original_text]


                #processado de romanos
                elif is_roman and roman_name:

                    # Si ya había un romano → cerrarlo en el artículo
                    if current_roman and roman_content:
                        article_content.append(f"<roman name='{current_roman}'>")
                        article_content.extend(roman_content)
                        article_content.append("</roman>")

                    # Iniciar nuevo subtema romano
                    current_roman = roman_name
                    roman_content = [original_text]




                # Texto normal
                else:
                    clean_words = []
                    for w in line_words:
                        in_table = any(
                            w["x0"] >= box[0] and w["x1"] <= box[2] and 
                            w["top"] >= box[1] and w["bottom"] <= box[3]
                            for box in table_boxes
                        )
                        if not in_table:
                            clean_words.append(w["text"])
                    
                    clean_text = " ".join(clean_words).strip()

                    if clean_text:
                        if current_roman:
                            roman_content.append(clean_text)
                        elif current_article:
                            article_content.append(clean_text)
                        elif current_section:
                            section_content.append(clean_text)


            # Separador de páginas
            if current_article:
                article_content.append("")
            elif current_section:
                section_content.append("")


        #ultimo romano
        if current_roman and roman_content:
            section_content.append(f"<roman name='{current_roman}'>")
            section_content.extend(roman_content)
            section_content.append("</roman>")

        # ultimo articulo
        if current_article and article_content:
            section_content.append(f"<article name='{current_article}'>")
            section_content.extend(article_content)
            section_content.append("</article>")

        # ultima seccion
        if current_section and section_content:
            full_text_parts.append(f"<section name='{current_section}'>")
            full_text_parts.extend(section_content)
            full_text_parts.append("</section>")



    #conversion a xml
    from xml.sax.saxutils import escape

    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append("<document>")

    for part in full_text_parts:
        if part.startswith("<section name="):
            name = part.split("=", 1)[1].strip("'>")
            xml_parts.append(f'  <section name="{escape(name)}">')
        elif part.startswith("</section"):
            xml_parts.append("  </section>")
        elif part.startswith("<article name="):
            name = part.split("=", 1)[1].strip("'>")
            xml_parts.append(f'    <article name="{escape(name)}">')
        elif part.startswith("</article"):
            xml_parts.append("    </article>")
        elif part.startswith("<roman name="):
            name = part.split("=", 1)[1].strip("'>")
            xml_parts.append(f'    <roman name="{escape(name)}">')
        elif part.startswith("</roman"):
            xml_parts.append("    </roman>")

        else:
            clean = escape(part)
            xml_parts.append(f"      <p>{clean}</p>")

    xml_parts.append("</document>")

    final_xml = "\n".join(xml_parts)

    if output_path:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Forzar extensión .xml
        if not output_path.lower().endswith(".xml"):
            output_path = output_path + "amealco.xml"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_xml)
        print(f"XML guardado correctamente en: {output_path}")

    print(f"Tablas guardadas en: {csv_folder}")
    return final_xml



# Función debug
def debug_sections(pdf_path: str, page_limit=3):
    """Debug para ver qué secciones y artículos detecta"""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages[:page_limit], start=1):
            print(f"\n=== PÁGINA {page_num} ===")
            
            words = page.extract_words(extra_attrs=["fontname", "size"])
            all_sizes = [w.get("size", 0) for w in words if w.get("size")]
            avg_size = sum(all_sizes) / len(all_sizes) if all_sizes else 0
            
            lines = {}
            for w in words:
                top = round(w["top"], 1)
                if top <= 40:
                    continue
                lines.setdefault(top, []).append(w)
            
            for top in sorted(lines.keys()):
                line_words = sorted(lines[top], key=lambda w: w["x0"])
                original_text = " ".join(w["text"] for w in line_words).strip()
                normalized_text = normalize_text(original_text).upper().strip()
                
                bold_count = sum(1 for w in line_words if is_bold_word(w, page, avg_size))
                total_words = len(line_words)
                is_bold = bold_count / total_words >= 0.7 if total_words > 0 else False
                
                # Detectar sección
                for section_key in SECCIONES.keys():
                    section_norm = normalize_text(section_key).upper()
                    if section_norm in normalized_text:
                        print(f"POSIBLE SECCIÓN: '{original_text}'")
                        print(f"  Normalizado: '{normalized_text}'")
                        print(f"  Coincide con: '{section_key}'")
                        print(f"  Está en negritas: {is_bold} ({bold_count}/{total_words})")
                        print("---")
                
                # Detectar artículo
                article_pattern = r'ART[IÍ]CULO\s+(\d+\.)'
                article_match = re.search(article_pattern, original_text, re.IGNORECASE)
                if article_match:
                    print(f"POSIBLE ARTÍCULO: '{original_text}'")
                    print(f"  Número: {article_match.group(1)}")
                    print(f"  Está en negritas: {is_bold} ({bold_count}/{total_words})")
                    print("---")


if __name__ == "__main__":

    pdf_path = "test_archives/Ley_amealco.pdf"
    extract_pdf_and_tables(pdf_path=pdf_path, output_path="../../standar-transformers/XMLs/amealco_XMLs/")
