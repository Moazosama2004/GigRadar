import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x300")
app.title("GigRadar - Test")
ctk.CTkLabel(app, text="GigRadar is ready!").pack(pady=40)
app.mainloop()
