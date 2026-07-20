import customtkinter as ctk

from database.dashboard.dashboard_docentes import (
    obtener_dashboard_docentes,
)


# ============================================================
# Paleta de colores
# ============================================================

BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"

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
# Fila estadística
# ============================================================

class FilaEstadistica(ctk.CTkFrame):

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

        self.grid_columnconfigure(1, weight=1)

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
                wraplength=650,
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

        fila_barra = 1

        if detalle:
            ctk.CTkLabel(
                self,
                text=detalle,
                font=("Consolas", 8),
                text_color=TEXT_SECONDARY,
                anchor="w",
                wraplength=850,
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
# Panel principal
# ============================================================

class PanelDashboardDocentes(ctk.CTkFrame):

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
    # Datos
    # ========================================================

    def _cargar_datos(self):
        try:
            self.datos = obtener_dashboard_docentes()

        except Exception as error:
            print(
                "\n========== ERROR CARGANDO DASHBOARD DE DOCENTES =========="
            )
            print(error)
            print(
                "==========================================================\n"
            )

            self.datos = {
                "resumen": {},
                "mas_activos": [],
                "pdfs_por_docente": [],
                "carreras_por_docente": [],
                "laboratorios_por_docente": [],
                "actividad_mensual": [],
                "ultimos": [],
            }

    # ========================================================
    # Interfaz
    # ========================================================

    def _construir_interfaz(self):
        self._crear_encabezado()
        self._crear_indicadores()
        self._crear_docentes_mas_activos()
        self._crear_pdfs_por_docente()
        self._crear_carreras_por_docente()
        self._crear_laboratorios_por_docente()
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
            text="👨‍🏫 ESTADÍSTICAS DE DOCENTES",
            font=("Consolas", 18, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text=(
                "Participación, actividad y documentos asociados "
                "a los docentes responsables"
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
                uniform="indicadores_docentes",
            )

        tarjetas = (
            (
                "Docentes",
                formatear_numero(
                    resumen.get("total_docentes", 0)
                ),
                "👨‍🏫",
                ACCENT,
                "Docentes responsables diferentes",
            ),
            (
                "Participaciones",
                formatear_numero(
                    resumen.get("total_participaciones", 0)
                ),
                "📋",
                BLUE,
                "Registros de prácticas con docente",
            ),
            (
                "Docentes con PDF",
                formatear_numero(
                    resumen.get("docentes_con_pdf", 0)
                ),
                "📄",
                YELLOW,
                "Docentes asociados a documentos PDF",
            ),
            (
                "Más activo",
                resumen.get(
                    "docente_mas_activo",
                    "Sin registros",
                ),
                "⭐",
                PURPLE,
                (
                    f"{formatear_numero(resumen.get(
                        'participaciones_docente_mas_activo',
                        0
                    ))} participaciones"
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
    # Docentes más activos
    # ========================================================

    def _crear_docentes_mas_activos(self):

        registros = self.datos.get(
            "mas_activos",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Docentes con mayor participación",
            subtitulo=(
                "Ranking según el número de prácticas de laboratorio"
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
                "No existen docentes registrados.",
            )
            return

        for indice, docente in enumerate(
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
                titulo=docente.get(
                    "docente",
                    "Sin nombre",
                ),
                valor=formatear_numero(
                    docente.get(
                        "participaciones",
                        0,
                    )
                ),
                detalle=(
                    f"{formatear_numero(docente.get('carreras', 0))} carreras · "
                    f"{formatear_numero(docente.get('laboratorios', 0))} "
                    f"laboratorios · "
                    f"{formatear_numero(docente.get('pdfs', 0))} PDF"
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
    # PDF por docente
    # ========================================================

    def _crear_pdfs_por_docente(self):

        registros = self.datos.get(
            "pdfs_por_docente",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Documentos PDF por docente",
            subtitulo=(
                "Comparación entre registros con documento y sin documento"
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
                "No existen datos de documentos por docente.",
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
                    "docente",
                    "Sin nombre",
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
                color=BLUE,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Carreras por docente
    # ========================================================

    def _crear_carreras_por_docente(self):

        registros = self.datos.get(
            "carreras_por_docente",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Carreras atendidas por docente",
            subtitulo=(
                "Cantidad de carreras diferentes asociadas a cada docente"
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
                "No existen carreras asociadas a docentes.",
            )
            return

        maximo = max(
            (
                item.get("cantidad_carreras", 0)
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "docente",
                    "Sin nombre",
                ),
                valor=item.get(
                    "cantidad_carreras",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{item.get('carreras', 'Sin carreras')} · "
                    f"{formatear_numero(item.get('participaciones', 0))} "
                    "participaciones"
                ),
                color=PURPLE,
            ).grid(
                row=indice,
                column=0,
                sticky="ew",
                pady=7,
            )

    # ========================================================
    # Laboratorios por docente
    # ========================================================

    def _crear_laboratorios_por_docente(self):

        registros = self.datos.get(
            "laboratorios_por_docente",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Laboratorios utilizados por docente",
            subtitulo=(
                "Número de laboratorios diferentes usados por cada docente"
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
                "No existen laboratorios asociados a docentes.",
            )
            return

        maximo = max(
            (
                item.get("cantidad_laboratorios", 0)
                for item in registros
            ),
            default=1,
        )

        for indice, item in enumerate(registros):

            BarraProporcional(
                seccion.contenido,
                titulo=item.get(
                    "docente",
                    "Sin nombre",
                ),
                valor=item.get(
                    "cantidad_laboratorios",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{item.get('laboratorios', 'Sin laboratorios')} · "
                    f"{formatear_numero(item.get('participaciones', 0))} "
                    "participaciones"
                ),
                color=ACCENT,
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
            "actividad_mensual",
            [],
        )

        seccion = SeccionDashboard(
            self,
            titulo="Actividad mensual de docentes",
            subtitulo=(
                "Participaciones registradas durante los últimos doce meses"
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
                "No existen registros mensuales.",
            )
            return

        maximo = max(
            (
                item.get("participaciones", 0)
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
                    "participaciones",
                    0,
                ),
                maximo=maximo,
                detalle=(
                    f"{formatear_numero(item.get('docentes', 0))} "
                    "docentes diferentes"
                ),
                color=YELLOW,
            ).grid(
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
            titulo="Últimas participaciones registradas",
            subtitulo=(
                "Prácticas recientes con docente responsable"
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
                "No existen participaciones recientes.",
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
            ("Docente", 190),
            ("Laboratorio", 190),
            ("Carrera", 150),
            ("Asignatura", 180),
            ("Fecha", 100),
            ("PDF", 60),
        )

        for indice, columna in enumerate(columnas):

            cabecera.grid_columnconfigure(
                indice,
                weight=1 if indice in (0, 1, 2, 3) else 0,
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
                item.get("docente", "Sin docente"),
                item.get("laboratorio", "Sin laboratorio"),
                item.get("carrera", "Sin carrera"),
                item.get("asignatura", "Sin asignatura"),
                formatear_fecha(item.get("fecha")),
                "Sí" if item.get("tiene_pdf") else "No",
            )

            for columna_indice, valor in enumerate(valores):

                fila.grid_columnconfigure(
                    columna_indice,
                    weight=(
                        1
                        if columna_indice in (0, 1, 2, 3)
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
                        if columna_indice == 5
                        and item.get("tiene_pdf")
                        else (
                            RED
                            if columna_indice == 5
                            else TEXT_PRIMARY
                        )
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
    # Actualizar
    # ========================================================

    def actualizar(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._cargar_datos()
        self._construir_interfaz()