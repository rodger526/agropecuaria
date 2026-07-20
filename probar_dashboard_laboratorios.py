import customtkinter as ctk

from views.dashboard.dashboard_laboratorios import (
    PanelDashboardLaboratorios,
)


class AplicacionPrueba(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(
            "Prueba Dashboard de Laboratorios"
        )

        self.geometry(
            "1450x850"
        )

        self.minsize(
            1100,
            700,
        )

        self.configure(
            fg_color="#0F1923"
        )

        self.grid_rowconfigure(
            0,
            weight=1,
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        contenedor = ctk.CTkScrollableFrame(
            self,
            fg_color="#0F1923",
            corner_radius=0,
            scrollbar_button_color="#4CAF7D",
            scrollbar_button_hover_color="#3A9166",
        )

        contenedor.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        contenedor.grid_columnconfigure(
            0,
            weight=1,
        )

        panel = PanelDashboardLaboratorios(
            contenedor
        )

        panel.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=15,
        )


if __name__ == "__main__":
    ctk.set_appearance_mode(
        "dark"
    )

    app = AplicacionPrueba()
    app.mainloop()