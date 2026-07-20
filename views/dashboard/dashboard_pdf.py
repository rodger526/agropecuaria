import os
import webbrowser
import customtkinter as ctk

from tkinter import messagebox

from database.dashboard.dashboard_pdf import (
    obtener_dashboard_pdfs,
)


# ============================================================
# Paleta de colores
# ============================================================

BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
BG_CARD_HOVER = "#263A54"

ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"

TEXT_PRIMARY = "#E8EDF2"
TEXT_SECONDARY = "#8A9BB0"

BORDER = "#2A3A50"

BLUE = "#4C8FE0"
YELLOW = "#E0B452"
RED = "#E05252"
PURPLE = "#9B6FE0"


# ============================================================
# Utilidades
# ============================================================

def formatear_numero(valor):
    """
    Convierte valores numéricos en texto legible.
    """

    try:
        numero = float(valor or 0)

        if numero.is_integer():
            return f"{int(numero):,}".replace(",", ".")

        return (
            f"{numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except (TypeError, ValueError):
        return "0"


def formatear_porcentaje(valor):
    """
    Convierte un valor en porcentaje.
    """

    try:
        numero = float(valor or 0)

        return (
            f"{numero:,.2f}%"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except (TypeError, ValueError):
        return "0,00%"


def formatear_fecha(fecha):
    """
    Convierte fechas a formato día/mes/año.
    """

    if not fecha:
        return "Sin fecha"

    try:
        return fecha.strftime("%d/%m/%Y")

    except Exception:
        return str(fecha)


def recortar_texto(texto, limite=55):
    """
    Recorta textos extensos para evitar desbordamientos.
    """

    texto = str(texto or "").strip()

    if len(texto) <= limite:
        return texto

    return texto[: limite - 3] + "..."


# ============================================================
# Tarjeta de indicador
# ============================================================

class TarjetaIndicador(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        titulo,
        valor,
        icono,
        color=ACCENT,
        descripcion="",
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )

        self.grid_columnconfigure(2, weight=1)

        ctk.CTkFrame(
            self,
            width=5,
            fg_color=color,
            corner_radius=3,
        ).grid(
            row=0,
            column=0,
            rowspan=3,
            sticky="ns",
        )

        ctk.CTkLabel(
            self,
            text=icono,
            width=48,
            font=("Segoe UI Emoji", 27),
            text_color=color,
        ).grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="w",
            padx=(16, 8),
            pady=(14, 4),
        )

        ctk.CTkLabel(
            self,
            text=titulo.upper(),
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(
            row=0,
            column=2,
            sticky="sw",
            padx=(0, 14),
            pady=(13, 0),
        )

        ctk.CTkLabel(
            self,
            text=str(valor),
            font=("Consolas", 22, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=230,
        ).grid(
            row=1,
            column=2,
            sticky="nw",
            padx=(0, 14),
            pady=(0, 2),
        )

        if descripcion:
            ctk.CTkLabel(
                self,
                text=descripcion,
                font=("Consolas", 9),
                text_color=TEXT_SECONDARY,
                anchor="w",
                wraplength=260,
            ).grid(
                row=2,
                column=1,
                columnspan=2,
                sticky="ew",
                padx=16,
                pady=(2, 13),
            )


# ============================================================
# Sección reutilizable
# ============================================================

class SeccionDashboard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        titulo,
        subtitulo="",
    ):
        super().__init__(
            parent,
            fg_color=BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )

        self.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        encabezado.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(16, 10),
        )

        ctk.CTkLabel(
            encabezado,
            text=titulo,
            font=("Consolas", 15, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        if subtitulo:
            ctk.CTkLabel(
                encabezado,
                text=subtitulo,
                font=("Consolas", 9),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).pack(
                anchor="w",
                pady=(3, 0),
            )

        ctk.CTkFrame(
            self,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
        )

        self.contenido = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.contenido.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=18,
            pady=15,
        )

        self.contenido.grid_columnconfigure(0, weight=1)


# ============================================================
# Barra proporcional
# ============================================================

class BarraProporcional(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        titulo,
        valor,
        maximo,
        detalle="",
        color=ACCENT,
        mostrar_porcentaje=False,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.grid_columnconfigure(0, weight=1)

        cabecera = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        cabecera.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        cabecera.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cabecera,
            text=titulo,
            font=("Consolas", 10, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        texto_valor = (
            formatear_porcentaje(valor)
            if mostrar_porcentaje
            else formatear_numero(valor)
        )

        ctk.CTkLabel(
            cabecera,
            text=texto_valor,
            font=("Consolas", 10, "bold"),
            text_color=color,
            anchor="e",
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

        fila_barra = 1

        if detalle:
            ctk.CTkLabel(
                self,
                text=detalle,
                font=("Consolas", 8),
                text_color=TEXT_SECONDARY,
                anchor="w",
                wraplength=900,
            ).grid(
                row=1,
                column=0,
                sticky="w",
                pady=(1, 4),
            )

            fila_barra = 2

        try:
            porcentaje = float(valor or 0) / float(maximo or 1)

        except Exception:
            porcentaje = 0

        porcentaje = max(
            0.02,
            min(porcentaje, 1.0),
        )

        barra = ctk.CTkProgressBar(
            self,
            height=10,
            corner_radius=5,
            progress_color=color,
            fg_color=BG_CARD,
        )

        barra.grid(
            row=fila_barra,
            column=0,
            sticky="ew",
            pady=(2, 0),
        )

        barra.set(porcentaje)


# ============================================================
# Tarjeta de documento reciente
# ============================================================

class TarjetaDocumento(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        documento,
        comando_abrir,
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )

        self.documento = documento
        self.comando_abrir = comando_abrir

        self.grid_columnconfigure(1, weight=1)

        tipo = documento.get(
            "tipo",
            "Documento",
        )

        ubicacion = documento.get(
            "ubicacion",
            "Sin ubicación",
        )

        color_tipo = (
            BLUE
            if tipo.lower() == "laboratorio"
            else PURPLE
        )

        icono = (
            "🧪"
            if tipo.lower() == "laboratorio"
            else "📘"
        )

        ctk.CTkLabel(
            self,
            text=icono,
            width=48,
            font=("Segoe UI Emoji", 26),
            text_color=color_tipo,
        ).grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(14, 10),
            pady=12,
        )

        encabezado = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        encabezado.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=(10, 0),
        )

        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            encabezado,
            text=tipo.upper(),
            fg_color=color_tipo,
            corner_radius=5,
            font=("Consolas", 8, "bold"),
            text_color=BG_DARK,
            width=95,
            height=24,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkLabel(
            encabezado,
            text=documento.get(
                "codigo",
                "Sin código",
            ),
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(10, 0),
        )

        ctk.CTkLabel(
            encabezado,
            text=formatear_fecha(
                documento.get("fecha")
            ),
            font=("Consolas", 9),
            text_color=TEXT_SECONDARY,
            anchor="e",
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=(10, 0),
        )

        ctk.CTkLabel(
            self,
            text=recortar_texto(
                documento.get(
                    "tema",
                    "Sin tema",
                ),
                90,
            ),
            font=("Consolas", 11, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=700,
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=(6, 2),
        )

        detalle = (
            f"{documento.get('carrera', 'Sin carrera')} · "
            f"{documento.get('asignatura', 'Sin asignatura')} · "
            f"{documento.get('responsable', 'Sin responsable')}"
        )

        ctk.CTkLabel(
            self,
            text=recortar_texto(
                detalle,
                120,
            ),
            font=("Consolas", 9),
            text_color=TEXT_SECONDARY,
            anchor="w",
            wraplength=750,
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=(0, 10),
        )

        color_ubicacion = (
            ACCENT
            if ubicacion.lower() == "web"
            else YELLOW
        )

        ctk.CTkLabel(
            self,
            text=(
                "☁ Web"
                if ubicacion.lower() == "web"
                else "💾 Local"
            ),
            font=("Consolas", 9, "bold"),
            text_color=color_ubicacion,
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=12,
            pady=(10, 0),
        )

        ctk.CTkButton(
            self,
            text="Abrir PDF",
            width=105,
            height=34,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 9, "bold"),
            corner_radius=6,
            command=lambda: self.comando_abrir(
                self.documento
            ),
        ).grid(
            row=1,
            column=2,
            rowspan=2,
            padx=12,
            pady=(6, 12),
        )


# ============================================================
# Panel principal
# ============================================================

class PanelDashboardPDF(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.grid_columnconfigure(0, weight=1)

        self.datos = {}

        self._cargar_datos()
        self._construir_interfaz()

    # ========================================================
    # Carga de datos
    # ========================================================

    def _cargar_datos(self):

        try:
            self.datos = obtener_dashboard_pdfs()

        except Exception as error:
            print(
                "\n========== ERROR CARGANDO DASHBOARD PDF =========="
            )
            print(error)
            print(
                "=================================================\n"
            )

            self.datos = {
                "resumen": {},
                "por_tipo": [],
                "por_carrera": [],
                "por_asignatura": [],
                "por_ubicacion": [],
                "por_mes": [],
                "ultimos": [],
            }

    # ========================================================
    # Construcción
    # ========================================================

    def _construir_interfaz(self):

        self._crear_encabezado()
        self._crear_indicadores()
        self._crear_comparacion_por_tipo()
        self._crear_distribucion_ubicacion()
        self._crear_pdfs_por_carrera()
        self._crear_pdfs_por_asignatura()
        self._crear_actividad_mensual()
        self._crear_ultimos_documentos()

    # ========================================================
    # Encabezado
    # ========================================================

    def _crear_encabezado(self):

        encabezado = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )

        encabezado.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=2,
            pady=(2, 12),
        )

        encabezado.grid_columnconfigure(0, weight=1)

        textos = ctk.CTkFrame(
            encabezado,
            fg_color="transparent",
        )

        textos.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=18,
        )

        ctk.CTkLabel(
            textos,
            text="📄 CONTROL DE DOCUMENTOS PDF",
            font=("Consolas", 18, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text=(
                "Disponibilidad, ubicación y distribución de "
                "documentos de prácticas y laboratorios"
            ),
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(4, 0),
        )

        ctk.CTkButton(
            encabezado,
            text="↻ Actualizar",
            width=125,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 10, "bold"),
            corner_radius=7,
            command=self.actualizar,
        ).grid(
            row=0,
            column=1,
            padx=20,
            pady=18,
        )

    # ========================================================
    # Indicadores
    # ========================================================

    def _crear_indicadores(self):

        resumen = self.datos.get(
            "resumen",
            {},
        )

        contenedor = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        contenedor.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        for columna in range(4):
            contenedor.grid_columnconfigure(
                columna,
                weight=1,
                uniform="indicadores_pdf",
            )

        tarjetas = (
            (
                "Documentos PDF",
                formatear_numero(
                    resumen.get(
                        "total_documentos",
                        0,
                    )
                ),
                "📄",
                ACCENT,
                "Archivos registrados en el sistema",
            ),
            (
                "Laboratorios",
                formatear_numero(
                    resumen.get(
                        "pdfs_laboratorios",
                        0,
                    )
                ),
                "🧪",
                BLUE,
                "PDF asociados a laboratorios",
            ),
            (
                "Prácticas",
                formatear_numero(
                    resumen.get(
                        "pdfs_practicas",
                        0,
                    )
                ),
                "📘",
                PURPLE,
                "PDF asociados a prácticas",
            ),
            (
                "Cobertura",
                formatear_porcentaje(
                    resumen.get(
                        "porcentaje_con_pdf",
                        0,
                    )
                ),
                "📊",
                YELLOW,
                (
                    f"{formatear_numero(resumen.get('registros_sin_pdf', 0))} "
                    "registros sin documento"
                ),
            ),
        )

        for columna, datos_tarjeta in enumerate(tarjetas):

            tarjeta = TarjetaIndicador(
                contenedor,
                titulo=datos_tarjeta[0],
                valor=datos_tarjeta[1],
                icono=datos_tarjeta[2],
                color=datos_tarjeta[3],
                descripcion=datos_tarjeta[4],
            )

            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=5,
            )

    # ========================================================
    # Comparación por tipo
    # ========================================================

    def _crear_comparacion_por_tipo(self):

        registros = self.datos.get(
            "por_tipo",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Documentos por tipo de registro",
            subtitulo=(
                "Comparación entre prácticas y laboratorios"
            ),
        )

        seccion.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen registros para comparar.",
            )
            return

        maximo = max(
            (
                item.get("total", 0)
                for item in registros
            ),
            default=1,
        )

        colores = (
            BLUE,
            PURPLE,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "tipo",
                    "Sin tipo",
                ),
                valor=item.get(
                    "con_pdf",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('con_pdf', 0))} con PDF · "
                    f"{formatear_numero(item.get('sin_pdf', 0))} sin PDF · "
                    f"{formatear_porcentaje(item.get('porcentaje', 0))} "
                    "de cobertura"
                ),
                color=colores[
                    indice % len(colores)
                ],
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Ubicación
    # ========================================================

    def _crear_distribucion_ubicacion(self):

        registros = self.datos.get(
            "por_ubicacion",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Ubicación de documentos",
            subtitulo=(
                "Diferencia entre enlaces almacenados en la nube "
                "y archivos locales"
            ),
        )

        seccion.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen documentos para clasificar.",
            )
            return

        maximo = max(
            (
                item.get("cantidad", 0)
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            ubicacion = item.get(
                "ubicacion",
                "Sin ubicación",
            )

            color = (
                ACCENT
                if ubicacion.lower() == "enlace web"
                else YELLOW
            )

            BarraProporcional(
                seccion.contenido,
                titulo=ubicacion,
                valor=item.get(
                    "cantidad",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    "Documento disponible mediante URL"
                    if ubicacion.lower() == "enlace web"
                    else "Archivo almacenado mediante ruta local"
                ),
                color=color,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Por carrera
    # ========================================================

    def _crear_pdfs_por_carrera(self):

        registros = self.datos.get(
            "por_carrera",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Documentos por carrera",
            subtitulo=(
                "Cantidad de registros con PDF según la carrera"
            ),
        )

        seccion.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen documentos agrupados por carrera.",
            )
            return

        maximo = max(
            (
                item.get("total", 0)
                for item in registros
            ),
            default=1,
        )

        colores = (
            ACCENT,
            BLUE,
            YELLOW,
            PURPLE,
            RED,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "carrera",
                    "Sin carrera",
                ),
                valor=item.get(
                    "con_pdf",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('con_pdf', 0))} con PDF · "
                    f"{formatear_numero(item.get('sin_pdf', 0))} sin PDF · "
                    f"{formatear_numero(item.get('total', 0))} total"
                ),
                color=colores[
                    indice % len(colores)
                ],
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Por asignatura
    # ========================================================

    def _crear_pdfs_por_asignatura(self):

        registros = self.datos.get(
            "por_asignatura",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Asignaturas con más documentos",
            subtitulo=(
                "Clasificación según la cantidad de archivos PDF registrados"
            ),
        )

        seccion.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen documentos agrupados por asignatura.",
            )
            return

        maximo = max(
            (
                item.get("total", 0)
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "asignatura",
                    "Sin asignatura",
                ),
                valor=item.get(
                    "con_pdf",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('con_pdf', 0))} con PDF · "
                    f"{formatear_numero(item.get('total', 0))} "
                    "registros totales"
                ),
                color=BLUE,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Actividad mensual
    # ========================================================

    def _crear_actividad_mensual(self):

        registros = self.datos.get(
            "por_mes",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Documentos registrados por mes",
            subtitulo=(
                "Actividad de almacenamiento de PDF durante "
                "los últimos doce meses"
            ),
        )

        seccion.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen documentos mensuales.",
            )
            return

        maximo = max(
            (
                item.get("total", 0)
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "mes",
                    "Sin mes",
                ),
                valor=item.get(
                    "total",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('laboratorios', 0))} "
                    f"de laboratorios · "
                    f"{formatear_numero(item.get('practicas', 0))} "
                    "de prácticas"
                ),
                color=YELLOW,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Últimos documentos
    # ========================================================

    def _crear_ultimos_documentos(self):

        registros = self.datos.get(
            "ultimos",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Últimos documentos registrados",
            subtitulo=(
                "PDF recientes disponibles para apertura"
            ),
        )

        seccion.grid(
            row=7,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 12),
        )

        if not registros:
            self._mostrar_sin_datos(
                seccion.contenido,
                "No existen documentos PDF registrados.",
            )
            return

        for indice, documento in enumerate(registros):

            TarjetaDocumento(
                seccion.contenido,
                documento=documento,
                comando_abrir=self._abrir_documento,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=5,
            )

    # ========================================================
    # Apertura de documentos
    # ========================================================

    def _abrir_documento(self, documento):

        ruta = str(
            documento.get(
                "pdf_url",
                "",
            )
            or ""
        ).strip()

        if not ruta:
            messagebox.showwarning(
                "Documento no disponible",
                "Este registro no contiene una ruta de PDF.",
            )
            return

        try:
            ruta_minuscula = ruta.lower()

            if (
                ruta_minuscula.startswith("http://")
                or ruta_minuscula.startswith("https://")
            ):
                webbrowser.open_new_tab(ruta)
                return

            ruta_local = os.path.abspath(
                os.path.expanduser(ruta)
            )

            if not os.path.exists(ruta_local):
                messagebox.showerror(
                    "Archivo no encontrado",
                    (
                        "La ruta local almacenada no existe:\n\n"
                        f"{ruta_local}"
                    ),
                )
                return

            if os.name == "nt":
                os.startfile(ruta_local)

            elif os.name == "posix":
                import subprocess

                comando = (
                    ["open", ruta_local]
                    if "darwin" in os.sys.platform
                    else ["xdg-open", ruta_local]
                )

                subprocess.Popen(comando)

            else:
                webbrowser.open(
                    f"file://{ruta_local}"
                )

        except Exception as error:
            messagebox.showerror(
                "Error al abrir PDF",
                (
                    "No fue posible abrir el documento.\n\n"
                    f"Detalle: {error}"
                ),
            )

    # ========================================================
    # Sin datos
    # ========================================================

    def _mostrar_sin_datos(
        self,
        parent,
        mensaje,
    ):

        contenedor = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )

        contenedor.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=5,
        )

        ctk.CTkLabel(
            contenedor,
            text="ℹ️",
            font=("Segoe UI Emoji", 24),
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=(18, 4),
        )

        ctk.CTkLabel(
            contenedor,
            text=mensaje,
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=(0, 18),
        )

    # ========================================================
    # Actualizar
    # ========================================================

    def actualizar(self):

        for widget in self.winfo_children():
            widget.destroy()

        self._cargar_datos()
        self._construir_interfaz()