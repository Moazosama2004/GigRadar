import customtkinter as ctk


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_stats()
        self._build_results_area()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(side="left")

        # Scan button lives in the header, top-right
        ctk.CTkButton(
            header,
            text="Start Scan",
            width=120,
            height=36,
            corner_radius=8,
        ).pack(side="right")

    def _build_stats(self):
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        stats = [
            ("Gigs Found",  "—",      "#1D9E75"),
            ("Matched",     "—",      "#EF9F27"),
            ("Last Scan",   "Never",  "#7F77DD"),
        ]

        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=(
                0 if i == 0 else 8, 0), sticky="ew")

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w", padx=16, pady=(14, 2))

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=color,
            ).pack(anchor="w", padx=16, pady=(0, 14))

    def _build_results_area(self):
        results_frame = ctk.CTkFrame(self, corner_radius=10)
        results_frame.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        # Placeholder message centered in the frame
        ctk.CTkLabel(
            results_frame,
            text="No results yet.\nUpload your resume and start a scan to see matched gigs here.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center",
        ).grid(row=0, column=0)
