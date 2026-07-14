import json
import os
import qrcode
import socket
import threading
import time
import uuid

import customtkinter as ctk

from customtkinter import CTkImage
from datetime import datetime
from PIL import Image
from tkinter import messagebox

from database.laboratorio.buscar_datos import (
    buscar_equipos_por_tipo,
    obtener_laboratorios_tipo,
)
from database.laboratorio.guardar_laboratorio import guardar_laboratorio
from firma.servidor_firma import app as flask_app
from models.laboratorio import Laboratorio
from pdf.generador_pdf_laboratorio import generar_pdf_laboratorio
from storage.subir_pdf_laboratorio import subir_pdf_laboratorio


# ============================================================
# Paleta
# ============================================================

BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
BG_CARD_HOV = "#243348"
ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI = "#E8EDF2"
TEXT_SEC = "#8A9BB0"
BORDER = "#2A3A50"
RED = "#E05252"


# ============================================================
# Rutas de firmas de responsables
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RUTA_FIRMA_DOCENTE_LAB = os.path.join(
    BASE_DIR,
    "firma",
    "firmas",
    "firma_docente_laboratorio.png",
)

RUTA_FIRMA_ENCARGADO_LAB = os.path.join(
    BASE_DIR,
    "firma",
    "firmas",
    "firma_encargado_laboratorio.png",
)


# ============================================================
# Componentes visuales
# ============================================================

def _label(parent, text):
    return ctk.CTkLabel(
        parent,
        text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT,
        anchor="w",
    )


def _entry(
    parent,
    placeholder="",
):
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


def _textbox(
    parent,
    height=110,
):
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


def _normalizar_hora(
    texto: str,
) -> str:
    """
    Convierte una hora a formato HH:MM.

    Ejemplos:
        8     -> 08:00
        830   -> 08:30
        0830  -> 08:30
        16:45 -> 16:45
    """

    texto = str(
        texto or ""
    ).strip()

    if not texto:
        raise ValueError(
            "La hora no puede estar vacía."
        )

    if ":" in texto:
        partes = texto.split(":")

        if len(partes) != 2:
            raise ValueError(
                f"Hora inválida: '{texto}'"
            )

        horas, minutos = partes

    else:
        if not texto.isdigit():
            raise ValueError(
                f"Hora inválida: '{texto}'"
            )

        if len(texto) <= 2:
            horas = texto
            minutos = "00"

        elif len(texto) == 3:
            horas = texto[0]
            minutos = texto[1:]

        else:
            horas = texto[:-2]
            minutos = texto[-2:]

    try:
        h = int(horas)
        m = int(minutos)

    except ValueError as error:
        raise ValueError(
            f"Hora inválida: '{texto}'"
        ) from error

    if not (
        0 <= h <= 23
        and 0 <= m <= 59
    ):
        raise ValueError(
            f"Hora fuera de rango: '{texto}'"
        )

    return f"{h:02d}:{m:02d}"


def _section_card(
    parent,
    title,
    subtitle="",
):
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
# Autocompletado
# ============================================================

class _Autocompletado:
    """
    Dropdown de sugerencias para un CTkEntry.
    """

    def __init__(
        self,
        entry,
        fn_buscar,
        on_seleccion,
        min_chars=1,
        retardo_ms=250,
    ):
        self.entry = entry
        self.fn_buscar = fn_buscar
        self.on_seleccion = on_seleccion
        self.min_chars = min_chars
        self.retardo_ms = retardo_ms

        self._toplevel = None
        self._after_id = None

        entry.bind(
            "<KeyRelease>",
            self._on_key,
        )

        entry.bind(
            "<FocusOut>",
            lambda _event: entry.after(
                150,
                self._cerrar,
            ),
        )

    def _on_key(
        self,
        event,
    ):
        if event.keysym in (
            "Up",
            "Down",
            "Return",
            "Escape",
            "Tab",
        ):
            return

        if self._after_id:
            try:
                self.entry.after_cancel(
                    self._after_id
                )
            except Exception:
                pass

        self._after_id = self.entry.after(
            self.retardo_ms,
            self._buscar,
        )

    def _buscar(self):
        if not self.entry.winfo_exists():
            return

        texto = self.entry.get().strip()

        if len(texto) < self.min_chars:
            self._cerrar()
            return

        try:
            resultados = self.fn_buscar(
                texto
            )
        except Exception:
            resultados = []

        if not resultados:
            self._cerrar()
            return

        self._mostrar(
            resultados
        )

    def _mostrar(
        self,
        resultados,
    ):
        self._cerrar()

        try:
            x = self.entry.winfo_rootx()
            y = (
                self.entry.winfo_rooty()
                + self.entry.winfo_height()
            )
            ancho = max(
                self.entry.winfo_width(),
                180,
            )
        except Exception:
            return

        self._toplevel = ctk.CTkToplevel(
            self.entry
        )

        self._toplevel.overrideredirect(
            True
        )

        alto = min(
            len(resultados),
            6,
        ) * 30

        self._toplevel.geometry(
            f"{ancho}x{alto}+{x}+{y}"
        )

        self._toplevel.configure(
            fg_color=BG_CARD
        )

        try:
            self._toplevel.attributes(
                "-topmost",
                True,
            )
        except Exception:
            pass

        for item in resultados[:6]:
            texto_item = item.get(
                "nombre",
                "",
            )

            if item.get("cantidad"):
                texto_item += (
                    f"   ({item['cantidad']})"
                )

            boton = ctk.CTkButton(
                self._toplevel,
                text=texto_item,
                anchor="w",
                fg_color=BG_CARD,
                hover_color=BG_CARD_HOV,
                text_color=TEXT_PRI,
                font=("Consolas", 12),
                corner_radius=0,
                height=30,
                command=lambda item_actual=item: self._elegir(
                    item_actual
                ),
            )
            boton.pack(
                fill="x"
            )

    def _elegir(
        self,
        item,
    ):
        self.on_seleccion(
            item
        )
        self._cerrar()

    def _cerrar(self):
        if self._toplevel is None:
            return

        try:
            self._toplevel.destroy()
        except Exception:
            pass

        self._toplevel = None


