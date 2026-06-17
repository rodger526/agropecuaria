import customtkinter as ctk
from tkinter import messagebox
import os

from models.practica import Practica
from database.guardar import guardar_practica
from pdf.generador_pdf import generar_pdf
from utils.generador_codigo import generar_codigo


class VentanaNuevaLaboratorio(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("REGISTRO DE PRÁCTICA DE LABORATORIO")
        self.geometry("1200x900")

        self.codigo = generar_codigo()

        titulo = ctk.CTkLabel(
            self,
            text="REGISTRO DE PRÁCTICA DE LABORATORIO",
            font=("Arial", 24, "bold")
        )

        titulo.pack(pady=10)

        self.scroll = ctk.CTkScrollableFrame(
            self,
            width=1100,
            height=750
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        ctk.CTkLabel(
            self.scroll,
            text="Laboratorio"
        ).pack(anchor="w")

        self.carrera = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Análisis",
                "Agua",
                "Lacteos",
                "Frutas y hortalizas",
            ]
        )

        self.estudiantes.pack(fill="x", pady=5)

        ctk.CTkEntry(
            self.scroll,
            text="Número de estudiantes:"
        ).pack(anchor="w")

        self.carrera.pack(fill="x", pady=5)

        self.asignatura.pack(fill="x", pady=5)

        ctk.CTkEntry(
            self.scroll,
            text="Asignatura:"
        ).pack(anchor="w")

        self.carrera.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Semestre"
        ).pack(anchor="w")

        self.semestre = ctk.CTkEntry(
            self.scroll
        )

        self.semestre.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Asignatura"
        ).pack(anchor="w")

        self.asignatura = ctk.CTkEntry(
            self.scroll
        )

        self.asignatura.pack(fill="x", pady=5)


        ctk.CTkLabel(
            self.scroll,
            text="Unidad Académica"
        ).pack(anchor="w")

        self.facultad = ctk.CTkComboBox(
            self.scroll,
            text="Facultad de Ciencias de la Vida y Tecnologías"
        )
        self.facultad.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="semestre"
        ).pack(anchor="w")
        self.semestre = ctk.CTkEntry(
            self.scroll
        )
        self.semestre.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Carrera"
        ).pack(anchor="w")

        self.carrera = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Agroindustria",
                "Agropecuaria",
                "Agronegocios"
            ]
        )

        self.carrera.pack(fill="x", pady=5)

        ctk.CTkButton(
            self.scroll,
            text="Hora de entrada",
        ).pack(anchor="w")
        self.hora_entrada = ctk.CTkEntry(
            self.scroll
        )
        self.hora_entrada.pack(fill="x", pady=5)

        ctk.CTkButton(
            self.scroll,
            text="Hora de salida",
        ).pack(anchor="w")
        self.hora_salida = ctk.CTkEntry(
            self.scroll
        )
        self.hora_salida.pack(fill="x", pady=5)

        ctk.CTkButton(
            self.scroll,
            text="Institución",
        ).pack(anchor="w")
        self.institucion = ctk.CTkEntry(
            self.scroll
        )
        self.institucion.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Ciudad"
        ).pack(anchor="w")

        self.ciudad = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Manta",
                "Chone",
                "Bahía de Caráquez",
                "El Carmen",
                "Pedernales",
            ]
        )

        self.ciudad.pack(fill="x", pady=5)

        ctk.CTkButton(
            self.scroll,
            text="Docente responsable",
        ).pack(anchor="w")
        self.docente = ctk.CTkEntry(
            self.scroll
        )
        self.docente.pack(fill="x", pady=5)
