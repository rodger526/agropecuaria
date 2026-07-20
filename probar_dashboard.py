import customtkinter as ctk

from views.dashboard.dashboard_principal import VentanaDashboard


class AplicacionPrueba(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Prueba del dashboard")
        self.geometry("500x300")
        self.configure(fg_color="#0F1923")

        ctk.CTkLabel(
            self,
            text="Prueba del centro de estadísticas",
            font=("Consolas", 18, "bold"),
        ).pack(
            pady=(70, 20)
        )

        ctk.CTkButton(
            self,
            text="📊 Abrir dashboard",
            width=220,
            height=45,
            command=self.abrir_dashboard,
        ).pack()

    def abrir_dashboard(self):
        ventana = VentanaDashboard(self)
        ventana.grab_set()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    app = AplicacionPrueba()
    app.mainloop()