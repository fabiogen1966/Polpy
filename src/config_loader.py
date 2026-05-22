"""Caricamento e validazione della configurazione."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Union

import yaml


@dataclass
class FontConfig:
    """Configurazione di un font."""

    name: str
    size: float


@dataclass
class PageConfig:
    """Configurazione della pagina PDF."""

    orientation: str = "landscape"
    size: str = "A4"
    left_margin_mm: float = 10
    top_margin_mm: float = 20
    bottom_margin_mm: float = 10


@dataclass
class AppConfig:
    """Configurazione completa dell'applicazione."""

    input_folder: str = "input"
    output_folder: str = "output"
    output_filename: str = "output_finale.pdf"
    page: PageConfig = field(default_factory=PageConfig)
    normal_font: FontConfig = field(default_factory=lambda: FontConfig("Courier", 10.5))
    title_font: FontConfig = field(default_factory=lambda: FontConfig("Courier-Bold", 13))
    line_height: float = 11.5
    file_pattern: str = "*.prn"
    pcl_cleanup_patterns: List[str] = field(default_factory=list)
    page_break_pattern: str = r'(pag\.?|pagina|page)\s*\d+'
    test_pattern: str = r'^\s*(0[1-9]|1[0-8])\s*-\s*ATP\s+Par\.\s*([0-9.]+)\s+(.+?)\s*$'
    consumption_pattern: str = r'^\s*01\s*-\s*Consumption\s*$'
    special_headers: List[str] = field(default_factory=list)


def load_config(config_path: Union[Path, str] = "config.yaml") -> AppConfig:
    """Carica la configurazione da file YAML.

    Args:
        config_path: Percorso al file di configurazione.

    Returns:
        AppConfig con tutti i parametri caricati.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        return AppConfig()

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    page_data = data.get("page", {})
    page_config = PageConfig(
        orientation=page_data.get("orientation", "landscape"),
        size=page_data.get("size", "A4"),
        left_margin_mm=page_data.get("left_margin_mm", 10),
        top_margin_mm=page_data.get("top_margin_mm", 20),
        bottom_margin_mm=page_data.get("bottom_margin_mm", 10),
    )

    fonts_data = data.get("fonts", {})
    normal_font_data = fonts_data.get("normal", {})
    title_font_data = fonts_data.get("title", {})

    normal_font = FontConfig(
        name=normal_font_data.get("name", "Courier"),
        size=normal_font_data.get("size", 10.5),
    )
    title_font = FontConfig(
        name=title_font_data.get("name", "Courier-Bold"),
        size=title_font_data.get("size", 13),
    )

    return AppConfig(
        input_folder=data.get("input_folder", "input"),
        output_folder=data.get("output_folder", "output"),
        output_filename=data.get("output_filename", "output_finale.pdf"),
        page=page_config,
        normal_font=normal_font,
        title_font=title_font,
        line_height=data.get("line_height", 11.5),
        file_pattern=data.get("file_pattern", "*.prn"),
        pcl_cleanup_patterns=data.get("pcl_cleanup_patterns", []),
        page_break_pattern=data.get("page_break_pattern", r'(pag\.?|pagina|page)\s*\d+'),
        test_pattern=data.get("test_pattern", r'^\s*(0[1-9]|1[0-8])\s*-\s*ATP\s+Par\.\s*([0-9.]+)\s+(.+?)\s*$'),
        consumption_pattern=data.get("consumption_pattern", r'^\s*01\s*-\s*Consumption\s*$'),
        special_headers=data.get("special_headers", []),
    )
