import customtkinter as ctk
from app.sidebar import Sidebar
from app.pages.dashboard import DashboardPage
from app.pages.resume import ResumePage
from app.pages.settings import SettingsPage


class GigRadarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Window config ──────────────────────────────────────
        self.title("GigRadar")
        self.geometry("1000x640")
        self.minsize(800, 500)

        # ── Layout: 2 columns (sidebar | content) ──────────────
        self.grid_columnconfigure(1, weight=1)   # content column stretches
        self.grid_rowconfigure(0, weight=1)       # single row stretches

        # ── Build sidebar ──────────────────────────────────────
        self.sidebar = Sidebar(self, navigate_callback=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ── Page container (right side) ────────────────────────
        self.content_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── Create all pages (hidden by default) ───────────────
        self.pages = {
            "dashboard": DashboardPage(self.content_frame),
            "resume":    ResumePage(self.content_frame),
            "settings":  SettingsPage(self.content_frame),
        }

        # ── Show default page ──────────────────────────────────
        self.show_page("dashboard")

    def show_page(self, name: str):
        """Hide all pages, then show the requested one."""
        for page in self.pages.values():
            page.grid_remove()                         # hide without destroying

        self.pages[name].grid(row=0, column=0, sticky="nsew")
        # highlight correct nav button
        self.sidebar.set_active(name)
