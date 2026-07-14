import os
import tempfile
import webbrowser

from datetime import date, datetime
from tkinter import messagebox
from urllib.parse import urlparse

import customtkinter as ctk
import requests

from database.laboratorio.buscar_laboratorio import (
    buscar_estudiantes_por_laboratorio,
    buscar_laboratorio_por_id,
    buscar_materiales_por_laboratorio,
    buscar_reactivos_por_laboratorio,
    listar_laboratorios,
)
from models.laboratorio import Laboratorio
from views.editar_laboratorio import VentanaEditarLaboratorio
from views.eliminar_laboratorio import eliminar


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
RED_DARK = "#B83C3C"
BG_INPUT = "#0F1923"


# ============================================================
# Índices devueltos por listar_laboratorios()
# ============================================================

# 0: id
# 1: fecha_practica
# 2: carrera
# 3: laboratorio
# 4: asignatura
# 5: docente_responsable
# 6: tema_practica
# 7: pdf_url
# 8: encargado_laboratorio
# 9: cargo_encargado

IDX_ID = 0
IDX_FECHA = 1
IDX_CARRERA = 2
IDX_LABORATORIO = 3
IDX_ASIGNATURA = 4
IDX_DOCENTE = 5
IDX_TEMA = 6
IDX_PDF = 7
IDX_ENCARGADO = 8
IDX_CARGO = 9


# ============================================================
# Funciones auxiliares
# ============================================================

def _formatear_fecha(valor):
    """
    Convierte date, datetime o texto a DD/MM/YYYY.
    """

    if valor is None:
        return "—"

    if isinstance(
        valor,
        datetime,
    ):
        return valor.strftime(
            "%d/%m/%Y"
        )

    if isinstance(
        valor,
        date,
    ):
        return valor.strftime(
            "%d/%m/%Y"
        )

    texto = str(
        valor
    ).strip()

    for formato in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%y",
    ):
        try:
            return datetime.strptime(
                texto,
                formato,
            ).strftime(
                "%d/%m/%Y"
            )

        except ValueError:
            continue

    return texto[:10] or "—"


def _obtener_fecha_datetime(
    valor,
):
    """
    Convierte un valor de fecha en datetime para los filtros.
    """

    if valor is None:
        return None

    if isinstance(
        valor,
        datetime,
    ):
        return valor

    if isinstance(
        valor,
        date,
    ):
        return datetime.combine(
            valor,
            datetime.min.time(),
        )

    texto = str(
        valor
    ).strip()

    for formato in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%y",
    ):
        try:
            return datetime.strptime(
                texto,
                formato,
            )

        except ValueError:
            continue

    return None


def _crear_boton(
    parent,
    texto,
    color,
    hover,
    text_color,
    comando,
):
    """
    Crea un botón de acción dentro de una tarjeta.
    """

    boton = ctk.CTkButton(
        parent,
        text=texto,
        width=100,
        height=34,
        fg_color=color,
        hover_color=hover,
        text_color=text_color,
        font=("Consolas", 11),
        corner_radius=6,
        border_width=1,
        border_color=BORDER,
        command=comando,
    )

    boton.pack(
        side="left",
        padx=4,
    )

    return boton


def _es_url_http(
    valor,
):
    """
    Comprueba si el valor es una URL HTTP o HTTPS.
    """

    texto = str(
        valor or ""
    ).strip()

    return texto.lower().startswith(
        (
            "http://",
            "https://",
        )
    )


def _nombre_temporal_desde_url(
    url,
):
    """
    Obtiene un nombre para el PDF temporal.
    """

    try:
        ruta = urlparse(
            url
        ).path

        nombre = os.path.basename(
            ruta
        )

        if nombre.lower().endswith(
            ".pdf"
        ):
            return nombre

    except Exception:
        pass

    return "laboratorio_temporal.pdf"


# ============================================================
# Ventana principal
# ============================================================

