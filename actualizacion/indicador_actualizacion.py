import sys
import threading

import customtkinter as ctk

from .descargar_actualizacion import (
    cerrar_aplicacion,
    descargar_e_iniciar_actualizacion,
)
from .verificar_actualizacion import hay_actualizacion


# ─── Colores ─────────────────────────────────────────────────────────
BG_NOTIFICACION = "#243348"
BG_ERROR = "#4A2428"

ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"

TEXT_PRI = "#E8EDF2"
TEXT_SEC = "#A8B5C5"

ERROR = "#FF6B6B"
WARNING = "#F5C451"


class IndicadorActualizacion(ctk.CTkFrame):
    """
    Indicador de actualización para colocarlo dentro del encabezado.

    El componente:

    - Comprueba GitHub en segundo plano.
    - Permanece oculto si no existe actualización.
    - Muestra un aviso si existe una versión más reciente.
    - Descarga la actualización cuando el usuario presiona el botón.
    - Ejecuta Actualizador.exe.
    - Cierra la aplicación principal.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_NOTIFICACION,
            corner_radius=9,
            border_width=1,
            border_color=ACCENT,
            height=54,
        )

        self.parent = parent

        self.version_local = None
        self.version_remota = None
        self.datos_release = None

        self.actualizando = False
        self.verificacion_iniciada = False

        self.pack_propagate(False)

        self._construir_interfaz()

        # El componente comienza oculto.
        self.pack_forget()

    def _construir_interfaz(self):
        # ── Icono ────────────────────────────────────────────────────
        self.label_icono = ctk.CTkLabel(
            self,
            text="⬇",
            width=28,
            font=("Segoe UI Emoji", 18),
            text_color=ACCENT,
        )
        self.label_icono.pack(
            side="left",
            padx=(10, 4),
        )

        # ── Información ──────────────────────────────────────────────
        informacion = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        informacion.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8),
            pady=5,
        )

        self.label_titulo = ctk.CTkLabel(
            informacion,
            text="Actualización disponible",
            font=("Consolas", 10, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
        )
        self.label_titulo.pack(
            anchor="w",
        )

        self.label_estado = ctk.CTkLabel(
            informacion,
            text="Nueva versión disponible",
            font=("Consolas", 8),
            text_color=TEXT_SEC,
            anchor="w",
        )
        self.label_estado.pack(
            anchor="w",
        )

        # ── Botones ──────────────────────────────────────────────────
        botones = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        botones.pack(
            side="right",
            padx=(0, 8),
            pady=6,
        )

        self.boton_actualizar = ctk.CTkButton(
            botones,
            text="Actualizar",
            width=82,
            height=25,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="#FFFFFF",
            font=("Consolas", 9, "bold"),
            corner_radius=6,
            command=self._solicitar_actualizacion,
        )
        self.boton_actualizar.pack(
            side="left",
            padx=(0, 4),
        )

        self.boton_cerrar = ctk.CTkButton(
            botones,
            text="×",
            width=27,
            height=25,
            fg_color="transparent",
            hover_color="#34465C",
            text_color=TEXT_SEC,
            font=("Consolas", 14, "bold"),
            corner_radius=6,
            command=self.ocultar,
        )
        self.boton_cerrar.pack(
            side="left",
        )

    # ─── Verificación ────────────────────────────────────────────────

    def iniciar_verificacion(self):
        """
        Inicia la consulta a GitHub después de que cargue la ventana.

        Se ejecuta una sola vez durante la sesión.
        """

        if self.verificacion_iniciada:
            return

        self.verificacion_iniciada = True

        # Espera un poco para no retrasar la apertura de la ventana.
        self.after(
            1200,
            self._ejecutar_verificacion_en_segundo_plano,
        )

    def _ejecutar_verificacion_en_segundo_plano(self):
        hilo = threading.Thread(
            target=self._verificar_actualizacion,
            daemon=True,
        )
        hilo.start()

    def _verificar_actualizacion(self):
        try:
            (
                actualizar,
                version_local,
                version_remota,
                datos_release,
            ) = hay_actualizacion()

            self._ejecutar_en_interfaz(
                lambda: self._procesar_resultado(
                    actualizar,
                    version_local,
                    version_remota,
                    datos_release,
                )
            )

        except Exception as error:
            # Los errores de Internet no interrumpen la aplicación.
            print(
                "No se pudo comprobar si existen actualizaciones:",
                error,
            )

    def _procesar_resultado(
        self,
        actualizar,
        version_local,
        version_remota,
        datos_release,
    ):
        self.version_local = version_local
        self.version_remota = version_remota
        self.datos_release = datos_release

        if not actualizar:
            self.ocultar()
            return

        if not version_remota or not datos_release:
            self.ocultar()
            return

        self.label_icono.configure(
            text="⬇",
            text_color=ACCENT,
        )

        self.label_titulo.configure(
            text="Actualización disponible",
            text_color=TEXT_PRI,
        )

        self.label_estado.configure(
            text=(
                f"Versión {version_local} → "
                f"{version_remota}"
            ),
            text_color=TEXT_SEC,
        )

        self.boton_actualizar.configure(
            text="Actualizar",
            state="normal",
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
        )

        self.boton_cerrar.configure(
            state="normal",
        )

        self.mostrar()

    # ─── Presentación ────────────────────────────────────────────────

    def mostrar(self):
        """
        Coloca el indicador en la parte derecha del encabezado.
        """

        if self.winfo_manager():
            return

        self.pack(
            side="right",
            padx=18,
            pady=8,
        )

    def ocultar(self):
        """
        Oculta la notificación durante la sesión actual.
        """

        if self.actualizando:
            return

        self.pack_forget()

    # ─── Descarga ────────────────────────────────────────────────────

    def _solicitar_actualizacion(self):
        """
        Empieza la descarga sin mostrar una ventana emergente.
        """

        if self.actualizando:
            return

        if not self.version_remota or not self.datos_release:
            self._mostrar_error(
                "No existen datos válidos de la actualización."
            )
            return

        # La sustitución automática se realiza cuando el programa
        # está convertido en ejecutable.
        if not getattr(sys, "frozen", False):
            self.label_icono.configure(
                text="ℹ",
                text_color=WARNING,
            )

            self.label_titulo.configure(
                text="Actualización detectada",
                text_color=WARNING,
            )

            self.label_estado.configure(
                text="La instalación se activa en el programa .exe",
                text_color=TEXT_SEC,
            )

            self.boton_actualizar.configure(
                text="Solo en .exe",
                state="disabled",
            )

            return

        self.actualizando = True

        self.label_icono.configure(
            text="⏳",
            text_color=WARNING,
        )

        self.label_titulo.configure(
            text="Descargando actualización",
            text_color=WARNING,
        )

        self.label_estado.configure(
            text=f"Preparando versión {self.version_remota}...",
            text_color=TEXT_SEC,
        )

        self.boton_actualizar.configure(
            text="Descargando",
            state="disabled",
        )

        self.boton_cerrar.configure(
            state="disabled",
        )

        hilo = threading.Thread(
            target=self._descargar_actualizacion,
            daemon=True,
        )
        hilo.start()

    def _descargar_actualizacion(self):
        try:
            resultado = descargar_e_iniciar_actualizacion(
                self.datos_release,
                self.version_remota,
            )

            if not resultado:
                raise RuntimeError(
                    "No se pudo descargar la actualización."
                )

            self._ejecutar_en_interfaz(
                self._actualizacion_descargada
            )

        except Exception as error:
            self._ejecutar_en_interfaz(
                lambda: self._mostrar_error(str(error))
            )

    def _actualizacion_descargada(self):
        self.label_icono.configure(
            text="✓",
            text_color=ACCENT,
        )

        self.label_titulo.configure(
            text="Actualización descargada",
            text_color=ACCENT,
        )

        self.label_estado.configure(
            text="Reiniciando la aplicación...",
            text_color=TEXT_SEC,
        )

        self.boton_actualizar.configure(
            text="Instalando",
            state="disabled",
        )

        # Da tiempo para mostrar el mensaje y luego cierra la aplicación.
        self.after(
            900,
            cerrar_aplicacion,
        )

    def _mostrar_error(self, mensaje):
        self.actualizando = False

        mensaje = mensaje.strip()

        if len(mensaje) > 65:
            mensaje = mensaje[:62] + "..."

        self.configure(
            fg_color=BG_ERROR,
            border_color=ERROR,
        )

        self.label_icono.configure(
            text="⚠",
            text_color=ERROR,
        )

        self.label_titulo.configure(
            text="No se pudo actualizar",
            text_color=ERROR,
        )

        self.label_estado.configure(
            text=mensaje or "Ocurrió un error desconocido.",
            text_color=TEXT_SEC,
        )

        self.boton_actualizar.configure(
            text="Reintentar",
            state="normal",
            fg_color=ERROR,
            hover_color="#D95454",
        )

        self.boton_cerrar.configure(
            state="normal",
        )

        self.mostrar()

    # ─── Utilidades ──────────────────────────────────────────────────

    def _ejecutar_en_interfaz(self, funcion):
        """
        Ejecuta una función en el hilo principal de CustomTkinter.
        """

        try:
            if self.winfo_exists():
                self.after(0, funcion)
        except Exception:
            pass