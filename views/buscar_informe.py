import webbrowser
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from database.informe.buscar_informe import (
    buscar_fotos_por_informe,
    buscar_informe_por_id,
    listar_informes,
)
from models.informe import InformeLaboratorio
from views.editar_informe import VentanaEditarInforme
from views.eliminar_informe import eliminar


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
RED = "#E05252"
RED_DARK = "#B83C3C"
BG_INPUT = "#0F1923"


# Índices de listar_informes()
IDX_ID = 0
IDX_FECHA = 1
IDX_CODIGO = 2
IDX_TITULO = 3
IDX_ASIGNATURA = 4
IDX_AUTORES = 5
IDX_DOCENTE = 6
IDX_PDF = 7


def _formatear_fecha(valor):
    """
    Convierte datetime o texto a DD/MM/YYYY.
    """

    if valor is None:
        return "—"

    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")

    try:
        return datetime.fromisoformat(
            str(valor)
        ).strftime(
            "%d/%m/%Y"
        )
    except Exception:
        return str(valor)[:10]


def _crear_boton(
    parent,
    texto,
    color,
    hover,
    comando,
):
    ctk.CTkButton(
        parent,
        text=texto,
        width=100,
        height=34,
        fg_color=color,
        hover_color=hover,
        text_color=TEXT_PRI,
        font=("Consolas", 11),
        corner_radius=6,
        border_width=1,
        border_color=BORDER,
        command=comando,
    ).pack(
        side="left",
        padx=4,
    )


