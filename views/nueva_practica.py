import customtkinter as ctk
from tkinter import messagebox
import os

from models.practica import Practica
from database.guardar import guardar_practica
from pdf.generador_pdf import generar_pdf
from utils.generador_codigo import generar_codigo


class VentanaNuevaPractica(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("PLANIFICACIÓN DE PRÁCTICAS")
        self.geometry("1200x900")

        self.codigo = generar_codigo()

        titulo = ctk.CTkLabel(
            self,
            text="PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO",
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
            text="Unidad del Sílabo"
        ).pack(anchor="w")

        self.unidad = ctk.CTkEntry(
            self.scroll
        )

        self.unidad.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Tipo de Práctica"
        ).pack(anchor="w")

        self.tipo = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Campo",
                "Laboratorio",
                "Visita Técnica"
            ]
        )

        self.tipo.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Docente Responsable"
        ).pack(anchor="w")

        self.ingeniero_revisor = ctk.CTkEntry(
            self.scroll,
            placeholder_text="Ingrese el nombre del docente responsable"
        )

        self.ingeniero_revisor.pack(
            fill="x",
            pady=5
        )

        ctk.CTkLabel(
            self.scroll,
            text="Lugar de ejecución"
        ).pack(anchor="w")

        self.lugar = ctk.CTkEntry(
            self.scroll
        )

        self.lugar.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Semana planificada"
        ).pack(anchor="w")

        self.semana = ctk.CTkEntry(
            self.scroll
        )

        self.semana.pack(fill="x", pady=5)

        # =====================================
        # DATOS ACADÉMICOS
        # =====================================

        ctk.CTkLabel(
            self.scroll,
            text="Tema de la práctica"
        ).pack(anchor="w")

        self.tema = ctk.CTkTextbox(
            self.scroll,
            height=100
        )

        self.tema.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Resultado de aprendizaje"
        ).pack(anchor="w")

        self.resultado = ctk.CTkTextbox(
            self.scroll,
            height=100
        )

        self.resultado.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Articulación Curricular"
        ).pack(anchor="w")

        self.articulacion = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Docencia",
                "Vinculación",
                "Investigación"
            ]
        )

        self.articulacion.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="2.1 Objetivo General"
        ).pack(anchor="w")

        self.objetivo = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.objetivo.pack(fill="x", pady=5)

        # =====================================
        # MATERIALES Y EQUIPOS
        # =====================================

        ctk.CTkLabel(
            self.scroll,
            text="2.2 Materiales y Equipos"
        ).pack(anchor="w")

        self.materiales = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.materiales.pack(fill="x", pady=5)

        # =====================================
        # DESCRIPCIÓN DE ACTIVIDADES
        # =====================================

        ctk.CTkLabel(
            self.scroll,
            text="2.3 Descripción de Actividad"
        ).pack(anchor="w")

        self.descripcion = ctk.CTkTextbox(
            self.scroll,
            height=150
        )

        self.descripcion.pack(fill="x", pady=5)

        # =====================================
        # EVIDENCIAS
        # =====================================

        ctk.CTkLabel(
            self.scroll,
            text="2.4 Evidencia de la práctica"
        ).pack(anchor="w")

        self.evidencias = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Registro fotográfico",
                "Informe técnico",
                "Bitácora de campo laboratorio",
                "Lista de asistencia",
                "Resultados experimentales",
                "Rúbrica de evaluación",
                "Otro"
            ]
        )

        self.evidencias.pack(
            fill="x",
            pady=5
        )

        # =====================================
        # BOTÓN GUARDAR
        # =====================================

        btn_guardar = ctk.CTkButton(
            self.scroll,
            text="Guardar Práctica",
            command=self.guardar
        )

        btn_guardar.pack(
            pady=20
        )

    def guardar(self):

        try:

            semestre = int(
                self.semestre.get().strip()
            )

            semana = int(
                self.semana.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Semestre y Semana deben ser números."
            )

            return

        if not self.ingeniero_revisor.get().strip():

            messagebox.showerror(
                "Error",
                "Debe ingresar el docente responsable."
            )

            return

        practica = Practica(

            self.codigo,

            # DATOS INFORMATIVOS
            self.carrera.get().strip(),
            semestre,
            self.asignatura.get().strip(),
            self.unidad.get().strip(),
            self.tipo.get().strip(),
            self.ingeniero_revisor.get().strip(),
            self.lugar.get().strip(),
            semana,

            # DATOS ACADÉMICOS
            self.tema.get(
                "1.0",
                "end"
            ).strip(),

            self.resultado.get(
                "1.0",
                "end"
            ).strip(),

            self.articulacion.get().strip(),

            # PLANIFICACIÓN
            self.objetivo.get(
                "1.0",
                "end"
            ).strip(),

            self.materiales.get(
                "1.0",
                "end"
            ).strip(),

            self.descripcion.get(
                "1.0",
                "end"
            ).strip(),

            self.evidencias.get().strip()
        )

        os.makedirs(
            "pdfs_planificacion",
            exist_ok=True
        )

        ruta_pdf = f"pdfs_planificacion/{self.codigo}.pdf"

        generar_pdf(
            practica,
            ruta_pdf
        )

        practica.pdf_url = ruta_pdf

        resultado = guardar_practica(
            practica
        )

        if resultado:

            messagebox.showinfo(
                "Correcto",
                f"Práctica guardada correctamente.\n\nPDF generado:\n{ruta_pdf}"
            )

            self.destroy()

        else:

            messagebox.showerror(
                "Error",
                "No fue posible guardar la práctica en la base de datos."
            )

        messagebox.showinfo(
            "Correcto",
            f"Práctica guardada correctamente.\n\nPDF generado:\n{ruta_pdf}"
        )

        self.destroy()