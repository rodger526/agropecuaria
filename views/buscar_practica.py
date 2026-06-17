import customtkinter as ctk
import os

from tkinter import messagebox

from database.buscar import (
    listar_practicas,
    buscar_por_id
)

from views.editar_practica import VentanaEditarPractica
from views.eliminar_practica import eliminar


class VentanaBuscar(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Buscar Prácticas")
        self.geometry("1100x650")

        titulo = ctk.CTkLabel(
            self,
            text="Prácticas Registradas",
            font=("Arial", 22, "bold")
        )

        titulo.pack(pady=15)

        self.frame = ctk.CTkScrollableFrame(
            self,
            width=1000,
            height=550
        )

        self.frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.cargar_datos()

    def cargar_datos(self):

        for widget in self.frame.winfo_children():
            widget.destroy()

        datos = listar_practicas()

        print("TOTAL:", len(datos))

        for fila in datos:
            print(fila)

        if not datos:

            ctk.CTkLabel(
                self.frame,
                text="No existen prácticas registradas."
            ).pack(pady=20)

            return

        for fila in datos:

            id_practica = fila[0]
            codigo = fila[1]
            carrera = fila[2]
            asignatura = fila[3]
            tema = fila[4]
            ingeniero_revisor = fila[5]
            pdf_url = fila[6]

            frame_fila = ctk.CTkFrame(
                self.frame
            )

            frame_fila.pack(
                fill="x",
                padx=5,
                pady=5
            )

            texto = (
                f"Código: {codigo} | "
                f"Carrera: {carrera} | "
                f"Asignatura: {asignatura} | "
                f"Docente Responsable: {ingeniero_revisor} | "
                f"Tema: {tema[:50]}... | "
                f"PDF: {'✔' if pdf_url else '✘'}"
            )

            lbl = ctk.CTkLabel(
                frame_fila,
                text=texto,
                anchor="w"
            )

            lbl.pack(
                side="left",
                padx=10,
                pady=10
            )

            btn_pdf = ctk.CTkButton(
                frame_fila,
                text="PDF",
                width=80,
                command=lambda p=pdf_url: self.abrir_pdf(p)
            )

            btn_pdf.pack(
                side="right",
                padx=5
            )

            btn_eliminar = ctk.CTkButton(
                frame_fila,
                text="Eliminar",
                width=90,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=id_practica: self.eliminar_y_recargar(i)
            )

            btn_eliminar.pack(
                side="right",
                padx=5
            )

            btn_editar = ctk.CTkButton(
                frame_fila,
                text="Editar",
                width=90,
                command=lambda i=id_practica: self.editar(i)
            )

            btn_editar.pack(
                side="right",
                padx=5
            )

    def abrir_pdf(self, ruta):

        ruta_completa = os.path.abspath(ruta)

        print("Ruta completa:", ruta_completa)

        if not os.path.isfile(ruta_completa):

            messagebox.showerror(
                "Error",
                f"No se encontró el archivo:\n\n{ruta_completa}"
            )

            return

        try:
            os.startfile(ruta_completa)

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    def editar(self, id_practica):

        registro = buscar_por_id(
            id_practica
        )

        if not registro:

            messagebox.showerror(
                "Error",
                "No se encontró la práctica."
            )

            return

        VentanaEditarPractica(
            self,
            registro
        )

    def eliminar_y_recargar(self, id_practica):

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Desea eliminar esta práctica?"
        )

        if not confirmar:
            return

        try:

            eliminar(
                id_practica
            )

            messagebox.showinfo(
                "Correcto",
                "Práctica eliminada correctamente."
            )

            self.cargar_datos()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )