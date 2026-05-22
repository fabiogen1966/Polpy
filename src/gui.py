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
    from src.profiles import ALL_PROFILES, DocumentProfile
else:
    from .config_loader import load_config, AppConfig, FontConfig, PageConfig
    from .pdf_generator import generate_pdf
    from .profiles import ALL_PROFILES, DocumentProfile


class PolpyApp:
    """Applicazione principale con interfaccia Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Polpy - PCL/PRN \u2192 PDF Converter")
        self.root.geometry("720x660")
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

        # Profilo
        self.var_profile = tk.StringVar(value="DMEP")

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

        # Tab 1: Conversione
        tab_convert = ttk.Frame(notebook, padding=10)
        notebook.add(tab_convert, text="Conversione")
        self._build_convert_tab(tab_convert)

        # Tab 2: Pagina
        tab_page = ttk.Frame(notebook, padding=10)
        notebook.add(tab_page, text="Pagina")
        self._build_page_tab(tab_page)

        # Tab 3: Font
        tab_fonts = ttk.Frame(notebook, padding=10)
        notebook.add(tab_fonts, text="Font")
        self._build_fonts_tab(tab_fonts)

        # Barra inferiore con progress e status
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill=tk.X)

        self.progress = ttk.Progressbar(bottom_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar(value="Pronto.")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, foreground="gray")
        status_label.pack(side=tk.LEFT)

    def _build_convert_tab(self, parent: ttk.Frame):
        """Tab principale per la conversione."""
        # Input folder
        ttk.Label(parent, text="Cartella di input:").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_input_folder, width=50).grid(
            row=0, column=1, sticky=tk.EW, padx=5, pady=4
        )
        ttk.Button(parent, text="Sfoglia...", command=self._browse_input).grid(
            row=0, column=2, pady=4
        )

        # Output folder
        ttk.Label(parent, text="Cartella di output:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_output_folder, width=50).grid(
            row=1, column=1, sticky=tk.EW, padx=5, pady=4
        )
        ttk.Button(parent, text="Sfoglia...", command=self._browse_output).grid(
            row=1, column=2, pady=4
        )

        # Separatore
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        # Selezione profilo
        ttk.Label(parent, text="Tipo documento:", font=("", 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=4
        )
        profile_frame = ttk.Frame(parent)
        profile_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Radiobutton(
            profile_frame, text="DMEP (ANV-213 DME-P)",
            variable=self.var_profile, value="DMEP"
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            profile_frame, text="MMR (ANV-243 MMR-RNAV)",
            variable=self.var_profile, value="MMR"
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            profile_frame, text="Tutti",
            variable=self.var_profile, value="ALL"
        ).pack(side=tk.LEFT)

        # Anteprima file
        info_frame = ttk.LabelFrame(parent, text="File trovati", padding=10)
        info_frame.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW, pady=10)

        self.file_listbox = tk.Listbox(info_frame, height=10)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pulsanti
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=5, column=0, columnspan=3, sticky=tk.EW, pady=8)

        ttk.Button(btn_frame, text="Aggiorna lista", command=self._refresh_file_list).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(
            btn_frame, text="Converti in PDF", command=self._on_convert
        ).pack(side=tk.RIGHT)

        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(4, weight=1)

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
        ttk.Combobox(
            parent,
            textvariable=self.var_page_size,
            values=["A4", "Letter", "Legal"],
            state="readonly",
            width=15,
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

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
            parent, textvariable=self.var_normal_font_name, values=available_fonts, width=20,
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(parent, text="Dimensione:").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_normal_font_size, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=4
        )

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        # Font titolo
        ttk.Label(parent, text="Font titoli", font=("", 9, "bold")).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4)
        )
        ttk.Label(parent, text="Nome:").grid(row=5, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            parent, textvariable=self.var_title_font_name, values=available_fonts, width=20,
        ).grid(row=5, column=1, sticky=tk.W, padx=5, pady=4)

        ttk.Label(parent, text="Dimensione:").grid(row=6, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_title_font_size, width=10).grid(
            row=6, column=1, sticky=tk.W, padx=5, pady=4
        )

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=7, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        # Altezza riga
        ttk.Label(parent, text="Altezza riga (pt):").grid(row=8, column=0, sticky=tk.W, pady=4)
        ttk.Entry(parent, textvariable=self.var_line_height, width=10).grid(
            row=8, column=1, sticky=tk.W, padx=5, pady=4
        )

    # =========================================================================
    # Azioni
    # =========================================================================

    def _browse_input(self):
        folder = filedialog.askdirectory(title="Seleziona cartella di input")
        if folder:
            self.var_input_folder.set(folder)

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Seleziona cartella di output")
        if folder:
            self.var_output_folder.set(folder)

    def _get_selected_profiles(self):
        """Restituisce la lista dei profili selezionati."""
        choice = self.var_profile.get()
        if choice == "ALL":
            return list(ALL_PROFILES.values())
        return [ALL_PROFILES[choice]]

    def _refresh_file_list(self):
        """Aggiorna la lista dei file trovati."""
        self.file_listbox.delete(0, tk.END)
        input_path = Path(self.var_input_folder.get())

        if not input_path.exists():
            self.file_listbox.insert(tk.END, f"(cartella '{input_path}' non trovata)")
            return

        profiles = self._get_selected_profiles()
        total = 0
        for profile in profiles:
            files = sorted(input_path.glob(profile.file_pattern))
            if files:
                self.file_listbox.insert(tk.END, f"--- {profile.name} ({len(files)} file) ---")
                for f in files:
                    self.file_listbox.insert(tk.END, f"  {f.name}")
                total += len(files)

        if total == 0:
            self.file_listbox.insert(tk.END, "(nessun file trovato per il profilo selezionato)")

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

        return AppConfig(
            input_folder=self.var_input_folder.get(),
            output_folder=self.var_output_folder.get(),
            output_filename="output.pdf",
            page=page,
            normal_font=normal_font,
            title_font=title_font,
            line_height=float(self.var_line_height.get()),
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

        profiles = self._get_selected_profiles()

        # Verifica che ci siano file per almeno un profilo
        has_files = False
        for profile in profiles:
            if list(input_path.glob(profile.file_pattern)):
                has_files = True
                break

        if not has_files:
            messagebox.showwarning(
                "Nessun file",
                "Nessun file trovato per il profilo selezionato.",
            )
            return

        self.status_var.set("Conversione in corso...")
        self.progress.start(10)

        def _worker():
            try:
                results = []
                for profile in profiles:
                    files = sorted(input_path.glob(profile.file_pattern))
                    if not files:
                        continue
                    output_path = generate_pdf(files, config, profile)
                    results.append(f"{profile.name}: {output_path}")

                result_msg = "\n".join(results)
                self.root.after(0, self._on_convert_done, result_msg)
            except Exception as e:
                self.root.after(0, self._on_convert_error, str(e))

        Thread(target=_worker, daemon=True).start()

    def _on_convert_done(self, result_msg: str):
        """Callback al termine della conversione."""
        self.progress.stop()
        self.status_var.set("Conversione completata.")
        messagebox.showinfo("Conversione completata", f"PDF generati:\n\n{result_msg}")

    def _on_convert_error(self, error_msg: str):
        """Callback in caso di errore."""
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
