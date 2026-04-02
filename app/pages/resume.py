import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.engine.resume_parser import ResumeParser
import os
import threading


class ResumePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.uploaded_file = None

        self._build_header()
        self._build_upload_area()
        self._build_profile_card()

    # ── Header ─────────────────────────────────────────────────────
    def _build_header(self):
        ctk.CTkLabel(
            self,
            text="Resume",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

    # ── Upload box ─────────────────────────────────────────────────
    def _build_upload_area(self):
        self.upload_box = ctk.CTkFrame(
            self,
            corner_radius=12,
            border_width=2,
            border_color=("gray70", "gray35"),
            fg_color=("gray95", "gray17"),
            height=180,
        )
        self.upload_box.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self.upload_box.grid_columnconfigure(0, weight=1)
        self.upload_box.grid_propagate(False)

        ctk.CTkLabel(
            self.upload_box,
            text="Drop your resume here",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=(36, 4))

        ctk.CTkLabel(
            self.upload_box,
            text="Supports PDF and DOCX",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, pady=(0, 12))

        self.browse_btn = ctk.CTkButton(
            self.upload_box,
            text="Browse file",
            width=140,
            height=36,
            corner_radius=8,
            command=self._pick_file,
        )
        self.browse_btn.grid(row=2, column=0, pady=(0, 36))

    # ── Profile card (shown after parsing) ─────────────────────────
    def _build_profile_card(self):
        self.card = ctk.CTkFrame(self, corner_radius=10)
        self.card.grid(row=2, column=0, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.status_label = ctk.CTkLabel(
            self.card,
            text="No resume loaded yet.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.status_label.grid(row=0, column=0, pady=20, padx=16, sticky="w")

        # These widgets are hidden until a resume is parsed
        self.profile_widgets = []

    # ── File picker ────────────────────────────────────────────────
    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Select your resume",
            filetypes=[
                ("Supported files", "*.pdf *.docx"),
                ("PDF files",       "*.pdf"),
                ("Word documents",  "*.docx"),
            ],
        )
        if not path:
            return

        self.uploaded_file = path
        self._start_parsing(path)

    # ── Parse in background thread (keeps UI responsive) ───────────
    def _start_parsing(self, path: str):
        self.browse_btn.configure(text="Parsing...", state="disabled")
        self.status_label.configure(
            text="Reading resume...", text_color="gray")

        # Clear any previous profile widgets
        for w in self.profile_widgets:
            w.destroy()
        self.profile_widgets.clear()

        def run():
            try:
                parser = ResumeParser(path)
                profile = parser.parse()
                # Schedule UI update back on the main thread
                self.after(0, lambda: self._show_profile(profile))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    # ── Display extracted profile ──────────────────────────────────
    def _show_profile(self, profile: dict):
        self.browse_btn.configure(text="Browse file", state="normal")
        self.status_label.configure(
            text=f"Parsed: {os.path.basename(profile['file_path'])}",
            text_color=("#1D9E75", "#5DCAA5"),
        )

        fields = [
            ("Name",        profile.get("name",       "—")),
            ("Title",       profile.get("title",      "—")),
            ("Experience",  profile.get("experience", "—")),
            ("Email",       profile.get("email",      "—")),
            ("Phone",       profile.get("phone",      "—")),
        ]

        for i, (label, value) in enumerate(fields):
            row_frame = ctk.CTkFrame(self.card, fg_color="transparent")
            row_frame.grid(row=i + 1, column=0, sticky="ew", padx=16, pady=3)
            row_frame.grid_columnconfigure(1, weight=1)

            lbl = ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=100,
                anchor="w",
            )
            lbl.grid(row=0, column=0, sticky="w")

            val = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            val.grid(row=0, column=1, sticky="w", padx=(8, 0))

            self.profile_widgets.extend([row_frame, lbl, val])

        # Skills section
        skills = profile.get("skills", [])
        if skills:
            skills_title = ctk.CTkLabel(
                self.card,
                text="Detected skills",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            )
            skills_title.grid(
                row=len(fields) + 1, column=0,
                sticky="w", padx=16, pady=(12, 4)
            )
            self.profile_widgets.append(skills_title)

            # Skills as a wrapping label (comma separated)
            skills_val = ctk.CTkLabel(
                self.card,
                text=",  ".join(skills),
                font=ctk.CTkFont(size=13),
                anchor="w",
                wraplength=500,
                justify="left",
            )
            skills_val.grid(
                row=len(fields) + 2, column=0,
                sticky="w", padx=16, pady=(0, 16)
            )
            self.profile_widgets.append(skills_val)

    # ── Error handler ──────────────────────────────────────────────
    def _show_error(self, message: str):
        self.browse_btn.configure(text="Browse file", state="normal")
        self.status_label.configure(
            text=f"Error: {message}",
            text_color=("#E24B4A", "#F09595"),
        )
        messagebox.showerror("Parse error", message)
