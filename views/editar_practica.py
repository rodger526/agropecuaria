import customtkinter as ctk
from tkinter import messagebox
import os
import threading
import time
import socket

from PIL import Image
from customtkinter import CTkImage
import qrcode

from database.editar import actualizar_practica
from firma.servidor_firma import app as flask_app
from models.practica import Practica
from pdf.generador_pdf import generar_pdf

# ─── Paleta compartida ───────────────────────────────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_CARD     = "#1E2D42"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"

# ─── Índices confirmados de `SELECT * FROM practicas` ────────────────
# id(0) codigo(1) carrera(2) semestre(3) asignatura(4) unidad_silabo(5)
# tipo_practica(6) lugar_ejecucion(7) semana_planificada(8) tema_practica(9)
# resultado_aprendizaje(10) articulacion_curricular(11) objetivo_general(12)
# materiales_equipos(13) descripcion_actividad(14) evidencias(15)
# pdf_url(16) fecha_registro(17) ingeniero_revisor(18) fecha_creacion(19)
# firma_docente(20) firma_comision(21)

IDX_ID          = 0
IDX_CODIGO      = 1
IDX_CARRERA     = 2
IDX_SEMESTRE    = 3
IDX_ASIGNATURA  = 4
IDX_UNIDAD      = 5
IDX_TIPO        = 6
IDX_LUGAR       = 7
IDX_SEMANA      = 8
IDX_TEMA        = 9
IDX_RESULTADO   = 10
IDX_ARTICUL     = 11
IDX_OBJETIVO    = 12
IDX_MATERIALES  = 13
IDX_DESCRIPCION = 14
IDX_EVIDENCIAS  = 15
IDX_PDF         = 16
IDX_FECHA_CREACION = 19
IDX_DOCENTE     = 18
IDX_FIRMA_DOC   = 20
IDX_FIRMA_COM   = 21


def _col(registro, idx, default=""):
    try:
        v = registro[idx]
        return v if v is not None else default
    except (IndexError, TypeError):
        return default


def _label(parent, text):
    return ctk.CTkLabel(
        parent, text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT, anchor="w",
    )


def _entry(parent):
    return ctk.CTkEntry(
        parent,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
        font=("Consolas", 13), corner_radius=6, height=38,
    )


def _textbox(parent, height=110):
    return ctk.CTkTextbox(
        parent, height=height,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, font=("Consolas", 13), corner_radius=6,
    )


def _section_card(parent, title, subtitle=""):
    outer = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=10)
    outer.pack(fill="x", pady=(0, 16))
    ctk.CTkFrame(outer, width=4, fg_color=ACCENT, corner_radius=2).pack(side="left", fill="y")
    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
    ctk.CTkLabel(
        inner, text=title, font=("Consolas", 13, "bold"),
        text_color=ACCENT, anchor="w",
    ).pack(anchor="w", pady=(0, 2))
    if subtitle:
        ctk.CTkLabel(
            inner, text=subtitle, font=("Consolas", 10),
            text_color=TEXT_SEC, anchor="w",
        ).pack(anchor="w", pady=(0, 8))
    return inner


