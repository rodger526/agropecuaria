from datetime import date, datetime
import os
import webbrowser

import customtkinter as ctk

from database.dashboard.dashboard_laboratorios import (
    obtener_asignaturas_mas_utilizadas,
    obtener_carreras_laboratorios,
    obtener_docentes_con_mas_registros,
    obtener_laboratorios_mas_utilizados,
    obtener_laboratorios_por_carrera,
    obtener_laboratorios_por_mes,
    obtener_resumen_laboratorios,
    obtener_total_materiales_laboratorios,
    obtener_total_reactivos_laboratorios,
    obtener_ultimos_laboratorios,
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
WARNING = "#E0A84E"


# ============================================================
# Panel de laboratorios
# ============================================================

class PanelDashboardLaboratorios(ctk.CTkFrame):
    """
    Panel estadístico del módulo de laboratorios.

    Muestra:

        - Total de laboratorios
        - Registros con PDF
        - Registros sin PDF
        - Docentes
        - Carreras
        - Asignaturas
        - Laboratorios físicos
        - Registros del mes
        - Reactivos utilizados
        - Materiales utilizados
        - Laboratorios por mes
        - Laboratorios más utilizados
        - Asignaturas más utilizadas
        - Docentes con más registros
        - Últimos registros
    """

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=BG_DARK,
            corner_radius=0,
        )

        self.anio_actual = date.today().year
        self.carrera_actual = "Todas"

        self.resumen = {}
        self.laboratorios_mes = []
        self.laboratorios_utilizados = []
        self.asignaturas = []
        self.docentes = []
        self.carreras = []
        self.ultimos_laboratorios = []

        self.total_reactivos = 0
        self.total_materiales = 0

        self.combo_anio = None
        self.combo_carrera = None
        self.lbl_estado = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self._crear_encabezado()
        self._crear_contenedor()

        self.after(
            100,
            self.cargar_datos,
        )

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
            text="Estadísticas de laboratorios",
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
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(
            side="left",
            padx=(0, 6),
        )

        self.combo_anio = ctk.CTkComboBox(
            zona_filtros,
            width=100,
            height=35,
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
            font=("Consolas", 10),
            command=self._cambiar_anio,
        )

        self.combo_anio.set(
            str(self.anio_actual)
        )

        self.combo_anio.pack(
            side="left",
        )

        ctk.CTkLabel(
            zona_filtros,
            text="Carrera:",
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(
            side="left",
            padx=(12, 6),
        )

        self.combo_carrera = ctk.CTkComboBox(
            zona_filtros,
            width=220,
            height=35,
            values=["Todas"],
            state="readonly",
            fg_color=BG_CARD,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER,
            dropdown_text_color=TEXT_PRIMARY,
            font=("Consolas", 10),
            command=self._cambiar_carrera,
        )

        self.combo_carrera.set(
            "Todas"
        )

        self.combo_carrera.pack(
            side="left",
        )

        ctk.CTkButton(
            zona_filtros,
            text="↻ Actualizar",
            width=115,
            height=35,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 10, "bold"),
            corner_radius=7,
            command=self.cargar_datos,
        ).pack(
            side="left",
            padx=(10, 0),
        )

    def _crear_contenedor(self):
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
    # Carga de datos
    # ========================================================

    def cargar_datos(self):
        self._mostrar_estado(
            "Consultando información...",
            TEXT_SECONDARY,
        )

        self.update_idletasks()

        try:
            carreras_disponibles = (
                obtener_carreras_laboratorios()
            )

            if not carreras_disponibles:
                carreras_disponibles = ["Todas"]

            self.combo_carrera.configure(
                values=carreras_disponibles
            )

            carrera_seleccionada = (
                self.combo_carrera.get()
            )

            if carrera_seleccionada not in carreras_disponibles:
                carrera_seleccionada = "Todas"

                self.combo_carrera.set(
                    carrera_seleccionada
                )

            self.carrera_actual = carrera_seleccionada

            try:
                self.anio_actual = int(
                    self.combo_anio.get()
                )
            except (TypeError, ValueError):
                self.anio_actual = date.today().year

            self.resumen = obtener_resumen_laboratorios(
                anio=self.anio_actual,
                carrera=self.carrera_actual,
            )

            self.total_reactivos = (
                obtener_total_reactivos_laboratorios(
                    anio=self.anio_actual,
                    carrera=self.carrera_actual,
                )
            )

            self.total_materiales = (
                obtener_total_materiales_laboratorios(
                    anio=self.anio_actual,
                    carrera=self.carrera_actual,
                )
            )

            self.laboratorios_mes = obtener_laboratorios_por_mes(
                anio=self.anio_actual,
                carrera=self.carrera_actual,
            )

            self.laboratorios_utilizados = (
                obtener_laboratorios_mas_utilizados(
                    anio=self.anio_actual,
                    carrera=self.carrera_actual,
                    limite=8,
                )
            )

            self.asignaturas = obtener_asignaturas_mas_utilizadas(
                anio=self.anio_actual,
                carrera=self.carrera_actual,
                limite=8,
            )

            self.docentes = obtener_docentes_con_mas_registros(
                anio=self.anio_actual,
                carrera=self.carrera_actual,
                limite=8,
            )

            self.carreras = obtener_laboratorios_por_carrera(
                anio=self.anio_actual,
                limite=8,
            )

            self.ultimos_laboratorios = (
                obtener_ultimos_laboratorios(
                    anio=self.anio_actual,
                    carrera=self.carrera_actual,
                    limite=10,
                )
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
                "\n"
                "========== ERROR CARGANDO DASHBOARD "
                "DE LABORATORIOS =========="
            )
            print(error)
            print(
                "==========================================\n"
            )

            self._mostrar_estado(
                "No fue posible cargar las estadísticas.",
                NEGATIVE,
            )

            self._mostrar_error(
                str(error)
            )

    def _cambiar_anio(self, valor):
        try:
            self.anio_actual = int(valor)
        except (TypeError, ValueError):
            self.anio_actual = date.today().year

        self.cargar_datos()

    def _cambiar_carrera(self, valor):
        self.carrera_actual = valor or "Todas"
        self.cargar_datos()

    def _mostrar_estado(self, mensaje, color):
        if self.lbl_estado is not None:
            self.lbl_estado.configure(
                text=mensaje,
                text_color=color,
            )

    # ========================================================
    # Construcción
    # ========================================================

    def _dibujar_dashboard(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

        self._crear_tarjetas()
        self._crear_grafico_mensual()
        self._crear_seccion_listas()
        self._crear_seccion_docentes_carreras()
        self._crear_tabla_ultimos_laboratorios()

    # ========================================================
    # Tarjetas
    # ========================================================

    def _crear_tarjetas(self):
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
                uniform="tarjetas_laboratorio",
            )

        total = self.resumen.get(
            "total_laboratorios",
            0,
        )

        con_pdf = self.resumen.get(
            "con_pdf",
            0,
        )

        porcentaje_pdf = 0

        if total > 0:
            porcentaje_pdf = round(
                (con_pdf / total) * 100,
                1,
            )

        tarjetas = [
            {
                "titulo": "Registros",
                "valor": total,
                "icono": "🧪",
                "descripcion": "Laboratorios registrados",
            },
            {
                "titulo": "Con PDF",
                "valor": con_pdf,
                "icono": "📄",
                "descripcion": f"{porcentaje_pdf}% con documento",
                "color": POSITIVE,
            },
            {
                "titulo": "Sin PDF",
                "valor": self.resumen.get(
                    "sin_pdf",
                    0,
                ),
                "icono": "⚠",
                "descripcion": "Registros sin documento",
                "color": WARNING,
            },
            {
                "titulo": "Este mes",
                "valor": self.resumen.get(
                    "registros_este_mes",
                    0,
                ),
                "icono": "📅",
                "descripcion": "Registros del mes actual",
            },
            {
                "titulo": "Docentes",
                "valor": self.resumen.get(
                    "docentes",
                    0,
                ),
                "icono": "👨‍🏫",
                "descripcion": "Docentes responsables",
            },
            {
                "titulo": "Asignaturas",
                "valor": self.resumen.get(
                    "asignaturas",
                    0,
                ),
                "icono": "📚",
                "descripcion": "Asignaturas diferentes",
            },
            {
                "titulo": "Reactivos",
                "valor": self._formatear_numero(
                    self.total_reactivos
                ),
                "icono": "⚗️",
                "descripcion": "Cantidad acumulada",
            },
            {
                "titulo": "Materiales",
                "valor": self._formatear_numero(
                    self.total_materiales
                ),
                "icono": "📦",
                "descripcion": "Cantidad acumulada",
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
                    "color",
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
        tarjeta = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            height=135,
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
            font=("Segoe UI Emoji", 21),
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
            font=("Consolas", 26, "bold"),
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

    def _crear_grafico_mensual(self):
        panel = self._crear_panel(
            self.contenido,
            titulo=f"Laboratorios registrados por mes — {self.anio_actual}",
            descripcion=(
                "Cantidad de registros realizados durante cada mes."
            ),
        )

        panel.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=5,
            pady=(0, 12),
        )

        zona = ctk.CTkFrame(
            panel,
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
                for registro in self.laboratorios_mes
            ]
            or [1]
        )

        if maximo <= 0:
            maximo = 1

        for registro in self.laboratorios_mes:
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
                text=registro.get(
                    "mes",
                    "",
                )[:3],
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
                registro.get(
                    "total",
                    0,
                )
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

            ctk.CTkLabel(
                fila,
                text=str(total),
                width=65,
                font=("Consolas", 10, "bold"),
                text_color=TEXT_PRIMARY,
                anchor="e",
            ).pack(
                side="right",
            )

    # ========================================================
    # Laboratorios y asignaturas
    # ========================================================

    def _crear_seccion_listas(self):
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
            uniform="listas_lab",
        )

        contenedor.grid_columnconfigure(
            1,
            weight=1,
            uniform="listas_lab",
        )

        panel_laboratorios = self._crear_panel(
            contenedor,
            titulo="Laboratorios más utilizados",
            descripcion=(
                "Espacios físicos con mayor cantidad de registros."
            ),
        )

        panel_laboratorios.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(5, 6),
        )

        self._crear_lista_ranking(
            parent=panel_laboratorios,
            datos=self.laboratorios_utilizados,
            clave_nombre="laboratorio",
        )

        panel_asignaturas = self._crear_panel(
            contenedor,
            titulo="Asignaturas con más registros",
            descripcion=(
                "Asignaturas que más utilizaron laboratorios."
            ),
        )

        panel_asignaturas.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 5),
        )

        self._crear_lista_ranking(
            parent=panel_asignaturas,
            datos=self.asignaturas,
            clave_nombre="asignatura",
        )

    # ========================================================
    # Docentes y carreras
    # ========================================================

    def _crear_seccion_docentes_carreras(self):
        contenedor = ctk.CTkFrame(
            self.contenido,
            fg_color="transparent",
        )

        contenedor.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )

        contenedor.grid_columnconfigure(
            0,
            weight=1,
            uniform="listas_secundarias",
        )

        contenedor.grid_columnconfigure(
            1,
            weight=1,
            uniform="listas_secundarias",
        )

        panel_docentes = self._crear_panel(
            contenedor,
            titulo="Docentes con más registros",
            descripcion=(
                "Participación de docentes responsables."
            ),
        )

        panel_docentes.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(5, 6),
        )

        self._crear_lista_ranking(
            parent=panel_docentes,
            datos=self.docentes,
            clave_nombre="docente",
        )

        panel_carreras = self._crear_panel(
            contenedor,
            titulo="Laboratorios por carrera",
            descripcion=(
                "Cantidad total de registros por carrera."
            ),
        )

        panel_carreras.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 5),
        )

        self._crear_lista_ranking(
            parent=panel_carreras,
            datos=self.carreras,
            clave_nombre="carrera",
        )

    def _crear_lista_ranking(
        self,
        parent,
        datos,
        clave_nombre,
    ):
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
                "No existen datos disponibles.",
            )
            return

        for indice, registro in enumerate(
            datos,
            start=1,
        ):
            nombre = registro.get(
                clave_nombre,
                "Sin especificar",
            )

            total = registro.get(
                "total",
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
                width=28,
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
                    34,
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
                text=str(total),
                width=65,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
                anchor="e",
            ).pack(
                side="right",
                padx=(4, 10),
                pady=8,
            )

    # ========================================================
    # Tabla de últimos laboratorios
    # ========================================================

    def _crear_tabla_ultimos_laboratorios(self):
        panel = self._crear_panel(
            self.contenido,
            titulo="Últimos laboratorios registrados",
            descripcion=(
                "Información reciente del módulo de laboratorios."
            ),
        )

        panel.grid(
            row=4,
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
            ("Código", 150),
            ("Fecha", 105),
            ("Carrera", 170),
            ("Laboratorio", 170),
            ("Asignatura", 180),
            ("Docente", 180),
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

        if not self.ultimos_laboratorios:
            self._crear_mensaje_vacio(
                tabla,
                "No existen laboratorios disponibles.",
            )
            return

        for indice, registro in enumerate(
            self.ultimos_laboratorios
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
                    self._recortar_texto(
                        registro.get(
                            "codigo",
                            "",
                        ),
                        20,
                    ),
                    150,
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
                        23,
                    ),
                    170,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "laboratorio",
                            "",
                        ),
                        23,
                    ),
                    170,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "asignatura",
                            "",
                        ),
                        25,
                    ),
                    180,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "docente",
                            "",
                        ),
                        25,
                    ),
                    180,
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
                boton = ctk.CTkButton(
                    fila,
                    text="Abrir",
                    width=70,
                    height=27,
                    fg_color=ACCENT,
                    hover_color=ACCENT_DARK,
                    text_color=BG_DARK,
                    font=("Consolas", 9, "bold"),
                    corner_radius=5,
                    command=lambda ruta=pdf_url: self._abrir_pdf(
                        ruta
                    ),
                )
            else:
                boton = ctk.CTkButton(
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

            boton.pack(
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
        ctk.CTkLabel(
            parent,
            text=mensaje,
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=30,
        )

    def _mostrar_error(self, error):
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
            text="No se pudo cargar el dashboard de laboratorios",
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
        if not ruta:
            return

        try:
            ruta = str(ruta).strip()

            if ruta.lower().startswith(
                ("http://", "https://")
            ):
                webbrowser.open(ruta)
                return

            if os.path.exists(ruta):
                os.startfile(ruta)
                return

            print(
                f"No se encontró el PDF: {ruta}"
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
        texto = str(
            texto or ""
        ).strip()

        if len(texto) <= limite:
            return texto

        return texto[:limite - 3] + "..."