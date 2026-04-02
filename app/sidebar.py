import customtkinter as ctk


# Navigation items: (display label, page key)
NAV_ITEMS = [
    ("Dashboard",  "dashboard"),
    ("Resume",     "resume"),
    ("Accounts",   "settings"),
    ("Scan",       "settings"),
    ("Results",    "settings"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback):
        super().__init__(parent, width=200, corner_radius=0)
        self.navigate_callback = navigate_callback
        self.nav_buttons = {}         # key → button, so we can highlight them

        self.grid_propagate(False)    # lock the sidebar width
        # row 10 is the spacer that pushes settings down
        self.grid_rowconfigure(10, weight=1)

        self._build_logo()
        self._build_nav()
        self._build_bottom()

    # ── Logo ────────────────────────────────────────────────────
    def _build_logo(self):
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(20, 8), sticky="ew")

        ctk.CTkLabel(
            logo_frame,
            text="GigRadar",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1a1a2e", "#e0e0ff"),   # (light mode, dark mode)
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame,
            text=" v0.1",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(side="left", pady=(6, 0))

    # ── Navigation buttons ───────────────────────────────────────
    def _build_nav(self):
        ctk.CTkLabel(
            self,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray",
        ).grid(row=1, column=0, padx=20, pady=(12, 4), sticky="w")

        for i, (label, key) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self.navigate_callback(k),
            )
            btn.grid(row=2 + i, column=0, padx=12, pady=3, sticky="ew")
            self.nav_buttons[key] = btn

    # ── Bottom: settings button ──────────────────────────────────
    def _build_bottom(self):
        ctk.CTkFrame(self, height=1, fg_color="gray30").grid(
            row=11, column=0, padx=16, pady=8, sticky="ew"
        )
        ctk.CTkButton(
            self,
            text="Settings",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray25"),
            command=lambda: self.navigate_callback("settings"),
        ).grid(row=12, column=0, padx=12, pady=(0, 16), sticky="ew")

    # ── Active state ─────────────────────────────────────────────
    def set_active(self, active_key: str):
        """Highlight the active nav button, reset all others."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(
                    fg_color=("#dce4ff", "#2a2d5e"),
                    text_color=("#1a1a2e", "#a0aaff"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                )
