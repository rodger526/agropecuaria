import json
import os
import qrcode
import shutil
import socket
import tempfile
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import customtkinter as ctk
from utils.rutas_app import ruta_datos
from customtkinter import CTkImage
from datetime import datetime
from PIL import Image
from tkinter import messagebox

from database.laboratorio.buscar_datos import (
    buscar_equipos_por_tipo,
    obtener_laboratorios_tipo,
)
from database.laboratorio.guardar_laboratorio import guardar_laboratorio
from firma.servidor_firma import (
    app as flask_app,
    eliminar_firmas_sesion,
    obtener_ruta_firma,
    CARPETA_SESIONES,
)
from models.laboratorio import Laboratorio
from pdf.generador_pdf_laboratorio import generar_pdf_laboratorio
from storage.subir_pdf_laboratorio import (
    eliminar_pdf_laboratorio_por_url,
    subir_pdf_laboratorio,
)
from views.nueva_practica import _combo


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

RUTA_FIRMA_DOCENTE_LAB = str(
    ruta_datos(
        "datos",
        "firmas",
        "firma_docente_laboratorio.png",
    )
)

RUTA_FIRMA_ENCARGADO_LAB = str(
    ruta_datos(
        "datos",
        "firmas",
        "firma_encargado_laboratorio.png",
    )
)

# Debe utilizar exactamente la misma carpeta donde
# servidor_firma.py guarda los JSON de estudiantes.
CARPETA_SESIONES_FIRMA = str(CARPETA_SESIONES)


# ============================================================
# Servidor global de firmas
# ============================================================

PUERTO_FIRMAS = 5000

_SERVIDOR_LOCK = threading.Lock()
_SERVIDOR_INICIADO = False


def _servidor_escuchando(
    host="127.0.0.1",
    puerto=PUERTO_FIRMAS,
):
    try:
        with socket.create_connection(
            (host, puerto),
            timeout=0.4,
        ):
            return True
    except OSError:
        return False


