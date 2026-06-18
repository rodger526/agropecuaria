import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from models.laboratorio import Laboratorio
from database.laboratorio.guardar_laboratorio import guardar_laboratorio
from pdf.generador_pdf_laboratorio import generar_pdf_laboratorio


class VentanaNuevoLaboratorio(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Registro de Laboratorio")
        self.geometry("1300x900")

        titulo = ctk.CTkLabel(
            self,
            text="REGISTRO DE PRÁCTICA DE LABORATORIO",
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=10)

        self.scroll = ctk.CTkScrollableFrame(
            self,
            width=1200,
            height=800
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.crear_campos()

    def crear_campos(self):

        # ==========================
        # DATOS INFORMATIVOS
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Laboratorio"
        ).pack(anchor="w")

        self.laboratorio = ctk.CTkEntry(self.scroll)
        self.laboratorio.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Número de Estudiantes"
        ).pack(anchor="w")

        self.numero_estudiantes = ctk.CTkEntry(self.scroll)
        self.numero_estudiantes.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Asignatura"
        ).pack(anchor="w")

        self.asignatura = ctk.CTkEntry(self.scroll)
        self.asignatura.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Unidad Académica"
        ).pack(anchor="w")

        self.unidad_academica = ctk.CTkEntry(self.scroll)
        self.unidad_academica.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Semestre"
        ).pack(anchor="w")

        self.semestre = ctk.CTkEntry(self.scroll)
        self.semestre.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Carrera"
        ).pack(anchor="w")

        self.carrera = ctk.CTkEntry(self.scroll)
        self.carrera.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Hora Entrada"
        ).pack(anchor="w")

        self.hora_entrada = ctk.CTkEntry(self.scroll)
        self.hora_entrada.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Hora Salida"
        ).pack(anchor="w")

        self.hora_salida = ctk.CTkEntry(self.scroll)
        self.hora_salida.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Institución"
        ).pack(anchor="w")

        self.institucion = ctk.CTkEntry(self.scroll)
        self.institucion.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Ciudad"
        ).pack(anchor="w")

        self.ciudad = ctk.CTkEntry(self.scroll)
        self.ciudad.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Docente Responsable"
        ).pack(anchor="w")

        self.docente = ctk.CTkEntry(self.scroll)
        self.docente.pack(fill="x", pady=5)

        # ==========================
        # DATOS ACADÉMICOS
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Tema de la Práctica"
        ).pack(anchor="w")

        self.tema = ctk.CTkTextbox(
            self.scroll,
            height=100
        )

        self.tema.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Subtema"
        ).pack(anchor="w")

        self.subtema = ctk.CTkTextbox(
            self.scroll,
            height=80
        )

        self.subtema.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Logro de Aprendizaje"
        ).pack(anchor="w")

        self.logro = ctk.CTkTextbox(
            self.scroll,
            height=100
        )

        self.logro.pack(fill="x", pady=5)

        # ==========================
        # PLANIFICACIÓN
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Objetivos"
        ).pack(anchor="w")

        self.objetivos = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.objetivos.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Metodología"
        ).pack(anchor="w")

        self.metodologia = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.metodologia.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Resultados"
        ).pack(anchor="w")

        self.resultados = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.resultados.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Conclusiones"
        ).pack(anchor="w")

        self.conclusiones = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.conclusiones.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.scroll,
            text="Observaciones"
        ).pack(anchor="w")

        self.observaciones = ctk.CTkTextbox(
            self.scroll,
            height=120
        )

        self.observaciones.pack(fill="x", pady=5)

        # ==========================
        # MATERIALES
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Materiales (uno por línea)"
        ).pack(anchor="w")

        self.materiales = ctk.CTkTextbox(
            self.scroll,
            height=150
        )

        self.materiales.pack(fill="x", pady=5)

        # ==========================
        # REACTIVOS
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Reactivos (uno por línea)"
        ).pack(anchor="w")

        self.reactivos = ctk.CTkTextbox(
            self.scroll,
            height=150
        )

        self.reactivos.pack(fill="x", pady=5)

        # ==========================
        # ESTUDIANTES
        # ==========================

        ctk.CTkLabel(
            self.scroll,
            text="Estudiantes (uno por línea)"
        ).pack(anchor="w")

        self.estudiantes = ctk.CTkTextbox(
            self.scroll,
            height=250
        )

        self.estudiantes.pack(fill="x", pady=5)

        # ==========================
        # BOTÓN GUARDAR
        # ==========================

        btn_guardar = ctk.CTkButton(
            self.scroll,
            text="Guardar Registro",
            command=self.guardar
        )

        btn_guardar.pack(pady=20)

    def guardar(self):

        try:

            codigo = datetime.now().strftime(
                "LAB-%Y%m%d%H%M%S"
            )

            laboratorio = Laboratorio(

                codigo,

                self.laboratorio.get().strip(),
                self.numero_estudiantes.get().strip(),

                self.asignatura.get().strip(),
                self.unidad_academica.get().strip(),

                self.semestre.get().strip(),
                self.carrera.get().strip(),

                self.hora_entrada.get().strip(),
                self.hora_salida.get().strip(),

                self.institucion.get().strip(),
                self.ciudad.get().strip(),

                self.docente.get().strip(),

                datetime.now().strftime("%d/%m/%Y"),

                self.tema.get(
                    "1.0",
                    "end"
                ).strip(),

                self.subtema.get(
                    "1.0",
                    "end"
                ).strip(),

                self.logro.get(
                    "1.0",
                    "end"
                ).strip(),

                self.objetivos.get(
                    "1.0",
                    "end"
                ).strip(),

                self.metodologia.get(
                    "1.0",
                    "end"
                ).strip(),

                self.resultados.get(
                    "1.0",
                    "end"
                ).strip(),

                self.conclusiones.get(
                    "1.0",
                    "end"
                ).strip(),

                self.observaciones.get(
                    "1.0",
                    "end"
                ).strip(),

                self.materiales.get(
                    "1.0",
                    "end"
                ).strip(),

                self.reactivos.get(
                    "1.0",
                    "end"
                ).strip(),

                self.estudiantes.get(
                    "1.0",
                    "end"
                ).strip()
            )

            guardar_laboratorio(
                laboratorio
            )

            generar_pdf_laboratorio(
                laboratorio
            )

            messagebox.showinfo(
                "Correcto",
                "Registro guardado correctamente."
            )

            self.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )