"""Entry point per la build PyInstaller."""

import sys
from pathlib import Path

# Assicura che il path del progetto sia nel sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.gui import main

main()