def _ejecutar_servidor_flask():
    flask_app.run(
        host="0.0.0.0",
        port=PUERTO_FIRMAS,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def _asegurar_servidor_firmas():
    global _SERVIDOR_INICIADO

    with _SERVIDOR_LOCK:
        if (
            _SERVIDOR_INICIADO
            or _servidor_escuchando()
        ):
            _SERVIDOR_INICIADO = True
            return

        threading.Thread(
            target=_ejecutar_servidor_flask,
            daemon=True,
            name="ServidorFirmasFlask",
        ).start()

        _SERVIDOR_INICIADO = True


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

    La búsqueda se ejecuta en un hilo secundario para evitar bloquear
    la interfaz mientras se consulta PostgreSQL. También utiliza caché
    temporal para que las búsquedas repetidas respondan más rápido.
    """

    def __init__(
        self,
        entry,
        fn_buscar,
        on_seleccion,
        min_chars=1,
        retardo_ms=120,
    ):
        self.entry = entry
        self.fn_buscar = fn_buscar
        self.on_seleccion = on_seleccion
        self.min_chars = min_chars
        self.retardo_ms = retardo_ms

        self._toplevel = None
        self._after_id = None
        self._consulta_id = 0
        self._cache = {}
        self._cache_orden = []
        self._cache_maximo = 40

        entry.bind(
            "<KeyRelease>",
            self._on_key,
        )

        entry.bind(
            "<Down>",
            self._enfocar_primera_opcion,
        )

        entry.bind(
            "<Escape>",
            lambda _event: self._cerrar(),
        )

        entry.bind(
            "<FocusOut>",
            lambda _event: entry.after(
                220,
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

        clave = texto.casefold()

        if clave in self._cache:
            self._mostrar_si_vigente(
                texto,
                self._cache[clave],
                self._consulta_id,
            )
            return

        self._consulta_id += 1
        consulta_actual = self._consulta_id

        threading.Thread(
            target=self._buscar_en_hilo,
            args=(
                texto,
                clave,
                consulta_actual,
            ),
            daemon=True,
            name="BuscarSugerenciasLaboratorio",
        ).start()

    def _buscar_en_hilo(
        self,
        texto,
        clave,
        consulta_actual,
    ):
        try:
            resultados = self.fn_buscar(
                texto
            ) or []
        except Exception:
            resultados = []

        resultados = list(
            resultados[:8]
        )

        self._guardar_cache(
            clave,
            resultados,
        )

        try:
            self.entry.after(
                0,
                lambda: self._mostrar_si_vigente(
                    texto,
                    resultados,
                    consulta_actual,
                ),
            )
        except Exception:
            pass

    def _guardar_cache(
        self,
        clave,
        resultados,
    ):
        if clave not in self._cache:
            self._cache_orden.append(
                clave
            )

        self._cache[clave] = resultados

        while len(self._cache_orden) > self._cache_maximo:
            clave_antigua = self._cache_orden.pop(
                0
            )
            self._cache.pop(
                clave_antigua,
                None,
            )

    def limpiar_cache(self):
        self._cache.clear()
        self._cache_orden.clear()

    def _mostrar_si_vigente(
        self,
        texto_consultado,
        resultados,
        consulta_actual,
    ):
        if not self.entry.winfo_exists():
            return

        texto_actual = self.entry.get().strip()

        if (
            texto_actual.casefold()
            != texto_consultado.casefold()
        ):
            return

        if (
            consulta_actual
            and consulta_actual != self._consulta_id
        ):
            return

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
                220,
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
            8,
        ) * 32

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

        for item in resultados[:8]:
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
                height=32,
                command=lambda item_actual=item: self._elegir(
                    item_actual
                ),
            )
            boton.pack(
                fill="x"
            )

            boton.bind(
                "<Return>",
                lambda _event, item_actual=item: self._elegir(
                    item_actual
                ),
            )

    def _enfocar_primera_opcion(
        self,
        _event=None,
    ):
        if (
            self._toplevel is None
            or not self._toplevel.winfo_exists()
        ):
            return

        hijos = self._toplevel.winfo_children()

        if hijos:
            hijos[0].focus_set()

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

        # Estado interno.
        self._polling_estudiantes_activo = False
        self._polling_responsables_activo = False
        self._guardando = False
        self._cerrando = False

        self._after_estudiantes = None
        self._after_responsables = None

        # Referencias de imágenes CTkImage.
        self._img_refs = {}
        self._firma_mtimes = {}

        self.protocol(
            "WM_DELETE_WINDOW",
            self._cerrar_ventana,
        )

        # Firmas de estudiantes.
        self._estudiantes_firmados = []

        # Datos del encargado seleccionado.
        self._encargado_actual = ""
        self._cargo_encargado_actual = ""

        # Limpiar únicamente la sesión recién creada.
        # No se eliminan archivos globales compartidos.
        try:
            eliminar_firmas_sesion(
                self._codigo_sesion
            )
        except Exception:
            pass

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

        self.unidad_academica = _combo(
            c4,
            [
                "Facultad de Ciencias de la Vida y Tecnologías",
                "Facultad de Ciencias Administrativas, Contables y Comercio",
                "Facultad de Ciencias de la Salud",
                "Facultad de Ciencias Sociales, Derecho y Bienestar",
                "Facultad de Educación, Turismo, Artes y Humanidades",
                "Facultad de Ingeniería, Industria y Construcción",
                "Extensión Bahía de Caráquez",
                "Extensión Chone",
                "Extensión El Carmen",
                "Extensión Flavio Alfaro",
                "Extensión Pedernales",
                "Extensión Pichincha",
                "Extensión Santo Domingo",
                "Extensión Tosagua",
                "Finca Experimental Lodana",
            ],
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

        self.carrera = _combo(
            c6,
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
            c9,
            "Nombre de la institución",
        )
        self.institucion.insert(
            0,
            "Universidad Laica Eloy Alfaro de Manabí",
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

        self.ciudad = _combo(
            c10,
            [
                "Manta",
                "Bahía de Caráquez",
                "Chone",
                "El Carmen",
                "Flavio Alfaro",
                "Pedernales",
                "Pichincha",
                "Santo Domingo",
                "Tosagua",
                "Lodana",
            ],
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
        self._btn_guardar = ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR REGISTRO",
            command=self.guardar,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=48,
        )
        self._btn_guardar.pack(
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
        """
        Inicia Flask una sola vez para toda la aplicación.
        """

        _asegurar_servidor_firmas()

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
        if self._cerrando:
            return

        try:
            self._asegurar_servidor()

            self._btn_qr_est.configure(
                state="disabled",
                text="GENERANDO QR...",
            )

            self.after(
                700,
                self._activar_qr_estudiantes,
            )

        except Exception as error:
            messagebox.showerror(
                "Servidor de firmas",
                (
                    "No se pudo iniciar el servidor de firmas.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    def _activar_qr_estudiantes(self):
        if self._cerrando or not self.winfo_exists():
            return

        try:
            self._generar_qr_estudiantes()

            if not self._polling_estudiantes_activo:
                self._polling_estudiantes_activo = True
                self._polling_estudiantes()

            self._btn_qr_est.configure(
                state="normal",
                text="↺  Regenerar QR para estudiantes",
            )

        except Exception as error:
            self._btn_qr_est.configure(
                state="normal",
                text="⬤  Generar QR para estudiantes",
            )

            messagebox.showerror(
                "Código QR",
                f"No se pudo generar el QR:\n\n{error}",
                parent=self,
            )

    def _generar_qr_estudiantes(self):
        ip = self._obtener_ip_red()
        sesion = quote(
            self._codigo_sesion,
            safe="",
        )

        url = (
            f"http://{ip}:{PUERTO_FIRMAS}/"
            f"firma/estudiante/{sesion}"
        )

        qr_img = qrcode.make(url).resize(
            (190, 190)
        ).convert("RGB")

        photo = CTkImage(
            light_image=qr_img,
            dark_image=qr_img,
            size=(190, 190),
        )

        self._img_refs["qr_estudiantes"] = photo

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
        if (
            self._cerrando
            or not self._polling_estudiantes_activo
            or not self.winfo_exists()
        ):
            return

        ruta_sesion = os.path.join(
            CARPETA_SESIONES_FIRMA,
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

        self._after_estudiantes = self.after(
            800,
            self._polling_estudiantes,
        )

    # ================================================================
    # QR responsables
    # ================================================================

    def _iniciar_firmas_responsables(self):
        if self._cerrando:
            return

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
                    "encargado configurado."
                ),
                parent=self,
            )
            return

        try:
            self._asegurar_servidor()

            self._btn_qr_responsables.configure(
                state="disabled",
                text="GENERANDO QR...",
            )

            self.after(
                700,
                self._activar_qrs_responsables,
            )

        except Exception as error:
            messagebox.showerror(
                "Servidor de firmas",
                (
                    "No se pudo iniciar el servidor de firmas.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    def _activar_qrs_responsables(self):
        if self._cerrando or not self.winfo_exists():
            return

        try:
            self._generar_qrs_responsables()

            if not self._polling_responsables_activo:
                self._polling_responsables_activo = True
                self._polling_firmas_responsables()

            self._btn_qr_responsables.configure(
                state="normal",
                text="↺  Regenerar QR de responsables",
            )

        except Exception as error:
            self._btn_qr_responsables.configure(
                state="normal",
                text="⬤  Generar QR de responsables",
            )

            messagebox.showerror(
                "Códigos QR",
                f"No se pudieron generar los QR:\n\n{error}",
                parent=self,
            )

    def _generar_qrs_responsables(self):
        ip = self._obtener_ip_red()
        sesion = quote(
            self._codigo_sesion,
            safe="",
        )

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
                f"http://{ip}:{PUERTO_FIRMAS}"
                f"/firma/{rol}?sesion={sesion}"
            )

            imagen_qr = qrcode.make(url).resize(
                (170, 170)
            ).convert("RGB")

            photo = CTkImage(
                light_image=imagen_qr,
                dark_image=imagen_qr,
                size=(170, 170),
            )

            self._img_refs[f"qr_{rol}"] = photo

            label_qr.configure(
                image=photo,
                text="",
            )

    def _polling_firmas_responsables(self):
        if (
            self._cerrando
            or not self._polling_responsables_activo
            or not self.winfo_exists()
        ):
            return

        configuraciones = (
            (
                "docente_laboratorio",
                self._lbl_estado_docente_lab,
                self._lbl_preview_docente_lab,
                "preview_docente_laboratorio",
            ),
            (
                "encargado_laboratorio",
                self._lbl_estado_encargado_lab,
                self._lbl_preview_encargado_lab,
                "preview_encargado_laboratorio",
            ),
        )

        for (
            rol,
            label_estado,
            label_preview,
            clave_preview,
        ) in configuraciones:
            ruta = obtener_ruta_firma(
                rol,
                self._codigo_sesion,
            )

            if ruta and os.path.isfile(ruta):
                label_estado.configure(
                    text="✔  Firmado",
                    text_color=ACCENT,
                )

                self._mostrar_preview_firma(
                    ruta,
                    label_preview,
                    clave_preview,
                )
            else:
                label_estado.configure(
                    text="⏳  Pendiente de firma",
                    text_color=TEXT_SEC,
                )

        self._after_responsables = self.after(
            2000,
            self._polling_firmas_responsables,
        )

    def _mostrar_preview_firma(
        self,
        ruta,
        label,
        key,
    ):
        try:
            mtime = os.path.getmtime(ruta)

            if self._firma_mtimes.get(key) == mtime:
                return

            with Image.open(ruta) as imagen_original:
                imagen = imagen_original.convert("RGBA")

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
                    fondo.paste(imagen)

                fondo = fondo.convert("RGB")
                fondo.thumbnail((200, 80))

            photo = CTkImage(
                light_image=fondo,
                dark_image=fondo,
                size=(
                    max(1, fondo.width),
                    max(1, fondo.height),
                ),
            )

            self._img_refs[key] = photo
            self._firma_mtimes[key] = mtime

            if label.winfo_exists():
                label.configure(
                    image=photo,
                    text="",
                )

        except (OSError, ValueError) as error:
            print(
                "No se pudo mostrar la firma:",
                error,
            )

    @staticmethod
    def _texto_textbox(widget):
        return widget.get(
            "1.0",
            "end",
        ).strip()

    def _validar_formulario(self):
        try:
            numero_estudiantes = int(
                self.numero_estudiantes.get().strip()
            )
            semestre = int(
                self.semestre.get().strip()
            )
            hora_entrada = _normalizar_hora(
                self.hora_entrada.get()
            )
            hora_salida = _normalizar_hora(
                self.hora_salida.get()
            )

        except ValueError as error:
            raise ValueError(
                "Revise el semestre, el número de estudiantes "
                f"y los horarios.\n\n{error}"
            ) from error

        if numero_estudiantes <= 0:
            raise ValueError(
                "El número de estudiantes debe ser mayor que cero."
            )

        if semestre <= 0:
            raise ValueError(
                "El semestre debe ser mayor que cero."
            )

        if hora_entrada >= hora_salida:
            raise ValueError(
                "La hora de salida debe ser posterior "
                "a la hora de entrada."
            )

        campos = {
            "Laboratorio": self.laboratorio.get().strip(),
            "Asignatura": self.asignatura.get().strip(),
            "Unidad académica": self.unidad_academica.get().strip(),
            "Carrera": self.carrera.get().strip(),
            "Institución": self.institucion.get().strip(),
            "Ciudad": self.ciudad.get().strip(),
            "Docente responsable": self.docente.get().strip(),
            "Tema de la práctica": self._texto_textbox(self.tema),
            "Subtema": self._texto_textbox(self.subtema),
            "Logro de aprendizaje": self._texto_textbox(self.logro),
            "Objetivos": self._texto_textbox(self.objetivos),
            "Metodología": self._texto_textbox(self.metodologia),
            "Resultados": self._texto_textbox(self.resultados),
            "Conclusiones": self._texto_textbox(self.conclusiones),
        }

        faltantes = [
            nombre
            for nombre, valor in campos.items()
            if not valor
        ]

        if faltantes:
            raise ValueError(
                "Debe completar los siguientes campos:\n\n• "
                + "\n• ".join(faltantes)
            )

        if not self._encargado_actual:
            raise ValueError(
                "El laboratorio seleccionado no tiene "
                "un encargado configurado."
            )

        if not self._cargo_encargado_actual:
            raise ValueError(
                "El encargado del laboratorio no tiene "
                "un cargo configurado."
            )

        return (
            numero_estudiantes,
            semestre,
            hora_entrada,
            hora_salida,
        )
    
    @staticmethod
    def _copiar_firma_persistente(
        ruta_origen,
        carpeta_destino,
        nombre_archivo,
    ):
        """
        Copia una firma temporal a una carpeta permanente.

        Esto evita que las rutas almacenadas en PostgreSQL dejen
        de funcionar después de limpiar la sesión temporal.
        """

        if not ruta_origen:
            return None

        ruta_origen = str(
            ruta_origen
        ).strip()

        if not os.path.isfile(
            ruta_origen
        ):
            return None

        os.makedirs(
            carpeta_destino,
            exist_ok=True,
        )

        ruta_destino = os.path.join(
            carpeta_destino,
            nombre_archivo,
        )

        shutil.copy2(
            ruta_origen,
            ruta_destino,
        )

        return os.path.abspath(
            ruta_destino
        )

    def _persistir_firmas_laboratorio(
        self,
        codigo,
        estudiantes,
    ):
        """
        Conserva permanentemente las firmas antes de generar el PDF
        y eliminar los archivos temporales.

        Devuelve:

            estudiantes con rutas permanentes,
            ruta permanente de la firma docente,
            ruta permanente de la firma del encargado.
        """

        carpeta_registro = str(
            ruta_datos(
                "datos",
                "firmas_laboratorios",
                codigo,
            )
        )

        carpeta_estudiantes = os.path.join(
            carpeta_registro,
            "estudiantes",
        )

        estudiantes_persistentes = []

        for indice, estudiante in enumerate(
            estudiantes,
            start=1,
        ):
            estudiante_copia = dict(
                estudiante
            )

            ruta_temporal = estudiante_copia.get(
                "firma_ruta"
            )

            cedula = str(
                estudiante_copia.get(
                    "cedula"
                )
                or f"sin_cedula_{indice}"
            ).strip()

            cedula_segura = "".join(
                caracter
                for caracter in cedula
                if (
                    caracter.isalnum()
                    or caracter in (
                        "-",
                        "_",
                    )
                )
            )

            if not cedula_segura:
                cedula_segura = (
                    f"estudiante_{indice}"
                )

            ruta_permanente = (
                self._copiar_firma_persistente(
                    ruta_temporal,
                    carpeta_estudiantes,
                    (
                        f"{indice:03d}_"
                        f"{cedula_segura}.png"
                    ),
                )
            )

            if ruta_permanente:
                estudiante_copia[
                    "firma_ruta"
                ] = ruta_permanente

            estudiantes_persistentes.append(
                estudiante_copia
            )

        firma_docente_temporal = (
            obtener_ruta_firma(
                "docente_laboratorio",
                self._codigo_sesion,
            )
        )

        firma_encargado_temporal = (
            obtener_ruta_firma(
                "encargado_laboratorio",
                self._codigo_sesion,
            )
        )

        firma_docente = (
            self._copiar_firma_persistente(
                firma_docente_temporal,
                carpeta_registro,
                "firma_docente.png",
            )
        )

        firma_encargado = (
            self._copiar_firma_persistente(
                firma_encargado_temporal,
                carpeta_registro,
                "firma_encargado.png",
            )
        )

        return (
            estudiantes_persistentes,
            firma_docente,
            firma_encargado,
        )

    def _crear_objeto_laboratorio(
        self,
        numero_estudiantes,
        semestre,
        hora_entrada,
        hora_salida,
    ):
        codigo = datetime.now().strftime(
            "LAB-%Y%m%d%H%M%S%f"
        )

        estudiantes = [
            {
                "nombre": estudiante.get("nombre"),
                "cedula": estudiante.get("cedula"),
                "firma_ruta": estudiante.get("firma_ruta"),
                "hora": estudiante.get("hora"),
                "fecha": estudiante.get("fecha"),
            }
            for estudiante in self._estudiantes_firmados
        ]

        for linea in self.estudiantes.get(
            "1.0",
            "end",
        ).splitlines():
            linea = linea.strip()

            if not linea:
                continue

            estudiantes.append(
                {
                    "nombre": linea,
                    "cedula": None,
                    "firma_ruta": None,
                    "hora": None,
                    "fecha": None,
                }
            )

        (
            estudiantes,
            firma_docente,
            firma_encargado,
        ) = self._persistir_firmas_laboratorio(
            codigo,
            estudiantes,
        )

        return Laboratorio(
            codigo=codigo,
            laboratorio=self.laboratorio.get().strip(),
            numero_estudiantes=numero_estudiantes,
            asignatura=self.asignatura.get().strip(),
            unidad_academica=self.unidad_academica.get().strip(),
            semestre=semestre,
            carrera=self.carrera.get().strip(),
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            institucion=self.institucion.get().strip(),
            ciudad=self.ciudad.get().strip(),
            docente_responsable=self.docente.get().strip(),
            fecha_practica=datetime.now().strftime("%Y-%m-%d"),
            tema_practica=self._texto_textbox(self.tema),
            subtema=self._texto_textbox(self.subtema),
            logro_aprendizaje=self._texto_textbox(self.logro),
            objetivos=self._texto_textbox(self.objetivos),
            metodologia=self._texto_textbox(self.metodologia),
            resultados=self._texto_textbox(self.resultados),
            conclusiones=self._texto_textbox(self.conclusiones),
            observaciones=self._texto_textbox(self.observaciones),
            materiales=self.widget_materiales.obtener_items(),
            reactivos=self.widget_reactivos.obtener_items(),
            estudiantes=estudiantes,
            encargado_laboratorio=self._encargado_actual,
            cargo_encargado=self._cargo_encargado_actual,
            firma_encargado_ruta=firma_encargado,
            firma_docente_ruta=firma_docente,
            codigo_sesion=self._codigo_sesion,
        )


    def guardar(self):
        """
        Valida y ejecuta el guardado fuera del hilo de Tkinter.
        """

        if self._guardando:
            return

        try:
            datos_validados = self._validar_formulario()
        except ValueError as error:
            messagebox.showerror(
                "Datos incompletos",
                str(error),
                parent=self,
            )
            return

        firma_docente = obtener_ruta_firma(
            "docente_laboratorio",
            self._codigo_sesion,
        )
        firma_encargado = obtener_ruta_firma(
            "encargado_laboratorio",
            self._codigo_sesion,
        )

        faltantes = []

        if not firma_docente:
            faltantes.append("Docente responsable")

        if not firma_encargado:
            faltantes.append("Encargado del laboratorio")

        if faltantes:
            respuesta = messagebox.askyesno(
                "Firmas pendientes",
                (
                    "Todavía faltan las siguientes firmas:\n\n• "
                    + "\n• ".join(faltantes)
                    + "\n\n¿Desea guardar el laboratorio "
                    "sin esas firmas?"
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

        threading.Thread(
            target=self._procesar_guardado,
            args=datos_validados,
            daemon=True,
            name="GuardarLaboratorio",
        ).start()

    def _procesar_guardado(
        self,
        numero_estudiantes,
        semestre,
        hora_entrada,
        hora_salida,
    ):
        ruta_pdf = None
        url_pdf = None
        guardado_correcto = False

        try:
            laboratorio = self._crear_objeto_laboratorio(
                numero_estudiantes,
                semestre,
                hora_entrada,
                hora_salida,
            )

            ruta_generada = generar_pdf_laboratorio(
                laboratorio
            )

            ruta_pdf = Path(
                ruta_generada
            ).resolve()

            if not ruta_pdf.is_file():
                raise RuntimeError(
                    "El generador no creó el PDF del laboratorio."
                )

            url_pdf = subir_pdf_laboratorio(
                str(ruta_pdf)
            )

            laboratorio.pdf_url = url_pdf

            resultado = guardar_laboratorio(
                laboratorio
            )

            if not resultado:
                raise RuntimeError(
                    "PostgreSQL no confirmó el registro "
                    "del laboratorio."
                )

            guardado_correcto = True

            self.after(
                0,
                lambda: self._guardado_exitoso(
                    url_pdf
                ),
            )

        except Exception as error:
            if url_pdf and not guardado_correcto:
                eliminar_pdf_laboratorio_por_url(
                    url_pdf
                )

            detalle = (
                str(error).strip()
                or error.__class__.__name__
            )

            self.after(
                0,
                lambda mensaje=detalle: (
                    self._guardado_fallido(mensaje)
                ),
            )

        finally:
            if ruta_pdf:
                try:
                    ruta_pdf.unlink(
                        missing_ok=True
                    )

                    carpeta = ruta_pdf.parent

                    if (
                        carpeta.is_dir()
                        and not any(carpeta.iterdir())
                    ):
                        carpeta.rmdir()

                except OSError as error:
                    print(
                        "No se pudo eliminar el PDF temporal:",
                        error,
                    )

    def _detener_polling(self):
        self._polling_estudiantes_activo = False
        self._polling_responsables_activo = False

        for atributo in (
            "_after_estudiantes",
            "_after_responsables",
        ):
            after_id = getattr(
                self,
                atributo,
                None,
            )

            if after_id is not None:
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass

                setattr(
                    self,
                    atributo,
                    None,
                )

    def _guardado_exitoso(self, url_pdf):
        self._guardando = False

        if not self.winfo_exists():
            return

        self._detener_polling()

        try:
            eliminar_firmas_sesion(
                self._codigo_sesion,
                incluir_estudiantes=True,
            )
        except Exception as error:
            print(
                "No se pudieron eliminar los temporales:",
                error,
            )

        messagebox.showinfo(
            "Laboratorio guardado",
            (
                "El laboratorio se guardó correctamente.\n\n"
                "El PDF fue generado, subido a Supabase y "
                "registrado en PostgreSQL.\n\n"
                "Los archivos temporales fueron eliminados."
            ),
            parent=self,
        )

        self._cerrar_ventana(
            confirmar=False,
            eliminar_temporales=False,
        )

    def _guardado_fallido(self, detalle):
        self._guardando = False

        if not self.winfo_exists():
            return

        self._btn_guardar.configure(
            state="normal",
            text="⬤  GUARDAR REGISTRO",
        )

        messagebox.showerror(
            "No se pudo guardar",
            (
                "No fue posible completar el registro "
                "del laboratorio.\n\n"
                f"Detalle:\n{detalle}\n\n"
                "Las firmas de la sesión se conservarán "
                "para que pueda volver a intentarlo."
            ),
            parent=self,
        )

    def _cerrar_ventana(
        self,
        confirmar=True,
        eliminar_temporales=True,
    ):
        if self._cerrando:
            return

        if self._guardando:
            messagebox.showwarning(
                "Proceso en ejecución",
                (
                    "El laboratorio se está guardando. "
                    "Espere a que el proceso termine."
                ),
                parent=self,
            )
            return

        if confirmar:
            respuesta = messagebox.askyesno(
                "Cerrar laboratorio",
                (
                    "¿Desea cerrar esta ventana?\n\n"
                    "Las firmas temporales de esta sesión "
                    "serán eliminadas."
                ),
                parent=self,
            )

            if not respuesta:
                return

        self._cerrando = True
        self._detener_polling()

        if eliminar_temporales:
            try:
                eliminar_firmas_sesion(
                    self._codigo_sesion
                )
            except Exception as error:
                print(
                    "No se pudieron limpiar los temporales:",
                    error,
                )

        self.destroy()