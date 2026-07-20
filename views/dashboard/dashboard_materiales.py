import customtkinter as ctk

from database.dashboard.dashboard_materiales import (
    obtener_dashboard_materiales,
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

RED = "#E05252"
YELLOW = "#E0B452"
BLUE = "#4C8FE0"


# ============================================================
# Utilidades
# ============================================================

def formatear_numero(valor):
    """
    Convierte un valor numérico en texto legible.
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


def formatear_fecha(fecha):
    """
    Convierte una fecha a formato día/mes/año.
    """

    if not fecha:
        return "Sin fecha"

    try:
        return fecha.strftime("%d/%m/%Y")
    except Exception:
        return str(fecha)


# ============================================================
# Tarjeta de indicador
# ============================================================

class TarjetaIndicador(ctk.CTkFrame):
    """
    Tarjeta para mostrar un indicador principal.
    """

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

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        barra = ctk.CTkFrame(
            self,
            width=5,
            fg_color=color,
            corner_radius=3,
        )

        barra.grid(
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
            font=("Consolas", 23, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
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
            ).grid(
                row=2,
                column=1,
                columnspan=2,
                sticky="ew",
                padx=16,
                pady=(2, 13),
            )


# ============================================================
# Sección
# ============================================================

class SeccionDashboard(ctk.CTkFrame):
    """
    Contenedor visual reutilizable para una sección.
    """

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

        self.grid_columnconfigure(
            0,
            weight=1,
        )

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
        ).pack(
            anchor="w",
        )

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

        self.contenido.grid_columnconfigure(
            0,
            weight=1,
        )


# ============================================================
# Fila estadística
# ============================================================

class FilaEstadistica(ctk.CTkFrame):
    """
    Fila utilizada para rankings y listados.
    """

    def __init__(
        self,
        parent,
        posicion,
        titulo,
        valor,
        detalle="",
        color=ACCENT,
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            corner_radius=7,
            border_width=1,
            border_color=BORDER,
        )

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        ctk.CTkLabel(
            self,
            text=str(posicion),
            width=34,
            height=34,
            fg_color=color,
            corner_radius=17,
            font=("Consolas", 11, "bold"),
            text_color=BG_DARK,
        ).grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(10, 11),
            pady=9,
        )

        ctk.CTkLabel(
            self,
            text=titulo,
            font=("Consolas", 11, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            pady=(9, 0),
        )

        if detalle:
            ctk.CTkLabel(
                self,
                text=detalle,
                font=("Consolas", 9),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).grid(
                row=1,
                column=1,
                sticky="ew",
                pady=(1, 9),
            )

        ctk.CTkLabel(
            self,
            text=valor,
            font=("Consolas", 12, "bold"),
            text_color=color,
            anchor="e",
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
            padx=14,
        )


# ============================================================
# Barra proporcional
# ============================================================

class BarraProporcional(ctk.CTkFrame):
    """
    Barra horizontal proporcional para representar cantidades.
    """

    def __init__(
        self,
        parent,
        titulo,
        valor,
        maximo,
        detalle="",
        color=ACCENT,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        cabecera = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        cabecera.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        cabecera.grid_columnconfigure(
            0,
            weight=1,
        )

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

        ctk.CTkLabel(
            cabecera,
            text=formatear_numero(valor),
            font=("Consolas", 10, "bold"),
            text_color=color,
            anchor="e",
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

        if detalle:
            ctk.CTkLabel(
                self,
                text=detalle,
                font=("Consolas", 8),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).grid(
                row=1,
                column=0,
                sticky="w",
                pady=(1, 4),
            )

            fila_barra = 2
        else:
            fila_barra = 1

        fondo = ctk.CTkFrame(
            self,
            height=10,
            fg_color=BG_CARD,
            corner_radius=5,
        )

        fondo.grid(
            row=fila_barra,
            column=0,
            sticky="ew",
            pady=(2, 0),
        )

        fondo.grid_propagate(False)
        fondo.grid_columnconfigure(
            0,
            weight=1,
        )

        try:
            porcentaje = float(valor or 0) / float(maximo or 1)
        except Exception:
            porcentaje = 0

        porcentaje = max(
            0.02,
            min(
                porcentaje,
                1.0,
            ),
        )

        barra = ctk.CTkProgressBar(
            fondo,
            height=10,
            corner_radius=5,
            progress_color=color,
            fg_color=BG_CARD,
        )

        barra.pack(
            fill="x",
            expand=True,
        )

        barra.set(
            porcentaje
        )


# ============================================================
# Panel principal
# ============================================================

class PanelDashboardMateriales(ctk.CTkFrame):
    """
    Panel de estadísticas de materiales.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.datos = {}

        self._cargar_datos()
        self._construir_interfaz()

    # ========================================================
    # Carga de datos
    # ========================================================

    def _cargar_datos(self):
        """
        Consulta todos los datos del dashboard.
        """

        try:
            self.datos = obtener_dashboard_materiales()

        except Exception as error:
            print(
                "\n========== ERROR CARGANDO DASHBOARD DE MATERIALES =========="
            )
            print(error)
            print(
                "============================================================\n"
            )

            self.datos = {
                "resumen": {},
                "mas_utilizados": [],
                "por_laboratorio": [],
                "por_carrera": [],
                "por_mes": [],
                "ultimos": [],
                "mas_frecuente": {},
            }

    # ========================================================
    # Construcción
    # ========================================================

    def _construir_interfaz(self):
        """
        Construye todos los componentes del panel.
        """

        self._crear_encabezado()
        self._crear_indicadores()
        self._crear_ranking_materiales()
        self._crear_distribucion_laboratorios()
        self._crear_distribucion_carreras()
        self._crear_actividad_mensual()
        self._crear_ultimos_registros()

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

        encabezado.grid_columnconfigure(
            0,
            weight=1,
        )

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
            text="📦 CONTROL DE MATERIALES",
            font=("Consolas", 18, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(
            anchor="w",
        )

        ctk.CTkLabel(
            textos,
            text=(
                "Cantidades, frecuencia y distribución de los "
                "materiales utilizados en laboratorio"
            ),
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(4, 0),
        )

        boton_actualizar = ctk.CTkButton(
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
        )

        boton_actualizar.grid(
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

        frecuente = self.datos.get(
            "mas_frecuente",
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
                uniform="indicadores_materiales",
            )

        tarjetas = (
            (
                "Registros",
                formatear_numero(
                    resumen.get(
                        "total_registros",
                        0,
                    )
                ),
                "📋",
                ACCENT,
                "Filas de materiales almacenadas",
            ),
            (
                "Materiales diferentes",
                formatear_numero(
                    resumen.get(
                        "materiales_diferentes",
                        0,
                    )
                ),
                "📦",
                BLUE,
                "Nombres únicos identificados",
            ),
            (
                "Cantidad acumulada",
                formatear_numero(
                    resumen.get(
                        "cantidad_acumulada",
                        0,
                    )
                ),
                "🔢",
                YELLOW,
                "Suma de todas las cantidades",
            ),
            (
                "Más frecuente",
                frecuente.get(
                    "material",
                    "Sin registros",
                ),
                "⭐",
                RED,
                (
                    f"{formatear_numero(frecuente.get('registros', 0))} "
                    "apariciones"
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
    # Ranking
    # ========================================================

    def _crear_ranking_materiales(self):

        registros = self.datos.get(
            "mas_utilizados",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Materiales con mayor cantidad acumulada",
            subtitulo=(
                "Ranking de materiales según la suma de cantidades "
                "registradas"
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
                "No existen materiales registrados.",
            )
            return

        for indice, material in enumerate(
            registros,
            start=1,
        ):
            color = ACCENT

            if indice == 1:
                color = YELLOW
            elif indice == 2:
                color = BLUE
            elif indice == 3:
                color = RED

            fila = FilaEstadistica(
                seccion.contenido,
                posicion=indice,
                titulo=material.get(
                    "material",
                    "Sin nombre",
                ),
                valor=formatear_numero(
                    material.get(
                        "cantidad",
                        0,
                    )
                ),
                detalle=(
                    f"{formatear_numero(material.get('registros', 0))} "
                    "registros"
                ),
                color=color,
            )

            fila.grid(
                row=indice - 1,
                column=0,
                sticky="ew",
                pady=4,
            )

    # ========================================================
    # Por laboratorio
    # ========================================================

    def _crear_distribucion_laboratorios(self):

        registros = self.datos.get(
            "por_laboratorio",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Materiales por laboratorio",
            subtitulo=(
                "Cantidad acumulada utilizada en cada laboratorio"
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
                "No existen datos agrupados por laboratorio.",
            )
            return

        maximo = max(
            (
                item.get(
                    "cantidad",
                    0,
                )
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            barra = BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "laboratorio",
                    "Sin laboratorio",
                ),
                valor=item.get(
                    "cantidad",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('materiales_diferentes', 0))} "
                    "materiales diferentes · "
                    f"{formatear_numero(item.get('registros', 0))} registros"
                ),
                color=ACCENT,
            )

            barra.grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Por carrera
    # ========================================================

    def _crear_distribucion_carreras(self):

        registros = self.datos.get(
            "por_carrera",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Distribución por carrera",
            subtitulo=(
                "Uso acumulado de materiales según la carrera registrada"
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
                "No existen datos agrupados por carrera.",
            )
            return

        maximo = max(
            (
                item.get(
                    "cantidad",
                    0,
                )
                for item in registros
            ),
            default=1,
        )

        colores = (
            ACCENT,
            BLUE,
            YELLOW,
            RED,
        )

        for indice, item in enumerate(registros):

            barra = BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "carrera",
                    "Sin carrera",
                ),
                valor=item.get(
                    "cantidad",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('materiales_diferentes', 0))} "
                    "materiales diferentes · "
                    f"{formatear_numero(item.get('laboratorios', 0))} "
                    "prácticas de laboratorio"
                ),
                color=colores[
                    indice % len(colores)
                ],
            )

            barra.grid(
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
            titulo="Actividad mensual",
            subtitulo=(
                "Cantidades de materiales registradas durante "
                "los últimos doce meses"
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
                "No existen registros mensuales.",
            )
            return

        maximo = max(
            (
                item.get(
                    "cantidad",
                    0,
                )
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            barra = BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "mes",
                    "Sin mes",
                ),
                valor=item.get(
                    "cantidad",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('registros', 0))} registros · "
                    f"{formatear_numero(item.get('materiales_diferentes', 0))} "
                    "materiales diferentes"
                ),
                color=BLUE,
            )

            barra.grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Últimos registros
    # ========================================================

    def _crear_ultimos_registros(self):

        registros = self.datos.get(
            "ultimos",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Últimos materiales registrados",
            subtitulo=(
                "Registros recientes vinculados a prácticas de laboratorio"
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
                "No existen materiales recientes.",
            )
            return

        cabecera = ctk.CTkFrame(
            seccion.contenido,
            fg_color=BG_CARD,
            corner_radius=6,
        )

        cabecera.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 5),
        )

        columnas = (
            ("Material", 180),
            ("Cantidad", 90),
            ("Laboratorio", 220),
            ("Carrera", 150),
            ("Fecha", 100),
        )

        for indice, columna in enumerate(columnas):
            cabecera.grid_columnconfigure(
                indice,
                weight=1 if indice in (0, 2, 3) else 0,
            )

            ctk.CTkLabel(
                cabecera,
                text=columna[0],
                width=columna[1],
                font=("Consolas", 9, "bold"),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).grid(
                row=0,
                column=indice,
                sticky="ew",
                padx=8,
                pady=9,
            )

        for fila_indice, item in enumerate(
            registros,
            start=1,
        ):

            fila = ctk.CTkFrame(
                seccion.contenido,
                fg_color=(
                    BG_CARD
                    if fila_indice % 2 == 0
                    else BG_PANEL
                ),
                corner_radius=5,
                border_width=1,
                border_color=BORDER,
            )

            fila.grid(
                row=fila_indice,
                column=0,
                sticky="ew",
                pady=3,
            )

            valores = (
                item.get(
                    "material",
                    "Sin nombre",
                ),
                formatear_numero(
                    item.get(
                        "cantidad",
                        0,
                    )
                ),
                item.get(
                    "laboratorio",
                    "Sin laboratorio",
                ),
                item.get(
                    "carrera",
                    "Sin carrera",
                ),
                formatear_fecha(
                    item.get(
                        "fecha"
                    )
                ),
            )

            for columna_indice, valor in enumerate(valores):

                fila.grid_columnconfigure(
                    columna_indice,
                    weight=(
                        1
                        if columna_indice in (0, 2, 3)
                        else 0
                    ),
                )

                ctk.CTkLabel(
                    fila,
                    text=str(valor),
                    width=columnas[columna_indice][1],
                    font=("Consolas", 9),
                    text_color=(
                        ACCENT
                        if columna_indice == 1
                        else TEXT_PRIMARY
                    ),
                    anchor="w",
                ).grid(
                    row=0,
                    column=columna_indice,
                    sticky="ew",
                    padx=8,
                    pady=9,
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
    # Actualización
    # ========================================================

    def actualizar(self):
        """
        Recarga los datos y reconstruye el panel.
        """

        for widget in self.winfo_children():
            widget.destroy()

        self._cargar_datos()
        self._construir_interfaz()