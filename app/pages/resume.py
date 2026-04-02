import customtkinter as ctk
from tkinter import filedialog
import os


class ResumePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.uploaded_file = None

        self._build_header()
        self._build_upload_area()
        self._build_file_info()

    def _build_header(self):
        ctk.CTkLabel(
            self,
            text="Resume",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

    def _build_upload_area(self):
        # The dashed upload box
        self.upload_box = ctk.CTkFrame(
            self,
            corner_radius=12,
            border_width=2,
            border_color=("gray70", "gray35"),
            fg_color=("gray95", "gray17"),
            height=200,
        )
        self.upload_box.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self.upload_box.grid_columnconfigure(0, weight=1)
        self.upload_box.grid_propagate(False)

        ctk.CTkLabel(
            self.upload_box,
            text="Drop your resume here",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=(48, 6))

        ctk.CTkLabel(
            self.upload_box,
            text="Supports PDF and DOCX",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, pady=(0, 16))

        ctk.CTkButton(
            self.upload_box,
            text="Browse file",
            width=140,
            height=36,
            corner_radius=8,
            command=self._pick_file,
        ).grid(row=2, column=0, pady=(0, 48))

    def _build_file_info(self):
        # This area updates once a file is selected
        self.file_info_frame = ctk.CTkFrame(self, corner_radius=10)
        self.file_info_frame.grid(row=2, column=0, sticky="ew")
        self.file_info_frame.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(
            self.file_info_frame,
            text="No file selected",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.file_label.pack(anchor="w", padx=16, pady=14)

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Select your resume",
            filetypes=[
                ("Supported files", "*.pdf *.docx"),
                ("PDF files",       "*.pdf"),
                ("Word documents",  "*.docx"),
            ],
        )
        if path:
            self.uploaded_file = path
            filename = os.path.basename(path)
            size_kb = os.path.getsize(path) // 1024
            self.file_label.configure(
                text=f"Selected: {filename}   ({size_kb} KB)",
                text_color=("#1D9E75", "#5DCAA5"),   # green in both modes
            )
