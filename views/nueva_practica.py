import customtkinter as ctk
from tkinter import messagebox
import os
import threading
import time
import socket

from PIL import Image
from customtkinter import CTkImage
import qrcode

from models.practica import Practica
from database.guardar import guardar_practica
from pdf.generador_pdf import generar_pdf
from firma.servidor_firma import app as flask_app

# ─── Paleta ──────────────────────────────────────────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_CARD     = "#1E2D42"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"

RUTA_FIRMA_DOC = "firma/firmas/firma_docente.png"
RUTA_FIRMA_COM = "firma/firmas/firma_comision.png"


def _label(parent, text):
    return ctk.CTkLabel(
        parent,
        text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT,
        anchor="w",
    )


def _entry(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        fg_color=BG_DARK,
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
        fg_color=BG_DARK,
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
        fg_color=BG_DARK,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        font=("Consolas", 13),
        corner_radius=6,
    )


def _section_card(parent, title, subtitle=""):
    outer = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=10)
    outer.pack(fill="x", pady=(0, 16))
    ctk.CTkFrame(outer, width=4, fg_color=ACCENT, corner_radius=2).pack(
        side="left", fill="y"
    )
    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
    ctk.CTkLabel(
        inner, text=title,
        font=("Consolas", 13, "bold"),
        text_color=ACCENT, anchor="w",
    ).pack(anchor="w", pady=(0, 2))
    if subtitle:
        ctk.CTkLabel(
            inner, text=subtitle,
            font=("Consolas", 10),
            text_color=TEXT_SEC, anchor="w",
        ).pack(anchor="w", pady=(0, 8))
    return inner


