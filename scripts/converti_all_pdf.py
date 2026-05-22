#!/usr/bin/env python
# coding: utf-8
"""
Script unificato di conversione PCL/PRN → PDF.
Supporta sia file DMEP (ANV-213 DME-P) che MMR (ANV-243 MMR-RNAV).
Rileva automaticamente il tipo di file e applica i pattern corretti.
"""

from pathlib import Path
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm

# =====================================================
# CONFIGURAZIONE
# =====================================================
WORK_DIR = Path(".")
OUTPUT_FOLDER = WORK_DIR

# =====================================================
# PULIZIA PCL
# =====================================================

def clean_pcl(text):
    """Rimuove tutte le sequenze di escape PCL note."""
    patterns = [
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
        r'\x1b&dD',   # Underline on
        r'\x1b&d@',   # Underline off
    ]
    for p in patterns:
        text = re.sub(p, '', text)
    return text.replace('\r\n', '\n').replace('\r', '\n')

# =====================================================
# PROFILI DOCUMENTO
# =====================================================

PROFILES = {
    "DMEP": {
        "file_pattern": "DMEP_Efa_*.prn",
        "output_filename": "DMEP_output.pdf",
        # Test DMEP: "NN - ATP Par. X.X descrizione" oppure "01 - Consumption"
        "test_pattern": re.compile(
            r'^\s*(0[1-9]|1[0-8])\s*-\s*(?:ATP\s+Par\.\s*)?([0-9.]+)\s+(.+?)\s*$',
            re.IGNORECASE
        ),
        "consumption_pattern": re.compile(
            r'^\s*01\s*-\s*Consumption\s*$',
            re.IGNORECASE
        ),
        "special_headers": [
            re.compile(r'SPE-J-344-A-0044', re.IGNORECASE),
            re.compile(r'ANV-213\s+DME-P\s+P/N', re.IGNORECASE),
        ],
    },
    "MMR": {
        "file_pattern": "MMR_Efa_*.prn",
        "output_filename": "MMR_output.pdf",
        # Test MMR: "NN - 10.X.X descrizione" (test da 01 a 30)
        "test_pattern": re.compile(
            r'^\s*(0[1-9]|[12]\d|30)\s*-\s*(\d+\.\d+(?:\.\d+)?)\s+(.+?)\s*$',
            re.IGNORECASE
        ),
        "consumption_pattern": re.compile(
            r'^\s*01\s*-\s*[\d.]+\s+Equipment\s+Power\s+Supply\s+Consumption\s*$',
            re.IGNORECASE
        ),
        "special_headers": [
            re.compile(r'SPE-J-343-A-0041', re.IGNORECASE),
            re.compile(r'ANV-243\s+MMR-RNAV\s+P/N', re.IGNORECASE),
        ],
    },
}

# Pattern cambio pagina comune: "- N -" a fine riga
PAGE_PATTERN = re.compile(r'-\s*\d+\s*-\s*$')

# =====================================================
# GENERAZIONE PDF
# =====================================================

def generate_pdf(files, profile, output_path):
    """Genera un PDF per un set di file con un profilo specifico."""

    PAGE_W, PAGE_H = landscape(A4)
    c = canvas.Canvas(str(output_path), pagesize=landscape(A4))

    normal_font = ("Courier", 10.5)
    title_font = ("Courier-Bold", 13)
    line_height = 11.5
    left_margin = 10 * mm
    top_margin = PAGE_H - 20 * mm
    bottom_limit = 10 * mm

    test_pattern = profile["test_pattern"]
    consumption_pattern = profile["consumption_pattern"]
    special_headers = profile["special_headers"]

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
        y = top_margin

        for idx, line in enumerate(lines):
            stripped = line.strip()

            # Intestazioni speciali (centrate, bold)
            if any(p.search(stripped) for p in special_headers):
                c.setFont(*title_font)
                c.drawCentredString(PAGE_W / 2, y, stripped)
                y -= (line_height + 2)

            # Consumption
            elif consumption_pattern.match(stripped):
                c.setFont(*title_font)
                c.drawCentredString(PAGE_W / 2, y, stripped)
                y -= (line_height + 2)

            # Test NN - Par. X.X descrizione
            else:
                tm = test_pattern.match(stripped)
                if tm:
                    test_no, par, desc = tm.groups()
                    formatted = f"{test_no} - {par} {desc}"
                    c.setFont(*title_font)
                    c.drawCentredString(PAGE_W / 2, y, formatted)
                    y -= (line_height + 2)
                else:
                    # Testo normale
                    c.setFont(*normal_font)
                    c.drawString(left_margin, y, line.rstrip())
                    y -= line_height

            # Cambio pagina logico (pattern "- N -")
            if PAGE_PATTERN.search(stripped):
                remaining = any(l.strip() for l in lines[idx + 1:])
                if remaining:
                    c.showPage()
                    y = top_margin
                continue

            # Overflow fisico
            if y < bottom_limit:
                remaining = any(l.strip() for l in lines[idx + 1:])
                if remaining:
                    c.showPage()
                    y = top_margin

    c.save()
    return output_path

# =====================================================
# MAIN
# =====================================================

def main():
    for name, profile in PROFILES.items():
        files = sorted(WORK_DIR.glob(profile["file_pattern"]))

        if not files:
            print(f"[{name}] Nessun file '{profile['file_pattern']}' trovato, skip.")
            continue

        output_path = OUTPUT_FOLDER / profile["output_filename"]
        print(f"[{name}] Trovati {len(files)} file, generazione PDF...")
        generate_pdf(files, profile, output_path)
        print(f"[{name}] PDF creato: {output_path}")

    print("\nConversione completata.")


if __name__ == "__main__":
    main()