class VentanaBuscarLaboratorio(
    ctk.CTkToplevel
):
    """
    Ventana para consultar, filtrar, abrir, editar y eliminar
    registros de laboratorio.
    """

    def __init__(
        self,
        master,
    ):
        super().__init__(
            master
        )

        self.title(
            "Buscar laboratorios"
        )

        self.geometry(
            "1250x760"
        )

        self.minsize(
            1050,
            650,
        )

        self.configure(
            fg_color=BG_DARK
        )

        self._todos = []

        # ========================================================
        # Header
        # ========================================================

        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=68,
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(
            False
        )

        ctk.CTkLabel(
            header,
            text="🧪  LABORATORIOS REGISTRADOS",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_PRI,
        ).pack(
            side="left",
            padx=20,
        )

        self._lbl_total = ctk.CTkLabel(
            header,
            text="",
            font=("Consolas", 11),
            text_color=ACCENT,
        )

        self._lbl_total.pack(
            side="right",
            padx=20,
        )

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(
            fill="x"
        )

        # ========================================================
        # Panel de filtros
        # ========================================================

        filtros = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
        )

        filtros.pack(
            fill="x"
        )

        # Primera fila
        fila_busqueda = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )

        fila_busqueda.pack(
            fill="x",
            padx=16,
            pady=(10, 4),
        )

        ctk.CTkLabel(
            fila_busqueda,
            text="BÚSQUEDA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=80,
            anchor="w",
        ).pack(
            side="left"
        )

        self._busqueda_var = ctk.StringVar()

        self._entrada_busqueda = ctk.CTkEntry(
            fila_busqueda,
            textvariable=self._busqueda_var,
            placeholder_text=(
                "Buscar por laboratorio, carrera, asignatura, "
                "docente, encargado o tema..."
            ),
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12),
            corner_radius=6,
            height=34,
        )

        self._entrada_busqueda.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10),
        )

        ctk.CTkButton(
            fila_busqueda,
            text="↺  Recargar",
            width=110,
            height=34,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
            command=self.cargar_datos,
        ).pack(
            side="right"
        )

        # Segunda fila
        fila_filtros = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )

        fila_filtros.pack(
            fill="x",
            padx=16,
            pady=(0, 10),
        )

        # Laboratorio
        ctk.CTkLabel(
            fila_filtros,
            text="LABORATORIO",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=90,
            anchor="w",
        ).pack(
            side="left"
        )

        self._laboratorio_var = ctk.StringVar(
            value="Todos"
        )

        self._combo_laboratorio = ctk.CTkComboBox(
            fila_filtros,
            variable=self._laboratorio_var,
            values=[
                "Todos",
                "Laboratorio de Análisis",
                "Laboratorio de Aguas",
            ],
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            dropdown_fg_color=BG_PANEL,
            dropdown_text_color=TEXT_PRI,
            dropdown_hover_color=ACCENT_DARK,
            font=("Consolas", 11),
            corner_radius=6,
            height=34,
            width=205,
            command=lambda _valor: self._aplicar_filtros(),
        )

        self._combo_laboratorio.pack(
            side="left",
            padx=(0, 14),
        )

        # Fecha desde
        ctk.CTkLabel(
            fila_filtros,
            text="DESDE",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=48,
            anchor="w",
        ).pack(
            side="left"
        )

        self._desde_var = ctk.StringVar()

        self._entrada_desde = ctk.CTkEntry(
            fila_filtros,
            textvariable=self._desde_var,
            placeholder_text="DD/MM/AAAA",
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
            height=34,
            width=125,
        )

        self._entrada_desde.pack(
            side="left",
            padx=(0, 8),
        )

        # Fecha hasta
        ctk.CTkLabel(
            fila_filtros,
            text="HASTA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=48,
            anchor="w",
        ).pack(
            side="left"
        )

        self._hasta_var = ctk.StringVar()

        self._entrada_hasta = ctk.CTkEntry(
            fila_filtros,
            textvariable=self._hasta_var,
            placeholder_text="DD/MM/AAAA",
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
            height=34,
            width=125,
        )

        self._entrada_hasta.pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            fila_filtros,
            text="✕ Limpiar",
            width=90,
            height=34,
            fg_color="transparent",
            hover_color=BG_CARD,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
            command=self._limpiar_filtros,
        ).pack(
            side="right"
        )

        # Traces
        self._busqueda_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        self._laboratorio_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        self._desde_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        self._hasta_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        # ========================================================
        # Cabecera de resultados
        # ========================================================

        cabecera = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=34,
        )

        cabecera.pack(
            fill="x",
            padx=20,
        )

        for texto, ancho in (
            ("FECHA", 95),
            ("LABORATORIO", 195),
            ("CARRERA / ASIGNATURA", 245),
            ("RESPONSABLES", 300),
            ("TEMA", 230),
            ("ACCIONES", 310),
        ):
            ctk.CTkLabel(
                cabecera,
                text=texto,
                font=("Consolas", 10, "bold"),
                text_color=TEXT_SEC,
                width=ancho,
                anchor="w",
            ).pack(
                side="left",
                padx=(8, 0),
                pady=6,
            )

        ctk.CTkFrame(
            self,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).pack(
            fill="x",
            padx=20,
        )

        # ========================================================
        # Lista desplazable
        # ========================================================

        self.frame = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )

        self.frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(4, 16),
        )

        self.cargar_datos()

    # ============================================================
    # Carga y filtros
    # ============================================================

    def cargar_datos(self):
        """
        Carga todos los laboratorios con PDF en línea.
        """

        try:
            self._todos = listar_laboratorios()

        except Exception as error:
            print(
                "\n========== ERROR CARGANDO LABORATORIOS =========="
            )
            print(error)
            print(
                "=================================================\n"
            )

            self._todos = []

            messagebox.showerror(
                "Error",
                (
                    "No fue posible cargar los laboratorios.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

        self._aplicar_filtros()

    def _limpiar_filtros(self):
        """
        Restablece todos los filtros.
        """

        self._busqueda_var.set("")
        self._laboratorio_var.set("Todos")
        self._desde_var.set("")
        self._hasta_var.set("")

    @staticmethod
    def _parsear_fecha_filtro(
        texto,
    ):
        """
        Convierte un texto de filtro en datetime.
        """

        texto = str(
            texto or ""
        ).strip()

        if not texto:
            return None

        for formato in (
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(
                    texto,
                    formato,
                )

            except ValueError:
                continue

        return None

    def _aplicar_filtros(self):
        """
        Filtra los laboratorios cargados.
        """

        busqueda = self._busqueda_var.get().strip().lower()

        laboratorio_filtro = (
            self._laboratorio_var.get().strip()
        )

        desde_texto = self._desde_var.get().strip()
        hasta_texto = self._hasta_var.get().strip()

        desde = self._parsear_fecha_filtro(
            desde_texto
        )

        hasta = self._parsear_fecha_filtro(
            hasta_texto
        )

        resultado = []

        for fila in self._todos:
            if len(fila) < 10:
                continue

            carrera = str(
                fila[IDX_CARRERA] or ""
            ).lower()

            laboratorio = str(
                fila[IDX_LABORATORIO] or ""
            ).lower()

            asignatura = str(
                fila[IDX_ASIGNATURA] or ""
            ).lower()

            docente = str(
                fila[IDX_DOCENTE] or ""
            ).lower()

            tema = str(
                fila[IDX_TEMA] or ""
            ).lower()

            encargado = str(
                fila[IDX_ENCARGADO] or ""
            ).lower()

            cargo = str(
                fila[IDX_CARGO] or ""
            ).lower()

            # Búsqueda libre
            if busqueda:
                coincide = any(
                    busqueda in campo
                    for campo in (
                        carrera,
                        laboratorio,
                        asignatura,
                        docente,
                        tema,
                        encargado,
                        cargo,
                    )
                )

                if not coincide:
                    continue

            # Filtro por laboratorio
            if (
                laboratorio_filtro
                and laboratorio_filtro != "Todos"
                and laboratorio_filtro.lower()
                not in laboratorio
            ):
                continue

            # Filtro de fechas
            if (
                desde_texto
                or hasta_texto
            ):
                fecha_fila = _obtener_fecha_datetime(
                    fila[IDX_FECHA]
                )

                if fecha_fila is None:
                    continue

                fecha_fila = fecha_fila.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                if (
                    desde is not None
                    and fecha_fila < desde
                ):
                    continue

                if hasta is not None:
                    hasta_final = hasta.replace(
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=999999,
                    )

                    if fecha_fila > hasta_final:
                        continue

            resultado.append(
                fila
            )

        self._renderizar(
            resultado
        )

    # ============================================================
    # Renderización
    # ============================================================

    def _renderizar(
        self,
        datos,
    ):
        """
        Dibuja los resultados.
        """

        for widget in self.frame.winfo_children():
            widget.destroy()

        total = len(
            datos
        )

        self._lbl_total.configure(
            text=(
                f"{total} laboratorio"
                f"{'s' if total != 1 else ''} "
                f"encontrado{'s' if total != 1 else ''}"
            )
        )

        if not datos:
            ctk.CTkLabel(
                self.frame,
                text=(
                    "No se encontraron laboratorios "
                    "con los criterios ingresados."
                ),
                font=("Consolas", 13),
                text_color=TEXT_SEC,
            ).pack(
                pady=40,
            )

            return

        for fila in datos:
            self._crear_tarjeta(
                fila
            )

    def _crear_tarjeta(
        self,
        fila,
    ):
        """
        Crea la tarjeta de un laboratorio.
        """

        id_laboratorio = fila[IDX_ID]

        fecha = _formatear_fecha(
            fila[IDX_FECHA]
        )

        carrera = str(
            fila[IDX_CARRERA] or "—"
        )

        nombre_laboratorio = str(
            fila[IDX_LABORATORIO] or "—"
        )

        asignatura = str(
            fila[IDX_ASIGNATURA] or "—"
        )

        docente = str(
            fila[IDX_DOCENTE] or "—"
        )

        tema = str(
            fila[IDX_TEMA] or "—"
        )

        pdf_url = fila[IDX_PDF]

        encargado = str(
            fila[IDX_ENCARGADO] or "—"
        )

        cargo = str(
            fila[IDX_CARGO] or "—"
        )

        tarjeta = ctk.CTkFrame(
            self.frame,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )

        tarjeta.pack(
            fill="x",
            pady=5,
        )

        ctk.CTkFrame(
            tarjeta,
            width=4,
            fg_color=ACCENT,
            corner_radius=2,
        ).pack(
            side="left",
            fill="y",
        )

        # Datos
        datos = ctk.CTkFrame(
            tarjeta,
            fg_color="transparent",
        )

        datos.pack(
            side="left",
            fill="both",
            expand=True,
            padx=12,
            pady=10,
        )

        fila_superior = ctk.CTkFrame(
            datos,
            fg_color="transparent",
        )

        fila_superior.pack(
            fill="x"
        )

        ctk.CTkLabel(
            fila_superior,
            text=fecha,
            font=("Consolas", 11, "bold"),
            text_color=ACCENT,
            width=95,
            anchor="w",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        laboratorio_corto = (
            nombre_laboratorio[:30] + "…"
            if len(nombre_laboratorio) > 30
            else nombre_laboratorio
        )

        ctk.CTkLabel(
            fila_superior,
            text=laboratorio_corto,
            font=("Consolas", 12, "bold"),
            text_color=TEXT_PRI,
            width=195,
            anchor="w",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        carrera_asignatura = (
            f"{carrera} / {asignatura}"
        )

        carrera_asignatura_corta = (
            carrera_asignatura[:43] + "…"
            if len(carrera_asignatura) > 43
            else carrera_asignatura
        )

        ctk.CTkLabel(
            fila_superior,
            text=carrera_asignatura_corta,
            font=("Consolas", 11),
            text_color=TEXT_PRI,
            width=245,
            anchor="w",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkLabel(
            fila_superior,
            text=f"Docente: {docente}",
            font=("Consolas", 10),
            text_color=TEXT_PRI,
            width=300,
            anchor="w",
        ).pack(
            side="left",
        )

        fila_inferior = ctk.CTkFrame(
            datos,
            fg_color="transparent",
        )

        fila_inferior.pack(
            fill="x",
            pady=(5, 0),
        )

        ctk.CTkLabel(
            fila_inferior,
            text=f"🔬 Encargado: {encargado}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            width=390,
            anchor="w",
        ).pack(
            side="left"
        )

        cargo_corto = (
            cargo[:52] + "…"
            if len(cargo) > 52
            else cargo
        )

        ctk.CTkLabel(
            fila_inferior,
            text=f"💼 {cargo_corto}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            width=315,
            anchor="w",
        ).pack(
            side="left",
            padx=(8, 0),
        )

        tema_corto = (
            tema[:60] + "…"
            if len(tema) > 60
            else tema
        )

        ctk.CTkLabel(
            fila_inferior,
            text=f"📄 {tema_corto}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            side="left",
            padx=(8, 0),
        )

        # Botones
        botones = ctk.CTkFrame(
            tarjeta,
            fg_color="transparent",
        )

        botones.pack(
            side="right",
            padx=14,
            pady=14,
        )

        _crear_boton(
            botones,
            "📄 PDF",
            ACCENT,
            ACCENT_DARK,
            BG_DARK,
            lambda url=pdf_url: self.abrir_pdf_laboratorio(
                url
            ),
        )

        _crear_boton(
            botones,
            "✏ Editar",
            BG_PANEL,
            BG_CARD_HOV,
            TEXT_PRI,
            lambda id_actual=id_laboratorio: self.editar(
                id_actual
            ),
        )

        _crear_boton(
            botones,
            "🗑 Eliminar",
            RED,
            RED_DARK,
            TEXT_PRI,
            lambda id_actual=id_laboratorio: self.eliminar_y_recargar(
                id_actual
            ),
        )

    # ============================================================
    # Abrir PDF
    # ============================================================

    def abrir_pdf_laboratorio(
        self,
        ruta,
    ):
        """
        Abre un PDF local o remoto.

        Para una URL pública:
            intenta abrirla directamente en el navegador.

        Si el navegador no puede abrirla:
            descarga una copia temporal y la abre en Windows.
        """

        if not ruta:
            messagebox.showwarning(
                "PDF no disponible",
                (
                    "Este laboratorio no tiene un PDF "
                    "asociado."
                ),
                parent=self,
            )
            return

        ruta = str(
            ruta
        ).strip()

        # URL en línea
        if _es_url_http(
            ruta
        ):
            try:
                abierto = webbrowser.open(
                    ruta,
                    new=2,
                )

                if abierto:
                    return

            except Exception as error:
                print(
                    "No se pudo abrir directamente el navegador:",
                    error,
                )

            # Respaldo: descargar archivo temporal
            try:
                respuesta = requests.get(
                    ruta,
                    timeout=30,
                )

                respuesta.raise_for_status()

                nombre_temporal = _nombre_temporal_desde_url(
                    ruta
                )

                carpeta_temporal = tempfile.gettempdir()

                ruta_temporal = os.path.join(
                    carpeta_temporal,
                    nombre_temporal,
                )

                with open(
                    ruta_temporal,
                    "wb",
                ) as archivo:
                    archivo.write(
                        respuesta.content
                    )

                if os.name == "nt":
                    os.startfile(
                        ruta_temporal
                    )

                else:
                    webbrowser.open(
                        f"file://{ruta_temporal}"
                    )

                return

            except requests.exceptions.RequestException as error:
                messagebox.showerror(
                    "Error de conexión",
                    (
                        "No fue posible descargar el PDF "
                        "desde Supabase.\n\n"
                        f"{error}"
                    ),
                    parent=self,
                )
                return

            except Exception as error:
                messagebox.showerror(
                    "Error",
                    (
                        "No fue posible abrir el PDF remoto.\n\n"
                        f"{error}"
                    ),
                    parent=self,
                )
                return

        # Archivo local
        ruta_local = os.path.abspath(
            ruta
        )

        if not os.path.isfile(
            ruta_local
        ):
            messagebox.showerror(
                "Archivo no encontrado",
                (
                    "No se encontró el PDF:\n\n"
                    f"{ruta_local}"
                ),
                parent=self,
            )
            return

        try:
            if os.name == "nt":
                os.startfile(
                    ruta_local
                )

            else:
                webbrowser.open(
                    f"file://{ruta_local}"
                )

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    "No fue posible abrir el PDF.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    # ============================================================
    # Editar
    # ============================================================

    def editar(
        self,
        id_laboratorio,
    ):
        """
        Recupera el registro completo y abre la ventana de edición.
        """

        fila = buscar_laboratorio_por_id(
            id_laboratorio
        )

        if not fila:
            messagebox.showerror(
                "Error",
                (
                    "No se encontró el laboratorio "
                    "seleccionado."
                ),
                parent=self,
            )
            return

        materiales = buscar_materiales_por_laboratorio(
            id_laboratorio
        )

        reactivos = buscar_reactivos_por_laboratorio(
            id_laboratorio
        )

        estudiantes = buscar_estudiantes_por_laboratorio(
            id_laboratorio
        )

        try:
            laboratorio = Laboratorio.from_row(
                fila,
                materiales=materiales,
                reactivos=reactivos,
                estudiantes=estudiantes,
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                (
                    "No fue posible reconstruir el registro.\n\n"
                    f"{error}"
                ),
                parent=self,
            )
            return

        if laboratorio is None:
            messagebox.showerror(
                "Error",
                (
                    "No fue posible cargar el laboratorio "
                    "seleccionado."
                ),
                parent=self,
            )
            return

        ventana = VentanaEditarLaboratorio(
            self,
            laboratorio,
        )

        ventana.grab_set()

        self.wait_window(
            ventana
        )

        self.cargar_datos()

    # ============================================================
    # Eliminar
    # ============================================================

    def eliminar_y_recargar(
        self,
        id_laboratorio,
    ):
        """
        Solicita confirmación y elimina el laboratorio.
        """

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            (
                "¿Desea eliminar este laboratorio?\n\n"
                "También se eliminarán sus materiales, "
                "reactivos y estudiantes relacionados."
            ),
            parent=self,
        )

        if not respuesta:
            return

        resultado = eliminar(
            id_laboratorio
        )

        if not resultado:
            messagebox.showerror(
                "Error",
                (
                    "No fue posible eliminar el "
                    "laboratorio."
                ),
                parent=self,
            )
            return

        messagebox.showinfo(
            "Correcto",
            (
                "Laboratorio eliminado "
                "correctamente."
            ),
            parent=self,
        )

        self.cargar_datos()