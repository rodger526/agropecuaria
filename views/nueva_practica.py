import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os

from models.practica import Practica
from database.guardar import guardar_practica
from pdf.generador_pdf import generar_pdf


# ─── Paleta de colores ───────────────────────────────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_FIELD    = "#0F1923"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"
BORDER_ACC  = "#4CAF7D"


def _label(parent, text, secondary=False):
    return ctk.CTkLabel(
        parent,
        text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=TEXT_SEC if secondary else ACCENT,
        anchor="w",
    )


def _entry(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        fg_color=BG_FIELD,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        placeholder_text_color=TEXT_SEC,
        font=("Consolas", 13),
        corner_radius=6,
        height=38,
    )


def _combo(parent, values):
    return ctk.CTkComboBox(
        parent,
        values=values,
        fg_color=BG_FIELD,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        button_color=ACCENT,
        button_hover_color=ACCENT_DARK,
        dropdown_fg_color=BG_PANEL,
        dropdown_text_color=TEXT_PRI,
        dropdown_hover_color=ACCENT_DARK,
        font=("Consolas", 13),
        corner_radius=6,
        height=38,
    )


def _textbox(parent, height=110):
    return ctk.CTkTextbox(
        parent,
        height=height,
        fg_color=BG_FIELD,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        font=("Consolas", 13),
        corner_radius=6,
    )


