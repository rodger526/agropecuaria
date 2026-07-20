from datetime import date, datetime
import webbrowser

import customtkinter as ctk

from database.dashboard.dashboard_practicas import (
    obtener_anios_practicas,
    obtener_estado_pdfs_practicas,
    obtener_practicas_por_asignatura,
    obtener_practicas_por_carrera,
    obtener_practicas_por_mes,
    obtener_practicas_por_revisor,
    obtener_practicas_por_semestre,
    obtener_practicas_por_tipo,
    obtener_resumen_practicas,
    obtener_ultimas_practicas,
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

BLUE = "#4A90E2"
PURPLE = "#9B6FE8"


# ============================================================
# Panel de prácticas
# ============================================================

class PanelDashboardPracticas(ctk.CTkFrame):
    """
    Panel visual del módulo de prácticas.

    Muestra:

        - Total de prácticas
        - Carreras
        - Asignaturas
        - Revisores
        - Semestres
        - Tipos de práctica
        - Registros mensuales
        - Estado de PDFs
        - Últimas prácticas
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
        self.registros_semestre = []
        self.registros_tipo = []
        self.registros_asignatura = []
        self.registros_revisor = []
        self.estado_pdfs = {}
        self.ultimas_practicas = []

        self.combo_anio = None
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
            text="Análisis de prácticas",
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
    # Carga de información
    # ========================================================

    def cargar_datos(self):
        self._mostrar_estado(
            "Consultando información...",
            TEXT_SECONDARY,
        )

        self.update_idletasks()

        try:
            anios = obtener_anios_practicas()

            if not anios:
                anios = [
                    date.today().year
                ]

            valores = [
                str(anio)
                for anio in anios
            ]

            self.combo_anio.configure(
                values=valores
            )

            anio_seleccionado = self.combo_anio.get()

            if anio_seleccionado not in valores:
                anio_seleccionado = valores[0]

                self.combo_anio.set(
                    anio_seleccionado
                )

            self.anio_actual = int(
                anio_seleccionado
            )

            self.resumen = obtener_resumen_practicas(
                self.anio_actual
            )

            self.registros_mensuales = obtener_practicas_por_mes(
                self.anio_actual
            )

            self.registros_carrera = obtener_practicas_por_carrera(
                limite=8,
                anio=self.anio_actual,
            )

            self.registros_semestre = obtener_practicas_por_semestre(
                anio=self.anio_actual
            )

            self.registros_tipo = obtener_practicas_por_tipo(
                limite=8,
                anio=self.anio_actual,
            )

            self.registros_asignatura = obtener_practicas_por_asignatura(
                limite=8,
                anio=self.anio_actual,
            )

            self.registros_revisor = obtener_practicas_por_revisor(
                limite=8,
                anio=self.anio_actual,
            )

            self.estado_pdfs = obtener_estado_pdfs_practicas(
                anio=self.anio_actual
            )

            self.ultimas_practicas = obtener_ultimas_practicas(
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
                "\n========== ERROR DASHBOARD PRÁCTICAS =========="
            )
            print(error)
            print(
                "================================================\n"
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
            self.anio_actual = int(
                valor
            )
        except (TypeError, ValueError):
            self.anio_actual = date.today().year

        self.cargar_datos()

    def _mostrar_estado(
        self,
        mensaje,
        color,
    ):
        if self.lbl_estado is not None:
            self.lbl_estado.configure(
                text=mensaje,
                text_color=color,
            )

    # ========================================================
    # Construcción general
    # ========================================================

    def _dibujar_dashboard(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

        self._crear_tarjetas_principales()
        self._crear_grafico_mensual()
        self._crear_seccion_distribucion()
        self._crear_seccion_academica()
        self._crear_seccion_pdf()
        self._crear_tabla_ultimas_practicas()

    # ========================================================
    # Tarjetas
    # ========================================================

    def _crear_tarjetas_principales(self):
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
                uniform="tarjetas_practicas",
            )

        variacion = self.resumen.get(
            "variacion_mensual",
            0,
        )

        tarjetas = [
            {
                "titulo": "Prácticas",
                "valor": self.resumen.get(
                    "total_practicas",
                    0,
                ),
                "icono": "📋",
                "descripcion": "Total registrado",
            },
            {
                "titulo": "Este año",
                "valor": self.resumen.get(
                    "total_anio",
                    0,
                ),
                "icono": "📅",
                "descripcion": f"Registros en {self.anio_actual}",
            },
            {
                "titulo": "Carreras",
                "valor": self.resumen.get(
                    "total_carreras",
                    0,
                ),
                "icono": "🎓",
                "descripcion": "Carreras diferentes",
            },
            {
                "titulo": "Asignaturas",
                "valor": self.resumen.get(
                    "total_asignaturas",
                    0,
                ),
                "icono": "📚",
                "descripcion": "Asignaturas diferentes",
            },
            {
                "titulo": "Revisores",
                "valor": self.resumen.get(
                    "total_revisores",
                    0,
                ),
                "icono": "👨‍🏫",
                "descripcion": "Ingenieros revisores",
            },
            {
                "titulo": "Semestres",
                "valor": self.resumen.get(
                    "total_semestres",
                    0,
                ),
                "icono": "🔢",
                "descripcion": "Semestres registrados",
            },
            {
                "titulo": "Tipos",
                "valor": self.resumen.get(
                    "total_tipos",
                    0,
                ),
                "icono": "🧩",
                "descripcion": "Tipos de práctica",
            },
            {
                "titulo": "Este mes",
                "valor": self.resumen.get(
                    "registros_este_mes",
                    0,
                ),
                "icono": "📈",
                "descripcion": self._texto_variacion(
                    variacion
                ),
                "color_descripcion": self._color_variacion(
                    variacion
                ),
            },
        ]

        for indice, datos in enumerate(
            tarjetas
        ):
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
        tarjeta = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            height=138,
        )

        tarjeta.grid_propagate(
            False
        )

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

    def _crear_grafico_mensual(self):
        panel = self._crear_panel(
            self.contenido,
            titulo=f"Prácticas registradas por mes — {self.anio_actual}",
            descripcion=(
                "Distribución mensual de las prácticas académicas."
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
                registro.get(
                    "total",
                    0,
                )
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

            nombre_mes = registro.get(
                "mes",
                "",
            )

            total = int(
                registro.get(
                    "total",
                    0,
                )
            )

            ctk.CTkLabel(
                fila,
                text=nombre_mes[:3],
                width=45,
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
                height=25,
            )

            contenedor_barra.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(6, 8),
            )

            contenedor_barra.pack_propagate(
                False
            )

            porcentaje = total / maximo

            ancho = max(
                1,
                int(porcentaje * 700),
            )

            if total > 0:
                barra = ctk.CTkFrame(
                    contenedor_barra,
                    width=ancho,
                    height=25,
                    fg_color=ACCENT,
                    corner_radius=5,
                )

                barra.pack(
                    side="left",
                )

                barra.pack_propagate(
                    False
                )

            ctk.CTkLabel(
                fila,
                text=str(total),
                width=60,
                font=("Consolas", 10, "bold"),
                text_color=TEXT_PRIMARY,
                anchor="e",
            ).pack(
                side="right",
            )

    # ========================================================
    # Distribución
    # ========================================================

    def _crear_seccion_distribucion(self):
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
            uniform="distribucion",
        )

        contenedor.grid_columnconfigure(
            1,
            weight=1,
            uniform="distribucion",
        )

        panel_carreras = self._crear_panel(
            contenedor,
            titulo="Prácticas por carrera",
            descripcion=(
                "Carreras con mayor número de prácticas."
            ),
        )

        panel_carreras.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(5, 6),
        )

        self._crear_lista_ranking(
            panel_carreras,
            self.registros_carrera,
            clave_nombre="carrera",
            clave_valor="total",
        )

        panel_tipos = self._crear_panel(
            contenedor,
            titulo="Prácticas por tipo",
            descripcion=(
                "Clasificación según el tipo registrado."
            ),
        )

        panel_tipos.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 5),
        )

        self._crear_lista_ranking(
            panel_tipos,
            self.registros_tipo,
            clave_nombre="tipo",
            clave_valor="total",
        )

    # ========================================================
    # Sección académica
    # ========================================================

    def _crear_seccion_academica(self):
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

        for columna in range(3):
            contenedor.grid_columnconfigure(
                columna,
                weight=1,
                uniform="academico",
            )

        panel_semestres = self._crear_panel(
            contenedor,
            titulo="Por semestre",
            descripcion="Distribución académica.",
        )

        panel_semestres.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(5, 4),
        )

        self._crear_lista_ranking(
            panel_semestres,
            self.registros_semestre,
            clave_nombre="nombre",
            clave_valor="total",
        )

        panel_asignaturas = self._crear_panel(
            contenedor,
            titulo="Asignaturas",
            descripcion="Asignaturas más registradas.",
        )

        panel_asignaturas.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=4,
        )

        self._crear_lista_ranking(
            panel_asignaturas,
            self.registros_asignatura,
            clave_nombre="asignatura",
            clave_valor="total",
        )

        panel_revisores = self._crear_panel(
            contenedor,
            titulo="Revisores",
            descripcion="Participación de revisores.",
        )

        panel_revisores.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=(4, 5),
        )

        self._crear_lista_ranking(
            panel_revisores,
            self.registros_revisor,
            clave_nombre="revisor",
            clave_valor="total",
        )

    # ========================================================
    # PDF
    # ========================================================

    def _crear_seccion_pdf(self):
        panel = self._crear_panel(
            self.contenido,
            titulo="Estado de documentos PDF",
            descripcion=(
                "Cantidad de prácticas con documento generado."
            ),
        )

        panel.grid(
            row=4,
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

        zona.grid_columnconfigure(
            0,
            weight=1,
            uniform="pdfs",
        )

        zona.grid_columnconfigure(
            1,
            weight=1,
            uniform="pdfs",
        )

        zona.grid_columnconfigure(
            2,
            weight=1,
            uniform="pdfs",
        )

        con_pdf = self.estado_pdfs.get(
            "con_pdf",
            0,
        )

        sin_pdf = self.estado_pdfs.get(
            "sin_pdf",
            0,
        )

        porcentaje = self.estado_pdfs.get(
            "porcentaje_con_pdf",
            0,
        )

        self._crear_tarjeta_resumen(
            zona,
            columna=0,
            titulo="CON PDF",
            valor=con_pdf,
            descripcion="Documentos disponibles",
            color=ACCENT,
        )

        self._crear_tarjeta_resumen(
            zona,
            columna=1,
            titulo="SIN PDF",
            valor=sin_pdf,
            descripcion="Documentos pendientes",
            color=NEGATIVE,
        )

        self._crear_tarjeta_resumen(
            zona,
            columna=2,
            titulo="COBERTURA",
            valor=f"{porcentaje:.1f}%",
            descripcion="Prácticas documentadas",
            color=BLUE,
        )

    def _crear_tarjeta_resumen(
        self,
        parent,
        columna,
        titulo,
        valor,
        descripcion,
        color,
    ):
        tarjeta = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
        )

        tarjeta.grid(
            row=0,
            column=columna,
            sticky="nsew",
            padx=5,
            pady=3,
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(
            anchor="w",
            padx=15,
            pady=(14, 4),
        )

        ctk.CTkLabel(
            tarjeta,
            text=str(valor),
            font=("Consolas", 25, "bold"),
            text_color=color,
        ).pack(
            anchor="w",
            padx=15,
        )

        ctk.CTkLabel(
            tarjeta,
            text=descripcion,
            font=("Consolas", 9),
            text_color=TEXT_SECONDARY,
        ).pack(
            anchor="w",
            padx=15,
            pady=(4, 14),
        )

    # ========================================================
    # Ranking reutilizable
    # ========================================================

    def _crear_lista_ranking(
        self,
        parent,
        datos,
        clave_nombre,
        clave_valor,
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
                "No existen datos disponibles."
            )
            return

        for indice, registro in enumerate(
            datos,
            start=1,
        ):
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
                text=str(valor),
                width=60,
                font=("Consolas", 10, "bold"),
                text_color=ACCENT,
                anchor="e",
            ).pack(
                side="right",
                padx=(4, 10),
                pady=8,
            )

    # ========================================================
    # Últimas prácticas
    # ========================================================

    def _crear_tabla_ultimas_practicas(self):
        panel = self._crear_panel(
            self.contenido,
            titulo="Últimas prácticas registradas",
            descripcion=(
                "Registros creados recientemente en el sistema."
            ),
        )

        panel.grid(
            row=5,
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
            ("Código", 105),
            ("Fecha", 105),
            ("Carrera", 145),
            ("Semestre", 90),
            ("Asignatura", 170),
            ("Tipo", 125),
            ("Revisor", 155),
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

        if not self.ultimas_practicas:
            self._crear_mensaje_vacio(
                tabla,
                "No existen prácticas registradas."
            )
            return

        for indice, registro in enumerate(
            self.ultimas_practicas
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

            semestre = registro.get(
                "semestre"
            )

            semestre_texto = (
                str(semestre)
                if semestre is not None
                else "—"
            )

            valores = [
                (
                    registro.get(
                        "codigo",
                        "—",
                    ),
                    105,
                ),
                (
                    fecha_texto,
                    105,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "carrera",
                            "—",
                        ),
                        20,
                    ),
                    145,
                ),
                (
                    semestre_texto,
                    90,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "asignatura",
                            "—",
                        ),
                        24,
                    ),
                    170,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "tipo_practica",
                            "—",
                        ),
                        17,
                    ),
                    125,
                ),
                (
                    self._recortar_texto(
                        registro.get(
                            "revisor",
                            "—",
                        ),
                        21,
                    ),
                    155,
                ),
            ]

            for valor, ancho in valores:
                ctk.CTkLabel(
                    fila,
                    text=str(
                        valor or "—"
                    ),
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
                    command=lambda url=pdf_url: self._abrir_pdf(
                        url
                    ),
                )
            else:
                boton = ctk.CTkButton(
                    fila,
                    text="Sin PDF",
                    width=70,
                    height=27,
                    fg_color="transparent",
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
            text="No se pudo cargar el dashboard de prácticas",
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

    @staticmethod
    def _texto_variacion(variacion):
        try:
            valor = float(
                variacion
            )
        except (TypeError, ValueError):
            valor = 0

        if valor > 0:
            return f"▲ +{valor:.1f}% respecto al mes anterior"

        if valor < 0:
            return f"▼ {valor:.1f}% respecto al mes anterior"

        return "Sin variación respecto al mes anterior"

    @staticmethod
    def _color_variacion(variacion):
        try:
            valor = float(
                variacion
            )
        except (TypeError, ValueError):
            valor = 0

        if valor > 0:
            return POSITIVE

        if valor < 0:
            return NEGATIVE

        return NEUTRAL

    @staticmethod
    def _abrir_pdf(ruta):
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