# ============================================================
# Lista de materiales y reactivos
# ============================================================

class ListaItemsConCantidad(ctk.CTkFrame):
    """
    Lista dinámica de materiales o reactivos.
    """

    def __init__(
        self,
        parent,
        fn_buscar,
        placeholder_nombre="Escribe para buscar...",
        placeholder_cantidad="Cantidad",
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )

        self._items = []
        self.fn_buscar = fn_buscar

        fila = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        fila.pack(
            fill="x"
        )

        self.entry_nombre = _entry(
            fila,
            placeholder_nombre,
        )
        self.entry_nombre.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        self.entry_nombre.bind(
            "<Return>",
            lambda _event: self._agregar(),
        )

        self.entry_cantidad = _entry(
            fila,
            placeholder_cantidad,
        )
        self.entry_cantidad.configure(
            width=120
        )
        self.entry_cantidad.pack(
            side="left",
            padx=(0, 8),
        )

        self.entry_cantidad.bind(
            "<Return>",
            lambda _event: self._agregar(),
        )

        ctk.CTkButton(
            fila,
            text="+  Agregar",
            width=100,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 13, "bold"),
            corner_radius=6,
            command=self._agregar,
        ).pack(
            side="left"
        )

        self._autocomplete = _Autocompletado(
            self.entry_nombre,
            self._buscar_wrapper,
            self._al_elegir_sugerencia,
        )

        self._contenedor_lista = ctk.CTkFrame(
            self,
            fg_color=BG_DARK,
            corner_radius=6,
            border_width=1,
            border_color=BORDER,
        )
        self._contenedor_lista.pack(
            fill="x",
            pady=(10, 0),
        )

        self._refrescar()

    def _buscar_wrapper(
        self,
        texto,
    ):
        return self.fn_buscar(
            texto
        )

    def _al_elegir_sugerencia(
        self,
        item,
    ):
        self.entry_nombre.delete(
            0,
            "end",
        )

        self.entry_nombre.insert(
            0,
            item.get(
                "nombre",
                "",
            ),
        )

        cantidad = item.get(
            "cantidad"
        )

        if (
            cantidad not in (
                None,
                "",
            )
            and not self.entry_cantidad.get().strip()
        ):
            self.entry_cantidad.delete(
                0,
                "end",
            )

            self.entry_cantidad.insert(
                0,
                str(cantidad),
            )

        self.entry_cantidad.focus_set()

    def _agregar(self):
        nombre = self.entry_nombre.get().strip()
        cantidad = self.entry_cantidad.get().strip()

        if not nombre:
            return

        self._items.append(
            {
                "nombre": nombre,
                "cantidad": cantidad or None,
            }
        )

        self.entry_nombre.delete(
            0,
            "end",
        )

        self.entry_cantidad.delete(
            0,
            "end",
        )

        self.entry_nombre.focus_set()

        self._refrescar()

    def _quitar(
        self,
        index,
    ):
        if 0 <= index < len(self._items):
            del self._items[index]

        self._refrescar()

    def _refrescar(self):
        for widget in self._contenedor_lista.winfo_children():
            widget.destroy()

        if not self._items:
            ctk.CTkLabel(
                self._contenedor_lista,
                text="Aún no se han agregado ítems.",
                text_color=TEXT_SEC,
                font=("Consolas", 11),
            ).pack(
                pady=10
            )
            return

        for indice, item in enumerate(
            self._items
        ):
            fila = ctk.CTkFrame(
                self._contenedor_lista,
                fg_color="transparent",
            )
            fila.pack(
                fill="x",
                padx=10,
                pady=4,
            )

            texto = item.get(
                "nombre",
                "",
            )

            if item.get("cantidad"):
                texto += (
                    f"   —   {item['cantidad']}"
                )

            ctk.CTkLabel(
                fila,
                text=texto,
                text_color=TEXT_PRI,
                font=("Consolas", 12),
                anchor="w",
            ).pack(
                side="left",
                fill="x",
                expand=True,
            )

            ctk.CTkButton(
                fila,
                text="✕",
                width=28,
                height=28,
                fg_color="transparent",
                hover_color="#3A2430",
                text_color="#D96C6C",
                font=("Consolas", 12, "bold"),
                corner_radius=6,
                command=lambda indice_actual=indice: self._quitar(
                    indice_actual
                ),
            ).pack(
                side="right"
            )

    def obtener_items(self):
        return list(
            self._items
        )


# ============================================================
# Ventana principal
# ============================================================

