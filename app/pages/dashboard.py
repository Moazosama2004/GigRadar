import customtkinter as ctk
import json
import os
import webbrowser

GIGS_CACHE_PATH = "gigs_cache.json"


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_stats()
        self._build_results_area()
        self.refresh()              # load any existing cache on startup

    # ── Header ─────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.refresh_btn = ctk.CTkButton(
            header,
            text="Refresh results",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            command=self.refresh,
        )
        self.refresh_btn.grid(row=0, column=1, sticky="e")

    # ── Stat cards ─────────────────────────────────────────────────
    def _build_stats(self):
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Store references so we can update them
        self.stat_values = {}

        stats = [
            ("gigs_found",  "Gigs found",  "—", "#1D9E75"),
            ("matched",     "Matched",     "—", "#EF9F27"),
            ("last_scan",   "Last scan",   "Never", "#7F77DD"),
        ]

        for i, (key, label, default, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, corner_radius=10)
            card.grid(
                row=0, column=i,
                padx=(0 if i == 0 else 8, 0),
                sticky="ew",
            )
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w", padx=16, pady=(14, 2))

            val_label = ctk.CTkLabel(
                card,
                text=default,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=color,
            )
            val_label.pack(anchor="w", padx=16, pady=(0, 14))
            self.stat_values[key] = val_label

    # ── Results area ────────────────────────────────────────────────
    def _build_results_area(self):
        # Filter bar
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.grid(row=2, column=0, sticky="new")
        filter_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            filter_bar,
            text="Min score:",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).grid(row=0, column=0, padx=(0, 8))

        self.min_score_var = ctk.IntVar(value=0)
        ctk.CTkSlider(
            filter_bar,
            from_=0,
            to=100,
            variable=self.min_score_var,
            command=lambda v: self._apply_filter(),
            width=160,
        ).grid(row=0, column=1, sticky="w")

        self.min_score_label = ctk.CTkLabel(
            filter_bar,
            text="0",
            font=ctk.CTkFont(size=13),
            width=30,
        )
        self.min_score_label.grid(row=0, column=2, padx=(4, 16))

        # Source filter
        self.source_var = ctk.StringVar(value="All")
        ctk.CTkSegmentedButton(
            filter_bar,
            values=["All", "mostaql", "nafzly"],
            variable=self.source_var,
            command=lambda v: self._apply_filter(),
            width=220,
        ).grid(row=0, column=3, padx=(0, 0))

        # Scrollable results list
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
            label_text="",
        )
        self.results_scroll.grid(
            row=3, column=0,
            sticky="nsew",
            pady=(10, 0),
        )
        self.results_scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.placeholder = ctk.CTkLabel(
            self.results_scroll,
            text="No results yet.\nGo to Scan to start finding gigs.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center",
        )
        self.placeholder.pack(pady=40)

        self._all_gigs = []

    # ── Load and display gigs ───────────────────────────────────────
    def refresh(self):
        if not os.path.exists(GIGS_CACHE_PATH):
            return

        with open(GIGS_CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)

        self._all_gigs = cache.get("gigs", [])
        scraped_at = cache.get("scraped_at", "")[:16].replace("T", " ")
        matched = sum(1 for g in self._all_gigs if g.get(
            "match_score", 0) >= 40)

        # Update stat cards
        self.stat_values["gigs_found"].configure(text=str(len(self._all_gigs)))
        self.stat_values["matched"].configure(text=str(matched))
        self.stat_values["last_scan"].configure(text=scraped_at or "—")

        self._apply_filter()

    def _apply_filter(self):
        min_score = int(self.min_score_var.get())
        source = self.source_var.get()

        self.min_score_label.configure(text=str(min_score))

        filtered = [
            g for g in self._all_gigs
            if g.get("match_score", 0) >= min_score
            and (source == "All" or g.get("source") == source)
        ]

        self._render_gigs(filtered)

    def _render_gigs(self, gigs: list):
        # Clear existing cards
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        if not gigs:
            ctk.CTkLabel(
                self.results_scroll,
                text="No gigs match the current filter.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).pack(pady=40)
            return

        for gig in gigs:
            self._build_gig_card(gig)

    def _build_gig_card(self, gig: dict):
        score = gig.get("match_score", 0)
        source = gig.get("source", "")

        # Score color
        if score >= 70:
            score_color = "#1D9E75"
        elif score >= 40:
            score_color = "#EF9F27"
        else:
            score_color = "#888780"

        # Source badge color
        source_color = "#534AB7" if source == "mostaql" else "#0F6E56"

        card = ctk.CTkFrame(
            self.results_scroll,
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray25"),
        )
        card.pack(fill="x", padx=2, pady=4)
        card.grid_columnconfigure(1, weight=1)

        # Score badge
        score_badge = ctk.CTkFrame(
            card,
            width=56,
            height=56,
            corner_radius=8,
            fg_color=score_color,
        )
        score_badge.grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=12)
        score_badge.grid_propagate(False)

        ctk.CTkLabel(
            score_badge,
            text=str(score),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        ).place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            score_badge,
            text="/100",
            font=ctk.CTkFont(size=9),
            text_color="white",
        ).place(relx=0.5, rely=0.78, anchor="center")

        # Title
        ctk.CTkLabel(
            card,
            text=gig.get("title", "Untitled")[:80],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            justify="left",
        ).grid(row=0, column=1, sticky="w", pady=(12, 2))

        # Meta row — budget, source badge, time
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.grid(row=1, column=1, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            meta_frame,
            text=gig.get("budget", "—"),
            font=ctk.CTkFont(size=12),
            text_color="#1D9E75",
        ).pack(side="left", padx=(0, 8))

        # Source pill
        source_pill = ctk.CTkFrame(
            meta_frame,
            corner_radius=6,
            fg_color=source_color,
            height=20,
        )
        source_pill.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            source_pill,
            text=source,
            font=ctk.CTkFont(size=11),
            text_color="white",
        ).pack(padx=6, pady=1)

        ctk.CTkLabel(
            meta_frame,
            text=gig.get("posted_at", ""),
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left")

        # Description preview
        desc = gig.get("description", "")[:120]
        if desc:
            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=500,
            ).grid(row=2, column=1, sticky="w", pady=(0, 4))

        # Open button
        url = gig.get("url", "")
        if url:
            ctk.CTkButton(
                card,
                text="Open gig",
                width=90,
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=12),
                command=lambda u=url: webbrowser.open(u),
            ).grid(row=0, column=2, rowspan=2, padx=12, pady=12)
