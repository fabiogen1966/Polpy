"""Interfaccia a riga di comando per Polpy."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .config_loader import load_config
from .pdf_generator import generate_pdf


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parsing degli argomenti da riga di comando."""
    parser = argparse.ArgumentParser(
        prog="polpy",
        description="Converte file PCL/PRN in un unico documento PDF.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Percorso al file di configurazione (default: config.yaml)",
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=None,
        help="Cartella di input (sovrascrive il valore nel config)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Nome del file PDF di output (sovrascrive il valore nel config)",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        default=None,
        help="Cartella di output (sovrascrive il valore nel config)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point principale dell'applicazione.

    Args:
        argv: Argomenti da riga di comando (None = sys.argv).

    Returns:
        Codice di uscita (0 = successo).
    """
    args = parse_args(argv)

    # Carica configurazione
    config = load_config(args.config)

    # Override da CLI
    if args.input:
        config.input_folder = str(args.input)
    if args.output:
        config.output_filename = args.output
    if args.output_folder:
        config.output_folder = str(args.output_folder)

    # Trova i file di input
    input_path = Path(config.input_folder)
    if not input_path.exists():
        print(f"Errore: la cartella di input '{input_path}' non esiste.", file=sys.stderr)
        return 1

    files = sorted(input_path.glob(config.file_pattern))
    if not files:
        print(f"Nessun file '{config.file_pattern}' trovato in '{input_path}'.", file=sys.stderr)
        return 1

    print(f"Trovati {len(files)} file da elaborare...")

    # Genera il PDF
    output_path = generate_pdf(files, config)
    print(f"PDF creato: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
