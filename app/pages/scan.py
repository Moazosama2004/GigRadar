import customtkinter as ctk
import threading
from app.engine.scraper_manager import ScraperManager
from app.engine.match_engine import MatchEngine


class ScanPage(ctk.CTkFrame):

    def __init__(self, parent, on_scan_complete=None):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.on_scan_complete = on_scan_complete   # callback to refresh dashboard

        self._build_header()
        self._build_controls()
        self._build_log()

    def _build_header(self):
        ctk.CTkLabel(
            self,
            text="Scan",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

    def _build_controls(self):
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Start a new scan to find gigs matching your resume profile.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 16))

        self.scan_btn = ctk.CTkButton(
            btn_row,
            text="Start scan",
            width=140,
            height=40,
            corner_radius=8,
            command=self._start_scan,
        )
        self.scan_btn.pack(side="left", padx=(0, 12))

        self.status_label = ctk.CTkLabel(
            btn_row,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.status_label.pack(side="left")

        # Progress bar
        self.progress = ctk.CTkProgressBar(card, height=6, corner_radius=3)
        self.progress.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.progress.set(0)

    def _build_log(self):
        ctk.CTkLabel(
            self,
            text="Scan log",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.log_box = ctk.CTkTextbox(
            self,
            corner_radius=10,
            font=ctk.CTkFont(family="Courier", size=12),
            state="disabled",
            height=300,
        )
        self.log_box.grid(row=3, column=0, sticky="nsew")
        self.grid_rowconfigure(3, weight=1)

    # ── Logging ────────────────────────────────────────────────────
    def _log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ── Scan ───────────────────────────────────────────────────────
    def _start_scan(self):
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.progress.set(0)
        self._clear_log()
        self._log("Starting GigRadar scan...")

        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        try:
            # ── Step 1: Scrape ─────────────────────────────────────
            self.after(0, lambda: self.progress.set(0.1))

            manager = ScraperManager()
            self.after(0, lambda: self._log(
                f"Keywords: {', '.join(manager.keywords[:5])}"
            ))

            gigs = manager.run(
                progress_callback=lambda msg: self.after(
                    0, lambda m=msg: self._log(m)
                )
            )

            self.after(0, lambda: self.progress.set(0.7))

            # ── Step 2: Score ──────────────────────────────────────
            self.after(0, lambda: self._log("Running match engine..."))

            engine = MatchEngine()
            scored = engine.score_all(
                progress_callback=lambda msg: self.after(
                    0, lambda m=msg: self._log(m)
                )
            )

            self.after(0, lambda: self.progress.set(1.0))

            # ── Step 3: Done ───────────────────────────────────────
            matched = sum(1 for g in scored if g.get("match_score", 0) >= 40)
            summary = f"Done. {len(scored)} gigs found, {matched} matched (score ≥ 40)."

            self.after(0, lambda: self._log(summary))
            self.after(0, lambda: self.status_label.configure(
                text=summary,
                text_color=("#1D9E75", "#5DCAA5"),
            ))

            # Notify dashboard to refresh
            if self.on_scan_complete:
                self.after(0, self.on_scan_complete)

        except Exception as e:
            self.after(0, lambda: self._log(f"ERROR: {e}"))
            self.after(0, lambda: self.status_label.configure(
                text=f"Scan failed: {e}",
                text_color=("#E24B4A", "#F09595"),
            ))
        finally:
            self.after(0, lambda: self.scan_btn.configure(
                state="normal",
                text="Start scan",
            ))
