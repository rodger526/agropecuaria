import customtkinter as ctk
from tkinter import messagebox

from database.editar import actualizar_practica


class VentanaEditarPractica(ctk.CTkToplevel):

    def __init__(self, master, registro):

        super().__init__(master)

        self.id_practica = registro[0]

        self.title("Editar Práctica")
        self.geometry("1000x850")

        titulo = ctk.CTkLabel(
            self,
            text="Editar Práctica",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=10)

        scroll = ctk.CTkScrollableFrame(
            self,
            width=900,
            height=700
        )
        scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # =====================================
        # DATOS INFORMATIVOS
        # =====================================

        ctk.CTkLabel(scroll, text="Carrera").pack(anchor="w")
        self.carrera = ctk.CTkEntry(scroll)
        self.carrera.insert(0, registro[2])
        self.carrera.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Semestre").pack(anchor="w")
        self.semestre = ctk.CTkEntry(scroll)
        self.semestre.insert(0, str(registro[3]))
        self.semestre.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Asignatura").pack(anchor="w")
        self.asignatura = ctk.CTkEntry(scroll)
        self.asignatura.insert(0, registro[4])
        self.asignatura.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Unidad del Sílabo").pack(anchor="w")
        self.unidad = ctk.CTkEntry(scroll)
        self.unidad.insert(0, registro[5])
        self.unidad.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Tipo de Práctica").pack(anchor="w")
        self.tipo = ctk.CTkEntry(scroll)
        self.tipo.insert(0, registro[6])
        self.tipo.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Docente Responsable").pack(anchor="w")
        self.ingeniero_revisor = ctk.CTkEntry(scroll)
        self.ingeniero_revisor.insert(0, registro[7])
        self.ingeniero_revisor.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Lugar de Ejecución").pack(anchor="w")
        self.lugar = ctk.CTkEntry(scroll)
        self.lugar.insert(0, registro[8])
        self.lugar.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Semana Planificada").pack(anchor="w")
        self.semana = ctk.CTkEntry(scroll)
        self.semana.insert(0, str(registro[9]))
        self.semana.pack(fill="x", pady=5)

        # =====================================
        # DATOS ACADÉMICOS
        # =====================================

        ctk.CTkLabel(
            scroll,
            text="Tema de la práctica"
        ).pack(anchor="w")

        self.tema = ctk.CTkTextbox(
            scroll,
            height=120
        )
        self.tema.pack(fill="x", pady=5)
        self.tema.insert("1.0", registro[10])

        ctk.CTkLabel(
            scroll,
            text="Resultado de aprendizaje"
        ).pack(anchor="w")

        self.resultado = ctk.CTkTextbox(
            scroll,
            height=120
        )
        self.resultado.pack(fill="x", pady=5)
        self.resultado.insert("1.0", registro[11])

        ctk.CTkLabel(
            scroll,
            text="Articulación Curricular"
        ).pack(anchor="w")

        self.articulacion = ctk.CTkEntry(scroll)
        self.articulacion.insert(0, registro[12])
        self.articulacion.pack(fill="x", pady=5)

        # =====================================
        # PLANIFICACIÓN
        # =====================================

        ctk.CTkLabel(
            scroll,
            text="Objetivo General"
        ).pack(anchor="w")

        self.objetivo = ctk.CTkTextbox(
            scroll,
            height=120
        )
        self.objetivo.pack(fill="x", pady=5)
        self.objetivo.insert("1.0", registro[13])

        ctk.CTkLabel(
            scroll,
            text="Materiales y Equipos"
        ).pack(anchor="w")

        self.materiales = ctk.CTkTextbox(
            scroll,
            height=120
        )
        self.materiales.pack(fill="x", pady=5)
        self.materiales.insert("1.0", registro[14])

        ctk.CTkLabel(
            scroll,
            text="Descripción de Actividad"
        ).pack(anchor="w")

        self.descripcion = ctk.CTkTextbox(
            scroll,
            height=150
        )
        self.descripcion.pack(fill="x", pady=5)
        self.descripcion.insert("1.0", registro[15])

        ctk.CTkLabel(
            scroll,
            text="Evidencia"
        ).pack(anchor="w")

        self.evidencias = ctk.CTkEntry(scroll)
        self.evidencias.insert(0, registro[16])
        self.evidencias.pack(fill="x", pady=5)

        # =====================================
        # BOTÓN ACTUALIZAR
        # =====================================

        btn_actualizar = ctk.CTkButton(
            scroll,
            text="Actualizar Práctica",
            command=self.actualizar
        )

        btn_actualizar.pack(pady=20)

        self.codigo = registro[1]
        self.pdf_url = registro[17]

    def actualizar(self):

        try:

            actualizar_practica(

                self.id_practica,

                self.codigo,

                self.carrera.get().strip(),
                int(self.semestre.get().strip()),
                self.asignatura.get().strip(),
                self.unidad.get().strip(),
                self.tipo.get().strip(),
                self.ingeniero_revisor.get().strip(),
                self.lugar.get().strip(),
                int(self.semana.get().strip()),

                self.tema.get(
                    "1.0",
                    "end"
                ).strip(),

                self.resultado.get(
                    "1.0",
                    "end"
                ).strip(),

                self.articulacion.get().strip(),

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

                self.evidencias.get().strip(),

                self.pdf_url
            )

            messagebox.showinfo(
                "Correcto",
                "Práctica actualizada correctamente."
            )

            self.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )