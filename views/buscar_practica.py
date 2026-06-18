import customtkinter as ctk
import os
from tkinter import messagebox
from datetime import datetime

from database.buscar import listar_practicas, buscar_por_id
from views.editar_practica import VentanaEditarPractica
from views.eliminar_practica import eliminar

# ─── Paleta compartida ───────────────────────────────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_CARD     = "#1E2D42"
BG_CARD_HOV = "#243348"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"
RED         = "#E05252"
RED_DARK    = "#B83C3C"
BG_INPUT    = "#0F1923"

# Índices de columna en la fila devuelta por listar_practicas().
# Deben coincidir EXACTAMENTE con el orden del SELECT en
# database/buscar.py -> listar_practicas(). Si cambias el SELECT,
# actualiza también estas constantes.
#
# 'codigo' no aparece aquí: es solo el nombre interno del PDF guardado,
# no se muestra ni se filtra en esta vista.
#
# id(0) fecha_creacion(1) carrera(2) asignatura(3)
# tema_practica(4) ingeniero_revisor(5) pdf_url(6)

IDX_ID       = 0
IDX_FECHA    = 1
IDX_CARRERA  = 2
IDX_ASIGN    = 3
IDX_TEMA     = 4
IDX_DOCENTE  = 5
IDX_PDF      = 6


def _fmt_fecha(val) -> str:
    """Convierte un timestamp (datetime o str) a 'DD/MM/YYYY'."""
    if val is None:
        return "—"
    if isinstance(val, datetime):
        return val.strftime("%d/%m/%Y")
    try:
        return datetime.fromisoformat(str(val)).strftime("%d/%m/%Y")
    except Exception:
        return str(val)[:10]


def _fecha_dt(fila) -> datetime | None:
    """Devuelve el datetime de creación para comparaciones de rango."""
    val = fila[IDX_FECHA]
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return None


def _btn(parent, text, color, hover, text_color, command):
    ctk.CTkButton(
        parent,
        text=text,
        width=100,
        height=32,
        fg_color=color,
        hover_color=hover,
        text_color=text_color,
        font=("Consolas", 11),
        corner_radius=6,
        border_width=1,
        border_color=BORDER,
        command=command,
    ).pack(side="left", padx=4)


class VentanaBuscar(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Buscar Prácticas")
        self.geometry("1150x720")
        self.configure(fg_color=BG_DARK)

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🔍  PRÁCTICAS REGISTRADAS",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_PRI,
        ).pack(side="left", padx=20)

        self._lbl_count = ctk.CTkLabel(
            header,
            text="",
            font=("Consolas", 11),
            text_color=ACCENT,
        )
        self._lbl_count.pack(side="right", padx=20)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Panel de filtros ──────────────────────────────────────────
        filtros = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0)
        filtros.pack(fill="x", padx=0, pady=0)

        # Fila 1: búsqueda libre + botón recargar
        f1 = ctk.CTkFrame(filtros, fg_color="transparent")
        f1.pack(fill="x", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            f1, text="BÚSQUEDA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=80, anchor="w",
        ).pack(side="left")

        self._search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            f1,
            textvariable=self._search_var,
            placeholder_text="Buscar por cualquier campo...",
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12),
            corner_radius=6,
            height=32,
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            f1,
            text="↺  Recargar",
            width=110, height=32,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT_SEC,
            font=("Consolas", 11),
            corner_radius=6,
            command=self.cargar_datos,
        ).pack(side="right")

        # Fila 2: filtro por carrera
        f2 = ctk.CTkFrame(filtros, fg_color="transparent")
        f2.pack(fill="x", padx=16, pady=(0, 10))

        # Carrera
        ctk.CTkLabel(
            f2, text="CARRERA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=70, anchor="w",
        ).pack(side="left")

        self._carrera_var = ctk.StringVar()
        carrera_combo = ctk.CTkComboBox(
            f2,
            variable=self._carrera_var,
            values=["Todas", "Agroindustria", "Agropecuaria", "Agronegocios"],
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_PRI,
            button_color=ACCENT, button_hover_color=ACCENT_DARK,
            dropdown_fg_color=BG_PANEL, dropdown_text_color=TEXT_PRI,
            dropdown_hover_color=ACCENT_DARK,
            font=("Consolas", 12), corner_radius=6, height=32, width=160,
        )
        carrera_combo.pack(side="left", padx=(0, 16))

        # Fecha desde
        ctk.CTkLabel(
            f2, text="DESDE",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=50, anchor="w",
        ).pack(side="left")

        self._desde_var = ctk.StringVar()
        ctk.CTkEntry(
            f2,
            textvariable=self._desde_var,
            placeholder_text="DD/MM/AAAA",
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12), corner_radius=6, height=32, width=120,
        ).pack(side="left", padx=(0, 8))

        # Fecha hasta
        ctk.CTkLabel(
            f2, text="HASTA",
            font=("Consolas", 9, "bold"),
            text_color=TEXT_SEC,
            width=50, anchor="w",
        ).pack(side="left")

        self._hasta_var = ctk.StringVar()
        ctk.CTkEntry(
            f2,
            textvariable=self._hasta_var,
            placeholder_text="DD/MM/AAAA",
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
            font=("Consolas", 12), corner_radius=6, height=32, width=120,
        ).pack(side="left", padx=(0, 8))

        # Botón limpiar filtros
        ctk.CTkButton(
            f2,
            text="✕ Limpiar",
            width=90, height=32,
            fg_color="transparent",
            hover_color=BG_CARD,
            border_width=1, border_color=BORDER,
            text_color=TEXT_SEC,
            font=("Consolas", 11), corner_radius=6,
            command=self._limpiar_filtros,
        ).pack(side="right")

        # ── Conectar los traces / callbacks recién AHORA, cuando ya
        #    existen todas las StringVar que usa _aplicar_filtros() ──
        self._search_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._carrera_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._desde_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._hasta_var.trace_add("write", lambda *_: self._aplicar_filtros())
        carrera_combo.configure(command=lambda _: self._aplicar_filtros())

        # Separador
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # ── Cabecera de tabla ─────────────────────────────────────────
        col_header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=34)
        col_header.pack(fill="x", padx=20)

        for texto, ancho in (
            ("FECHA",      100),
            ("CARRERA",    130),
            ("ASIGNATURA", 190),
            ("DOCENTE",    200),
            ("TEMA",       220),
            ("PDF",         50),
        ):
            ctk.CTkLabel(
                col_header,
                text=texto,
                font=("Consolas", 10, "bold"),
                text_color=TEXT_SEC,
                width=ancho, anchor="w",
            ).pack(side="left", padx=(8, 0), pady=6)

        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(
            fill="x", padx=20
        )

        # ── Lista desplazable ─────────────────────────────────────────
        self.frame = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.frame.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        self._todos = []
        # set inicial DESPUÉS de conectar los traces (carga los datos una
        # sola vez al final, en vez de disparar _aplicar_filtros() a medias)
        self._carrera_var.set("Todas")
        self.cargar_datos()

    # ─── Carga y filtros ──────────────────────────────────────────────

    def cargar_datos(self):
        self._todos = listar_practicas()
        self._renderizar(self._todos)

    def _limpiar_filtros(self):
        self._search_var.set("")
        self._carrera_var.set("Todas")
        self._desde_var.set("")
        self._hasta_var.set("")

    def _parse_fecha(self, texto: str) -> datetime | None:
        texto = texto.strip()
        if not texto:
            return None
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, fmt)
            except ValueError:
                continue
        return None

    def _aplicar_filtros(self):
        q       = self._search_var.get().lower()
        carrera = self._carrera_var.get()
        desde   = self._parse_fecha(self._desde_var.get())
        hasta   = self._parse_fecha(self._hasta_var.get())

        resultado = []
        for f in self._todos:
            # Búsqueda libre
            if q and not any(
                q in str(f[i]).lower()
                for i in (IDX_CARRERA, IDX_ASIGN, IDX_DOCENTE, IDX_TEMA)
            ):
                continue

            # Filtro carrera
            if carrera and carrera != "Todas" and carrera.lower() not in str(f[IDX_CARRERA] or "").lower():
                continue

            # Filtro rango fechas
            if desde or hasta:
                dt = _fecha_dt(f)
                if dt is None:
                    continue
                dt_only = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                if desde and dt_only < desde:
                    continue
                if hasta:
                    hasta_fin = hasta.replace(hour=23, minute=59, second=59)
                    if dt_only > hasta_fin:
                        continue

            resultado.append(f)

        self._renderizar(resultado)

    def _renderizar(self, datos):
        for w in self.frame.winfo_children():
            w.destroy()

        total = len(datos)
        self._lbl_count.configure(
            text=f"{total} práctica{'s' if total != 1 else ''} encontrada{'s' if total != 1 else ''}"
        )

        if not datos:
            ctk.CTkLabel(
                self.frame,
                text="No se encontraron prácticas con esos criterios.",
                font=("Consolas", 13),
                text_color=TEXT_SEC,
            ).pack(pady=40)
            return

        for fila in datos:
            self._fila_card(fila)

    def _fila_card(self, fila):
        id_practica       = fila[IDX_ID]
        carrera           = fila[IDX_CARRERA]
        asignatura        = fila[IDX_ASIGN]
        tema              = fila[IDX_TEMA]
        ingeniero_revisor = fila[IDX_DOCENTE] or "—"
        pdf_url           = fila[IDX_PDF]
        fecha_txt         = _fmt_fecha(fila[IDX_FECHA])

        card = ctk.CTkFrame(
            self.frame,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        card.pack(fill="x", pady=4)

        # Borde izquierdo de acento
        ctk.CTkFrame(card, width=4, fg_color=ACCENT, corner_radius=2).pack(
            side="left", fill="y"
        )

        # ── Datos ─────────────────────────────────────────────────────
        data_row = ctk.CTkFrame(card, fg_color="transparent")
        data_row.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        # Fila superior: FECHA destacada + carrera + asignatura
        top = ctk.CTkFrame(data_row, fg_color="transparent")
        top.pack(fill="x")

        # Fecha como elemento principal (antes ocupaba el código)
        fecha_frame = ctk.CTkFrame(top, fg_color="#162030", corner_radius=6, width=95)
        fecha_frame.pack(side="left", padx=(0, 10))
        fecha_frame.pack_propagate(False)
        ctk.CTkLabel(
            fecha_frame,
            text=fecha_txt,
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
            anchor="center",
        ).pack(expand=True, fill="both", padx=6, pady=4)

        ctk.CTkLabel(
            top,
            text=carrera,
            font=("Consolas", 13, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
            width=130,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            top,
            text=asignatura,
            font=("Consolas", 13),
            text_color=TEXT_PRI,
            anchor="w",
        ).pack(side="left")

        # Fila inferior: docente + tema recortado
        bot = ctk.CTkFrame(data_row, fg_color="transparent")
        bot.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(
            bot,
            text=f"👤 {ingeniero_revisor}",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
            anchor="w",
            width=250,
        ).pack(side="left")

        tema_corto = (tema[:75] + "…") if tema and len(tema) > 75 else (tema or "—")
        ctk.CTkLabel(
            bot,
            text=f"📄 {tema_corto}",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(side="left", padx=(8, 0))

        # ── Botones ───────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(side="right", padx=16, pady=14)

        _btn(btn_row, "📄 PDF",     ACCENT,   ACCENT_DARK, "#0F1923",
             lambda p=pdf_url: self.abrir_pdf(p))
        _btn(btn_row, "✏ Editar",   BG_PANEL, BG_CARD_HOV, TEXT_PRI,
             lambda i=id_practica: self.editar(i))
        _btn(btn_row, "🗑 Eliminar", RED,      RED_DARK,    TEXT_PRI,
             lambda i=id_practica: self.eliminar_y_recargar(i))

    # ─── Acciones ────────────────────────────────────────────────────

    def abrir_pdf(self, ruta):
        ruta_completa = os.path.abspath(ruta)
        if not os.path.isfile(ruta_completa):
            messagebox.showerror("Error", f"No se encontró el archivo:\n\n{ruta_completa}")
            return
        try:
            os.startfile(ruta_completa)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar(self, id_practica):
        registro = buscar_por_id(id_practica)
        if not registro:
            messagebox.showerror("Error", "No se encontró la práctica.")
            return
        VentanaEditarPractica(self, registro)

    def eliminar_y_recargar(self, id_practica):
        if not messagebox.askyesno("Confirmar", "¿Desea eliminar esta práctica?"):
            return
        try:
            eliminar(id_practica)
            messagebox.showinfo("Correcto", "Práctica eliminada correctamente.")
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", str(e))