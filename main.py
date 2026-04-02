import customtkinter as ctk
from app.window import GigRadarApp

# Set the appearance before creating any window
ctk.set_appearance_mode("dark")          # "dark" or "light" or "system"
ctk.set_default_color_theme("blue")      # built-in theme base

if __name__ == "__main__":
    app = GigRadarApp()
    app.mainloop()