class VentanaNuevaPractica(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("PLANIFICACIÓN DE PRÁCTICAS")
        self.geometry("1200x900")
        self.configure(fg_color=BG_DARK)

        # Estado interno firmas
        self._servidor_iniciado = False
        self._polling_activo    = False
        self._img_refs          = {}

        # Limpiar firmas anteriores
        for ruta in (RUTA_FIRMA_DOC, RUTA_FIRMA_COM):
            if os.path.exists(ruta):
                os.remove(ruta)

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

        from datetime import datetime
        ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%d/%m/%Y  %H:%M"),
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        ).pack(side="right", padx=24)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Scroll ────────────────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ══ SECCIÓN 1 — DATOS INFORMATIVOS ═══════════════════════════
        s1 = _section_card(self.scroll, "1.  DATOS INFORMATIVOS")

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

        # ══ SECCIÓN 2 — DATOS ACADÉMICOS ═════════════════════════════
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

        # ══ SECCIÓN 3 — PLANIFICACIÓN ════════════════════════════════
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

        # ══ SECCIÓN 4 — FIRMAS ═══════════════════════════════════════
        s4 = _section_card(
            self.scroll,
            "4.  FIRMAS",
            "Genera el QR para que el docente y la comisión firmen desde su teléfono",
        )

        self._btn_qr = ctk.CTkButton(
            s4,
            text="⬤  Generar QR de firmas",
            fg_color=BG_CARD,
            hover_color="#243348",
            text_color=ACCENT,
            font=("Consolas", 13, "bold"),
            corner_radius=8,
            height=42,
            border_width=1,
            border_color=ACCENT,
            command=self._iniciar_servidor,
        )
        self._btn_qr.pack(fill="x", pady=(0, 14))

        # Dos columnas: docente | comisión
        qr_row = ctk.CTkFrame(s4, fg_color="transparent")
        qr_row.pack(fill="x")

        # ── Columna Docente ───────────────────────────────────────────
        col_d = ctk.CTkFrame(qr_row, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        col_d.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=4)

        ctk.CTkLabel(
            col_d, text="👤  DOCENTE RESPONSABLE",
            font=("Consolas", 11, "bold"), text_color=ACCENT,
        ).pack(pady=(12, 4))

        self._lbl_qr_doc = ctk.CTkLabel(col_d, text="Presiona «Generar QR» para activar", text_color=TEXT_SEC, font=("Consolas", 10))
        self._lbl_qr_doc.pack(pady=(0, 6))

        self._lbl_estado_doc = ctk.CTkLabel(
            col_d, text="⏳  Pendiente de firma",
            font=("Consolas", 11), text_color=TEXT_SEC,
        )
        self._lbl_estado_doc.pack()

        self._lbl_preview_doc = ctk.CTkLabel(col_d, text="")
        self._lbl_preview_doc.pack(pady=(4, 12))

        # ── Columna Comisión ──────────────────────────────────────────
        col_c = ctk.CTkFrame(qr_row, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        col_c.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=4)

        ctk.CTkLabel(
            col_c, text="📋  COMISIÓN",
            font=("Consolas", 11, "bold"), text_color=ACCENT,
        ).pack(pady=(12, 4))

        self._lbl_qr_com = ctk.CTkLabel(col_c, text="Presiona «Generar QR» para activar", text_color=TEXT_SEC, font=("Consolas", 10))
        self._lbl_qr_com.pack(pady=(0, 6))

        self._lbl_estado_com = ctk.CTkLabel(
            col_c, text="⏳  Pendiente de firma",
            font=("Consolas", 11), text_color=TEXT_SEC,
        )
        self._lbl_estado_com.pack()

        self._lbl_preview_com = ctk.CTkLabel(col_c, text="")
        self._lbl_preview_com.pack(pady=(4, 12))

        # ══ BOTÓN GUARDAR ════════════════════════════════════════════
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

    # ─── Servidor y QR ───────────────────────────────────────────────

    def _iniciar_servidor(self):
        if not self._servidor_iniciado:
            t = threading.Thread(
                target=lambda: flask_app.run(
                    host="0.0.0.0", port=5000,
                    debug=False, use_reloader=False
                ),
                daemon=True,
            )
            t.start()
            self._servidor_iniciado = True
            time.sleep(0.9)

        self._generar_qrs()

        if not self._polling_activo:
            self._polling_activo = True
            self._polling_firmas()

        self._btn_qr.configure(text="↺  Regenerar QR")

    def _generar_qrs(self):
        # Obtener IP de red real (no 127.0.0.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = socket.gethostbyname(socket.gethostname())

        for rol, lbl_qr in (
            ("docente",  self._lbl_qr_doc),
            ("comision", self._lbl_qr_com),
        ):
            url = f"http://{ip}:5000/firma/{rol}"
            qr_img = qrcode.make(url).resize((170, 170)).convert("RGB")
            photo  = CTkImage(light_image=qr_img, dark_image=qr_img, size=(170, 170))
            self._img_refs[f"qr_{rol}"] = photo
            lbl_qr.configure(image=photo, text="")

    def _polling_firmas(self):
        """Revisa cada 2 s si las firmas ya fueron guardadas."""
        if not self.winfo_exists():
            return

        # Docente
        if os.path.exists(RUTA_FIRMA_DOC):
            self._lbl_estado_doc.configure(text="✔  Firmado", text_color=ACCENT)
            self._mostrar_preview(RUTA_FIRMA_DOC, self._lbl_preview_doc, "prev_doc")
        else:
            self._lbl_estado_doc.configure(text="⏳  Pendiente de firma", text_color=TEXT_SEC)

        # Comisión
        if os.path.exists(RUTA_FIRMA_COM):
            self._lbl_estado_com.configure(text="✔  Firmado", text_color=ACCENT)
            self._mostrar_preview(RUTA_FIRMA_COM, self._lbl_preview_com, "prev_com")
        else:
            self._lbl_estado_com.configure(text="⏳  Pendiente de firma", text_color=TEXT_SEC)

        self.after(2000, self._polling_firmas)

    def _mostrar_preview(self, ruta, label, key):
        """Carga y muestra la firma como thumbnail (solo la primera vez)."""
        if key in self._img_refs:
            return
        try:
            img = Image.open(ruta).convert("RGBA")
            # Fondo blanco para PNG transparente
            fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
            fondo.paste(img, mask=img.split()[3])
            fondo = fondo.convert("RGB")
            fondo.thumbnail((200, 80))
            photo = CTkImage(light_image=fondo, dark_image=fondo, size=(200, 80))
            self._img_refs[key] = photo
            label.configure(image=photo, text="")
        except Exception:
            pass

    # ─── Guardar ─────────────────────────────────────────────────────

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
            self.carrera.get().strip(),
            semestre,
            self.asignatura.get().strip(),
            self.unidad.get().strip(),
            self.tipo.get().strip(),
            self.ingeniero_revisor.get().strip(),
            self.lugar.get().strip(),
            semana,
            self.tema.get("1.0", "end").strip(),
            self.resultado.get("1.0", "end").strip(),
            self.articulacion.get().strip(),
            self.objetivo.get("1.0", "end").strip(),
            self.materiales.get("1.0", "end").strip(),
            self.descripcion.get("1.0", "end").strip(),
            self.evidencias.get().strip(),
        )

        # Asignar rutas de firma si ya fueron firmadas
        if os.path.exists(RUTA_FIRMA_DOC):
            practica.firma_docente = RUTA_FIRMA_DOC
        if os.path.exists(RUTA_FIRMA_COM):
            practica.firma_comision = RUTA_FIRMA_COM

        os.makedirs("pdfs_planificacion", exist_ok=True)
        nombre_pdf = practica.fecha_creacion.strftime("%Y%m%d_%H%M%S")
        ruta_pdf = f"pdfs_planificacion/{nombre_pdf}.pdf"

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