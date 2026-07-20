import customtkinter as ctk
from views.dashboard.dashboard_principal import VentanaDashboard
from views.buscar_informe import VentanaBuscarInforme
from views.buscar_laboratorio import VentanaBuscarLaboratorio
from views.buscar_practica import VentanaBuscar
from views.nuevo_informe import VentanaNuevoInforme
from views.nueva_laboratorio import VentanaNuevoLaboratorio
from views.nueva_practica import VentanaNuevaPractica
from actualizacion.indicador_actualizacion import IndicadorActualizacion

# ─── Paleta ──────────────────────────────────────────────────────────
BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
BG_CARD_HOV = "#243348"
ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI = "#E8EDF2"
TEXT_SEC = "#8A9BB0"
BORDER = "#2A3A50"


class _MenuCard(ctk.CTkFrame):
    """
    Tarjeta de acción clickable con ícono, título y descripción.
    """

    def __init__(
        self,
        parent,
        icon: str,
        title: str,
        subtitle: str,
        command,
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            cursor="hand2",
        )

        self.configure(height=95)
        self.pack_propagate(False)

        self._cmd = command

        # Borde izquierdo de acento
        ctk.CTkFrame(
            self,
            width=4,
            fg_color=ACCENT,
            corner_radius=2,
        ).pack(
            side="left",
            fill="y",
        )

        inner = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        inner.pack(
            side="left",
            fill="both",
            expand=True,
            padx=14,
            pady=10,
        )

        top = ctk.CTkFrame(
            inner,
            fg_color="transparent",
        )
        top.pack(
            fill="x",
        )

        ctk.CTkLabel(
            top,
            text=icon,
            font=("Segoe UI Emoji", 20),
            text_color=ACCENT,
            width=30,
        ).pack(
            side="left",
        )

        ctk.CTkLabel(
            top,
            text=title,
            font=("Consolas", 13, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
        ).pack(
            side="left",
            padx=(10, 0),
        )

        ctk.CTkLabel(
            inner,
            text=subtitle,
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(3, 0),
        )

        ctk.CTkLabel(
            self,
            text="›",
            font=("Consolas", 22, "bold"),
            text_color=TEXT_SEC,
        ).pack(
            side="right",
            padx=16,
        )

        self._bind_recursive(
            self
        )

    def _bind_recursive(
        self,
        widget,
    ):
        widget.bind(
            "<Button-1>",
            lambda _event: self._cmd(),
        )

        widget.bind(
            "<Enter>",
            lambda _event: self._on_enter(),
        )

        widget.bind(
            "<Leave>",
            lambda _event: self._on_leave(),
        )

        for child in widget.winfo_children():
            self._bind_recursive(
                child
            )

    def _on_enter(self):
        self.configure(
            fg_color=BG_CARD_HOV,
            border_color=ACCENT,
        )

    def _on_leave(self):
        self.configure(
            fg_color=BG_CARD,
            border_color=BORDER,
        )


class App(ctk.CTk):
    """
    Ventana principal del Sistema Integrado de Gestión de Prácticas Académicas.
    """

    ANCHO = 1000
    ALTO = 900

    def __init__(self):
        super().__init__()

        self.title(
            "Sistema Integrado de Gestión de Prácticas Académicas"
        )

        self.geometry(
            f"{self.ANCHO}x{self.ALTO}"
        )

        self.resizable(
            False,
            False,
        )

        self.configure(
            fg_color=BG_DARK
        )

        self._construir_interfaz()

    def _construir_interfaz(self):
        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=70,
        )
        header.pack(
            fill="x"
        )
        header.pack_propagate(
            False
        )

        ctk.CTkLabel(
            header,
            text="🌿",
            font=("Segoe UI Emoji", 26),
        ).pack(
            side="left",
            padx=(20, 6),
        )

        title_col = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        title_col.pack(
            side="left",
            pady=12,
        )

        ctk.CTkLabel(
            title_col,
            text="SISTEMA DE PRÁCTICAS",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
        ).pack(
            anchor="w",
        )

        ctk.CTkLabel(
            title_col,
            text="Gestión académica de campo, laboratorio e informes",
            font=("Consolas", 9),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            anchor="w",
        )

        # ── Notificación de actualización ────────────────────────────
        self.indicador_actualizacion = IndicadorActualizacion(
            header
        )

        self.indicador_actualizacion.iniciar_verificacion()

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(
            fill="x"
        )
        

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(
            fill="x"
        )

        # ── Cuerpo desplazable ────────────────────────────────────────
        body = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        body.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10,
        )

        ctk.CTkLabel(
            body,
            text="SELECCIONA UNA ACCIÓN",
            font=("Consolas", 10, "bold"),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(0, 12),
        )

        acciones = (
            (
                "📊",
                "Centro de estadísticas",
                "Indicadores generales y dashboards del sistema",
                self._abrir_dashboard,
            ),
            (
                "📋",
                "Nueva planificación",
                "Planificación de práctica de campo o laboratorio",
                self._abrir_nueva_practica,
            ),
            (
                "🔬",
                "Registro de laboratorio",
                "Registrar una práctica de laboratorio realizada",
                self._abrir_nueva_laboratorio,
            ),
            (
                "📝",
                "Nuevo informe de laboratorio",
                "Crear el informe completo de una práctica realizada",
                self._abrir_nuevo_informe,
            ),
            (
                "🔍",
                "Buscar planificaciones",
                "Consultar, editar o eliminar planificaciones registradas",
                self._abrir_busqueda,
            ),
            (
                "📂",
                "Buscar prácticas de laboratorio",
                "Consultar, editar o eliminar registros de laboratorio",
                self._abrir_busqueda_laboratorio,
            ),
            (
                "📚",
                "Buscar informes de laboratorio",
                "Consultar, editar o eliminar informes registrados",
                self._abrir_busqueda_informe,
            ),
        )

        for icon, title, subtitle, command in acciones:
            _MenuCard(
                body,
                icon,
                title,
                subtitle,
                command,
            ).pack(
                fill="x",
                pady=5,
            )

        ctk.CTkFrame(
            body,
            height=1,
            fg_color=BORDER,
        ).pack(
            fill="x",
            pady=(18, 0),
        )

        ctk.CTkButton(
            body,
            text="Salir del sistema",
            height=36,
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_SEC,
            hover_color=BG_PANEL,
            font=("Consolas", 11),
            corner_radius=8,
            command=self.destroy,
        ).pack(
            pady=(8, 12),
            fill="x",
        )

    # ─── Navegación ──────────────────────────────────────────────────

    def _abrir_subventana(
        self,
        clase_ventana,
    ):
        self.withdraw()

        ventana = None

        try:
            ventana = clase_ventana(
                self
            )

            ventana.grab_set()

            ventana.protocol(
                "WM_DELETE_WINDOW",
                lambda: self._restaurar(
                    ventana
                ),
            )

            self.wait_window(
                ventana
            )

        except Exception as error:
            print(
                "\n========== ERROR ABRIENDO VENTANA =========="
            )
            print(error)
            print(
                "============================================\n"
            )

        finally:
            self.deiconify()
            self.lift()
            self.focus_force()

    def _restaurar(
        self,
        ventana,
    ):
        try:
            if ventana and ventana.winfo_exists():
                ventana.grab_release()
                ventana.destroy()

        except Exception:
            pass
        
    def _abrir_dashboard(self):
        self._abrir_subventana(
            VentanaDashboard
        )

    def _abrir_nueva_practica(self):
        self._abrir_subventana(
            VentanaNuevaPractica
        )

    def _abrir_nueva_laboratorio(self):
        self._abrir_subventana(
            VentanaNuevoLaboratorio
        )

    def _abrir_nuevo_informe(self):
        self._abrir_subventana(
            VentanaNuevoInforme
        )

    def _abrir_busqueda(self):
        self._abrir_subventana(
            VentanaBuscar
        )

    def _abrir_busqueda_laboratorio(self):
        self._abrir_subventana(
            VentanaBuscarLaboratorio
        )

    def _abrir_busqueda_informe(self):
        self._abrir_subventana(
            VentanaBuscarInforme
        )


if __name__ == "__main__":
    ctk.set_appearance_mode(
        "dark"
    )

    ctk.set_default_color_theme(
        "blue"
    )

    app = App()
    app.mainloop()