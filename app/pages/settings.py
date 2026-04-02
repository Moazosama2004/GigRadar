import customtkinter as ctk
import json
import os

CONFIG_PATH = "config.json"


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self._load_config()
        self._build_header()
        self._build_accounts_section()
        self._build_sites_section()
        self._build_save_button()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                content = f.read().strip()
                self.config = json.loads(
                    content) if content else self._default_config()
        else:
            self.config = self._default_config()

    def _default_config(self):
        return {
            "mostaql_url": "",
            "nafzly_url":  "",
            "sites": {"mostaql": True, "nafzly": True},
        }

    def _build_header(self):
        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

    def _build_accounts_section(self):
        ctk.CTkLabel(
            self,
            text="Account links",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(1, weight=1)

        fields = [
            ("Mostaql profile URL",   "mostaql_url",
             "https://mostaql.com/u/yourname"),
            ("Nafzly profile URL",    "nafzly_url",
             "https://nafzly.com/freelancer/yourname"),
        ]

        self.entry_vars = {}

        for i, (label, key, placeholder) in enumerate(fields):
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=13),
            ).grid(row=i, column=0, padx=16, pady=(14 if i == 0 else 6, 6), sticky="w")

            var = ctk.StringVar(value=self.config.get(key, ""))
            entry = ctk.CTkEntry(
                card,
                textvariable=var,
                placeholder_text=placeholder,
                height=36,
                corner_radius=8,
            )
            entry.grid(row=i, column=1, padx=(0, 16), pady=(
                14 if i == 0 else 6, 6), sticky="ew")
            self.entry_vars[key] = var

        # Add bottom padding to the last row
        ctk.CTkFrame(card, height=8, fg_color="transparent").grid(
            row=len(fields), column=0)

    def _build_sites_section(self):
        ctk.CTkLabel(
            self,
            text="Platforms to scan",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray",
        ).grid(row=3, column=0, sticky="w", pady=(0, 6))

        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=4, column=0, sticky="ew", pady=(0, 20))

        sites = [
            ("Mostaql",  "mostaql"),
            ("Nafzly",   "nafzly"),
        ]

        self.site_vars = {}

        for i, (label, key) in enumerate(sites):
            var = ctk.BooleanVar(value=self.config["sites"].get(key, True))
            ctk.CTkSwitch(
                card,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=13),
                onvalue=True,
                offvalue=False,
            ).pack(anchor="w", padx=16, pady=(14 if i == 0 else 4, 14 if i == len(sites) - 1 else 4))
            self.site_vars[key] = var

    def _build_save_button(self):
        self.save_btn = ctk.CTkButton(
            self,
            text="Save settings",
            height=40,
            corner_radius=8,
            command=self._save,
        )
        self.save_btn.grid(row=5, column=0, sticky="w", pady=(0, 20))

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("#1D9E75", "#5DCAA5"),
        )
        self.status_label.grid(row=6, column=0, sticky="w")

    def _save(self):
        self.config["mostaql_url"] = self.entry_vars["mostaql_url"].get()
        self.config["nafzly_url"] = self.entry_vars["nafzly_url"].get()
        self.config["sites"] = {k: v.get() for k, v in self.site_vars.items()}

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

        self.status_label.configure(text="Settings saved successfully.")
        self.after(3000, lambda: self.status_label.configure(text=""))
