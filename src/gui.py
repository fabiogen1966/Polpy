"""Interfaccia grafica Tkinter per Polpy."""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from threading import Thread

# Supporta sia l'esecuzione come modulo (python -m src) sia diretta (python src/gui.py)
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.config_loader import load_config, AppConfig, FontConfig, PageConfig
    from src.pdf_generator import generate_pdf
else:
    from .config_loader import load_config, AppConfig, FontConfig, PageConfig
    from .pdf_generator import generate_pdf


class PolpyApp:
    """Applicazione principale con interfaccia Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Polpy - PCL/PRN → PDF Converter")
        self.root.geometry("700x620")
        self.root.resizable(True, True)

        # Carica configurazione come valori di default
        self.config = load_config()

        # Variabili Tk
        self._init_variables()

        # Costruisci l'interfaccia
        self._build_ui()

    def _init_variables(self):
        """Inizializza le variabili Tk dai valori di configurazione."""
        self.var_input_folder = tk.StringVar(value=self.config.input_folder)
        self.var_output_folder = tk.StringVar(value=self.config.output_folder)
        self.var_output_filename = tk.StringVar(value=self.config.output_filename)
        self.var_file_pattern = tk.StringVar(value=self.config.file_pattern)

        # Pagina
        self.var_orientation = tk.StringVar(value=self.config.page.orientation)
        self.var_page_size = tk.StringVar(value=self.config.page.size)
        self.var_left_margin = tk.StringVar(value=str(self.config.page.left_margin_mm))
        self.var_top_margin = tk.StringVar(value=str(self.config.page.top_margin_mm))
        self.var_bottom_margin = tk.StringVar(value=str(self.config.page.bottom_margin_mm))

        # Font
        self.var_normal_font_name = tk.StringVar(value=self.config.normal_font.name)
        self.var_normal_font_size = tk.StringVar(value=str(self.config.normal_font.size))
        self.var_title_font_name = tk.StringVar(value=self.config.title_font.name)
        self.var_title_font_size = tk.StringVar(value=str(self.config.title_font.size))
        self.var_line_height = tk.StringVar(value=str(self.config.line_height))

    def _build_ui(self):
        """Costruisce tutti i widget dell'interfaccia."""
        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: File e Cartelle
        tab_files = ttk.Frame(notebook, padding=10)
        notebook.add(tab_files, text="File e Cartelle")
        self._build_files_tab(tab_files)

        # Tab 2: Pagina
        tab_page = ttk.Frame(notebook, padding=10)
        notebook.add(tab_page, text="Pagina")
        self._build_page_tab(tab_page)

        # Tab 3: Font
        tab_fonts = ttk.Frame(notebook, padding=10)
        notebook.add(tab_fonts, text="Font")
        self._build_fonts_tab(tab_fonts)

        # Tab 4: Pattern
        tab_patterns = ttk.Frame(notebook, padding=10)
        notebook.add(tab_patterns, text="Pattern")
        self._build_patterns_tab(tab_patterns)

        # Barra inferiore con pulsanti e progress
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill=tk.X)

        self.progress = ttk.Progressbar(bottom_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar(value="Pronto.")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, foreground="gray")
        status_label.pack(side=tk.LEFT)

        btn_convert = ttk.Button(
            bottom_frame, text="Converti in PDF", command=self._on_convert
        )
        btn_convert.pack(side=tk.RIGHT)

    def _build_files_tab(self, parent: ttk.Frame):
        """Tab per la configurazione di file e cartelle."""
        # Input folder
        ttk.Label(parent, text="Cartella di input:").grid(row=0, column=0, sticky=tk.W, pady=4)
        entry_input = ttk.Entry(parent, textvariable=self.var_input_folder, width=50)
        entry_input.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=4)
        ttk.Button(parent, text="Sfoglia...", command=self._browse_input).grid(
            row=0, column=2, pady=4
        )

        # Output folder
        ttk.Label(parent, text="Cartella di output:").grid(row=1, column=0, sticky=tk.W, pady=4)
        entry_output = ttk.Entry(parent, textvariable=self.var_output_folder, width=50)
        entry_output.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=4)
        ttk.Button(parent, text="Sfoglia...", command=self._browse_output).grid(
            row=1, column=2, pady=4
        )

        # Output filename
        ttk.Label(parent, text="Nome file PDF:").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_output_filename, width=50).grid(
            row=2, column=1, sticky=tk.EW, padx=5, pady=4
        )

        # File pattern
        ttk.Label(parent, text="Pattern file (glob):").grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_file_pattern, width=50).grid(
            row=3, column=1, sticky=tk.EW, padx=5, pady=4
        )

        # Info
        info_frame = ttk.LabelFrame(parent, text="Anteprima file", padding=10)
        info_frame.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW, pady=10)

        self.file_listbox = tk.Listbox(info_frame, height=8)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(parent, text="Aggiorna lista file", command=self._refresh_file_list).grid(
            row=5, column=1, sticky=tk.E, pady=4
        )

        parent.columnconfigure(1, weight=1)

    def _build_page_tab(self, parent: ttk.Frame):
        """Tab per la configurazione della pagina."""
        # Orientamento
        ttk.Label(parent, text="Orientamento:").grid(row=0, column=0, sticky=tk.W, pady=4)
        orientation_frame = ttk.Frame(parent)
        orientation_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)
        ttk.Radiobutton(
            orientation_frame, text="Landscape", variable=self.var_orientation, value="landscape"
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            orientation_frame, text="Portrait", variable=self.var_orientation, value="portrait"
        ).pack(side=tk.LEFT)

        # Formato pagina
        ttk.Label(parent, text="Formato pagina:").grid(row=1, column=0, sticky=tk.W, pady=4)
        size_combo = ttk.Combobox(
            parent,
            textvariable=self.var_page_size,
            values=["A4", "Letter", "Legal"],
            state="readonly",
            width=15,
        )
        size_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        # Margini
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=2, sticky=tk.EW, pady=10
        )
        ttk.Label(parent, text="Margini (mm)", font=("", 9, "bold")).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=4
        )

        ttk.Label(parent, text="Sinistro:").grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_left_margin, width=10).grid(
            row=4, column=1, sticky=tk.W, padx=5, pady=4
        )

        ttk.Label(parent, text="Superiore:").grid(row=5, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_top_margin, width=10).grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=4
        )

        ttk.Label(parent, text="Inferiore:").grid(row=6, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_bottom_margin, width=10).grid(
            row=6, column=1, sticky=tk.W, padx=5, pady=4
        )

    def _build_fonts_tab(self, parent: ttk.Frame):
        """Tab per la configurazione dei font."""
        available_fonts = ["Courier", "Courier-Bold", "Helvetica", "Helvetica-Bold", "Times-Roman"]

        # Font normale
        ttk.Label(parent, text="Font normale", font=("", 9, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4)
        )

        ttk.Label(parent, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            parent,
            textvariable=self.var_normal_font_name,
            values=available_fonts,
            width=20,
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(parent, text="Dimensione:").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_normal_font_size, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=4
        )

        # Separatore
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        # Font titolo
        ttk.Label(parent, text="Font titoli", font=("", 9, "bold")).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4)
        )

        ttk.Label(parent, text="Nome:").grid(row=5, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            parent,
            textvariable=self.var_title_font_name,
            values=available_fonts,
            width=20,
        ).grid(row=5, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(parent, text="Dimensione:").grid(row=6, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_title_font_size, width=10).grid(
            row=6, column=1, sticky=tk.W, padx=5, pady=4
        )

        # Separatore
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=7, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        # Altezza riga
        ttk.Label(parent, text="Altezza riga (pt):").grid(row=8, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_line_height, width=10).grid(
            row=8, column=1, sticky=tk.W, padx=5, pady=4
        )

    def _build_patterns_tab(self, parent: ttk.Frame):
        """Tab per la configurazione dei pattern regex."""
        ttk.Label(parent, text="Sequenze PCL da rimuovere (una per riga):").grid(
            row=0, column=0, sticky=tk.W, pady=4
        )

        self.pcl_text = tk.Text(parent, height=5, width=60, font=("Courier", 9))
        self.pcl_text.grid(row=1, column=0, sticky=tk.NSEW, pady=4)
        pcl_content = "\n".join(self.config.pcl_cleanup_patterns)
        self.pcl_text.insert("1.0", pcl_content)

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=2, column=0, sticky=tk.EW, pady=10
        )

        ttk.Label(parent, text="Intestazioni speciali (regex, una per riga):").grid(
            row=3, column=0, sticky=tk.W, pady=4
        )

        self.headers_text = tk.Text(parent, height=5, width=60, font=("Courier", 9))
        self.headers_text.grid(row=4, column=0, sticky=tk.NSEW, pady=4)
        headers_content = "\n".join(self.config.special_headers)
        self.headers_text.insert("1.0", headers_content)

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=5, column=0, sticky=tk.EW, pady=10
        )

        ttk.Label(parent, text="Pattern cambio pagina (regex):").grid(
            row=6, column=0, sticky=tk.W, pady=4
        )
        self.var_page_break = tk.StringVar(value=self.config.page_break_pattern)
        ttk.Entry(parent, textvariable=self.var_page_break, width=60).grid(
            row=7, column=0, sticky=tk.EW, pady=4
        )

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(4, weight=1)

    # =========================================================================
    # Azioni
    # =========================================================================

    def _browse_input(self):
        """Apre il dialogo per selezionare la cartella di input."""
        folder = filedialog.askdirectory(title="Seleziona cartella di input")
        if folder:
            self.var_input_folder.set(folder)

    def _browse_output(self):
        """Apre il dialogo per selezionare la cartella di output."""
        folder = filedialog.askdirectory(title="Seleziona cartella di output")
        if folder:
            self.var_output_folder.set(folder)

    def _refresh_file_list(self):
        """Aggiorna la lista dei file trovati nella cartella di input."""
        self.file_listbox.delete(0, tk.END)
        input_path = Path(self.var_input_folder.get())
        pattern = self.var_file_pattern.get()

        if not input_path.exists():
            self.file_listbox.insert(tk.END, f"(cartella '{input_path}' non trovata)")
            return

        files = sorted(input_path.glob(pattern))
        if not files:
            self.file_listbox.insert(tk.END, f"(nessun file '{pattern}' trovato)")
            return

        for f in files:
            self.file_listbox.insert(tk.END, f.name)

    def _build_config_from_ui(self) -> AppConfig:
        """Costruisce un AppConfig dai valori correnti dell'interfaccia."""
        page = PageConfig(
            orientation=self.var_orientation.get(),
            size=self.var_page_size.get(),
            left_margin_mm=float(self.var_left_margin.get()),
            top_margin_mm=float(self.var_top_margin.get()),
            bottom_margin_mm=float(self.var_bottom_margin.get()),
        )

        normal_font = FontConfig(
            name=self.var_normal_font_name.get(),
            size=float(self.var_normal_font_size.get()),
        )

        title_font = FontConfig(
            name=self.var_title_font_name.get(),
            size=float(self.var_title_font_size.get()),
        )

        pcl_patterns = [
            line.strip()
            for line in self.pcl_text.get("1.0", tk.END).splitlines()
            if line.strip()
        ]

        special_headers = [
            line.strip()
            for line in self.headers_text.get("1.0", tk.END).splitlines()
            if line.strip()
        ]

        return AppConfig(
            input_folder=self.var_input_folder.get(),
            output_folder=self.var_output_folder.get(),
            output_filename=self.var_output_filename.get(),
            page=page,
            normal_font=normal_font,
            title_font=title_font,
            line_height=float(self.var_line_height.get()),
            file_pattern=self.var_file_pattern.get(),
            pcl_cleanup_patterns=pcl_patterns,
            page_break_pattern=self.var_page_break.get(),
            test_pattern=self.config.test_pattern,
            consumption_pattern=self.config.consumption_pattern,
            special_headers=special_headers,
        )

    def _on_convert(self):
        """Avvia la conversione in un thread separato."""
        try:
            config = self._build_config_from_ui()
        except ValueError as e:
            messagebox.showerror("Errore di configurazione", str(e))
            return

        input_path = Path(config.input_folder)
        if not input_path.exists():
            messagebox.showerror("Errore", f"La cartella di input '{input_path}' non esiste.")
            return

        files = sorted(input_path.glob(config.file_pattern))
        if not files:
            messagebox.showwarning(
                "Nessun file",
                f"Nessun file '{config.file_pattern}' trovato in '{input_path}'.",
            )
            return

        self.status_var.set(f"Conversione di {len(files)} file in corso...")
        self.progress.start(10)

        def _worker():
            try:
                output_path = generate_pdf(files, config)
                self.root.after(0, self._on_convert_done, str(output_path))
            except Exception as e:
                self.root.after(0, self._on_convert_error, str(e))

        Thread(target=_worker, daemon=True).start()

    def _on_convert_done(self, output_path: str):
        """Callback al termine della conversione."""
        self.progress.stop()
        self.status_var.set(f"PDF creato: {output_path}")
        messagebox.showinfo("Conversione completata", f"PDF generato:\n{output_path}")

    def _on_convert_error(self, error_msg: str):
        """Callback in caso di errore durante la conversione."""
        self.progress.stop()
        self.status_var.set("Errore durante la conversione.")
        messagebox.showerror("Errore", f"Errore durante la conversione:\n{error_msg}")


def main():
    """Entry point per l'interfaccia grafica."""
    root = tk.Tk()
    PolpyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
