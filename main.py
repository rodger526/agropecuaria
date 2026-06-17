import customtkinter as ctk

from views.buscar_practica import VentanaBuscar
from views.nueva_practica import VentanaNuevaPractica

from views.nueva_laboratorio import VentanaNuevaLaboratorio

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("Sistema de Prácticas")
app.geometry("600x300")


def abrir_busqueda():
    VentanaBuscar(app)


def abrir_nueva():
    VentanaNuevaPractica(app)

def abrir_laboratorio():
    VentanaNuevaLaboratorio(app)

titulo = ctk.CTkLabel(
    app,
    text="Sistema de Prácticas",
    font=("Arial", 28, "bold")
)
titulo.pack(pady=30)



btn_nueva = ctk.CTkButton(
    app,
    text="Nueva planificacion de Práctica",
    command=abrir_nueva
)
btn_nueva.pack(pady=10)

btn_nueva = ctk.CTkButton(
    app,
    text="Registro de practica de laboratorio",
    command=abrir_nueva
)
btn_nueva.pack(pady=10)

btn_buscar = ctk.CTkButton(
    app,
    text="Buscar Práctica",
    command=abrir_busqueda
)
btn_buscar.pack(pady=10)

btn_salir = ctk.CTkButton(
    app,
    text="Salir",
    command=app.destroy
)
btn_salir.pack(pady=10)


app.mainloop()