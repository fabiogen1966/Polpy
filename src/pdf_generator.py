"""Generazione del PDF a partire dai file PRN ripuliti."""

import re
from pathlib import Path
from typing import List, Tuple, Union

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, portrait, A4, letter, legal
from reportlab.lib.units import mm

from .config_loader import AppConfig
from .profiles import DocumentProfile


# Mapping delle dimensioni pagina supportate
PAGE_SIZES = {
    "A4": A4,
    "LETTER": letter,
    "LEGAL": legal,
}

# Mapping degli orientamenti
ORIENTATIONS = {
    "landscape": landscape,
    "portrait": portrait,
}


def _get_page_dimensions(config: AppConfig) -> Tuple[float, float]:
    """Calcola le dimensioni della pagina in base alla configurazione."""
    base_size = PAGE_SIZES.get(config.page.size.upper(), A4)
    orientation_fn = ORIENTATIONS.get(config.page.orientation.lower(), landscape)
    return orientation_fn(base_size)


def generate_pdf(files: List[Path], config: AppConfig,
                 profile: "DocumentProfile" = None) -> Path:
    """Genera un PDF a partire da una lista di file di testo.

    Args:
        files: Lista di Path ai file PRN.
        config: Configurazione dell'applicazione (pagina, font, margini).
        profile: Profilo documento (pattern specifici). Se None, usa i pattern dal config.

    Returns:
        Path del file PDF generato.
    """
    from .pcl_cleaner import clean_pcl

    page_w, page_h = _get_page_dimensions(config)
    pagesize = (page_w, page_h)

    # Calcola output path
    output_dir = Path(config.output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Se c'è un profilo, usa il suo output filename
    if profile:
        output_filename = profile.output_filename
    else:
        output_filename = config.output_filename

    output_path = output_dir / output_filename

    c = canvas.Canvas(str(output_path), pagesize=pagesize)

    # Margini
    left_margin = config.page.left_margin_mm * mm
    top_margin = page_h - config.page.top_margin_mm * mm
    bottom_limit = config.page.bottom_margin_mm * mm

    # Font
    normal_font = (config.normal_font.name, config.normal_font.size)
    title_font = (config.title_font.name, config.title_font.size)
    line_height = config.line_height

    # Compila i pattern regex dal profilo o dal config
    if profile:
        pcl_patterns = profile.pcl_cleanup_patterns
        page_pattern = re.compile(profile.page_break_pattern, re.IGNORECASE)
        test_pattern = re.compile(profile.test_pattern, re.IGNORECASE)
        consumption_pattern = re.compile(profile.consumption_pattern, re.IGNORECASE)
        special_headers = [re.compile(p, re.IGNORECASE) for p in profile.special_headers]
    else:
        pcl_patterns = config.pcl_cleanup_patterns
        page_pattern = re.compile(config.page_break_pattern, re.IGNORECASE)
        test_pattern = re.compile(config.test_pattern, re.IGNORECASE)
        consumption_pattern = re.compile(config.consumption_pattern, re.IGNORECASE)
        special_headers = [re.compile(p, re.IGNORECASE) for p in config.special_headers]

    first = True

    for file in files:
        raw = file.read_text(errors="ignore")
        text = clean_pcl(raw, pcl_patterns)
        lines = text.split("\n")

        # Salta file vuoti
        if not any(line.strip() for line in lines):
            continue

        if not first:
            c.showPage()
        first = False

        y = top_margin

        for idx, line in enumerate(lines):
            stripped = line.strip()

            # Intestazioni speciali
            if any(p.search(stripped) for p in special_headers):
                c.setFont(*title_font)
                c.drawCentredString(page_w / 2, y, stripped)
                y -= (line_height + 2)

            # Consumption
            elif consumption_pattern.match(stripped):
                c.setFont(*title_font)
                c.drawCentredString(page_w / 2, y, stripped)
                y -= (line_height + 2)

            # Test
            else:
                tm = test_pattern.match(stripped)
                if tm:
                    test_no, par, desc = tm.groups()
                    formatted = f"{test_no} - {par} {desc}"
                    c.setFont(*title_font)
                    c.drawCentredString(page_w / 2, y, formatted)
                    y -= (line_height + 2)
                else:
                    # Testo normale
                    c.setFont(*normal_font)
                    c.drawString(left_margin, y, line.rstrip())
                    y -= line_height

            # Cambio pagina logico
            if page_pattern.search(stripped):
                remaining = any(l.strip() for l in lines[idx + 1:])
                if remaining:
                    c.showPage()
                    y = top_margin
                continue

            # Overflow fisico della pagina
            if y < bottom_limit:
                remaining = any(l.strip() for l in lines[idx + 1:])
                if remaining:
                    c.showPage()
                    y = top_margin

    c.save()
    return output_path
