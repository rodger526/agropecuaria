import os
import socket
import tempfile
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import customtkinter as ctk
import qrcode
from customtkinter import CTkImage
from PIL import Image
from tkinter import messagebox

from database.guardar import guardar_practica
from firma.servidor_firma import (
    app as flask_app,
    eliminar_firmas_sesion,
    obtener_ruta_firma,
)
from models.practica import Practica
from pdf.generador_pdf import generar_pdf
from storage.subir_pdf import eliminar_pdf, subir_pdf


# ============================================================
# PALETA
# ============================================================

BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI = "#E8EDF2"
TEXT_SEC = "#8A9BB0"
BORDER = "#2A3A50"


# ============================================================
# CONFIGURACIÓN DEL SERVIDOR DE FIRMAS
# ============================================================

PUERTO_FIRMAS = 5000

_SERVIDOR_LOCK = threading.Lock()
_SERVIDOR_INICIADO = False


def _servidor_escuchando(host="127.0.0.1", puerto=PUERTO_FIRMAS):
    """
    Comprueba si ya existe un servidor escuchando en el puerto indicado.
    """

    try:
        with socket.create_connection(
            (host, puerto),
            timeout=0.4,
        ):
            return True
    except OSError:
        return False


def _ejecutar_servidor_flask():
    """
    Ejecuta Flask en un hilo secundario.
    """

    flask_app.run(
        host="0.0.0.0",
        port=PUERTO_FIRMAS,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def _asegurar_servidor_firmas():
    """
    Inicia el servidor una sola vez para toda la aplicación.

    Si el puerto ya está ocupado por el servidor de firmas, se considera
    que ya se encuentra disponible y no se intenta iniciar otro proceso.
    """

    global _SERVIDOR_INICIADO

    with _SERVIDOR_LOCK:
        if _SERVIDOR_INICIADO or _servidor_escuchando():
            _SERVIDOR_INICIADO = True
            return

        hilo = threading.Thread(
            target=_ejecutar_servidor_flask,
            daemon=True,
            name="ServidorFirmasFlask",
        )
        hilo.start()
        _SERVIDOR_INICIADO = True


# ============================================================
# COMPONENTES DE INTERFAZ
# ============================================================

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
    outer = ctk.CTkFrame(
        parent,
        fg_color=BG_PANEL,
        corner_radius=10,
    )
    outer.pack(
        fill="x",
        pady=(0, 16),
    )

    ctk.CTkFrame(
        outer,
        width=4,
        fg_color=ACCENT,
        corner_radius=2,
    ).pack(
        side="left",
        fill="y",
    )

    inner = ctk.CTkFrame(
        outer,
        fg_color="transparent",
    )
    inner.pack(
        side="left",
        fill="both",
        expand=True,
        padx=16,
        pady=14,
    )

    ctk.CTkLabel(
        inner,
        text=title,
        font=("Consolas", 13, "bold"),
        text_color=ACCENT,
        anchor="w",
    ).pack(
        anchor="w",
        pady=(0, 2),
    )

    if subtitle:
        ctk.CTkLabel(
            inner,
            text=subtitle,
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(0, 8),
        )

    return inner


# ============================================================
# VENTANA NUEVA PRÁCTICA
# ============================================================

class VentanaNuevaPractica(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("PLANIFICACIÓN DE PRÁCTICAS")
        self.geometry("1200x900")
        self.minsize(950, 700)
        self.configure(fg_color=BG_DARK)

        # Cada formulario usa una sesión independiente.
        self.codigo_sesion = uuid.uuid4().hex

        # Estado interno.
        self._polling_activo = False
        self._guardando = False
        self._cerrando = False
        self._img_refs = {}
        self._firma_mtimes = {}
        self._after_polling = None

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cerrar_ventana,
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=72,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_PRI,
        ).pack(
            side="left",
            padx=24,
        )

        ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%d/%m/%Y  %H:%M"),
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        ).pack(
            side="right",
            padx=24,
        )

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(fill="x")

        # ====================================================
        # CONTENEDOR DESPLAZABLE
        # ====================================================

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        # ====================================================
        # SECCIÓN 1 — DATOS INFORMATIVOS
        # ====================================================

        s1 = _section_card(
            self.scroll,
            "1.  DATOS INFORMATIVOS",
        )

        row1 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row1.pack(
            fill="x",
            pady=(6, 0),
        )

        col_car = ctk.CTkFrame(
            row1,
            fg_color="transparent",
        )
        col_car.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            col_car,
            "Carrera",
        ).pack(anchor="w")

        self.carrera = _combo(
            col_car,
            [
                "Ingeniería Agroindustria",
                "Ingeniería Agropecuaria",
                "Ingeniería Agronegocios",
            ],
        )
        self.carrera.pack(
            fill="x",
            pady=5,
        )

        col_sem = ctk.CTkFrame(
            row1,
            fg_color="transparent",
        )
        col_sem.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            col_sem,
            "Semestre",
        ).pack(anchor="w")

        self.semestre = _entry(
            col_sem,
            "Ej: 3",
        )
        self.semestre.pack(
            fill="x",
            pady=5,
        )

        row2 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row2.pack(
            fill="x",
            pady=(6, 0),
        )

        col_asi = ctk.CTkFrame(
            row2,
            fg_color="transparent",
        )
        col_asi.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            col_asi,
            "Asignatura",
        ).pack(anchor="w")

        self.asignatura = _entry(
            col_asi,
        )
        self.asignatura.pack(
            fill="x",
            pady=5,
        )

        col_uni = ctk.CTkFrame(
            row2,
            fg_color="transparent",
        )
        col_uni.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            col_uni,
            "Unidad del Sílabo",
        ).pack(anchor="w")
        self.unidad = _entry(
            col_uni,
            "titulo de la unidad del sílabo",
        )
        self.unidad.pack(
            fill="x",
            pady=5,
        )

        self.unidad.pack(
            fill="x",
            pady=5,
        )

        row3 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row3.pack(
            fill="x",
            pady=(6, 0),
        )

        col_tipo = ctk.CTkFrame(
            row3,
            fg_color="transparent",
        )
        col_tipo.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            col_tipo,
            "Tipo de Práctica",
        ).pack(anchor="w")

        self.tipo = _combo(
            col_tipo,
            [
                "Campo",
                "Laboratorio",
                "Visita Técnica",
            ],
        )
        self.tipo.pack(
            fill="x",
            pady=5,
        )

        col_semana = ctk.CTkFrame(
            row3,
            fg_color="transparent",
        )
        col_semana.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            col_semana,
            "Semana Planificada",
        ).pack(anchor="w")

        self.semana = _entry(
            col_semana,
            "Ej: 5",
        )
        self.semana.pack(
            fill="x",
            pady=5,
        )

        row4 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row4.pack(
            fill="x",
            pady=(6, 0),
        )

        col_doc = ctk.CTkFrame(
            row4,
            fg_color="transparent",
        )
        col_doc.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            col_doc,
            "Docente Responsable",
        ).pack(anchor="w")

        self.ingeniero_revisor = _entry(
            col_doc,
            "Nombre completo del docente",
        )
        self.ingeniero_revisor.pack(
            fill="x",
            pady=5,
        )

        col_lugar = ctk.CTkFrame(
            row4,
            fg_color="transparent",
        )
        col_lugar.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            col_lugar,
            "Lugar de Ejecución",
        ).pack(anchor="w")

        self.lugar = _combo(
            col_lugar,
            [
                "Campus Matriz Manta",
                "Extension Bahía de Caráquez",
                "Extension Chone",
                "Extension El Carmen",
                "Extension Flavio Alfaro",
                "Extension Pedernales",
                "Extension Pichincha",
                "Extension Santo Domingo (Sede)",
                "Extension Tosagua",
                "Finca Experimental Lodana",
            ],
        )
        self.lugar.pack(
            fill="x",
            pady=5,
        )

        # ====================================================
        # SECCIÓN 2 — DATOS ACADÉMICOS
        # ====================================================

        s2 = _section_card(
            self.scroll,
            "2.  DATOS ACADÉMICOS",
        )

        _label(
            s2,
            "Tema de la Práctica",
        ).pack(anchor="w")

        self.tema = _textbox(
            s2,
            height=90,
        )
        self.tema.pack(
            fill="x",
            pady=5,
        )

        _label(
            s2,
            "Resultado de Aprendizaje",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.resultado = _textbox(
            s2,
            height=90,
        )
        self.resultado.pack(
            fill="x",
            pady=5,
        )

        _label(
            s2,
            "Articulación Curricular",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.articulacion = _combo(
            s2,
            [
                "Docencia",
                "Vinculación",
                "Investigación",
            ],
        )
        self.articulacion.pack(
            fill="x",
            pady=5,
        )

        # ====================================================
        # SECCIÓN 3 — PLANIFICACIÓN
        # ====================================================

        s3 = _section_card(
            self.scroll,
            "3.  PLANIFICACIÓN",
        )

        _label(
            s3,
            "2.1  Objetivo General",
        ).pack(anchor="w")

        self.objetivo = _textbox(
            s3,
            height=110,
        )
        self.objetivo.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "2.2  Materiales y Equipos",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.materiales = _textbox(
            s3,
            height=110,
        )
        self.materiales.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "2.3  Descripción de Actividad",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.descripcion = _textbox(
            s3,
            height=130,
        )
        self.descripcion.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "2.4  Evidencia de la Práctica",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.evidencias = _combo(
            s3,
            [
                "Registro fotográfico",
                "Informe técnico",
                "Bitácora de campo laboratorio",
                "Lista de asistencia",
                "Resultados experimentales",
                "Rúbrica de evaluación",
                "Otro",
            ],
        )
        self.evidencias.pack(
            fill="x",
            pady=5,
        )

        # ====================================================
        # SECCIÓN 4 — FIRMAS
        # ====================================================

        s4 = _section_card(
            self.scroll,
            "4.  FIRMAS",
            (
                "Genera los códigos QR para que el docente y la comisión "
                "firmen desde su teléfono"
            ),
        )

        self._lbl_sesion = ctk.CTkLabel(
            s4,
            text=f"SESIÓN: {self.codigo_sesion}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        )
        self._lbl_sesion.pack(
            fill="x",
            pady=(0, 8),
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
        self._btn_qr.pack(
            fill="x",
            pady=(0, 14),
        )

        qr_row = ctk.CTkFrame(
            s4,
            fg_color="transparent",
        )
        qr_row.pack(fill="x")

        # ---------------- DOCENTE ----------------

        col_d = ctk.CTkFrame(
            qr_row,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_d.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
            pady=4,
        )

        ctk.CTkLabel(
            col_d,
            text="👤  DOCENTE RESPONSABLE",
            font=("Consolas", 11, "bold"),
            text_color=ACCENT,
        ).pack(
            pady=(12, 4),
        )

        self._lbl_qr_doc = ctk.CTkLabel(
            col_d,
            text="Presiona «Generar QR» para activar",
            text_color=TEXT_SEC,
            font=("Consolas", 10),
        )
        self._lbl_qr_doc.pack(
            pady=(0, 6),
        )

        self._lbl_estado_doc = ctk.CTkLabel(
            col_d,
            text="⏳  Pendiente de firma",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
        )
        self._lbl_estado_doc.pack()

        self._lbl_preview_doc = ctk.CTkLabel(
            col_d,
            text="",
        )
        self._lbl_preview_doc.pack(
            pady=(4, 12),
        )

        # ---------------- COMISIÓN ----------------

        col_c = ctk.CTkFrame(
            qr_row,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_c.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
            pady=4,
        )

        ctk.CTkLabel(
            col_c,
            text="📋  COMISIÓN",
            font=("Consolas", 11, "bold"),
            text_color=ACCENT,
        ).pack(
            pady=(12, 4),
        )

        self._lbl_qr_com = ctk.CTkLabel(
            col_c,
            text="Presiona «Generar QR» para activar",
            text_color=TEXT_SEC,
            font=("Consolas", 10),
        )
        self._lbl_qr_com.pack(
            pady=(0, 6),
        )

        self._lbl_estado_com = ctk.CTkLabel(
            col_c,
            text="⏳  Pendiente de firma",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
        )
        self._lbl_estado_com.pack()

        self._lbl_preview_com = ctk.CTkLabel(
            col_c,
            text="",
        )
        self._lbl_preview_com.pack(
            pady=(4, 12),
        )

        # ====================================================
        # BOTÓN GUARDAR
        # ====================================================

        self._btn_guardar = ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR PRÁCTICA",
            command=self.guardar,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="#0F1923",
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=48,
        )
        self._btn_guardar.pack(
            pady=24,
            fill="x",
        )

    # ========================================================
    # SERVIDOR Y CÓDIGOS QR
    # ========================================================

    def _iniciar_servidor(self):
        """
        Inicia Flask y muestra los códigos QR de la sesión actual.
        """

        try:
            _asegurar_servidor_firmas()

            self._btn_qr.configure(
                text="↺  Regenerar QR",
                state="disabled",
            )

            self._lbl_estado_doc.configure(
                text="⏳  Esperando firma",
                text_color=TEXT_SEC,
            )
            self._lbl_estado_com.configure(
                text="⏳  Esperando firma",
                text_color=TEXT_SEC,
            )

            # Da un pequeño margen para que Flask abra el puerto.
            self.after(
                700,
                self._activar_qrs,
            )

        except Exception as error:
            messagebox.showerror(
                "Servidor de firmas",
                (
                    "No fue posible iniciar el servidor de firmas.\n\n"
                    f"Detalle: {error}"
                ),
                parent=self,
            )

    def _activar_qrs(self):
        """
        Genera los QR y activa la revisión periódica de firmas.
        """

        if self._cerrando or not self.winfo_exists():
            return

        try:
            self._generar_qrs()

            if not self._polling_activo:
                self._polling_activo = True
                self._polling_firmas()

            self._btn_qr.configure(
                text="↺  Regenerar QR",
                state="normal",
            )

        except Exception as error:
            self._btn_qr.configure(
                text="⬤  Generar QR de firmas",
                state="normal",
            )

            messagebox.showerror(
                "Códigos QR",
                (
                    "No fue posible generar los códigos QR.\n\n"
                    f"Detalle: {error}"
                ),
                parent=self,
            )

    def _obtener_ip_local(self):
        """
        Obtiene la dirección IP de la computadora dentro de la red local.
        """

        socket_temporal = None

        try:
            socket_temporal = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
            )
            socket_temporal.connect(
                ("8.8.8.8", 80)
            )
            return socket_temporal.getsockname()[0]

        except OSError:
            try:
                return socket.gethostbyname(
                    socket.gethostname()
                )
            except OSError:
                return "127.0.0.1"

        finally:
            if socket_temporal is not None:
                socket_temporal.close()

    def _generar_qrs(self):
        """
        Genera un QR independiente para cada rol, usando la misma sesión.
        """

        ip = self._obtener_ip_local()
        sesion = quote(
            self.codigo_sesion,
            safe="",
        )

        configuraciones = (
            (
                "docente",
                self._lbl_qr_doc,
            ),
            (
                "comision",
                self._lbl_qr_com,
            ),
        )

        for rol, label_qr in configuraciones:
            url = (
                f"http://{ip}:{PUERTO_FIRMAS}"
                f"/firma/{rol}?sesion={sesion}"
            )

            imagen_qr = qrcode.make(
                url
            ).resize(
                (170, 170)
            ).convert(
                "RGB"
            )

            imagen_ctk = CTkImage(
                light_image=imagen_qr,
                dark_image=imagen_qr,
                size=(170, 170),
            )

            self._img_refs[f"qr_{rol}"] = imagen_ctk

            label_qr.configure(
                image=imagen_ctk,
                text="",
            )

    # ========================================================
    # ESTADO Y PREVISUALIZACIÓN DE FIRMAS
    # ========================================================

    def _polling_firmas(self):
        """
        Revisa cada dos segundos si las firmas fueron registradas.
        """

        if (
            self._cerrando
            or not self._polling_activo
            or not self.winfo_exists()
        ):
            return

        self._actualizar_estado_firma(
            rol="docente",
            label_estado=self._lbl_estado_doc,
            label_preview=self._lbl_preview_doc,
            clave_preview="prev_doc",
        )

        self._actualizar_estado_firma(
            rol="comision",
            label_estado=self._lbl_estado_com,
            label_preview=self._lbl_preview_com,
            clave_preview="prev_com",
        )

        self._after_polling = self.after(
            2000,
            self._polling_firmas,
        )

    def _actualizar_estado_firma(
        self,
        rol,
        label_estado,
        label_preview,
        clave_preview,
    ):
        """
        Actualiza el texto y la imagen de una firma específica.
        """

        if (
            self._cerrando
            or not self._polling_activo
            or not self.winfo_exists()
        ):
            return

        try:
            if (
                not label_estado.winfo_exists()
                or not label_preview.winfo_exists()
            ):
                return
        except Exception:
            return

        ruta = obtener_ruta_firma(
            rol,
            self.codigo_sesion,
        )

        if ruta and os.path.isfile(ruta):
            try:
                label_estado.configure(
                    text="✔  Firmado",
                    text_color=ACCENT,
                )

                self._mostrar_preview(
                    ruta=ruta,
                    label=label_preview,
                    key=clave_preview,
                )
            except Exception:
                # La ventana o la imagen pudieron destruirse mientras
                # se ejecutaba este callback.
                return

            return

        try:
            label_estado.configure(
                text="⏳  Pendiente de firma",
                text_color=TEXT_SEC,
            )

            # No se asigna image=None porque CustomTkinter puede mantener
            # internamente una referencia a un pyimage ya destruido.
            label_preview.configure(
                text="",
            )
        except Exception:
            return

        self._img_refs.pop(
            clave_preview,
            None,
        )
        self._firma_mtimes.pop(
            clave_preview,
            None,
        )

    def _mostrar_preview(
        self,
        ruta,
        label,
        key,
    ):
        """
        Carga la firma como miniatura.

        La imagen vuelve a cargarse cuando el archivo fue reemplazado.
        """

        try:
            mtime = os.path.getmtime(
                ruta
            )

            if self._firma_mtimes.get(key) == mtime:
                return

            with Image.open(ruta) as imagen_original:
                imagen = imagen_original.convert(
                    "RGBA"
                )

                fondo = Image.new(
                    "RGBA",
                    imagen.size,
                    (255, 255, 255, 255),
                )

                if "A" in imagen.getbands():
                    fondo.paste(
                        imagen,
                        mask=imagen.getchannel("A"),
                    )
                else:
                    fondo.paste(
                        imagen,
                    )

                fondo = fondo.convert(
                    "RGB"
                )
                fondo.thumbnail(
                    (200, 80)
                )

                ancho = max(
                    fondo.width,
                    1,
                )
                alto = max(
                    fondo.height,
                    1,
                )

                imagen_ctk = CTkImage(
                    light_image=fondo,
                    dark_image=fondo,
                    size=(ancho, alto),
                )

            self._img_refs[key] = imagen_ctk
            self._firma_mtimes[key] = mtime

            label.configure(
                image=imagen_ctk,
                text="",
            )

        except (
            OSError,
            ValueError,
        ):
            pass

    # ========================================================
    # VALIDACIONES
    # ========================================================

    @staticmethod
    def _texto_textbox(widget):
        return widget.get(
            "1.0",
            "end",
        ).strip()

    def _validar_formulario(self):
        """
        Valida los campos y devuelve semestre y semana convertidos a int.
        """

        try:
            semestre = int(
                self.semestre.get().strip()
            )
            semana = int(
                self.semana.get().strip()
            )
        except ValueError as error:
            raise ValueError(
                "Semestre y Semana deben ser números enteros."
            ) from error

        if semestre <= 0:
            raise ValueError(
                "El semestre debe ser mayor que cero."
            )

        if semana <= 0:
            raise ValueError(
                "La semana planificada debe ser mayor que cero."
            )

        campos_obligatorios = {
            "Carrera": self.carrera.get().strip(),
            "Asignatura": self.asignatura.get().strip(),
            "Unidad del sílabo": self.unidad.get().strip(),
            "Tipo de práctica": self.tipo.get().strip(),
            "Docente responsable": self.ingeniero_revisor.get().strip(),
            "Lugar de ejecución": self.lugar.get().strip(),
            "Tema de la práctica": self._texto_textbox(self.tema),
            "Resultado de aprendizaje": self._texto_textbox(self.resultado),
            "Articulación curricular": self.articulacion.get().strip(),
            "Objetivo general": self._texto_textbox(self.objetivo),
            "Materiales y equipos": self._texto_textbox(self.materiales),
            "Descripción de actividad": self._texto_textbox(self.descripcion),
            "Evidencia de la práctica": self.evidencias.get().strip(),
        }

        faltantes = [
            nombre
            for nombre, valor in campos_obligatorios.items()
            if not valor
        ]

        if faltantes:
            raise ValueError(
                "Debe completar los siguientes campos:\n\n• "
                + "\n• ".join(faltantes)
            )

        return semestre, semana

    def _crear_objeto_practica(
        self,
        semestre,
        semana,
    ):
        """
        Construye el modelo Practica usando los valores del formulario.
        """

        nueva_practica = Practica(
            self.carrera.get().strip(),
            semestre,
            self.asignatura.get().strip(),
            self.unidad.get().strip(),
            self.tipo.get().strip(),
            self.ingeniero_revisor.get().strip(),
            self.lugar.get().strip(),
            semana,
            self._texto_textbox(self.tema),
            self._texto_textbox(self.resultado),
            self.articulacion.get().strip(),
            self._texto_textbox(self.objetivo),
            self._texto_textbox(self.materiales),
            self._texto_textbox(self.descripcion),
            self.evidencias.get().strip(),
        )

        nueva_practica.firma_docente = obtener_ruta_firma(
            "docente",
            self.codigo_sesion,
        )

        nueva_practica.firma_comision = obtener_ruta_firma(
            "comision",
            self.codigo_sesion,
        )

        return nueva_practica

    # ========================================================
    # GUARDADO
    # ========================================================

    def guardar(self):
        """
        Ejecuta el flujo completo:

        1. Valida los datos.
        2. Obtiene las firmas temporales de la sesión.
        3. Genera un PDF temporal.
        4. Sube el PDF a Supabase Storage.
        5. Guarda únicamente la URL en PostgreSQL.
        6. Elimina el PDF local temporal.
        7. Elimina las firmas temporales cuando todo finaliza correctamente.
        """

        if self._guardando:
            return

        try:
            semestre, semana = self._validar_formulario()
        except ValueError as error:
            messagebox.showerror(
                "Datos incompletos",
                str(error),
                parent=self,
            )
            return

        firma_docente = obtener_ruta_firma(
            "docente",
            self.codigo_sesion,
        )

        firma_comision = obtener_ruta_firma(
            "comision",
            self.codigo_sesion,
        )

        if not firma_docente or not firma_comision:
            faltantes = []

            if not firma_docente:
                faltantes.append(
                    "Docente responsable"
                )

            if not firma_comision:
                faltantes.append(
                    "Comisión académica"
                )

            respuesta = messagebox.askyesno(
                "Firmas pendientes",
                (
                    "Todavía faltan las siguientes firmas:\n\n• "
                    + "\n• ".join(faltantes)
                    + "\n\n¿Desea guardar la práctica sin esas firmas?"
                ),
                parent=self,
            )

            if not respuesta:
                return

        self._guardando = True

        self._btn_guardar.configure(
            state="disabled",
            text="GUARDANDO, ESPERE...",
        )

        # El procesamiento se ejecuta fuera del hilo de la interfaz.
        hilo = threading.Thread(
            target=self._procesar_guardado,
            args=(semestre, semana),
            daemon=True,
            name="GuardarPractica",
        )
        hilo.start()

    def _procesar_guardado(
        self,
        semestre,
        semana,
    ):
        """
        Realiza el trabajo pesado de PDF, Supabase y PostgreSQL.
        """

        ruta_pdf_temporal = None
        url_pdf = None
        guardado_correcto = False

        try:
            nueva_practica = self._crear_objeto_practica(
                semestre,
                semana,
            )

            nombre_pdf = (
                "PRA-"
                + nueva_practica.fecha_creacion.strftime(
                    "%Y%m%d-%H%M%S"
                )
                + "-"
                + uuid.uuid4().hex[:8]
                + ".pdf"
            )

            carpeta_temporal = Path(
                tempfile.gettempdir()
            ) / "sistema_practicas_pdf"

            carpeta_temporal.mkdir(
                parents=True,
                exist_ok=True,
            )

            ruta_pdf_temporal = carpeta_temporal / nombre_pdf

            generar_pdf(
                nueva_practica,
                str(ruta_pdf_temporal),
            )

            if not ruta_pdf_temporal.is_file():
                raise RuntimeError(
                    "El generador no creó el archivo PDF."
                )

            url_pdf = subir_pdf(
                str(ruta_pdf_temporal)
            )

            nueva_practica.pdf_url = url_pdf

            resultado = guardar_practica(
                nueva_practica
            )

            if not resultado:
                raise RuntimeError(
                    "PostgreSQL no confirmó el registro de la práctica."
                )

            guardado_correcto = True

            # La limpieza de firmas se realiza en el hilo principal de
            # Tkinter, después de detener el polling. Esto evita que un
            # callback intente reutilizar una imagen temporal eliminada.
            self.after(
                0,
                lambda: self._guardado_exitoso(
                    url_pdf
                ),
            )

        except Exception as error:
            # Si el PDF llegó a Supabase pero PostgreSQL falló,
            # se elimina el archivo remoto para evitar documentos huérfanos.
            if url_pdf and not guardado_correcto:
                eliminar_pdf(
                    url_pdf
                )

            mensaje = str(error).strip() or error.__class__.__name__

            self.after(
                0,
                lambda detalle=mensaje: self._guardado_fallido(
                    detalle
                ),
            )

        finally:
            # El PDF local siempre es temporal y nunca debe permanecer.
            if ruta_pdf_temporal:
                try:
                    ruta = Path(
                        ruta_pdf_temporal
                    )

                    if ruta.is_file():
                        ruta.unlink()

                    carpeta = ruta.parent

                    if (
                        carpeta.is_dir()
                        and not any(carpeta.iterdir())
                    ):
                        carpeta.rmdir()

                except OSError as error:
                    print(
                        "No se pudo eliminar el PDF temporal "
                        f"{ruta_pdf_temporal}: {error}"
                    )

    def _guardado_exitoso(
        self,
        url_pdf,
    ):
        """
        Detiene el polling, elimina los temporales y notifica el éxito.
        """

        self._guardando = False
        self._polling_activo = False

        if not self.winfo_exists():
            return

        if self._after_polling is not None:
            try:
                self.after_cancel(
                    self._after_polling
                )
            except Exception:
                pass

            self._after_polling = None

        # Las firmas se eliminan solo cuando ya no existe ningún callback
        # pendiente que pueda intentar volver a mostrarlas.
        try:
            eliminar_firmas_sesion(
                self.codigo_sesion
            )
        except Exception as error:
            print(
                "No se pudieron eliminar las firmas temporales "
                f"después del guardado: {error}"
            )

        messagebox.showinfo(
            "Práctica guardada",
            (
                "La práctica se guardó correctamente.\n\n"
                "El PDF fue generado, subido a Supabase y su URL "
                "fue registrada en PostgreSQL.\n\n"
                "Los archivos temporales fueron eliminados."
            ),
            parent=self,
        )

        self._cerrar_ventana(
            confirmar=False,
            eliminar_temporales=False,
        )

    def _guardado_fallido(
        self,
        detalle,
    ):
        """
        Reactiva la interfaz cuando ocurre un error.
        """

        self._guardando = False

        if not self.winfo_exists():
            return

        self._btn_guardar.configure(
            state="normal",
            text="⬤  GUARDAR PRÁCTICA",
        )

        messagebox.showerror(
            "No se pudo guardar",
            (
                "No fue posible completar el registro de la práctica.\n\n"
                f"Detalle:\n{detalle}\n\n"
                "Las firmas de esta sesión se conservarán temporalmente "
                "para que pueda corregir el problema e intentarlo nuevamente."
            ),
            parent=self,
        )

    # ========================================================
    # CIERRE Y LIMPIEZA
    # ========================================================

    def _cerrar_ventana(
        self,
        confirmar=True,
        eliminar_temporales=True,
    ):
        """
        Cierra la ventana y elimina las firmas temporales de la sesión.
        """

        if self._cerrando:
            return

        if self._guardando:
            messagebox.showwarning(
                "Proceso en ejecución",
                (
                    "La práctica se está guardando. Espere a que el proceso "
                    "termine antes de cerrar esta ventana."
                ),
                parent=self,
            )
            return

        if confirmar:
            respuesta = messagebox.askyesno(
                "Cerrar planificación",
                (
                    "¿Desea cerrar esta ventana?\n\n"
                    "Las firmas temporales de esta sesión serán eliminadas."
                ),
                parent=self,
            )

            if not respuesta:
                return

        self._cerrando = True
        self._polling_activo = False

        if self._after_polling is not None:
            try:
                self.after_cancel(
                    self._after_polling
                )
            except Exception:
                pass

            self._after_polling = None

        if eliminar_temporales:
            try:
                eliminar_firmas_sesion(
                    self.codigo_sesion
                )
            except Exception as error:
                print(
                    "No se pudieron limpiar las firmas temporales "
                    f"de la sesión: {error}"
                )

        self.destroy()