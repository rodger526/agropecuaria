from datetime import date, datetime
import webbrowser

import customtkinter as ctk

from database.dashboard.dashboard_general import (
    obtener_anios_disponibles,
    obtener_reactivos_mas_utilizados,
    obtener_registros_por_carrera,
    obtener_registros_por_mes,
    obtener_resumen_general,
    obtener_ultimos_registros,
)


# ============================================================
# Colores
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

POSITIVE = "#4CAF7D"
NEGATIVE = "#E05252"
NEUTRAL = "#E0A84E"


# ============================================================
# Panel general
# ============================================================

class PanelDashboardGeneral(ctk.CTkFrame):
    """
    Panel visual de estadísticas generales.

    Este panel obtiene información de:

        - Laboratorios
        - Prácticas
        - PDFs
        - Reactivos
        - Materiales
        - Docentes
        - Carreras
        - Registros mensuales
    """

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=BG_DARK,
            corner_radius=0,
        )

        self.anio_actual = date.today().year

        self.resumen = {}
        self.registros_mensuales = []
        self.registros_carrera = []
        self.reactivos = []
        self.ultimos_registros = []

        self.combo_anio = None
        self.lbl_estado = None

        self.grid_columnconfigure(0, weight=1)

        self._crear_encabezado_filtros()
        self._crear_contenedor_contenido()

        self.after(
            100,
            self.cargar_datos,
        )

    # ========================================================
    # Encabezado y filtros
    # ========================================================

    def _crear_encabezado_filtros(self):
        """
        Crea la zona superior con el filtro de año.
        """

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
            padx=4,
            pady=(4, 12),
        )

        encabezado.grid_columnconfigure(
            0,
            weight=1,
        )

        zona_titulo = ctk.CTkFrame(
            encabezado,
            fg_color="transparent",
        )

        zona_titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=15,
        )

        ctk.CTkLabel(
            zona_titulo,
            text="Resumen del sistema",
            font=("Consolas", 17, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(
            anchor="w",
        )

        self.lbl_estado = ctk.CTkLabel(
            zona_titulo,
            text="Consultando información...",
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
        )

        self.lbl_estado.pack(
            anchor="w",
            pady=(3, 0),
        )

        zona_filtros = ctk.CTkFrame(
            encabezado,
            fg_color="transparent",
        )

        zona_filtros.grid(
            row=0,
            column=1,
            sticky="e",
            padx=18,
            pady=15,
        )

        ctk.CTkLabel(
            zona_filtros,
            text="Año:",
            font=("Consolas", 11, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.combo_anio = ctk.CTkComboBox(
            zona_filtros,
            width=115,
            height=36,
            values=[str(self.anio_actual)],
            state="readonly",
            fg_color=BG_CARD,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER,
            dropdown_text_color=TEXT_PRIMARY,
            font=("Consolas", 11),
            command=self._cambiar_anio,
        )

        self.combo_anio.set(
            str(self.anio_actual)
        )

        self.combo_anio.pack(
            side="left",
        )

        ctk.CTkButton(
            zona_filtros,
            text="↻ Actualizar",
            width=120,
            height=36,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 11, "bold"),
            corner_radius=7,
            command=self.cargar_datos,
        ).pack(
            side="left",
            padx=(10, 0),
        )

    def _crear_contenedor_contenido(self):
        """
        Crea el contenedor donde se dibujará el dashboard.
        """

        self.contenido = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.contenido.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.contenido.grid_columnconfigure(
            0,
            weight=1,
        )

    # ========================================================
    # Carga de información
    # ========================================================

    def cargar_datos(self):
        """
        Consulta PostgreSQL y vuelve a construir el panel.
        """

        self._mostrar_estado(
            "Consultando información...",
            TEXT_SECONDARY,
        )

        self.update_idletasks()

        try:
            anios = obtener_anios_disponibles()

            if not anios:
                anios = [
                    self.anio_actual
                ]

            valores_anios = [
                str(anio)
                for anio in anios
            ]

            self.combo_anio.configure(
                values=valores_anios
            )

            anio_seleccionado = self.combo_anio.get()

            if anio_seleccionado not in valores_anios:
                anio_seleccionado = valores_anios[0]

                self.combo_anio.set(
                    anio_seleccionado
                )

            self.anio_actual = int(
                anio_seleccionado
            )

            self.resumen = obtener_resumen_general()

            self.registros_mensuales = obtener_registros_por_mes(
                self.anio_actual
            )

            self.registros_carrera = obtener_registros_por_carrera(
                limite=8
            )

            self.reactivos = obtener_reactivos_mas_utilizados(
                limite=8
            )

            self.ultimos_registros = obtener_ultimos_registros(
                limite=10
            )

            self._dibujar_dashboard()

            hora = datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

            self._mostrar_estado(
                f"Información actualizada: {hora}",
                ACCENT,
            )

        except Exception as error:
            print(
                "\n========== ERROR CARGANDO DASHBOARD =========="
            )
            print(error)
            print(
                "==============================================\n"
            )

            self._mostrar_estado(
                "No fue posible cargar las estadísticas.",
                NEGATIVE,
            )

            self._mostrar_error(
                str(error)
            )

    def _cambiar_anio(self, valor):
        """
        Se ejecuta cuando se selecciona otro año.
        """

        try:
            self.anio_actual = int(valor)
        except (TypeError, ValueError):
            self.anio_actual = date.today().year

        self.cargar_datos()

    def _mostrar_estado(
        self,
        mensaje,
        color,
    ):
        """
        Actualiza el mensaje de estado.
        """

        if self.lbl_estado is not None:
            self.lbl_estado.configure(
                text=mensaje,
                text_color=color,
            )

    # ========================================================
    # Construcción visual
    # ========================================================

    def _dibujar_dashboard(self):
        """
        Limpia y vuelve a construir todas las secciones.
        """

        for widget in self.contenido.winfo_children():
            widget.destroy()

        self._crear_tarjetas_principales()
        self._crear_seccion_graficos_principales()
        self._crear_seccion_graficos_secundarios()
        self._crear_tabla_ultimos_registros()

    # ========================================================
    # Tarjetas KPI
    # ========================================================

    def _crear_tarjetas_principales(self):
        """
        Crea ocho tarjetas con indicadores principales.
        """

        contenedor = ctk.CTkFrame(
            self.contenido,
            fg_color="transparent",
        )

        contenedor.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )

        for columna in range(4):
            contenedor.grid_columnconfigure(
                columna,
                weight=1,
                uniform="kpis",
            )

        variacion = self.resumen.get(
            "variacion_mensual",
            0,
        )

        descripcion_variacion = self._texto_variacion(
            variacion
        )

        tarjetas = [
            {
                "titulo": "Laboratorios",
                "valor": self.resumen.get(
                    "total_laboratorios",
                    0,
                ),
                "icono": "🧪",
                "descripcion": "Registros de laboratorio",
            },
            {
                "titulo": "Prácticas",
                "valor": self.resumen.get(
                    "total_practicas",
                    0,
                ),
                "icono": "📋",
                "descripcion": "Prácticas registradas",
            },
            {
                "titulo": "PDF generados",
                "valor": self.resumen.get(
                    "total_pdfs",
                    0,
                ),
                "icono": "📄",
                "descripcion": "Documentos disponibles",
            },
            {
                "titulo": "Reactivos",
                "valor": self._formatear_numero(
                    self.resumen.get(
                        "total_reactivos",
                        0,
                    )
                ),
                "icono": "⚗️",
                "descripcion": "Cantidad acumulada",
            },
            {
                "titulo": "Materiales",
                "valor": self._formatear_numero(
                    self.resumen.get(
                        "total_materiales",
                        0,
                    )
                ),
                "icono": "📦",
                "descripcion": "Cantidad acumulada",
            },
            {
                "titulo": "Docentes",
                "valor": self.resumen.get(
                    "total_docentes",
                    0,
                ),
                "icono": "👨‍🏫",
                "descripcion": "Docentes diferentes",
            },
            {
                "titulo": "Carreras",
                "valor": self.resumen.get(
                    "total_carreras",
                    0,
                ),
                "icono": "🎓",
                "descripcion": "Carreras registradas",
            },
            {
                "titulo": "Este mes",
                "valor": self.resumen.get(
                    "registros_este_mes",
                    0,
                ),
                "icono": "📅",
                "descripcion": descripcion_variacion,
                "color_descripcion": self._color_variacion(
                    variacion
                ),
            },
        ]

        for indice, datos in enumerate(tarjetas):
            fila = indice // 4
            columna = indice % 4

            tarjeta = self._crear_tarjeta_kpi(
                parent=contenedor,
                titulo=datos["titulo"],
                valor=datos["valor"],
                icono=datos["icono"],
                descripcion=datos["descripcion"],
                color_descripcion=datos.get(
                    "color_descripcion",
                    TEXT_SECONDARY,
                ),
            )

            tarjeta.grid(
                row=fila,
                column=columna,
                sticky="nsew",
                padx=5,
                pady=5,
            )

    def _crear_tarjeta_kpi(
        self,
        parent,
        titulo,
        valor,
        icono,
        descripcion,
        color_descripcion=TEXT_SECONDARY,
    ):
        """
        Crea una tarjeta KPI.
        """

        tarjeta = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            height=138,
        )

        tarjeta.grid_propagate(False)

        cabecera = ctk.CTkFrame(
            tarjeta,
            fg_color="transparent",
        )

        cabecera.pack(
            fill="x",
            padx=15,
            pady=(14, 3),
        )

        ctk.CTkLabel(
            cabecera,
            text=icono,
            font=("Segoe UI Emoji", 22),
            text_color=ACCENT,
        ).pack(
            side="left",
        )

        ctk.CTkLabel(
            cabecera,
            text=titulo.upper(),
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        ctk.CTkLabel(
            tarjeta,
            text=str(valor),
            font=("Consolas", 27, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(
            fill="x",
            padx=15,
            pady=(2, 0),
        )

        ctk.CTkLabel(
            tarjeta,
            text=descripcion,
            font=("Consolas", 9),
            text_color=color_descripcion,
            anchor="w",
        ).pack(
            fill="x",
            padx=15,
            pady=(4, 10),
        )

        return tarjeta

    # ========================================================
    # Gráfico mensual
    # ========================================================

    def _crear_seccion_graficos_principales(self):
        """
        Crea el gráfico grande de registros mensuales.
        """

        panel = self._crear_panel(
            self.contenido,
            titulo=f"Registros por mes — {self.anio_actual}",
            descripcion=(
                "Comparación mensual de laboratorios y prácticas."
            ),
        )

        panel.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=5,
            pady=(0, 12),
        )

        self._crear_grafico_mensual(
            panel
        )

    def _crear_grafico_mensual(self, parent):
        """
        Crea un gráfico horizontal usando componentes
        CustomTkinter.
        """

        zona = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        zona.pack(
            fill="x",
            padx=18,
            pady=(4, 18),
        )

        maximo = max(
            [
                registro.get("total", 0)
                for registro in self.registros_mensuales
            ]
            or [1]
        )

        if maximo <= 0:
            maximo = 1

        for registro in self.registros_mensuales:
            fila = ctk.CTkFrame(
                zona,
                fg_color="transparent",
            )

            fila.pack(
                fill="x",
                pady=4,
            )

            ctk.CTkLabel(
                fila,
                text=registro.get("mes", "")[:3],
                width=42,
                font=("Consolas", 10, "bold"),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).pack(
                side="left",
            )

            contenedor_barra = ctk.CTkFrame(
                fila,
                fg_color=BG_DARK,
                corner_radius=5,
                height=24,
            )

            contenedor_barra.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(6, 8),
            )

            contenedor_barra.pack_propagate(False)

            total = int(
                registro.get("total", 0)
            )

            porcentaje = total / maximo

            ancho_estimado = max(
                1,
                int(porcentaje * 700),
            )

            if total > 0:
                barra = ctk.CTkFrame(
                    contenedor_barra,
                    width=ancho_estimado,
                    height=24,
                    fg_color=ACCENT,
                    corner_radius=5,
                )

                barra.pack(
                    side="left",
                )

                barra.pack_propagate(False)

            detalle = (
                f"{total}  "
                f"(L: {registro.get('laboratorios', 0)} | "
                f"P: {registro.get('practicas', 0)})"
            )

            ctk.CTkLabel(
                fila,
                text=detalle,
                width=145,
                font=("Consolas", 9),
                text_color=TEXT_PRIMARY,
                anchor="e",
            ).pack(
                side="right",
            )

    # ========================================================
    # Gráficos secundarios
    # ========================================================

    def _crear_seccion_graficos_secundarios(self):
        """
        Crea los paneles de carrera y reactivos.
        """

        contenedor = ctk.CTkFrame(
            self.contenido,
            fg_color="transparent",
        )

        contenedor.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )

        contenedor.grid_columnconfigure(
            0,
            weight=1,
            uniform="graficos",
        )

        contenedor.grid_columnconfigure(
            1,
            weight=1,
            uniform="graficos",
        )

        panel_carreras = self._crear_panel(
            contenedor,
            titulo="Registros por carrera",
            descripcion=(
                "Laboratorios y prácticas agrupados por carrera."
            ),
        )

        panel_carreras.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(5, 6),
        )

        self._crear_lista_barras(
            parent=panel_carreras,
            datos=self.registros_carrera,
            clave_nombre="carrera",
            clave_valor="total",
            mostrar_unidad=False,
        )

        panel_reactivos = self._crear_panel(
            contenedor,
            titulo="Reactivos más utilizados",
            descripcion=(
                "Cantidades acumuladas registradas en prácticas."
            ),
        )

        panel_reactivos.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 5),
        )

        self._crear_lista_reactivos(
            panel_reactivos
        )

    def _crear_lista_barras(
        self,
        parent,
        datos,
        clave_nombre,
        clave_valor,
        mostrar_unidad=False,
    ):
        """
        Dibuja una lista de barras sencilla.
        """

        zona = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        zona.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(4, 16),
        )

        if not datos:
            self._crear_mensaje_vacio(
                zona,
                "No existen datos disponibles."
            )
            return

        maximo = max(
            [
                float(
                    registro.get(
                        clave_valor,
                        0,
                    )
                    or 0
                )
                for registro in datos
            ]
            or [1]
        )

        if maximo <= 0:
            maximo = 1

        for indice, registro in enumerate(datos, start=1):
            nombre = str(
                registro.get(
                    clave_nombre,
                    "Sin especificar",
                )
            )

            valor = registro.get(
                clave_valor,
                0,
            )

            fila = ctk.CTkFrame(
                zona,
                fg_color=(
                    BG_CARD
                    if indice % 2 != 0
                    else BG_PANEL
                ),
                corner_radius=6,
            )

            fila.pack(
                fill="x",
                pady=3,
            )

            ctk.CTkLabel(
                fila,
                text=str(indice),
                width=26,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
            ).pack(
                side="left",
                padx=(8, 3),
                pady=8,
            )

            ctk.CTkLabel(
                fila,
                text=self._recortar_texto(
                    nombre,
                    30,
                ),
                font=("Consolas", 10),
                text_color=TEXT_PRIMARY,
                anchor="w",
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=4,
                pady=8,
            )

            texto_valor = self._formatear_numero(
                valor
            )

            if mostrar_unidad:
                texto_valor = f"{texto_valor}"

            ctk.CTkLabel(
                fila,
                text=texto_valor,
                width=75,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
                anchor="e",
            ).pack(
                side="right",
                padx=(4, 10),
                pady=8,
            )

    def _crear_lista_reactivos(self, parent):
        """
        Muestra los reactivos más utilizados con su unidad.
        """

        zona = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        zona.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(4, 16),
        )

        if not self.reactivos:
            self._crear_mensaje_vacio(
                zona,
                "No existen reactivos registrados."
            )
            return

        for indice, reactivo in enumerate(
            self.reactivos,
            start=1,
        ):
            nombre = reactivo.get(
                "reactivo",
                "Sin especificar",
            )

            cantidad = self._formatear_numero(
                reactivo.get(
                    "cantidad",
                    0,
                )
            )

            unidad = reactivo.get(
                "unidad",
                "",
            )

            valor = (
                f"{cantidad} {unidad}".strip()
            )

            fila = ctk.CTkFrame(
                zona,
                fg_color=(
                    BG_CARD
                    if indice % 2 != 0
                    else BG_PANEL
                ),
                corner_radius=6,
            )

            fila.pack(
                fill="x",
                pady=3,
            )

            ctk.CTkLabel(
                fila,
                text=str(indice),
                width=26,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
            ).pack(
                side="left",
                padx=(8, 3),
                pady=8,
            )

            ctk.CTkLabel(
                fila,
                text=self._recortar_texto(
                    nombre,
                    28,
                ),
                font=("Consolas", 10),
                text_color=TEXT_PRIMARY,
                anchor="w",
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=4,
                pady=8,
            )

            ctk.CTkLabel(
                fila,
                text=valor,
                width=100,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
                anchor="e",
            ).pack(
                side="right",
                padx=(4, 10),
                pady=8,
            )

    # ========================================================
    # Últimos registros
    # ========================================================

    def _crear_tabla_ultimos_registros(self):
        """
        Crea la tabla con los últimos registros.
        """

        panel = self._crear_panel(
            self.contenido,
            titulo="Últimos registros",
            descripcion=(
                "Últimos laboratorios y prácticas registrados."
            ),
        )

        panel.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=5,
            pady=(0, 12),
        )

        tabla = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        tabla.pack(
            fill="x",
            padx=16,
            pady=(4, 18),
        )

        columnas = [
            ("Módulo", 95),
            ("Código", 110),
            ("Fecha", 105),
            ("Carrera", 150),
            ("Asignatura", 190),
            ("Responsable", 170),
            ("PDF", 80),
        ]

        cabecera = ctk.CTkFrame(
            tabla,
            fg_color=BG_DARK,
            corner_radius=6,
        )

        cabecera.pack(
            fill="x",
            pady=(0, 5),
        )

        for titulo, ancho in columnas:
            ctk.CTkLabel(
                cabecera,
                text=titulo.upper(),
                width=ancho,
                font=("Consolas", 9, "bold"),
                text_color=TEXT_SECONDARY,
                anchor="w",
            ).pack(
                side="left",
                padx=5,
                pady=9,
            )

        if not self.ultimos_registros:
            self._crear_mensaje_vacio(
                tabla,
                "No existen registros disponibles."
            )
            return

        for indice, registro in enumerate(
            self.ultimos_registros
        ):
            fila = ctk.CTkFrame(
                tabla,
                fg_color=(
                    BG_CARD
                    if indice % 2 == 0
                    else BG_PANEL
                ),
                corner_radius=5,
            )

            fila.pack(
                fill="x",
                pady=2,
            )

            fecha = registro.get(
                "fecha"
            )

            if hasattr(fecha, "strftime"):
                fecha_texto = fecha.strftime(
                    "%d/%m/%Y"
                )
            else:
                fecha_texto = str(
                    fecha or ""
                )

            valores = [
                (
                    registro.get(
                        "modulo",
                        "",
                    ),
                    95,
                ),
                (
                    registro.get(
                        "codigo",
                        "",
                    ),
                    110,
                ),
                (
                    fecha_texto,
                    105,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "carrera",
                            "",
                        ),
                        22,
                    ),
                    150,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "asignatura",
                            "",
                        ),
                        27,
                    ),
                    190,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "responsable",
                            "",
                        ),
                        23,
                    ),
                    170,
                ),
            ]

            for valor, ancho in valores:
                ctk.CTkLabel(
                    fila,
                    text=str(valor or "—"),
                    width=ancho,
                    font=("Consolas", 9),
                    text_color=TEXT_PRIMARY,
                    anchor="w",
                ).pack(
                    side="left",
                    padx=5,
                    pady=8,
                )

            pdf_url = registro.get(
                "pdf_url",
                "",
            )

            if pdf_url:
                boton_pdf = ctk.CTkButton(
                    fila,
                    text="Abrir",
                    width=70,
                    height=27,
                    fg_color=ACCENT,
                    hover_color=ACCENT_DARK,
                    text_color=BG_DARK,
                    font=("Consolas", 9, "bold"),
                    corner_radius=5,
                    command=lambda url=pdf_url: self._abrir_pdf(
                        url
                    ),
                )
            else:
                boton_pdf = ctk.CTkButton(
                    fila,
                    text="Sin PDF",
                    width=70,
                    height=27,
                    fg_color="transparent",
                    hover_color=BG_CARD_HOVER,
                    border_width=1,
                    border_color=BORDER,
                    text_color=TEXT_SECONDARY,
                    font=("Consolas", 8),
                    corner_radius=5,
                    state="disabled",
                )

            boton_pdf.pack(
                side="left",
                padx=10,
                pady=5,
            )

    # ========================================================
    # Componentes reutilizables
    # ========================================================

    def _crear_panel(
        self,
        parent,
        titulo,
        descripcion="",
    ):
        """
        Crea un panel reutilizable.
        """

        panel = ctk.CTkFrame(
            parent,
            fg_color=BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )

        cabecera = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        cabecera.pack(
            fill="x",
            padx=18,
            pady=(16, 8),
        )

        ctk.CTkLabel(
            cabecera,
            text=titulo,
            font=("Consolas", 14, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(
            anchor="w",
        )

        if descripcion:
            ctk.CTkLabel(
                cabecera,
                text=descripcion,
                font=("Consolas", 9),
                text_color=TEXT_SECONDARY,
            ).pack(
                anchor="w",
                pady=(3, 0),
            )

        ctk.CTkFrame(
            panel,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 10),
        )

        return panel

    def _crear_mensaje_vacio(
        self,
        parent,
        mensaje,
    ):
        """
        Muestra un mensaje cuando no existen datos.
        """

        ctk.CTkLabel(
            parent,
            text=mensaje,
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=30,
        )

    def _mostrar_error(self, error):
        """
        Muestra el error dentro del área del dashboard.
        """

        for widget in self.contenido.winfo_children():
            widget.destroy()

        panel = ctk.CTkFrame(
            self.contenido,
            fg_color=BG_PANEL,
            border_width=1,
            border_color=NEGATIVE,
            corner_radius=10,
        )

        panel.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5,
            pady=5,
        )

        ctk.CTkLabel(
            panel,
            text="No se pudo cargar el dashboard",
            font=("Consolas", 16, "bold"),
            text_color=NEGATIVE,
        ).pack(
            pady=(25, 8),
        )

        ctk.CTkLabel(
            panel,
            text=error,
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
            wraplength=800,
            justify="center",
        ).pack(
            padx=25,
            pady=(0, 25),
        )

    # ========================================================
    # Utilidades
    # ========================================================

    def _abrir_pdf(self, ruta):
        """
        Abre una URL de PDF en el navegador.
        """

        if not ruta:
            return

        try:
            webbrowser.open(
                str(ruta)
            )

        except Exception as error:
            print(
                "\n========== ERROR ABRIENDO PDF =========="
            )
            print(error)
            print(
                "========================================\n"
            )

    @staticmethod
    def _formatear_numero(valor):
        """
        Formatea números para mostrarlos en tarjetas.
        """

        try:
            numero = float(valor)

            if numero.is_integer():
                return f"{int(numero):,}".replace(
                    ",",
                    ".",
                )

            return f"{numero:,.2f}".replace(
                ",",
                "X",
            ).replace(
                ".",
                ",",
            ).replace(
                "X",
                ".",
            )

        except (TypeError, ValueError):
            return str(valor or 0)

    @staticmethod
    def _recortar_texto(
        texto,
        limite,
    ):
        """
        Recorta textos demasiado largos.
        """

        texto = str(
            texto or ""
        ).strip()

        if len(texto) <= limite:
            return texto

        return texto[:limite - 3] + "..."

    @staticmethod
    def _texto_variacion(variacion):
        """
        Devuelve un texto según la variación mensual.
        """

        try:
            valor = float(variacion)
        except (TypeError, ValueError):
            valor = 0

        if valor > 0:
            return (
                f"▲ +{valor:.1f}% respecto al mes anterior"
            )

        if valor < 0:
            return (
                f"▼ {valor:.1f}% respecto al mes anterior"
            )

        return "Sin variación respecto al mes anterior"

    @staticmethod
    def _color_variacion(variacion):
        """
        Devuelve el color correspondiente a la variación.
        """

        try:
            valor = float(variacion)
        except (TypeError, ValueError):
            valor = 0

        if valor > 0:
            return POSITIVE

        if valor < 0:
            return NEGATIVE

        return NEUTRAL