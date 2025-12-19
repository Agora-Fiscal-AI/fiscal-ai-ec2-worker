import pdfplumber
import os


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extracts raw, ordered, line-preserved text from a PDF file.
    Tables are intentionally ignored at this stage.
    """

    full_text_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"Procesando página {page_num}...")

            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=False,
                extra_attrs=["fontname", "size"]
            )

      
            lines = {}
            for w in words:
                top = round(w["top"], 1)

                if top <= 40:
                    continue

                lines.setdefault(top, []).append(w)

            for top in sorted(lines.keys()):
                line_words = sorted(lines[top], key=lambda w: w["x0"])
                line_text = " ".join(w["text"] for w in line_words).strip()

                if line_text:
                    full_text_lines.append(line_text)

            full_text_lines.append("")

    return "\n".join(full_text_lines)


def get_text(pdf_path: str) -> str:

    raw_text = extract_pdf_text(pdf_path)
    
    with open("texto_amealco_raw.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    print("Extracción completada.")
    

    return raw_text