class VentanaEditarPractica(ctk.CTkToplevel):

    def __init__(self, master, registro):
        super().__init__(master)

        self.id_practica = _col(registro, IDX_ID, None)
        self.codigo      = _col(registro, IDX_CODIGO, None)
        self.pdf_url     = _col(registro, IDX_PDF, None)

        # Datos originales que no se editan en este formulario pero
        # se necesitan para regenerar el PDF correctamente
        self._fecha_creacion_original = _col(registro, IDX_FECHA_CREACION, None)
        self._firma_docente_bd        = _col(registro, IDX_FIRMA_DOC, None)

        # Firma de comisión ya guardada en BD (ruta) o None
        self._firma_comision_bd = _col(registro, IDX_FIRMA_COM, None)

        self._servidor_iniciado = False
        self._polling_activo    = False
        self._img_refs          = {}

        self.title("Editar Práctica")
        self.geometry("1100x900")
        self.configure(fg_color=BG_DARK)

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="✏  EDITAR PRÁCTICA",
            font=("Consolas", 15, "bold"), text_color=TEXT_PRI,
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header, text=f"ID #{self.id_practica}",
            font=("Consolas", 12, "bold"), text_color=ACCENT,
        ).pack(side="right", padx=20)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Scroll ────────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ══ SECCIÓN 1 — DATOS INFORMATIVOS ═══════════════════════════
        s1 = _section_card(scroll, "1.  DATOS INFORMATIVOS")

        row1 = ctk.CTkFrame(s1, fg_color="transparent")
        row1.pack(fill="x", pady=(6, 0))
        col_a = ctk.CTkFrame(row1, fg_color="transparent")
        col_a.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_a, "Carrera").pack(anchor="w")
        self.carrera = _entry(col_a)
        self.carrera.insert(0, _col(registro, IDX_CARRERA))
        self.carrera.pack(fill="x", pady=5)

        col_b = ctk.CTkFrame(row1, fg_color="transparent")
        col_b.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_b, "Semestre").pack(anchor="w")
        self.semestre = _entry(col_b)
        self.semestre.insert(0, str(_col(registro, IDX_SEMESTRE)))
        self.semestre.pack(fill="x", pady=5)

        row2 = ctk.CTkFrame(s1, fg_color="transparent")
        row2.pack(fill="x", pady=(6, 0))
        col_c = ctk.CTkFrame(row2, fg_color="transparent")
        col_c.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_c, "Asignatura").pack(anchor="w")
        self.asignatura = _entry(col_c)
        self.asignatura.insert(0, _col(registro, IDX_ASIGNATURA))
        self.asignatura.pack(fill="x", pady=5)

        col_d = ctk.CTkFrame(row2, fg_color="transparent")
        col_d.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_d, "Unidad del Sílabo").pack(anchor="w")
        self.unidad = _entry(col_d)
        self.unidad.insert(0, _col(registro, IDX_UNIDAD))
        self.unidad.pack(fill="x", pady=5)

        row3 = ctk.CTkFrame(s1, fg_color="transparent")
        row3.pack(fill="x", pady=(6, 0))
        col_e = ctk.CTkFrame(row3, fg_color="transparent")
        col_e.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_e, "Tipo de Práctica").pack(anchor="w")
        self.tipo = _entry(col_e)
        self.tipo.insert(0, _col(registro, IDX_TIPO))
        self.tipo.pack(fill="x", pady=5)

        col_f = ctk.CTkFrame(row3, fg_color="transparent")
        col_f.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_f, "Semana Planificada").pack(anchor="w")
        self.semana = _entry(col_f)
        self.semana.insert(0, str(_col(registro, IDX_SEMANA)))
        self.semana.pack(fill="x", pady=5)

        row4 = ctk.CTkFrame(s1, fg_color="transparent")
        row4.pack(fill="x", pady=(6, 0))
        col_g = ctk.CTkFrame(row4, fg_color="transparent")
        col_g.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_g, "Docente Responsable").pack(anchor="w")
        self.ingeniero_revisor = _entry(col_g)
        self.ingeniero_revisor.insert(0, _col(registro, IDX_DOCENTE))
        self.ingeniero_revisor.pack(fill="x", pady=5)

        col_h = ctk.CTkFrame(row4, fg_color="transparent")
        col_h.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_h, "Lugar de Ejecución").pack(anchor="w")
        self.lugar = _entry(col_h)
        self.lugar.insert(0, _col(registro, IDX_LUGAR))
        self.lugar.pack(fill="x", pady=5)

        # ══ SECCIÓN 2 — DATOS ACADÉMICOS ═════════════════════════════
        s2 = _section_card(scroll, "2.  DATOS ACADÉMICOS")

        _label(s2, "Tema de la Práctica").pack(anchor="w")
        self.tema = _textbox(s2, height=90)
        self.tema.pack(fill="x", pady=5)
        self.tema.insert("1.0", _col(registro, IDX_TEMA))

        _label(s2, "Resultado de Aprendizaje").pack(anchor="w", pady=(8, 0))
        self.resultado = _textbox(s2, height=90)
        self.resultado.pack(fill="x", pady=5)
        self.resultado.insert("1.0", _col(registro, IDX_RESULTADO))

        _label(s2, "Articulación Curricular").pack(anchor="w", pady=(8, 0))
        self.articulacion = _entry(s2)
        self.articulacion.insert(0, _col(registro, IDX_ARTICUL))
        self.articulacion.pack(fill="x", pady=5)

        # ══ SECCIÓN 3 — PLANIFICACIÓN ════════════════════════════════
        s3 = _section_card(scroll, "3.  PLANIFICACIÓN")

        _label(s3, "Objetivo General").pack(anchor="w")
        self.objetivo = _textbox(s3, height=110)
        self.objetivo.pack(fill="x", pady=5)
        self.objetivo.insert("1.0", _col(registro, IDX_OBJETIVO))

        _label(s3, "Materiales y Equipos").pack(anchor="w", pady=(8, 0))
        self.materiales = _textbox(s3, height=110)
        self.materiales.pack(fill="x", pady=5)
        self.materiales.insert("1.0", _col(registro, IDX_MATERIALES))

        _label(s3, "Descripción de Actividad").pack(anchor="w", pady=(8, 0))
        self.descripcion = _textbox(s3, height=130)
        self.descripcion.pack(fill="x", pady=5)
        self.descripcion.insert("1.0", _col(registro, IDX_DESCRIPCION))

        _label(s3, "Evidencia").pack(anchor="w", pady=(8, 0))
        self.evidencias = _entry(s3)
        self.evidencias.insert(0, _col(registro, IDX_EVIDENCIAS))
        self.evidencias.pack(fill="x", pady=5)

        # ══ SECCIÓN 4 — ESTADO DE FIRMAS ═════════════════════════════
        firma_doc_existente = bool(_col(registro, IDX_FIRMA_DOC, None))
        firma_com_existente = bool(self._firma_comision_bd)

        s4 = _section_card(
            scroll, "4.  FIRMAS",
            "Estado actual de las firmas registradas para esta práctica",
        )

        estado_row = ctk.CTkFrame(s4, fg_color="transparent")
        estado_row.pack(fill="x", pady=(0, 10))

        # Docente: solo informativo (no editable aquí)
        col_doc = ctk.CTkFrame(estado_row, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        col_doc.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(
            col_doc, text="👤  DOCENTE RESPONSABLE",
            font=("Consolas", 11, "bold"), text_color=ACCENT,
        ).pack(pady=(12, 4))
        ctk.CTkLabel(
            col_doc,
            text="✔  Firmado" if firma_doc_existente else "⏳  Sin firma",
            font=("Consolas", 12, "bold"),
            text_color=ACCENT if firma_doc_existente else TEXT_SEC,
        ).pack(pady=(0, 12))

        # Comisión: si ya firmó, mostrar estado. Si no, mostrar panel de firma.
        self._col_com = ctk.CTkFrame(estado_row, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        self._col_com.pack(side="left", fill="x", expand=True, padx=(8, 0))

        ctk.CTkLabel(
            self._col_com, text="📋  COMISIÓN",
            font=("Consolas", 11, "bold"), text_color=ACCENT,
        ).pack(pady=(12, 4))

        if firma_com_existente:
            ctk.CTkLabel(
                self._col_com, text="✔  Firmado",
                font=("Consolas", 12, "bold"), text_color=ACCENT,
            ).pack(pady=(0, 12))
        else:
            # ── Panel activo de firma para comisión ──
            ctk.CTkLabel(
                self._col_com, text="⏳  Pendiente de firma",
                font=("Consolas", 11), text_color=TEXT_SEC,
            ).pack()

            self._btn_qr_com = ctk.CTkButton(
                self._col_com,
                text="⬤  Generar QR de firma",
                fg_color=BG_CARD, hover_color="#243348",
                text_color=ACCENT, font=("Consolas", 12, "bold"),
                corner_radius=8, height=36,
                border_width=1, border_color=ACCENT,
                command=self._iniciar_servidor_comision,
            )
            self._btn_qr_com.pack(fill="x", padx=14, pady=(8, 8))

            self._lbl_qr_com = ctk.CTkLabel(self._col_com, text="")
            self._lbl_qr_com.pack(pady=(0, 6))

            self._lbl_estado_com = ctk.CTkLabel(
                self._col_com, text="",
                font=("Consolas", 11), text_color=TEXT_SEC,
            )
            self._lbl_estado_com.pack()

            self._lbl_preview_com = ctk.CTkLabel(self._col_com, text="")
            self._lbl_preview_com.pack(pady=(4, 12))

        # ══ BOTÓN ACTUALIZAR ═════════════════════════════════════════
        ctk.CTkButton(
            scroll,
            text="⬤  ACTUALIZAR PRÁCTICA",
            command=self.actualizar,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="#0F1923", font=("Consolas", 14, "bold"),
            corner_radius=8, height=48,
        ).pack(pady=24, fill="x")

    # ─── Firma de comisión (post-creación) ───────────────────────────

    def _iniciar_servidor_comision(self):
        if not self._servidor_iniciado:
            t = threading.Thread(
                target=lambda: flask_app.run(
                    host="0.0.0.0", port=5000, debug=False, use_reloader=False
                ),
                daemon=True,
            )
            t.start()
            self._servidor_iniciado = True
            time.sleep(0.9)

        self._generar_qr_comision()

        if not self._polling_activo:
            self._polling_activo = True
            self._polling_firma_comision()

        self._btn_qr_com.configure(text="↺  Regenerar QR")

    def _generar_qr_comision(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = socket.gethostbyname(socket.gethostname())

        url = f"http://{ip}:5000/firma/comision"
        qr_img = qrcode.make(url).resize((160, 160)).convert("RGB")
        photo  = CTkImage(light_image=qr_img, dark_image=qr_img, size=(160, 160))
        self._img_refs["qr_com"] = photo
        self._lbl_qr_com.configure(image=photo, text="")

    def _polling_firma_comision(self):
        if not self.winfo_exists():
            return

        ruta_com = "firma/firmas/firma_comision.png"

        if os.path.exists(ruta_com):
            self._lbl_estado_com.configure(text="✔  Firmado", text_color=ACCENT)
            self._mostrar_preview_comision(ruta_com)

            # Guardar la ruta en BD inmediatamente, sin esperar al botón Actualizar
            from database.editar import actualizar_firma_comision
            actualizar_firma_comision(self.id_practica, ruta_com)
            self._firma_comision_bd = ruta_com

            # Detener polling: ya se firmó, no hace falta seguir consultando
            self._polling_activo = False
            return
        else:
            self._lbl_estado_com.configure(text="⏳  Esperando firma…", text_color=TEXT_SEC)

        self.after(2000, self._polling_firma_comision)

    def _mostrar_preview_comision(self, ruta):
        if "preview_com" in self._img_refs:
            return
        try:
            img = Image.open(ruta).convert("RGBA")
            fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
            fondo.paste(img, mask=img.split()[3])
            fondo = fondo.convert("RGB")
            fondo.thumbnail((200, 80))
            photo = CTkImage(light_image=fondo, dark_image=fondo, size=fondo.size)
            self._img_refs["preview_com"] = photo
            self._lbl_preview_com.configure(image=photo, text="")
        except Exception:
            pass

    # ─── Guardar cambios ─────────────────────────────────────────────

    def actualizar(self):
        try:
            carrera      = self.carrera.get().strip()
            semestre     = int(self.semestre.get().strip())
            asignatura   = self.asignatura.get().strip()
            unidad       = self.unidad.get().strip()
            tipo         = self.tipo.get().strip()
            docente      = self.ingeniero_revisor.get().strip()
            lugar        = self.lugar.get().strip()
            semana       = int(self.semana.get().strip())
            tema         = self.tema.get("1.0", "end").strip()
            resultado    = self.resultado.get("1.0", "end").strip()
            articulacion = self.articulacion.get().strip()
            objetivo     = self.objetivo.get("1.0", "end").strip()
            materiales   = self.materiales.get("1.0", "end").strip()
            descripcion  = self.descripcion.get("1.0", "end").strip()
            evidencias   = self.evidencias.get().strip()

        except ValueError:
            messagebox.showerror("Error", "Semestre y Semana deben ser números.")
            return

        resultado_bd = actualizar_practica(
            self.id_practica,
            self.codigo,
            carrera,
            semestre,
            asignatura,
            unidad,
            tipo,
            docente,
            lugar,
            semana,
            tema,
            resultado,
            articulacion,
            objetivo,
            materiales,
            descripcion,
            evidencias,
            self.pdf_url,
            None,                          # firma_docente: no se edita aquí
            self._firma_comision_bd,       # ya actualizada por polling si aplica
        )

        if not resultado_bd:
            messagebox.showerror("Error", "No fue posible actualizar la práctica.")
            return

        # ── Regenerar el PDF físico con los datos editados ─────────────
        try:
            practica = Practica(
                carrera, semestre, asignatura, unidad, tipo, docente,
                lugar, semana, tema, resultado, articulacion,
                objetivo, materiales, descripcion, evidencias,
            )

            # Conservar la fecha de creación original (no la de hoy)
            if self._fecha_creacion_original:
                practica.fecha_creacion = self._fecha_creacion_original

            practica.pdf_url       = self.pdf_url
            practica.firma_docente = self._firma_docente_bd
            practica.firma_comision = self._firma_comision_bd

            if self.pdf_url:
                generar_pdf(practica, self.pdf_url)

        except Exception as e:
            # La BD ya se actualizó correctamente; solo avisamos que el
            # PDF no pudo regenerarse, sin perder los cambios guardados.
            messagebox.showwarning(
                "Advertencia",
                f"La práctica se actualizó en la base de datos,\n"
                f"pero no fue posible regenerar el PDF:\n\n{e}"
            )
            self.destroy()
            return

        messagebox.showinfo(
            "Correcto",
            "Práctica actualizada correctamente.\nEl PDF fue regenerado con los nuevos datos."
        )
        self.destroy()