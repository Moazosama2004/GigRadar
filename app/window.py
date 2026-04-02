import customtkinter as ctk
from app.sidebar import Sidebar
from app.pages.dashboard import DashboardPage
from app.pages.resume import ResumePage
from app.pages.settings import SettingsPage
from app.pages.scan import ScanPage


class GigRadarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GigRadar")
        self.geometry("1100x680")
        self.minsize(800, 500)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, navigate_callback=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=16, pady=16
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Dashboard created first so scan can callback into it
        dashboard_page = DashboardPage(self.content_frame)

        self.pages = {
            "dashboard": dashboard_page,
            "resume":    ResumePage(self.content_frame),
            "scan":      ScanPage(
                self.content_frame,
                on_scan_complete=dashboard_page.refresh,
            ),
            "settings":  SettingsPage(self.content_frame),
        }

        self.show_page("dashboard")

    def show_page(self, name: str):
        for page in self.pages.values():
            page.grid_remove()
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        self.sidebar.set_active(name)