class VentanaBuscarInforme(ctk.CTkToplevel):
    """
    Ventana para buscar, abrir, editar y eliminar
    informes de laboratorio.
    """

    def __init__(self, master):
        super().__init__(master)

        self.title(
            "Buscar informes de laboratorio"
        )

        self.geometry(
            "1200x760"
        )

        self.minsize(
            1000,
            650,
        )

        self.configure(
            fg_color=BG_DARK
        )

        self._todos = []

        # ── Header ────────────────────────────────────────────────────
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
            text="📚  INFORMES DE LABORATORIO",
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

        # ── Filtros ───────────────────────────────────────────────────
        filtros = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
        )
        filtros.pack(
            fill="x"
        )

        fila_busqueda = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )
        fila_busqueda.pack(
            fill="x",
            padx=16,
            pady=(10, 5),
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
                "Buscar por código, título, asignatura, "
                "autores o docente..."
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

        fila_filtros = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )
        fila_filtros.pack(
            fill="x",
            padx=16,
            pady=(0, 10),
        )

        ctk.CTkLabel(
            fila_filtros,
            text="ASIGNATURA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=85,
            anchor="w",
        ).pack(
            side="left"
        )

        self._asignatura_var = ctk.StringVar()

        self._entrada_asignatura = ctk.CTkEntry(
            fila_filtros,
            textvariable=self._asignatura_var,
            placeholder_text="Filtrar por asignatura",
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12),
            corner_radius=6,
            height=34,
            width=220,
        )
        self._entrada_asignatura.pack(
            side="left",
            padx=(0, 14),
        )

        ctk.CTkLabel(
            fila_filtros,
            text="AUTOR",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=50,
            anchor="w",
        ).pack(
            side="left"
        )

        self._autor_var = ctk.StringVar()

        self._entrada_autor = ctk.CTkEntry(
            fila_filtros,
            textvariable=self._autor_var,
            placeholder_text="Filtrar por autor",
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12),
            corner_radius=6,
            height=34,
            width=220,
        )
        self._entrada_autor.pack(
            side="left",
            padx=(0, 14),
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

        self._asignatura_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        self._autor_var.trace_add(
            "write",
            lambda *_: self._aplicar_filtros(),
        )

        # ── Cabecera de tabla ─────────────────────────────────────────
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
            ("CÓDIGO", 170),
            ("TÍTULO", 280),
            ("ASIGNATURA", 180),
            ("AUTORES / DOCENTE", 280),
            ("ACCIONES", 230),
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

        # ── Lista desplazable ─────────────────────────────────────────
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

    # ─── Carga y filtros ──────────────────────────────────────────────

    def cargar_datos(self):
        """
        Carga los informes desde PostgreSQL.
        """

        self._todos = listar_informes()

        self._aplicar_filtros()

    def _limpiar_filtros(self):
        self._busqueda_var.set("")
        self._asignatura_var.set("")
        self._autor_var.set("")

    def _aplicar_filtros(self):
        """
        Aplica los filtros sin realizar una consulta nueva.
        """

        busqueda = self._busqueda_var.get().strip().lower()
        asignatura = self._asignatura_var.get().strip().lower()
        autor = self._autor_var.get().strip().lower()

        resultado = []

        for fila in self._todos:
            codigo = str(
                fila[IDX_CODIGO]
                or ""
            ).lower()

            titulo = str(
                fila[IDX_TITULO]
                or ""
            ).lower()

            asignatura_fila = str(
                fila[IDX_ASIGNATURA]
                or ""
            ).lower()

            autores = str(
                fila[IDX_AUTORES]
                or ""
            ).lower()

            docente = str(
                fila[IDX_DOCENTE]
                or ""
            ).lower()

            if busqueda:
                coincide = any(
                    busqueda in campo
                    for campo in (
                        codigo,
                        titulo,
                        asignatura_fila,
                        autores,
                        docente,
                    )
                )

                if not coincide:
                    continue

            if (
                asignatura
                and asignatura not in asignatura_fila
            ):
                continue

            if autor and autor not in autores:
                continue

            resultado.append(
                fila
            )

        self._renderizar(
            resultado
        )

    def _renderizar(self, datos):
        """
        Dibuja las tarjetas de los informes.
        """

        for widget in self.frame.winfo_children():
            widget.destroy()

        total = len(
            datos
        )

        self._lbl_total.configure(
            text=(
                f"{total} informe"
                f"{'s' if total != 1 else ''}"
            )
        )

        if not datos:
            ctk.CTkLabel(
                self.frame,
                text=(
                    "No se encontraron informes "
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

    def _crear_tarjeta(self, fila):
        """
        Construye una fila visual para un informe.
        """

        id_informe = fila[IDX_ID]
        fecha = _formatear_fecha(
            fila[IDX_FECHA]
        )
        codigo = fila[IDX_CODIGO] or "—"
        titulo = fila[IDX_TITULO] or "Sin título"
        asignatura = fila[IDX_ASIGNATURA] or "—"
        autores = fila[IDX_AUTORES] or "—"
        docente = fila[IDX_DOCENTE] or "—"
        pdf_url = fila[IDX_PDF]

        tarjeta = ctk.CTkFrame(
            self.frame,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
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

        ctk.CTkLabel(
            fila_superior,
            text=codigo,
            font=("Consolas", 11, "bold"),
            text_color=TEXT_PRI,
            width=170,
            anchor="w",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        titulo_corto = (
            titulo[:52] + "…"
            if len(titulo) > 52
            else titulo
        )

        ctk.CTkLabel(
            fila_superior,
            text=titulo_corto,
            font=("Consolas", 12, "bold"),
            text_color=TEXT_PRI,
            width=280,
            anchor="w",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkLabel(
            fila_superior,
            text=asignatura,
            font=("Consolas", 11),
            text_color=TEXT_PRI,
            width=180,
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

        autores_corto = (
            autores[:70] + "…"
            if len(autores) > 70
            else autores
        )

        ctk.CTkLabel(
            fila_inferior,
            text=f"👥 {autores_corto}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            side="left",
        )

        ctk.CTkLabel(
            fila_inferior,
            text=f"   👤 Docente: {docente}",
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            side="left",
            padx=(12, 0),
        )

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
            lambda url=pdf_url: self.abrir_pdf(
                url
            ),
        )

        _crear_boton(
            botones,
            "✏ Editar",
            BG_PANEL,
            BG_CARD_HOV,
            lambda informe_id=id_informe: self.editar(
                informe_id
            ),
        )

        _crear_boton(
            botones,
            "🗑 Eliminar",
            RED,
            RED_DARK,
            lambda informe_id=id_informe: self.eliminar_y_recargar(
                informe_id
            ),
        )

    # ─── Acciones ────────────────────────────────────────────────────

    def abrir_pdf(self, pdf_url):
        """
        Abre el PDF público en el navegador.
        """

        if not pdf_url:
            messagebox.showwarning(
                "PDF no disponible",
                "Este informe no tiene un PDF asociado.",
                parent=self,
            )
            return

        pdf_url = str(
            pdf_url
        ).strip()

        if not pdf_url.lower().startswith(
            ("http://", "https://")
        ):
            messagebox.showerror(
                "URL inválida",
                (
                    "La dirección almacenada para el PDF "
                    "no es una URL válida."
                ),
                parent=self,
            )
            return

        try:
            webbrowser.open(
                pdf_url,
                new=2,
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

    def editar(self, id_informe):
        """
        Recupera el informe completo y abre la edición.
        """

        fila = buscar_informe_por_id(
            id_informe
        )

        if not fila:
            messagebox.showerror(
                "Error",
                "No se encontró el informe seleccionado.",
                parent=self,
            )
            return

        fotos = buscar_fotos_por_informe(
            id_informe
        )

        informe = InformeLaboratorio.from_row(
            fila
        )

        if informe is None:
            messagebox.showerror(
                "Error",
                "No fue posible reconstruir el informe.",
                parent=self,
            )
            return

        informe.fotos = fotos

        ventana = VentanaEditarInforme(
            self,
            informe,
        )

        ventana.grab_set()

        self.wait_window(
            ventana
        )

        self.cargar_datos()

    def eliminar_y_recargar(self, id_informe):
        """
        Solicita confirmación y elimina el informe.
        """

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            (
                "¿Desea eliminar este informe?\n\n"
                "También se intentarán eliminar de Supabase "
                "el PDF, la hoja de datos y las fotografías."
            ),
            parent=self,
        )

        if not respuesta:
            return

        resultado = eliminar(
            id_informe
        )

        if not resultado:
            messagebox.showerror(
                "Error",
                "No fue posible eliminar el informe.",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Correcto",
            "Informe eliminado correctamente.",
            parent=self,
        )

        self.cargar_datos()