"""Entry point per Polpy.

Lancia la GUI di default. Usa --cli per la modalità a riga di comando.
"""

import sys


def main():
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        from .cli import main as cli_main
        raise SystemExit(cli_main())
    else:
        from .gui import main as gui_main
        gui_main()


main()