class VentanaNuevoLaboratorio(ctk.CTkToplevel):

    def __init__(
        self,
        master,
    ):
        super().__init__(
            master
        )

        self.title(
            "Registro de Laboratorio"
        )

        self.geometry(
            "1300x950"
        )

        self.minsize(
            1100,
            760,
        )

        self.configure(
            fg_color=BG_DARK
        )

        # Código de sesión para estudiantes.
        self._codigo_sesion = (
            f"LAB-{uuid.uuid4().hex[:10]}"
        )

        # Estado servidor Flask.
        self._servidor_iniciado = False

        # Polling independiente.
        self._polling_estudiantes_activo = False
        self._polling_responsables_activo = False

        # Referencias de imágenes CTkImage.
        self._img_refs = {}

        # Firmas de estudiantes.
        self._estudiantes_firmados = []

        # Datos del encargado seleccionado.
        self._encargado_actual = ""
        self._cargo_encargado_actual = ""

        # Eliminar firmas responsables anteriores.
        for ruta_firma in (
            RUTA_FIRMA_DOCENTE_LAB,
            RUTA_FIRMA_ENCARGADO_LAB,
        ):
            try:
                if os.path.isfile(
                    ruta_firma
                ):
                    os.remove(
                        ruta_firma
                    )
            except Exception as error:
                print(
                    "No se pudo limpiar una firma anterior:",
                    error,
                )

        # Catálogo de laboratorios.
        self._labs_tipo = obtener_laboratorios_tipo()

        self._labs_tipo_por_nombre = {
            laboratorio["nombre"]: laboratorio
            for laboratorio in self._labs_tipo
        }

        self._laboratorio_tipo_id_actual = None

        # ── Encabezado ────────────────────────────────────────────────
        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=72,
        )
        header.pack(
            fill="x"
        )
        header.pack_propagate(
            False
        )

        ctk.CTkLabel(
            header,
            text="REGISTRO DE PRÁCTICA DE LABORATORIO",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_PRI,
        ).pack(
            side="left",
            padx=24,
        )

        self._lbl_fecha = ctk.CTkLabel(
            header,
            text=datetime.now().strftime(
                "%d/%m/%Y  %H:%M"
            ),
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        )
        self._lbl_fecha.pack(
            side="right",
            padx=24,
        )

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(
            fill="x"
        )

        # ── Contenedor desplazable ────────────────────────────────────
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

        self.crear_campos()

    # ================================================================
    # Construcción de campos
    # ================================================================

    def crear_campos(self):
        # ══ SECCIÓN 1 — DATOS INFORMATIVOS ═══════════════════════════
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

        c1 = ctk.CTkFrame(
            row1,
            fg_color="transparent",
        )
        c1.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            c1,
            "Laboratorio",
        ).pack(
            anchor="w"
        )

        nombres_tipo = [
            laboratorio["nombre"]
            for laboratorio in self._labs_tipo
        ]

        self.laboratorio = ctk.CTkComboBox(
            c1,
            values=nombres_tipo,
            fg_color=BG_DARK,
            border_color=BORDER,
            border_width=1,
            button_color=BG_CARD,
            button_hover_color=BG_CARD_HOV,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRI,
            text_color=TEXT_PRI,
            font=("Consolas", 13),
            corner_radius=6,
            height=38,
            command=self._on_laboratorio_seleccionado,
        )
        self.laboratorio.pack(
            fill="x",
            pady=5,
        )

        self.laboratorio.bind(
            "<KeyRelease>",
            self._on_laboratorio_escrito,
        )

        c2 = ctk.CTkFrame(
            row1,
            fg_color="transparent",
        )
        c2.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            c2,
            "Número de estudiantes",
        ).pack(
            anchor="w"
        )

        self.numero_estudiantes = _entry(
            c2,
            "Ej: 25",
        )
        self.numero_estudiantes.pack(
            fill="x",
            pady=5,
        )

        # Encargado automático.
        responsable_frame = ctk.CTkFrame(
            s1,
            fg_color=BG_DARK,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
        )
        responsable_frame.pack(
            fill="x",
            pady=(8, 4),
        )

        ctk.CTkLabel(
            responsable_frame,
            text="ENCARGADO DEL LABORATORIO",
            font=("Consolas", 10, "bold"),
            text_color=ACCENT,
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 2),
        )

        self._lbl_encargado = ctk.CTkLabel(
            responsable_frame,
            text="Seleccione un laboratorio.",
            font=("Consolas", 12, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
        )
        self._lbl_encargado.pack(
            anchor="w",
            padx=12,
        )

        self._lbl_cargo_encargado = ctk.CTkLabel(
            responsable_frame,
            text="Cargo no disponible.",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        )
        self._lbl_cargo_encargado.pack(
            anchor="w",
            padx=12,
            pady=(2, 10),
        )

        # Selección inicial.
        if nombres_tipo:
            self.laboratorio.set(
                nombres_tipo[0]
            )
            self._actualizar_datos_laboratorio(
                nombres_tipo[0]
            )
        else:
            self.laboratorio.set("")

        row2 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row2.pack(
            fill="x",
            pady=(6, 0),
        )

        c3 = ctk.CTkFrame(
            row2,
            fg_color="transparent",
        )
        c3.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            c3,
            "Asignatura",
        ).pack(
            anchor="w"
        )

        self.asignatura = _entry(
            c3
        )
        self.asignatura.pack(
            fill="x",
            pady=5,
        )

        c4 = ctk.CTkFrame(
            row2,
            fg_color="transparent",
        )
        c4.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            c4,
            "Unidad académica",
        ).pack(
            anchor="w"
        )

        self.unidad_academica = _entry(
            c4
        )
        self.unidad_academica.pack(
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

        c5 = ctk.CTkFrame(
            row3,
            fg_color="transparent",
        )
        c5.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            c5,
            "Semestre",
        ).pack(
            anchor="w"
        )

        self.semestre = _entry(
            c5,
            "Ej: 3",
        )
        self.semestre.pack(
            fill="x",
            pady=5,
        )

        c6 = ctk.CTkFrame(
            row3,
            fg_color="transparent",
        )
        c6.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            c6,
            "Carrera",
        ).pack(
            anchor="w"
        )

        self.carrera = _entry(
            c6
        )
        self.carrera.pack(
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

        c7 = ctk.CTkFrame(
            row4,
            fg_color="transparent",
        )
        c7.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            c7,
            "Hora entrada",
        ).pack(
            anchor="w"
        )

        self.hora_entrada = _entry(
            c7,
            "Ej: 0830 u 8:30",
        )
        self.hora_entrada.pack(
            fill="x",
            pady=5,
        )

        c8 = ctk.CTkFrame(
            row4,
            fg_color="transparent",
        )
        c8.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            c8,
            "Hora salida",
        ).pack(
            anchor="w"
        )

        self.hora_salida = _entry(
            c8,
            "Ej: 1645 o 16:45",
        )
        self.hora_salida.pack(
            fill="x",
            pady=5,
        )

        row5 = ctk.CTkFrame(
            s1,
            fg_color="transparent",
        )
        row5.pack(
            fill="x",
            pady=(6, 0),
        )

        c9 = ctk.CTkFrame(
            row5,
            fg_color="transparent",
        )
        c9.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            c9,
            "Institución",
        ).pack(
            anchor="w"
        )

        self.institucion = _entry(
            c9
        )
        self.institucion.pack(
            fill="x",
            pady=5,
        )

        c10 = ctk.CTkFrame(
            row5,
            fg_color="transparent",
        )
        c10.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            c10,
            "Ciudad",
        ).pack(
            anchor="w"
        )

        self.ciudad = _entry(
            c10
        )
        self.ciudad.pack(
            fill="x",
            pady=5,
        )

        _label(
            s1,
            "Docente responsable",
        ).pack(
            anchor="w",
            pady=(6, 0),
        )

        self.docente = _entry(
            s1,
            "Nombre completo del docente",
        )
        self.docente.pack(
            fill="x",
            pady=5,
        )

        # ══ SECCIÓN 2 — DATOS ACADÉMICOS ═════════════════════════════
        s2 = _section_card(
            self.scroll,
            "2.  DATOS ACADÉMICOS",
        )

        _label(
            s2,
            "Tema de la práctica",
        ).pack(
            anchor="w"
        )

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
            "Subtema",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.subtema = _textbox(
            s2,
            height=70,
        )
        self.subtema.pack(
            fill="x",
            pady=5,
        )

        _label(
            s2,
            "Logro de aprendizaje",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.logro = _textbox(
            s2,
            height=90,
        )
        self.logro.pack(
            fill="x",
            pady=5,
        )

        # ══ SECCIÓN 3 — PLANIFICACIÓN ════════════════════════════════
        s3 = _section_card(
            self.scroll,
            "3.  PLANIFICACIÓN",
        )

        _label(
            s3,
            "Objetivos",
        ).pack(
            anchor="w"
        )

        self.objetivos = _textbox(
            s3,
            height=100,
        )
        self.objetivos.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "Metodología",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.metodologia = _textbox(
            s3,
            height=100,
        )
        self.metodologia.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "Resultados",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.resultados = _textbox(
            s3,
            height=100,
        )
        self.resultados.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "Conclusiones",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.conclusiones = _textbox(
            s3,
            height=100,
        )
        self.conclusiones.pack(
            fill="x",
            pady=5,
        )

        _label(
            s3,
            "Observaciones",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.observaciones = _textbox(
            s3,
            height=100,
        )
        self.observaciones.pack(
            fill="x",
            pady=5,
        )

        # ══ SECCIÓN 4 — MATERIALES Y REACTIVOS ═══════════════════════
        s4 = _section_card(
            self.scroll,
            "4.  MATERIALES Y REACTIVOS",
            (
                "Escribe para ver sugerencias del catálogo del "
                "laboratorio seleccionado."
            ),
        )

        _label(
            s4,
            "Materiales",
        ).pack(
            anchor="w"
        )

        self.widget_materiales = ListaItemsConCantidad(
            s4,
            fn_buscar=lambda texto: buscar_equipos_por_tipo(
                self._laboratorio_tipo_id_actual,
                texto,
            ),
            placeholder_nombre="Ej: Matraz Erlenmeyer",
            placeholder_cantidad="Cantidad",
        )
        self.widget_materiales.pack(
            fill="x",
            pady=(5, 14),
        )

        _label(
            s4,
            "Reactivos",
        ).pack(
            anchor="w",
            pady=(4, 0),
        )

        self.widget_reactivos = ListaItemsConCantidad(
            s4,
            fn_buscar=lambda texto: buscar_equipos_por_tipo(
                self._laboratorio_tipo_id_actual,
                texto,
            ),
            placeholder_nombre="Ej: Ácido clorhídrico",
            placeholder_cantidad="Ej: 250 ml",
        )
        self.widget_reactivos.pack(
            fill="x",
            pady=5,
        )

        # ══ SECCIÓN 5 — FIRMAS DE ESTUDIANTES ════════════════════════
        s5 = _section_card(
            self.scroll,
            "5.  FIRMAS DE ESTUDIANTES",
            (
                "Cada estudiante escanea el QR, ingresa nombre, "
                "cédula y firma desde su teléfono."
            ),
        )

        self._btn_qr_est = ctk.CTkButton(
            s5,
            text="⬤  Generar QR para estudiantes",
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            text_color=ACCENT,
            font=("Consolas", 13, "bold"),
            corner_radius=8,
            height=42,
            border_width=1,
            border_color=ACCENT,
            command=self._iniciar_servidor_estudiantes,
        )
        self._btn_qr_est.pack(
            fill="x",
            pady=(0, 14),
        )

        contenedor_estudiantes = ctk.CTkFrame(
            s5,
            fg_color="transparent",
        )
        contenedor_estudiantes.pack(
            fill="x"
        )

        col_qr_est = ctk.CTkFrame(
            contenedor_estudiantes,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_qr_est.pack(
            side="left",
            padx=(0, 8),
            pady=4,
        )

        ctk.CTkLabel(
            col_qr_est,
            text="ESCANEA PARA FIRMAR",
            font=("Consolas", 10, "bold"),
            text_color=ACCENT,
        ).pack(
            pady=(12, 6),
            padx=20,
        )

        self._lbl_qr_est = ctk.CTkLabel(
            col_qr_est,
            text=(
                "Presiona el botón\n"
                "para generar el QR"
            ),
            text_color=TEXT_SEC,
            font=("Consolas", 10),
        )
        self._lbl_qr_est.pack(
            padx=20,
            pady=(0, 14),
        )

        col_lista = ctk.CTkFrame(
            contenedor_estudiantes,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_lista.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
            pady=4,
        )

        self._lbl_contador = ctk.CTkLabel(
            col_lista,
            text="0 / —  estudiantes firmados",
            font=("Consolas", 13, "bold"),
            text_color=ACCENT,
        )
        self._lbl_contador.pack(
            pady=(14, 4),
            padx=14,
            anchor="w",
        )

        self._barra_progreso = ctk.CTkProgressBar(
            col_lista,
            progress_color=ACCENT,
            fg_color=BG_PANEL,
            height=8,
        )
        self._barra_progreso.set(
            0
        )
        self._barra_progreso.pack(
            fill="x",
            padx=14,
            pady=(0, 10),
        )

        self._lista_estudiantes = ctk.CTkTextbox(
            col_lista,
            height=140,
            fg_color=BG_PANEL,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
        )
        self._lista_estudiantes.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14),
        )

        self._lista_estudiantes.insert(
            "1.0",
            "Aún no hay firmas registradas.",
        )

        self._lista_estudiantes.configure(
            state="disabled"
        )

        # ══ SECCIÓN 6 — FIRMAS DE RESPONSABLES ═══════════════════════
        s6 = _section_card(
            self.scroll,
            "6.  FIRMAS DE RESPONSABLES",
            (
                "Genera los códigos QR para que el docente responsable "
                "y el encargado del laboratorio firmen desde su teléfono."
            ),
        )

        self._btn_qr_responsables = ctk.CTkButton(
            s6,
            text="⬤  Generar QR de responsables",
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            text_color=ACCENT,
            font=("Consolas", 13, "bold"),
            corner_radius=8,
            height=42,
            border_width=1,
            border_color=ACCENT,
            command=self._iniciar_firmas_responsables,
        )
        self._btn_qr_responsables.pack(
            fill="x",
            pady=(0, 14),
        )

        qr_responsables = ctk.CTkFrame(
            s6,
            fg_color="transparent",
        )
        qr_responsables.pack(
            fill="x"
        )

        # Docente
        col_docente = ctk.CTkFrame(
            qr_responsables,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_docente.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8),
            pady=4,
        )

        ctk.CTkLabel(
            col_docente,
            text="👤  DOCENTE RESPONSABLE",
            font=("Consolas", 11, "bold"),
            text_color=ACCENT,
        ).pack(
            pady=(12, 3),
        )

        self._lbl_nombre_docente_firma = ctk.CTkLabel(
            col_docente,
            text="Ingrese el nombre del docente.",
            font=("Consolas", 10),
            text_color=TEXT_PRI,
        )
        self._lbl_nombre_docente_firma.pack(
            pady=(0, 5),
        )

        self._lbl_qr_docente_lab = ctk.CTkLabel(
            col_docente,
            text="Presiona «Generar QR»",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
        )
        self._lbl_qr_docente_lab.pack(
            pady=(0, 6),
        )

        self._lbl_estado_docente_lab = ctk.CTkLabel(
            col_docente,
            text="⏳  Pendiente de firma",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
        )
        self._lbl_estado_docente_lab.pack()

        self._lbl_preview_docente_lab = ctk.CTkLabel(
            col_docente,
            text="",
        )
        self._lbl_preview_docente_lab.pack(
            pady=(5, 12),
        )

        # Encargado
        col_encargado = ctk.CTkFrame(
            qr_responsables,
            fg_color=BG_DARK,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        col_encargado.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
            pady=4,
        )

        ctk.CTkLabel(
            col_encargado,
            text="🔬  ENCARGADO DEL LABORATORIO",
            font=("Consolas", 11, "bold"),
            text_color=ACCENT,
        ).pack(
            pady=(12, 3),
        )

        self._lbl_nombre_encargado_firma = ctk.CTkLabel(
            col_encargado,
            text="Seleccione un laboratorio.",
            font=("Consolas", 10, "bold"),
            text_color=TEXT_PRI,
        )
        self._lbl_nombre_encargado_firma.pack()

        self._lbl_cargo_encargado_firma = ctk.CTkLabel(
            col_encargado,
            text="Cargo no disponible.",
            font=("Consolas", 9),
            text_color=TEXT_SEC,
        )
        self._lbl_cargo_encargado_firma.pack(
            pady=(2, 5),
        )

        # Sincronizar los datos cargados al inicio con los widgets
        # de la sección de firmas, que recién ahora existen.
        self._lbl_nombre_encargado_firma.configure(
            text=(
                self._encargado_actual
                or "Encargado no registrado."
            )
        )
        self._lbl_cargo_encargado_firma.configure(
            text=(
                self._cargo_encargado_actual
                or "Cargo no registrado."
            )
        )

        self._lbl_qr_encargado_lab = ctk.CTkLabel(
            col_encargado,
            text="Presiona «Generar QR»",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
        )
        self._lbl_qr_encargado_lab.pack(
            pady=(0, 6),
        )

        self._lbl_estado_encargado_lab = ctk.CTkLabel(
            col_encargado,
            text="⏳  Pendiente de firma",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
        )
        self._lbl_estado_encargado_lab.pack()

        self._lbl_preview_encargado_lab = ctk.CTkLabel(
            col_encargado,
            text="",
        )
        self._lbl_preview_encargado_lab.pack(
            pady=(5, 12),
        )

        # Actualizar nombre docente en tiempo real.
        self.docente.bind(
            "<KeyRelease>",
            self._actualizar_nombre_docente_firma,
        )

        # ══ SECCIÓN 7 — LISTA MANUAL ═════════════════════════════════
        s7 = _section_card(
            self.scroll,
            "7.  ESTUDIANTES (LISTA MANUAL, OPCIONAL)",
            (
                "Si no se utiliza el QR, puede ingresar un estudiante "
                "por línea."
            ),
        )

        _label(
            s7,
            "Estudiantes",
        ).pack(
            anchor="w"
        )

        self.estudiantes = _textbox(
            s7,
            height=200,
        )
        self.estudiantes.pack(
            fill="x",
            pady=5,
        )

        # ══ BOTÓN GUARDAR ════════════════════════════════════════════
        ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR REGISTRO",
            command=self.guardar,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=48,
        ).pack(
            pady=24,
            fill="x",
        )

    # ================================================================
    # Laboratorio y encargado
    # ================================================================

    def _actualizar_datos_laboratorio(
        self,
        nombre_laboratorio,
    ):
        datos = self._labs_tipo_por_nombre.get(
            nombre_laboratorio
        )

        if not datos:
            self._laboratorio_tipo_id_actual = None
            self._encargado_actual = ""
            self._cargo_encargado_actual = ""

            self._lbl_encargado.configure(
                text="Encargado no registrado."
            )

            self._lbl_cargo_encargado.configure(
                text="Cargo no registrado."
            )

            # Estos widgets se crean más adelante, en la sección 6.
            if hasattr(self, "_lbl_nombre_encargado_firma"):
                self._lbl_nombre_encargado_firma.configure(
                    text="Encargado no registrado."
                )

            if hasattr(self, "_lbl_cargo_encargado_firma"):
                self._lbl_cargo_encargado_firma.configure(
                    text="Cargo no registrado."
                )

            return

        self._laboratorio_tipo_id_actual = datos.get(
            "id"
        )

        self._encargado_actual = str(
            datos.get(
                "encargado"
            )
            or ""
        ).strip()

        self._cargo_encargado_actual = str(
            datos.get(
                "cargo"
            )
            or ""
        ).strip()

        nombre_visible = (
            self._encargado_actual
            or "Encargado no registrado."
        )

        cargo_visible = (
            self._cargo_encargado_actual
            or "Cargo no registrado."
        )

        self._lbl_encargado.configure(
            text=nombre_visible
        )

        self._lbl_cargo_encargado.configure(
            text=cargo_visible
        )

        # Estos widgets se crean más adelante, en la sección 6.
        # Durante la carga inicial todavía pueden no existir.
        if hasattr(self, "_lbl_nombre_encargado_firma"):
            self._lbl_nombre_encargado_firma.configure(
                text=nombre_visible
            )

        if hasattr(self, "_lbl_cargo_encargado_firma"):
            self._lbl_cargo_encargado_firma.configure(
                text=cargo_visible
            )

    def _on_laboratorio_seleccionado(
        self,
        valor,
    ):
        self._actualizar_datos_laboratorio(
            valor
        )

    def _on_laboratorio_escrito(
        self,
        _event,
    ):
        valor = self.laboratorio.get().strip()

        self._actualizar_datos_laboratorio(
            valor
        )

    def _actualizar_nombre_docente_firma(
        self,
        _event=None,
    ):
        nombre = self.docente.get().strip()

        self._lbl_nombre_docente_firma.configure(
            text=(
                nombre
                or "Ingrese el nombre del docente."
            )
        )

    # ================================================================
    # Servidor Flask
    # ================================================================

    def _asegurar_servidor(self):
        if self._servidor_iniciado:
            return

        hilo = threading.Thread(
            target=lambda: flask_app.run(
                host="0.0.0.0",
                port=5000,
                debug=False,
                use_reloader=False,
            ),
            daemon=True,
        )

        hilo.start()

        self._servidor_iniciado = True

        time.sleep(
            0.9
        )

    @staticmethod
    def _obtener_ip_red():
        try:
            socket_red = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
            )

            socket_red.connect(
                (
                    "8.8.8.8",
                    80,
                )
            )

            ip = socket_red.getsockname()[0]

            socket_red.close()

            return ip

        except Exception:
            return socket.gethostbyname(
                socket.gethostname()
            )

    # ================================================================
    # QR estudiantes
    # ================================================================

    def _iniciar_servidor_estudiantes(self):
        self._asegurar_servidor()

        self._generar_qr_estudiantes()

        if not self._polling_estudiantes_activo:
            self._polling_estudiantes_activo = True
            self._polling_estudiantes()

        self._btn_qr_est.configure(
            text="↺  Regenerar QR"
        )

    def _generar_qr_estudiantes(self):
        ip = self._obtener_ip_red()

        url = (
            f"http://{ip}:5000/"
            f"firma/estudiante/{self._codigo_sesion}"
        )

        qr_img = qrcode.make(
            url
        ).resize(
            (
                190,
                190,
            )
        ).convert(
            "RGB"
        )

        photo = CTkImage(
            light_image=qr_img,
            dark_image=qr_img,
            size=(
                190,
                190,
            ),
        )

        self._img_refs[
            "qr_estudiantes"
        ] = photo

        self._lbl_qr_est.configure(
            image=photo,
            text="",
        )

    def _limite_estudiantes(self):
        try:
            cantidad = int(
                self.numero_estudiantes.get().strip()
            )

            return (
                cantidad
                if cantidad > 0
                else None
            )

        except ValueError:
            return None

    def _polling_estudiantes(self):
        if not self.winfo_exists():
            return

        ruta_sesion = os.path.join(
            BASE_DIR,
            "firma",
            "sesiones",
            f"{self._codigo_sesion}.json",
        )

        try:
            with open(
                ruta_sesion,
                "r",
                encoding="utf-8",
            ) as archivo:
                datos = json.load(
                    archivo
                )

            self._estudiantes_firmados = datos.get(
                "estudiantes",
                [],
            )

        except (
            FileNotFoundError,
            json.JSONDecodeError,
        ):
            pass

        total = len(
            self._estudiantes_firmados
        )

        limite = self._limite_estudiantes()

        if limite:
            self._lbl_contador.configure(
                text=(
                    f"{total} / {limite} "
                    "estudiantes firmados"
                )
            )

            self._barra_progreso.set(
                min(
                    total / limite,
                    1.0,
                )
            )

        else:
            self._lbl_contador.configure(
                text=f"{total} estudiantes firmados"
            )

            self._barra_progreso.set(
                0
            )

        self._lista_estudiantes.configure(
            state="normal"
        )

        self._lista_estudiantes.delete(
            "1.0",
            "end",
        )

        if total == 0:
            self._lista_estudiantes.insert(
                "1.0",
                "Aún no hay firmas registradas.",
            )

        else:
            texto = "\n".join(
                (
                    f"{indice + 1}. "
                    f"{estudiante.get('nombre', '')}"
                    f" — {estudiante.get('cedula', '')}"
                    + (
                        f" ({estudiante.get('hora')})"
                        if estudiante.get("hora")
                        else ""
                    )
                )
                for indice, estudiante in enumerate(
                    self._estudiantes_firmados
                )
            )

            self._lista_estudiantes.insert(
                "1.0",
                texto,
            )

        self._lista_estudiantes.configure(
            state="disabled"
        )

        if (
            limite
            and total >= limite
        ):
            self._lbl_contador.configure(
                text=(
                    f"✔ {total} / {limite} "
                    "¡Completo!"
                )
            )

            self._polling_estudiantes_activo = False
            return

        self.after(
            2500,
            self._polling_estudiantes,
        )

    # ================================================================
    # QR responsables
    # ================================================================

    def _iniciar_firmas_responsables(self):
        if not self.docente.get().strip():
            messagebox.showwarning(
                "Docente pendiente",
                (
                    "Ingrese el nombre del docente responsable "
                    "antes de generar los códigos QR."
                ),
                parent=self,
            )
            return

        if not self._encargado_actual:
            messagebox.showwarning(
                "Encargado pendiente",
                (
                    "El laboratorio seleccionado no tiene un "
                    "encargado configurado en la base de datos."
                ),
                parent=self,
            )
            return

        self._asegurar_servidor()

        self._generar_qrs_responsables()

        if not self._polling_responsables_activo:
            self._polling_responsables_activo = True
            self._polling_firmas_responsables()

        self._btn_qr_responsables.configure(
            text="↺  Regenerar QR de responsables"
        )

    def _generar_qrs_responsables(self):
        ip = self._obtener_ip_red()

        configuraciones = (
            (
                "docente_laboratorio",
                self._lbl_qr_docente_lab,
            ),
            (
                "encargado_laboratorio",
                self._lbl_qr_encargado_lab,
            ),
        )

        for rol, label_qr in configuraciones:
            url = (
                f"http://{ip}:5000/firma/{rol}"
            )

            imagen_qr = qrcode.make(
                url
            ).resize(
                (
                    170,
                    170,
                )
            ).convert(
                "RGB"
            )

            photo = CTkImage(
                light_image=imagen_qr,
                dark_image=imagen_qr,
                size=(
                    170,
                    170,
                ),
            )

            self._img_refs[
                f"qr_{rol}"
            ] = photo

            label_qr.configure(
                image=photo,
                text="",
            )

    def _polling_firmas_responsables(self):
        if not self.winfo_exists():
            return

        # Docente
        if os.path.isfile(
            RUTA_FIRMA_DOCENTE_LAB
        ):
            self._lbl_estado_docente_lab.configure(
                text="✔  Firmado",
                text_color=ACCENT,
            )

            self._mostrar_preview_firma(
                RUTA_FIRMA_DOCENTE_LAB,
                self._lbl_preview_docente_lab,
                "preview_docente_laboratorio",
            )

        else:
            self._lbl_estado_docente_lab.configure(
                text="⏳  Pendiente de firma",
                text_color=TEXT_SEC,
            )

        # Encargado
        if os.path.isfile(
            RUTA_FIRMA_ENCARGADO_LAB
        ):
            self._lbl_estado_encargado_lab.configure(
                text="✔  Firmado",
                text_color=ACCENT,
            )

            self._mostrar_preview_firma(
                RUTA_FIRMA_ENCARGADO_LAB,
                self._lbl_preview_encargado_lab,
                "preview_encargado_laboratorio",
            )

        else:
            self._lbl_estado_encargado_lab.configure(
                text="⏳  Pendiente de firma",
                text_color=TEXT_SEC,
            )

        self.after(
            2000,
            self._polling_firmas_responsables,
        )

    def _mostrar_preview_firma(
        self,
        ruta,
        label,
        key,
    ):
        if key in self._img_refs:
            return

        try:
            imagen = Image.open(
                ruta
            ).convert(
                "RGBA"
            )

            fondo = Image.new(
                "RGBA",
                imagen.size,
                (
                    255,
                    255,
                    255,
                    255,
                ),
            )

            if "A" in imagen.getbands():
                fondo.paste(
                    imagen,
                    mask=imagen.getchannel(
                        "A"
                    ),
                )
            else:
                fondo.paste(
                    imagen
                )

            fondo = fondo.convert(
                "RGB"
            )

            fondo.thumbnail(
                (
                    200,
                    80,
                )
            )

            photo = CTkImage(
                light_image=fondo,
                dark_image=fondo,
                size=(
                    200,
                    80,
                ),
            )

            self._img_refs[
                key
            ] = photo

            label.configure(
                image=photo,
                text="",
            )

        except Exception as error:
            print(
                "No se pudo mostrar la firma:",
                error,
            )

    # ================================================================
    # Guardar
    # ================================================================

    def guardar(self):
        try:
            codigo = datetime.now().strftime(
                "LAB-%Y%m%d%H%M%S%f"
            )

            try:
                numero_estudiantes = int(
                    self.numero_estudiantes.get().strip()
                )

                semestre = int(
                    self.semestre.get().strip()
                )

                hora_entrada_norm = _normalizar_hora(
                    self.hora_entrada.get()
                )

                hora_salida_norm = _normalizar_hora(
                    self.hora_salida.get()
                )

            except ValueError as error:
                messagebox.showerror(
                    "Datos inválidos",
                    (
                        "Revise el semestre, el número de "
                        "estudiantes y las horas.\n\n"
                        f"{error}"
                    ),
                    parent=self,
                )
                return

            if numero_estudiantes <= 0:
                messagebox.showerror(
                    "Error",
                    (
                        "El número de estudiantes debe "
                        "ser mayor que cero."
                    ),
                    parent=self,
                )
                return

            if semestre <= 0:
                messagebox.showerror(
                    "Error",
                    "El semestre debe ser mayor que cero.",
                    parent=self,
                )
                return

            if hora_entrada_norm >= hora_salida_norm:
                messagebox.showerror(
                    "Horario inválido",
                    (
                        "La hora de salida debe ser posterior "
                        "a la hora de entrada."
                    ),
                    parent=self,
                )
                return

            nombre_laboratorio = self.laboratorio.get().strip()
            nombre_docente = self.docente.get().strip()

            if not nombre_laboratorio:
                messagebox.showerror(
                    "Error",
                    (
                        "Debe seleccionar o escribir "
                        "un laboratorio."
                    ),
                    parent=self,
                )
                return

            if not self.asignatura.get().strip():
                messagebox.showerror(
                    "Error",
                    "Debe ingresar la asignatura.",
                    parent=self,
                )
                return

            if not nombre_docente:
                messagebox.showerror(
                    "Error",
                    (
                        "Debe ingresar el docente "
                        "responsable."
                    ),
                    parent=self,
                )
                return

            if not self._encargado_actual:
                messagebox.showerror(
                    "Encargado no configurado",
                    (
                        "El laboratorio seleccionado no tiene "
                        "un encargado registrado en Supabase."
                    ),
                    parent=self,
                )
                return

            if not self._cargo_encargado_actual:
                messagebox.showerror(
                    "Cargo no configurado",
                    (
                        "El encargado del laboratorio no tiene "
                        "un cargo registrado."
                    ),
                    parent=self,
                )
                return

            materiales_lista = (
                self.widget_materiales.obtener_items()
            )

            reactivos_lista = (
                self.widget_reactivos.obtener_items()
            )

            estudiantes_lista = [
                {
                    "nombre": estudiante.get(
                        "nombre"
                    ),
                    "cedula": estudiante.get(
                        "cedula"
                    ),
                    "firma_ruta": estudiante.get(
                        "firma_ruta"
                    ),
                }
                for estudiante in self._estudiantes_firmados
            ]

            for linea in self.estudiantes.get(
                "1.0",
                "end",
            ).splitlines():
                linea = linea.strip()

                if linea:
                    estudiantes_lista.append(
                        {
                            "nombre": linea,
                            "cedula": None,
                            "firma_ruta": None,
                        }
                    )

            laboratorio = Laboratorio(
                codigo,
                nombre_laboratorio,
                numero_estudiantes,
                self.asignatura.get().strip(),
                self.unidad_academica.get().strip(),
                semestre,
                self.carrera.get().strip(),
                hora_entrada_norm,
                hora_salida_norm,
                self.institucion.get().strip(),
                self.ciudad.get().strip(),
                nombre_docente,
                datetime.now().strftime(
                    "%Y-%m-%d"
                ),
                self.tema.get(
                    "1.0",
                    "end",
                ).strip(),
                self.subtema.get(
                    "1.0",
                    "end",
                ).strip(),
                self.logro.get(
                    "1.0",
                    "end",
                ).strip(),
                self.objetivos.get(
                    "1.0",
                    "end",
                ).strip(),
                self.metodologia.get(
                    "1.0",
                    "end",
                ).strip(),
                self.resultados.get(
                    "1.0",
                    "end",
                ).strip(),
                self.conclusiones.get(
                    "1.0",
                    "end",
                ).strip(),
                self.observaciones.get(
                    "1.0",
                    "end",
                ).strip(),
                materiales=materiales_lista,
                reactivos=reactivos_lista,
                estudiantes=estudiantes_lista,
                encargado_laboratorio=self._encargado_actual,
                cargo_encargado=self._cargo_encargado_actual,
                firma_encargado_ruta=(
                    RUTA_FIRMA_ENCARGADO_LAB
                    if os.path.isfile(
                        RUTA_FIRMA_ENCARGADO_LAB
                    )
                    else None
                ),
                firma_docente_ruta=(
                    RUTA_FIRMA_DOCENTE_LAB
                    if os.path.isfile(
                        RUTA_FIRMA_DOCENTE_LAB
                    )
                    else None
                ),
                codigo_sesion=self._codigo_sesion,
            )

            # Generar PDF local.
            ruta_pdf = generar_pdf_laboratorio(
                laboratorio
            )

            # Subir PDF a Supabase.
            pdf_url = subir_pdf_laboratorio(
                ruta_pdf
            )

            laboratorio.pdf_url = pdf_url

            # Guardar en PostgreSQL.
            resultado = guardar_laboratorio(
                laboratorio
            )

            if resultado:
                messagebox.showinfo(
                    "Correcto",
                    (
                        "Registro guardado correctamente.\n\n"
                        "El PDF fue generado y subido "
                        "a Supabase."
                    ),
                    parent=self,
                )

                self.destroy()

            else:
                messagebox.showerror(
                    "Error",
                    (
                        "No fue posible guardar el registro "
                        "en PostgreSQL."
                    ),
                    parent=self,
                )

        except Exception as error:
            print(
                "\n========== ERROR GUARDANDO LABORATORIO =========="
            )
            print(error)
            print(
                "=================================================\n"
            )

            messagebox.showerror(
                "Error",
                str(error),
                parent=self,
            )