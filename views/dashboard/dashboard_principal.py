import customtkinter as ctk
from views.dashboard.dashboard_reactivos import PanelDashboardReactivos
from views.dashboard.dashboard_general import PanelDashboardGeneral
from views.dashboard.dashboard_laboratorios import PanelDashboardLaboratorios
from views.dashboard.dashboard_practicas import PanelDashboardPracticas
from views.dashboard.dashboard_materiales import PanelDashboardMateriales
from views.dashboard.dashboard_docentes import PanelDashboardDocentes
# ============================================================
# Colores del dashboard
# ============================================================

BG_DARK = "#0F1923"
BG_SIDEBAR = "#142131"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
BG_CARD_HOVER = "#263A54"

ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"

TEXT_PRIMARY = "#E8EDF2"
TEXT_SECONDARY = "#8A9BB0"

BORDER = "#2A3A50"
RED = "#E05252"


# ============================================================
# Ventana principal
# ============================================================

class VentanaDashboard(ctk.CTkToplevel):
    """
    Ventana principal del centro de estadísticas.

    Permite seleccionar un módulo desde el menú lateral y
    mostrar sus estadísticas dentro de la misma ventana.
    """

    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.title("Centro de estadísticas")

        self.geometry("1400x850")
        self.minsize(1100, 700)

        self.configure(
            fg_color=BG_DARK
        )

        self.transient(master)

        self.modulo_actual = "general"

        self.botones_menu = {}

        self.panel_actual = None

        self.grid_rowconfigure(
            0,
            weight=1,
        )

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        self._crear_menu_lateral()
        self._crear_area_principal()

        self.mostrar_general()

    # ========================================================
    # Menú lateral
    # ========================================================

    def _crear_menu_lateral(self):
        """
        Construye el menú lateral del dashboard.
        """

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color=BG_SIDEBAR,
            corner_radius=0,
            border_width=0,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.sidebar.grid_propagate(False)

        # ----------------------------------------------------
        # Encabezado
        # ----------------------------------------------------

        encabezado = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )

        encabezado.pack(
            fill="x",
            padx=18,
            pady=(24, 18),
        )

        ctk.CTkLabel(
            encabezado,
            text="📊",
            font=("Segoe UI Emoji", 36),
            text_color=ACCENT,
        ).pack()

        ctk.CTkLabel(
            encabezado,
            text="ESTADÍSTICAS",
            font=("Consolas", 18, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(
            pady=(7, 0)
        )

        ctk.CTkLabel(
            encabezado,
            text="Centro de información",
            font=("Consolas", 10),
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=(3, 0)
        )

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 15),
        )

        ctk.CTkLabel(
            self.sidebar,
            text="MÓDULOS",
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 8),
        )

        # ----------------------------------------------------
        # Botones del menú
        # ----------------------------------------------------

        self._crear_boton_menu(
            clave="general",
            texto="🏠  Resumen general",
            comando=self.mostrar_general,
        )

        self._crear_boton_menu(
            clave="laboratorios",
            texto="🧪  Laboratorios",
            comando=self.mostrar_laboratorios,
        )

        self._crear_boton_menu(
            clave="practicas",
            texto="📋  Prácticas",
            comando=self.mostrar_practicas,
        )

        self._crear_boton_menu(
            clave="pdfs",
            texto="📄  Documentos PDF",
            comando=self.mostrar_pdfs,
        )

        self._crear_boton_menu(
            clave="reactivos",
            texto="⚗️  Reactivos",
            comando=self.mostrar_reactivos,
        )

        self._crear_boton_menu(
            clave="materiales",
            texto="📦  Materiales",
            comando=self.mostrar_materiales,
        )

        self._crear_boton_menu(
            clave="docentes",
            texto="👨‍🏫  Docentes",
            comando=self.mostrar_docentes,
        )

        # ----------------------------------------------------
        # Zona inferior
        # ----------------------------------------------------

        inferior = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )

        inferior.pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=18,
        )

        ctk.CTkFrame(
            inferior,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).pack(
            fill="x",
            pady=(0, 14),
        )

        ctk.CTkButton(
            inferior,
            text="↻  Actualizar dashboard",
            height=40,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=("Consolas", 11),
            corner_radius=7,
            command=self.actualizar_modulo_actual,
        ).pack(
            fill="x",
            pady=(0, 8),
        )

        ctk.CTkButton(
            inferior,
            text="✕  Cerrar",
            height=40,
            fg_color="transparent",
            hover_color=RED,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_SECONDARY,
            font=("Consolas", 11),
            corner_radius=7,
            command=self.destroy,
        ).pack(
            fill="x",
        )

    def _crear_boton_menu(
        self,
        clave,
        texto,
        comando,
    ):
        """
        Crea un botón dentro del menú lateral.
        """

        boton = ctk.CTkButton(
            self.sidebar,
            text=texto,
            height=43,
            anchor="w",
            fg_color="transparent",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            font=("Consolas", 12),
            corner_radius=7,
            border_width=0,
            command=comando,
        )

        boton.pack(
            fill="x",
            padx=12,
            pady=3,
        )

        self.botones_menu[clave] = boton

    # ========================================================
    # Área principal
    # ========================================================

    def _crear_area_principal(self):
        """
        Crea el encabezado y el área donde se cargarán los paneles.
        """

        self.area_principal = ctk.CTkFrame(
            self,
            fg_color=BG_DARK,
            corner_radius=0,
        )

        self.area_principal.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.area_principal.grid_rowconfigure(
            1,
            weight=1,
        )

        self.area_principal.grid_columnconfigure(
            0,
            weight=1,
        )

        # ----------------------------------------------------
        # Encabezado superior
        # ----------------------------------------------------

        self.header = ctk.CTkFrame(
            self.area_principal,
            height=84,
            fg_color=BG_PANEL,
            corner_radius=0,
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.header.grid_propagate(False)

        self.header.grid_columnconfigure(
            0,
            weight=1,
        )

        contenedor_titulo = ctk.CTkFrame(
            self.header,
            fg_color="transparent",
        )

        contenedor_titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=14,
        )

        self.lbl_titulo = ctk.CTkLabel(
            contenedor_titulo,
            text="Resumen general",
            font=("Consolas", 22, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )

        self.lbl_titulo.pack(
            anchor="w"
        )

        self.lbl_subtitulo = ctk.CTkLabel(
            contenedor_titulo,
            text="Indicadores generales de todos los módulos",
            font=("Consolas", 11),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )

        self.lbl_subtitulo.pack(
            anchor="w",
            pady=(3, 0),
        )

        # Línea de color inferior
        ctk.CTkFrame(
            self.area_principal,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).grid(
            row=0,
            column=0,
            sticky="sew",
        )

        # ----------------------------------------------------
        # Contenedor desplazable
        # ----------------------------------------------------

        self.contenedor = ctk.CTkScrollableFrame(
            self.area_principal,
            fg_color=BG_DARK,
            corner_radius=0,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )

        self.contenedor.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=12,
        )

        self.contenedor.grid_columnconfigure(
            0,
            weight=1,
        )

    # ========================================================
    # Utilidades
    # ========================================================

    def _limpiar_contenedor(self):
        """
        Elimina el panel actualmente mostrado.
        """

        for widget in self.contenedor.winfo_children():
            widget.destroy()

        self.panel_actual = None

    def _seleccionar_boton(self, clave):
        """
        Resalta visualmente el botón del módulo seleccionado.
        """

        for nombre, boton in self.botones_menu.items():

            if nombre == clave:
                boton.configure(
                    fg_color=ACCENT,
                    hover_color=ACCENT_DARK,
                    text_color=BG_DARK,
                    font=("Consolas", 12, "bold"),
                )

            else:
                boton.configure(
                    fg_color="transparent",
                    hover_color=BG_CARD_HOVER,
                    text_color=TEXT_SECONDARY,
                    font=("Consolas", 12),
                )

    def _preparar_modulo(
        self,
        clave,
        titulo,
        subtitulo,
    ):
        """
        Cambia la información del encabezado y limpia el contenido.
        """

        self.modulo_actual = clave

        self.lbl_titulo.configure(
            text=titulo
        )

        self.lbl_subtitulo.configure(
            text=subtitulo
        )

        self._seleccionar_boton(
            clave
        )

        self._limpiar_contenedor()

    def _insertar_panel(self, panel):
        """
        Inserta un panel dentro del contenedor principal.
        """

        self.panel_actual = panel

        self.panel_actual.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=2,
            pady=2,
        )

    # ========================================================
    # Resumen general
    # ========================================================

    def mostrar_general(self):
        """
        Muestra las estadísticas generales reales.
        """

        self._preparar_modulo(
            clave="general",
            titulo="Resumen general",
            subtitulo=(
                "Indicadores principales de todos los módulos"
            ),
        )

        panel = PanelDashboardGeneral(
            self.contenedor
        )

        self._insertar_panel(
            panel
        )

    # ========================================================
    # Laboratorios
    # ========================================================

    def mostrar_laboratorios(self):

        self._preparar_modulo(
            clave="laboratorios",
            titulo="Estadísticas de laboratorios",
            subtitulo="Uso de laboratorios, carreras y asignaturas",
        )

        panel = PanelDashboardLaboratorios(
            self.contenedor
        )

        self._insertar_panel(panel)
    # ========================================================
    # Prácticas
    # ========================================================

    def mostrar_practicas(self):
        """
        Muestra las estadísticas reales de prácticas.
        """

        self._preparar_modulo(
            clave="practicas",
            titulo="Estadísticas de prácticas",
            subtitulo=(
                "Actividad y planificación de prácticas académicas"
            ),
        )

        panel = PanelDashboardPracticas(
            self.contenedor
        )

        self._insertar_panel(
            panel
        )
    # ========================================================
    # PDFs
    # ========================================================

    def mostrar_pdfs(self):
        """
        Muestra temporalmente el panel de PDFs.
        """

        self._preparar_modulo(
            clave="pdfs",
            titulo="Estadísticas de documentos PDF",
            subtitulo=(
                "Generación y disponibilidad de documentos"
            ),
        )

        panel = self._crear_panel_proximamente(
            titulo="Dashboard de documentos PDF",
            descripcion=(
                "Esta sección mostrará los documentos generados "
                "por todos los módulos del sistema."
            ),
            estadisticas=[
                "Total de PDFs generados",
                "PDFs generados por mes",
                "PDFs generados por módulo",
                "PDFs por carrera",
                "PDFs por docente",
                "Registros con PDF y sin PDF",
            ],
        )

        self._insertar_panel(
            panel
        )

    # ========================================================
    # Reactivos
    # ========================================================

    def mostrar_reactivos(self):
        """
        Muestra las estadísticas reales de reactivos.
        """

        self._preparar_modulo(
            clave="reactivos",
            titulo="Estadísticas de reactivos",
            subtitulo=(
                "Cantidades, consumo y frecuencia de reactivos"
            ),
        )

        panel = PanelDashboardReactivos(
            self.contenedor
        )

        self._insertar_panel(
            panel
        )

    # ========================================================
    # Materiales
    # ========================================================

    def mostrar_materiales(self):
        """
        Muestra las estadísticas reales de materiales.
        """

        self._preparar_modulo(
            clave="materiales",
            titulo="Estadísticas de materiales",
            subtitulo=(
                "Uso, cantidad y frecuencia de materiales de laboratorio"
            ),
        )

        panel = PanelDashboardMateriales(
            self.contenedor
        )

        self._insertar_panel(
            panel
        )

    # ========================================================
    # Docentes
    # ========================================================

    def mostrar_docentes(self):
        """
        Muestra las estadísticas reales de docentes.
        """

        self._preparar_modulo(
            clave="docentes",
            titulo="Estadísticas de docentes",
            subtitulo=(
                "Participación, actividad y documentos asociados "
                "a docentes responsables"
            ),
        )

        panel = PanelDashboardDocentes(
            self.contenedor
        )

        self._insertar_panel(
            panel
        )

    # ========================================================
    # Panel temporal
    # ========================================================

    def _crear_panel_proximamente(
        self,
        titulo,
        descripcion,
        estadisticas,
    ):
        """
        Crea un panel temporal para los módulos todavía no
        conectados con PostgreSQL.
        """

        panel = ctk.CTkFrame(
            self.contenedor,
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
            padx=22,
            pady=(22, 12),
        )

        ctk.CTkLabel(
            cabecera,
            text=titulo,
            font=("Consolas", 18, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            cabecera,
            text=descripcion,
            font=("Consolas", 11),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=850,
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        ctk.CTkFrame(
            panel,
            height=1,
            fg_color=BORDER,
            corner_radius=0,
        ).pack(
            fill="x",
            padx=22,
            pady=(0, 15),
        )

        contenedor_estadisticas = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        contenedor_estadisticas.pack(
            fill="x",
            padx=22,
            pady=(0, 15),
        )

        for estadistica in estadisticas:

            fila = ctk.CTkFrame(
                contenedor_estadisticas,
                fg_color=BG_CARD,
                corner_radius=7,
                border_width=1,
                border_color=BORDER,
            )

            fila.pack(
                fill="x",
                pady=5,
            )

            ctk.CTkLabel(
                fila,
                text="•",
                width=30,
                font=("Consolas", 18, "bold"),
                text_color=ACCENT,
            ).pack(
                side="left",
                padx=(10, 0),
                pady=11,
            )

            ctk.CTkLabel(
                fila,
                text=estadistica,
                font=("Consolas", 11),
                text_color=TEXT_PRIMARY,
                anchor="w",
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=(5, 12),
                pady=11,
            )

        ctk.CTkLabel(
            panel,
            text=(
                "Este módulo será conectado con PostgreSQL "
                "en los siguientes pasos."
            ),
            font=("Consolas", 10),
            text_color=ACCENT,
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 22),
        )

        return panel

    # ========================================================
    # Actualización
    # ========================================================

    def actualizar_modulo_actual(self):
        """
        Recarga el módulo actualmente seleccionado.
        """

        acciones = {
            "general": self.mostrar_general,
            "laboratorios": self.mostrar_laboratorios,
            "practicas": self.mostrar_practicas,
            "pdfs": self.mostrar_pdfs,
            "reactivos": self.mostrar_reactivos,
            "materiales": self.mostrar_materiales,
            "docentes": self.mostrar_docentes,
        }

        accion = acciones.get(
            self.modulo_actual,
            self.mostrar_general,
        )

        accion()