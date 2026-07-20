
import webbrowser
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from database.buscar import buscar_por_id, listar_practicas
from database.eliminar import eliminar_practica
from views.editar_practica import VentanaEditarPractica


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

IDX_ID = 0
IDX_FECHA = 1
IDX_CARRERA = 2
IDX_ASIGNATURA = 3
IDX_TEMA = 4
IDX_DOCENTE = 5
IDX_PDF = 6


def _fecha_texto(valor):
    if valor is None:
        return "—"

    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")

    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except Exception:
        return str(valor)[:10]


def _fecha_datetime(valor):
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor

    try:
        return datetime.fromisoformat(str(valor))
    except Exception:
        return None


def _boton(parent, texto, color, hover, text_color, comando):
    boton = ctk.CTkButton(
        parent,
        text=texto,
        width=100,
        height=32,
        fg_color=color,
        hover_color=hover,
        text_color=text_color,
        font=("Consolas", 11),
        corner_radius=6,
        border_width=1,
        border_color=BORDER,
        command=comando,
    )
    boton.pack(side="left", padx=4)
    return boton


class VentanaBuscar(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Buscar Prácticas")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(fg_color=BG_DARK)

        self._todos = []

        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
            height=68,
        )
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

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(fill="x")

        filtros = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=0,
        )
        filtros.pack(fill="x")

        fila1 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila1.pack(fill="x", padx=16, pady=(10, 4))

        self._search_var = ctk.StringVar()

        ctk.CTkEntry(
            fila1,
            textvariable=self._search_var,
            placeholder_text="Buscar por carrera, asignatura, docente o tema...",
            fg_color=BG_DARK,
            border_color=BORDER,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            height=34,
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            fila1,
            text="↺ Recargar",
            width=110,
            height=34,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            command=self.cargar_datos,
        ).pack(side="right")

        fila2 = ctk.CTkFrame(filtros, fg_color="transparent")
        fila2.pack(fill="x", padx=16, pady=(4, 10))

        self._carrera_var = ctk.StringVar(value="Todas")
        self._desde_var = ctk.StringVar()
        self._hasta_var = ctk.StringVar()

        ctk.CTkComboBox(
            fila2,
            variable=self._carrera_var,
            values=[
                "Todas",
                "Agroindustria",
                "Agropecuaria",
                "Agronegocios",
            ],
            width=180,
            fg_color=BG_DARK,
            border_color=BORDER,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            command=lambda _: self._aplicar_filtros(),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkEntry(
            fila2,
            textvariable=self._desde_var,
            placeholder_text="Desde DD/MM/AAAA",
            width=160,
            fg_color=BG_DARK,
            border_color=BORDER,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkEntry(
            fila2,
            textvariable=self._hasta_var,
            placeholder_text="Hasta DD/MM/AAAA",
            width=160,
            fg_color=BG_DARK,
            border_color=BORDER,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            fila2,
            text="✕ Limpiar",
            width=100,
            fg_color="transparent",
            hover_color=BG_CARD,
            border_width=1,
            border_color=BORDER,
            command=self._limpiar_filtros,
        ).pack(side="right")

        self.frame = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.frame.pack(fill="both", expand=True, padx=20, pady=16)

        self._search_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._carrera_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._desde_var.trace_add("write", lambda *_: self._aplicar_filtros())
        self._hasta_var.trace_add("write", lambda *_: self._aplicar_filtros())

        self.cargar_datos()

    def cargar_datos(self):
        self._todos = listar_practicas()
        self._aplicar_filtros()

    def _parse_fecha(self, texto):
        texto = str(texto or "").strip()

        if not texto:
            return None

        for formato in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue

        return None

    def _limpiar_filtros(self):
        self._search_var.set("")
        self._carrera_var.set("Todas")
        self._desde_var.set("")
        self._hasta_var.set("")

    def _aplicar_filtros(self):
        if not hasattr(self, "frame"):
            return

        texto = self._search_var.get().strip().lower()
        carrera = self._carrera_var.get().strip()
        desde = self._parse_fecha(self._desde_var.get())
        hasta = self._parse_fecha(self._hasta_var.get())

        datos = []

        for fila in self._todos:
            if texto:
                contenido = " ".join(
                    str(fila[indice] or "")
                    for indice in (
                        IDX_CARRERA,
                        IDX_ASIGNATURA,
                        IDX_TEMA,
                        IDX_DOCENTE,
                    )
                ).lower()

                if texto not in contenido:
                    continue

            if carrera and carrera != "Todas":
                if carrera.lower() not in str(
                    fila[IDX_CARRERA] or ""
                ).lower():
                    continue

            fecha = _fecha_datetime(fila[IDX_FECHA])

            if desde:
                if not fecha or fecha.date() < desde.date():
                    continue

            if hasta:
                if not fecha or fecha.date() > hasta.date():
                    continue

            datos.append(fila)

        self._renderizar(datos)

    def _renderizar(self, datos):
        for widget in self.frame.winfo_children():
            widget.destroy()

        total = len(datos)
        self._lbl_count.configure(
            text=f"{total} práctica{'s' if total != 1 else ''}"
        )

        if not datos:
            ctk.CTkLabel(
                self.frame,
                text="No se encontraron prácticas.",
                font=("Consolas", 13),
                text_color=TEXT_SEC,
            ).pack(pady=50)
            return

        for fila in datos:
            self._crear_tarjeta(fila)

    def _crear_tarjeta(self, fila):
        id_practica = fila[IDX_ID]
        fecha = _fecha_texto(fila[IDX_FECHA])
        carrera = str(fila[IDX_CARRERA] or "—")
        asignatura = str(fila[IDX_ASIGNATURA] or "—")
        tema = str(fila[IDX_TEMA] or "—")
        docente = str(fila[IDX_DOCENTE] or "—")
        pdf_url = fila[IDX_PDF]

        tarjeta = ctk.CTkFrame(
            self.frame,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        tarjeta.pack(fill="x", pady=5)

        ctk.CTkFrame(
            tarjeta,
            width=4,
            fg_color=ACCENT,
            corner_radius=2,
        ).pack(side="left", fill="y")

        datos = ctk.CTkFrame(tarjeta, fg_color="transparent")
        datos.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        ctk.CTkLabel(
            datos,
            text=f"{fecha}   |   {carrera}   |   {asignatura}",
            font=("Consolas", 13, "bold"),
            text_color=TEXT_PRI,
            anchor="w",
        ).pack(fill="x")

        tema_corto = tema if len(tema) <= 100 else tema[:100] + "…"

        ctk.CTkLabel(
            datos,
            text=f"Docente: {docente}\nTema: {tema_corto}",
            font=("Consolas", 11),
            text_color=TEXT_SEC,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(4, 0))

        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.pack(side="right", padx=12)

        _boton(
            botones,
            "📄 PDF",
            ACCENT,
            ACCENT_DARK,
            BG_DARK,
            lambda url=pdf_url: self.abrir_pdf(url),
        )

        _boton(
            botones,
            "✏ Editar",
            BG_PANEL,
            BG_CARD_HOV,
            TEXT_PRI,
            lambda identificador=id_practica: self.editar(identificador),
        )

        _boton(
            botones,
            "🗑 Eliminar",
            RED,
            RED_DARK,
            TEXT_PRI,
            lambda identificador=id_practica: self.eliminar_y_recargar(
                identificador
            ),
        )

    def abrir_pdf(self, url):
        url = str(url or "").strip()

        if not url:
            messagebox.showwarning(
                "PDF no disponible",
                "Este registro no tiene PDF.",
                parent=self,
            )
            return

        if not url.lower().startswith(("http://", "https://")):
            messagebox.showerror(
                "PDF no válido",
                "El registro no contiene una URL pública válida.",
                parent=self,
            )
            return

        if not webbrowser.open(url):
            messagebox.showerror(
                "Error",
                "No fue posible abrir el navegador.",
                parent=self,
            )

    def editar(self, id_practica):
        registro = buscar_por_id(id_practica)

        if not registro:
            messagebox.showerror(
                "Error",
                "No se encontró la práctica.",
                parent=self,
            )
            return

        ventana = VentanaEditarPractica(self, registro)

        try:
            ventana.grab_set()
        except Exception:
            pass

        self.wait_window(ventana)
        self.cargar_datos()

    def eliminar_y_recargar(self, id_practica):
        confirmar = messagebox.askyesno(
            "Eliminar práctica",
            (
                "¿Desea eliminar esta práctica?\n\n"
                "Se eliminará también el PDF almacenado en Supabase. "
                "Esta acción no se puede deshacer."
            ),
            parent=self,
        )

        if not confirmar:
            return

        exito, mensaje = eliminar_practica(id_practica)

        if not exito:
            messagebox.showerror(
                "No se pudo eliminar",
                mensaje,
                parent=self,
            )
            return

        messagebox.showinfo(
            "Práctica eliminada",
            mensaje,
            parent=self,
        )

        self.cargar_datos()