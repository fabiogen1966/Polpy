from pathlib import Path
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm

# =====================================================
# CONFIGURAZIONE
# =====================================================
INPUT_FOLDER = "."
OUTPUT_PDF = "output_finale.pdf"

# =====================================================
# PULIZIA PCL
# =====================================================
def clean_pcl(text):
    patterns = [
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
    ]
    for p in patterns:
        text = re.sub(p, '', text)
    return text.replace('\r\n', '\n').replace('\r', '\n')

# =====================================================
# LETTURA FILES
# =====================================================
base = Path(INPUT_FOLDER)
files = sorted(base.glob("*.prn"))

# =====================================================
# CREAZIONE PDF
# =====================================================
PAGE_W, PAGE_H = landscape(A4)
c = canvas.Canvas(OUTPUT_PDF, pagesize=landscape(A4))

normal_font = ("Courier", 10.5)
title_font = ("Courier-Bold", 13)
line_height = 11.5
left_margin = 10 * mm
top_margin = PAGE_H - 20 * mm
bottom_limit = 10 * mm

# =====================================================
# REGEX
# =====================================================
page_pattern = re.compile(r'(pag\.?|pagina|page)\s*\d+', re.IGNORECASE)

# TEST 01-18
test_pattern = re.compile(
    r'^\s*(0[1-9]|1[0-8])\s*-\s*ATP\s+Par\.\s*([0-9.]+)\s+(.+?)\s*$',
    re.IGNORECASE
)

# Consumption
consumption_pattern = re.compile(
    r'^\s*01\s*-\s*Consumption\s*$',
    re.IGNORECASE
)

# Intestazioni speciali
special_headers = [
    re.compile(r'DOCUMENT-CODE-1\s+Issue\s+\w+\s+\w+\s+\d{4}', re.IGNORECASE),
    re.compile(r'DOCUMENT-CODE-2\s+EQUIPMENT\s+P/N\s+[\d-/]+', re.IGNORECASE),
]

# =====================================================
# CREAZIONE PAGINA
# =====================================================
def new_page():
    return top_margin

# =====================================================
# ELABORAZIONE FILES
# =====================================================
first = True

for file in files:
    raw = file.read_text(errors="ignore")
    text = clean_pcl(raw)
    lines = text.split("\n")

    if not any(l.strip() for l in lines):
        continue

    if not first:
        c.showPage()
    first = False

    y = new_page()

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # =============================================
        # TITOLI SPECIALI
        # =============================================
        if any(p.search(stripped) for p in special_headers):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)

        # =============================================
        # CONSUMPTION
        # =============================================
        elif consumption_pattern.match(stripped):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)

        # =============================================
        # TEST 01-18
        # =============================================
        else:
            tm = test_pattern.match(stripped)
            if tm:
                test_no, par, desc = tm.groups()
                formatted = f"{test_no} - ATP Par. {par} {desc}"
                c.setFont(*title_font)
                c.drawCentredString(PAGE_W / 2, y, formatted)
                y -= (line_height + 2)

            # =========================================
            # TESTO NORMALE
            # =========================================
            else:
                c.setFont(*normal_font)
                c.drawString(left_margin, y, line.rstrip())
                y -= line_height

        # =============================================
        # CAMBIO PAGINA LOGICO
        # =============================================
        if page_pattern.search(stripped):
            remaining = any(l.strip() for l in lines[idx + 1:])
            if remaining:
                c.showPage()
                y = new_page()
                continue

        # =============================================
        # OVERFLOW FISICO
        # =============================================
        if y < bottom_limit:
            remaining = any(l.strip() for l in lines[idx + 1:])
            if remaining:
                c.showPage()
                y = new_page()

# =====================================================
# SALVATAGGIO PDF
# =====================================================
c.save()
print(f"PDF creato: {OUTPUT_PDF}")