def _section_card(parent, title, subtitle=""):
    outer = ctk.CTkFrame(
        parent,
        fg_color=BG_PANEL,
        corner_radius=10,
        border_width=0,
    )
    outer.pack(fill="x", pady=(0, 16))

    ctk.CTkFrame(outer, width=4, fg_color=ACCENT, corner_radius=2).pack(
        side="left", fill="y"
    )

    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)

    ctk.CTkLabel(
        inner,
        text=title,
        font=("Consolas", 13, "bold"),
        text_color=ACCENT,
        anchor="w",
    ).pack(anchor="w", pady=(0, 2))

    if subtitle:
        ctk.CTkLabel(
            inner,
            text=subtitle,
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

    return inner


class VentanaNuevaPractica(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        ctk.set_appearance_mode("dark")
        self.title("PLANIFICACIÓN DE PRÁCTICAS")
        self.geometry("1200x900")
        self.configure(fg_color=BG_DARK)

        # Fecha generada al abrir la ventana
        self.fecha_creacion = datetime.now()
        fecha_str = self.fecha_creacion.strftime("%d/%m/%Y  %H:%M")

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_PRI,
        ).pack(side="left", padx=24)

        ctk.CTkLabel(
            header,
            text=f"📅  {fecha_str}",
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        ).pack(side="right", padx=24)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Scroll ────────────────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self,
            width=1100,
            height=750,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Sección 1: Datos informativos ─────────────────────────────
        s1 = _section_card(
            self.scroll,
            "1.  DATOS INFORMATIVOS",
            "Información general de la práctica",
        )

        row1 = ctk.CTkFrame(s1, fg_color="transparent")
        row1.pack(fill="x", pady=(6, 0))

        col_car = ctk.CTkFrame(row1, fg_color="transparent")
        col_car.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_car, "Carrera").pack(anchor="w")
        self.carrera = _combo(col_car, ["Agroindustria", "Agropecuaria", "Agronegocios"])
        self.carrera.pack(fill="x", pady=5)

        col_sem = ctk.CTkFrame(row1, fg_color="transparent")
        col_sem.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_sem, "Semestre").pack(anchor="w")
        self.semestre = _entry(col_sem, "Ej: 3")
        self.semestre.pack(fill="x", pady=5)

        row2 = ctk.CTkFrame(s1, fg_color="transparent")
        row2.pack(fill="x", pady=(6, 0))

        col_asi = ctk.CTkFrame(row2, fg_color="transparent")
        col_asi.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_asi, "Asignatura").pack(anchor="w")
        self.asignatura = _entry(col_asi)
        self.asignatura.pack(fill="x", pady=5)

        col_uni = ctk.CTkFrame(row2, fg_color="transparent")
        col_uni.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_uni, "Unidad del Sílabo").pack(anchor="w")
        self.unidad = _entry(col_uni)
        self.unidad.pack(fill="x", pady=5)

        row3 = ctk.CTkFrame(s1, fg_color="transparent")
        row3.pack(fill="x", pady=(6, 0))

        col_tipo = ctk.CTkFrame(row3, fg_color="transparent")
        col_tipo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_tipo, "Tipo de Práctica").pack(anchor="w")
        self.tipo = _combo(col_tipo, ["Campo", "Laboratorio", "Visita Técnica"])
        self.tipo.pack(fill="x", pady=5)

        col_semana = ctk.CTkFrame(row3, fg_color="transparent")
        col_semana.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_semana, "Semana Planificada").pack(anchor="w")
        self.semana = _entry(col_semana, "Ej: 5")
        self.semana.pack(fill="x", pady=5)

        row4 = ctk.CTkFrame(s1, fg_color="transparent")
        row4.pack(fill="x", pady=(6, 0))

        col_doc = ctk.CTkFrame(row4, fg_color="transparent")
        col_doc.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_doc, "Docente Responsable").pack(anchor="w")
        self.ingeniero_revisor = _entry(col_doc, "Nombre completo del docente")
        self.ingeniero_revisor.pack(fill="x", pady=5)

        col_lugar = ctk.CTkFrame(row4, fg_color="transparent")
        col_lugar.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_lugar, "Lugar de Ejecución").pack(anchor="w")
        self.lugar = _entry(col_lugar)
        self.lugar.pack(fill="x", pady=5)

        # ── Sección 2: Datos académicos ───────────────────────────────
        s2 = _section_card(self.scroll, "2.  DATOS ACADÉMICOS")

        _label(s2, "Tema de la Práctica").pack(anchor="w")
        self.tema = _textbox(s2, height=90)
        self.tema.pack(fill="x", pady=5)

        _label(s2, "Resultado de Aprendizaje").pack(anchor="w", pady=(8, 0))
        self.resultado = _textbox(s2, height=90)
        self.resultado.pack(fill="x", pady=5)

        _label(s2, "Articulación Curricular").pack(anchor="w", pady=(8, 0))
        self.articulacion = _combo(s2, ["Docencia", "Vinculación", "Investigación"])
        self.articulacion.pack(fill="x", pady=5)

        # ── Sección 3: Planificación ──────────────────────────────────
        s3 = _section_card(self.scroll, "3.  PLANIFICACIÓN")

        _label(s3, "2.1  Objetivo General").pack(anchor="w")
        self.objetivo = _textbox(s3, height=110)
        self.objetivo.pack(fill="x", pady=5)

        _label(s3, "2.2  Materiales y Equipos").pack(anchor="w", pady=(8, 0))
        self.materiales = _textbox(s3, height=110)
        self.materiales.pack(fill="x", pady=5)

        _label(s3, "2.3  Descripción de Actividad").pack(anchor="w", pady=(8, 0))
        self.descripcion = _textbox(s3, height=130)
        self.descripcion.pack(fill="x", pady=5)

        _label(s3, "2.4  Evidencia de la Práctica").pack(anchor="w", pady=(8, 0))
        self.evidencias = _combo(s3, [
            "Registro fotográfico",
            "Informe técnico",
            "Bitácora de campo laboratorio",
            "Lista de asistencia",
            "Resultados experimentales",
            "Rúbrica de evaluación",
            "Otro",
        ])
        self.evidencias.pack(fill="x", pady=5)

        # ── Botón guardar ─────────────────────────────────────────────
        ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR PRÁCTICA",
            command=self.guardar,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="#0F1923",
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=48,
        ).pack(pady=24, fill="x")

    def guardar(self):

        try:
            semestre = int(self.semestre.get().strip())
            semana   = int(self.semana.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Semestre y Semana deben ser números.")
            return

        if not self.ingeniero_revisor.get().strip():
            messagebox.showerror("Error", "Debe ingresar el docente responsable.")
            return

        practica = Practica(
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
            self.tema.get("1.0", "end").strip(),
            self.resultado.get("1.0", "end").strip(),
            self.articulacion.get().strip(),
            # PLANIFICACIÓN
            self.objetivo.get("1.0", "end").strip(),
            self.materiales.get("1.0", "end").strip(),
            self.descripcion.get("1.0", "end").strip(),
            self.evidencias.get().strip(),
        )

        # Usar la fecha para nombrar el PDF
        os.makedirs("pdfs_planificacion", exist_ok=True)
        timestamp = self.fecha_creacion.strftime("%Y%m%d_%H%M%S")
        ruta_pdf  = f"pdfs_planificacion/{timestamp}.pdf"

        generar_pdf(practica, ruta_pdf)
        practica.pdf_url = ruta_pdf

        resultado = guardar_practica(practica)

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
