import pdfplumber

def group_words_into_lines(words, tolerance=2.5):
    lines = []

    for w in sorted(words, key=lambda w: w["top"]):
        placed = False
        for line in lines:
            if abs(line["top"] - w["top"]) <= tolerance:
                line["words"].append(w)
                placed = True
                break
        if not placed:
            lines.append({"top": w["top"], "words": [w]})

    return lines

def extract_pdf_text(pdf_path: str) -> str:
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

            words = [w for w in words if w["top"] > 0]  #In case of having headers in the pages, is necesary to calculate the main coordinate where they are located and stablish here the most accurable Y value to avoiding them. If not, leave it as a 0

            lines = group_words_into_lines(words, tolerance=2.5)

            for line in lines:
                line_words = sorted(line["words"], key=lambda w: w["x0"])
                line_text = " ".join(w["text"] for w in line_words).strip()
                if line_text:
                    full_text_lines.append(line_text)

            full_text_lines.append("")

    return "\n".join(full_text_lines)


def get_text(pdf_path: str) -> str:

    raw_text = extract_pdf_text(pdf_path)
    
    with open("texto_transparencia_raw.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    print("Extracción completada.")
    

    return raw_text
