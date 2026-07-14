import os

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from models.informe import InformeLaboratorio


# ─── Paleta ──────────────────────────────────────────────────────────
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


def _label(parent, texto):
    return ctk.CTkLabel(
        parent,
        text=texto.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT,
        anchor="w",
    )


def _entry(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        fg_color=BG_DARK,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        placeholder_text_color=TEXT_SEC,
        font=("Consolas", 13),
        corner_radius=6,
        height=38,
    )


def _textbox(parent, height=110):
    return ctk.CTkTextbox(
        parent,
        height=height,
        fg_color=BG_DARK,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        font=("Consolas", 13),
        corner_radius=6,
    )


def _section_card(
    parent,
    titulo,
    subtitulo="",
):
    tarjeta = ctk.CTkFrame(
        parent,
        fg_color=BG_PANEL,
        corner_radius=10,
    )
    tarjeta.pack(
        fill="x",
        pady=(0, 16),
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

    contenido = ctk.CTkFrame(
        tarjeta,
        fg_color="transparent",
    )
    contenido.pack(
        side="left",
        fill="both",
        expand=True,
        padx=16,
        pady=14,
    )

    ctk.CTkLabel(
        contenido,
        text=titulo,
        font=("Consolas", 13, "bold"),
        text_color=ACCENT,
        anchor="w",
    ).pack(
        anchor="w",
        pady=(0, 2),
    )

    if subtitulo:
        ctk.CTkLabel(
            contenido,
            text=subtitulo,
            font=("Consolas", 10),
            text_color=TEXT_SEC,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(0, 8),
        )

    return contenido


class FormularioInformeBase(ctk.CTkToplevel):
    """
    Formulario base reutilizable para crear y editar informes.

    Las clases hijas deben implementar el método guardar().
    """

    def __init__(
        self,
        master,
        titulo_ventana,
        texto_boton,
        informe=None,
    ):
        super().__init__(master)

        self.informe_original = informe

        self.ruta_hoja_datos_local = None

        self.fotos = []

        self.title(
            titulo_ventana
        )

        self.geometry(
            "1250x930"
        )

        self.minsize(
            1050,
            760,
        )

        self.configure(
            fg_color=BG_DARK
        )

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
            text=titulo_ventana.upper(),
            font=("Consolas", 16, "bold"),
            text_color=TEXT_PRI,
        ).pack(
            side="left",
            padx=24,
        )

        if informe and informe.codigo:
            ctk.CTkLabel(
                header,
                text=str(
                    informe.codigo
                ),
                font=("Consolas", 12, "bold"),
                text_color=ACCENT,
            ).pack(
                side="right",
                padx=24,
            )

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(
            fill="x"
        )

        # ── Scroll principal ──────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        self._crear_campos(
            texto_boton
        )

        if informe:
            self._cargar_informe(
                informe
            )

    # ─── Construcción del formulario ─────────────────────────────────

    def _crear_campos(
        self,
        texto_boton,
    ):
        # ══ 1. DATOS GENERALES ═══════════════════════════════════════
        seccion_datos = _section_card(
            self.scroll,
            "1.  DATOS GENERALES",
        )

        fila_1 = ctk.CTkFrame(
            seccion_datos,
            fg_color="transparent",
        )
        fila_1.pack(
            fill="x",
        )

        columna_titulo = ctk.CTkFrame(
            fila_1,
            fg_color="transparent",
        )
        columna_titulo.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            columna_titulo,
            "Título de la práctica",
        ).pack(
            anchor="w",
        )

        self.titulo_practica = _entry(
            columna_titulo,
            "Título completo del informe",
        )
        self.titulo_practica.pack(
            fill="x",
            pady=5,
        )

        columna_asignatura = ctk.CTkFrame(
            fila_1,
            fg_color="transparent",
        )
        columna_asignatura.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            columna_asignatura,
            "Asignatura",
        ).pack(
            anchor="w",
        )

        self.asignatura = _entry(
            columna_asignatura,
        )
        self.asignatura.pack(
            fill="x",
            pady=5,
        )

        _label(
            seccion_datos,
            "Autores",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.autores = _entry(
            seccion_datos,
            "Apellido 1, Nombre 1; Apellido 2, Nombre 2",
        )
        self.autores.pack(
            fill="x",
            pady=5,
        )

        fila_2 = ctk.CTkFrame(
            seccion_datos,
            fg_color="transparent",
        )
        fila_2.pack(
            fill="x",
            pady=(8, 0),
        )

        columna_carrera = ctk.CTkFrame(
            fila_2,
            fg_color="transparent",
        )
        columna_carrera.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        _label(
            columna_carrera,
            "Carrera",
        ).pack(
            anchor="w",
        )

        self.carrera = _entry(
            columna_carrera,
        )
        self.carrera.pack(
            fill="x",
            pady=5,
        )

        columna_semestre = ctk.CTkFrame(
            fila_2,
            fg_color="transparent",
        )
        columna_semestre.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
        )

        _label(
            columna_semestre,
            "Semestre",
        ).pack(
            anchor="w",
        )

        self.semestre = _entry(
            columna_semestre,
            "Ej: 3",
        )
        self.semestre.pack(
            fill="x",
            pady=5,
        )

        columna_docente = ctk.CTkFrame(
            fila_2,
            fg_color="transparent",
        )
        columna_docente.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(
            columna_docente,
            "Docente",
        ).pack(
            anchor="w",
        )

        self.docente = _entry(
            columna_docente,
        )
        self.docente.pack(
            fill="x",
            pady=5,
        )

        # ══ 2. CONTENIDO DEL INFORME ═════════════════════════════════
        seccion_contenido = _section_card(
            self.scroll,
            "2.  CONTENIDO DEL INFORME",
            (
                "El resumen debe tener máximo 150 palabras. "
                "Los campos opcionales pueden quedar vacíos."
            ),
        )

        self._crear_campo_texto(
            seccion_contenido,
            "Resumen",
            "resumen",
            120,
        )

        _label(
            seccion_contenido,
            "Palabras clave",
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        self.palabras_clave = _entry(
            seccion_contenido,
            "Entre 3 y 5 palabras o frases clave",
        )
        self.palabras_clave.pack(
            fill="x",
            pady=5,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "1. Introducción",
            "introduccion",
            170,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "2.1 Objetivo general",
            "objetivo_general",
            90,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "2.2 Objetivos específicos",
            "objetivos_especificos",
            130,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "3.1 Materiales y reactivos",
            "materiales_reactivos",
            150,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "3.2 Procedimiento experimental",
            "procedimiento_experimental",
            180,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "4. Resultados",
            "resultados",
            180,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "5. Discusión",
            "discusion",
            180,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "6. Conclusiones",
            "conclusiones",
            150,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "7. Recomendaciones",
            "recomendaciones",
            130,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "8. Bibliografía",
            "bibliografia",
            160,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "Cuestionario (opcional)",
            "cuestionario",
            130,
        )

        self._crear_campo_texto(
            seccion_contenido,
            "Anexos (opcional)",
            "anexos",
            130,
        )

        # ══ 3. ARCHIVOS Y FOTOGRAFÍAS ════════════════════════════════
        seccion_archivos = _section_card(
            self.scroll,
            "3.  ARCHIVOS Y FOTOGRAFÍAS",
            (
                "Puede adjuntar una hoja de datos en PDF o imagen. "
                "Se permiten hasta seis fotografías."
            ),
        )

        self.lbl_hoja = ctk.CTkLabel(
            seccion_archivos,
            text="No se ha seleccionado una hoja de datos.",
            text_color=TEXT_SEC,
            font=("Consolas", 11),
            anchor="w",
        )
        self.lbl_hoja.pack(
            anchor="w",
            pady=(0, 6),
        )

        fila_botones_archivos = ctk.CTkFrame(
            seccion_archivos,
            fg_color="transparent",
        )
        fila_botones_archivos.pack(
            fill="x",
        )

        ctk.CTkButton(
            fila_botones_archivos,
            text="Seleccionar hoja de datos",
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            text_color=ACCENT,
            border_width=1,
            border_color=BORDER,
            command=self._seleccionar_hoja,
        ).pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            fila_botones_archivos,
            text="+ Agregar fotografía",
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOV,
            text_color=ACCENT,
            border_width=1,
            border_color=BORDER,
            command=self._seleccionar_foto,
        ).pack(
            side="left",
        )

        self.contenedor_fotos = ctk.CTkFrame(
            seccion_archivos,
            fg_color=BG_DARK,
            corner_radius=6,
            border_width=1,
            border_color=BORDER,
        )
        self.contenedor_fotos.pack(
            fill="x",
            pady=(12, 0),
        )

        self._refrescar_fotos()

        # ══ BOTÓN GUARDAR ════════════════════════════════════════════
        ctk.CTkButton(
            self.scroll,
            text=texto_boton,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 14, "bold"),
            height=48,
            corner_radius=8,
            command=self.guardar,
        ).pack(
            fill="x",
            pady=24,
        )

    def _crear_campo_texto(
        self,
        parent,
        etiqueta,
        nombre_atributo,
        altura,
    ):
        _label(
            parent,
            etiqueta,
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        widget = _textbox(
            parent,
            altura,
        )
        widget.pack(
            fill="x",
            pady=5,
        )

        setattr(
            self,
            nombre_atributo,
            widget,
        )

    # ─── Selección de archivos ───────────────────────────────────────

    def _seleccionar_hoja(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar hoja de datos",
            filetypes=[
                (
                    "PDF o imagen",
                    "*.pdf *.png *.jpg *.jpeg",
                ),
                (
                    "Archivos PDF",
                    "*.pdf",
                ),
                (
                    "Imágenes",
                    "*.png *.jpg *.jpeg",
                ),
                (
                    "Todos los archivos",
                    "*.*",
                ),
            ],
        )

        if not ruta:
            return

        extension = Path(
            ruta
        ).suffix.lower()

        if extension not in {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
        }:
            messagebox.showerror(
                "Archivo inválido",
                (
                    "La hoja de datos debe ser un archivo "
                    "PDF, PNG, JPG o JPEG."
                ),
                parent=self,
            )
            return

        self.ruta_hoja_datos_local = ruta

        self.lbl_hoja.configure(
            text=Path(
                ruta
            ).name,
            text_color=TEXT_PRI,
        )

    def _seleccionar_foto(self):
        if len(
            self.fotos
        ) >= 6:
            messagebox.showwarning(
                "Límite",
                "Solo se permiten hasta seis fotografías.",
                parent=self,
            )
            return

        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar fotografía",
            filetypes=[
                (
                    "Imágenes",
                    "*.png *.jpg *.jpeg",
                ),
            ],
        )

        if not ruta:
            return

        extension = Path(
            ruta
        ).suffix.lower()

        if extension not in {
            ".png",
            ".jpg",
            ".jpeg",
        }:
            messagebox.showerror(
                "Archivo inválido",
                "La fotografía debe ser PNG, JPG o JPEG.",
                parent=self,
            )
            return

        self.fotos.append(
            {
                "ruta_local": ruta,
                "foto_url": None,
                "descripcion": "",
                "orden": len(
                    self.fotos
                ) + 1,
            }
        )

        self._refrescar_fotos()

    # ─── Lista visual de fotografías ─────────────────────────────────

    def _refrescar_fotos(self):
        for widget in self.contenedor_fotos.winfo_children():
            widget.destroy()

        if not self.fotos:
            ctk.CTkLabel(
                self.contenedor_fotos,
                text="Aún no se han agregado fotografías.",
                text_color=TEXT_SEC,
                font=("Consolas", 11),
            ).pack(
                pady=12,
            )
            return

        for indice, foto in enumerate(
            self.fotos
        ):
            fila = ctk.CTkFrame(
                self.contenedor_fotos,
                fg_color="transparent",
            )
            fila.pack(
                fill="x",
                padx=8,
                pady=5,
            )

            origen = (
                foto.get(
                    "ruta_local"
                )
                or foto.get(
                    "foto_url"
                )
                or "Fotografía"
            )

            nombre_visible = os.path.basename(
                str(
                    origen
                ).split(
                    "?",
                    1,
                )[0]
            )

            if not nombre_visible:
                nombre_visible = (
                    f"Fotografía {indice + 1}"
                )

            ctk.CTkLabel(
                fila,
                text=nombre_visible[:40],
                text_color=TEXT_PRI,
                font=("Consolas", 11),
                width=280,
                anchor="w",
            ).pack(
                side="left",
            )

            entrada_descripcion = _entry(
                fila,
                "Descripción de la fotografía",
            )

            entrada_descripcion.insert(
                0,
                str(
                    foto.get(
                        "descripcion"
                    )
                    or ""
                ),
            )

            entrada_descripcion.pack(
                side="left",
                fill="x",
                expand=True,
                padx=8,
            )

            foto["_entry_descripcion"] = (
                entrada_descripcion
            )

            ctk.CTkButton(
                fila,
                text="✕",
                width=34,
                height=34,
                fg_color=RED,
                hover_color=RED_DARK,
                text_color=TEXT_PRI,
                command=lambda posicion=indice: self._quitar_foto(
                    posicion
                ),
            ).pack(
                side="right",
            )

    def _quitar_foto(
        self,
        indice,
    ):
        if (
            indice < 0
            or indice >= len(
                self.fotos
            )
        ):
            return

        del self.fotos[
            indice
        ]

        for posicion, foto in enumerate(
            self.fotos,
            start=1,
        ):
            foto[
                "orden"
            ] = posicion

        self._refrescar_fotos()

    # ─── Cargar informe existente ────────────────────────────────────

    def _cargar_informe(
        self,
        informe,
    ):
        self._set_entry(
            self.titulo_practica,
            informe.titulo,
        )

        self._set_entry(
            self.autores,
            informe.autores,
        )

        self._set_entry(
            self.asignatura,
            informe.asignatura,
        )

        self._set_entry(
            self.carrera,
            informe.carrera,
        )

        self._set_entry(
            self.semestre,
            informe.semestre,
        )

        self._set_entry(
            self.docente,
            informe.docente,
        )

        self._set_text(
            self.resumen,
            informe.resumen,
        )

        self._set_entry(
            self.palabras_clave,
            informe.palabras_clave,
        )

        self._set_text(
            self.introduccion,
            informe.introduccion,
        )

        self._set_text(
            self.objetivo_general,
            informe.objetivo_general,
        )

        self._set_text(
            self.objetivos_especificos,
            informe.objetivos_especificos,
        )

        self._set_text(
            self.materiales_reactivos,
            informe.materiales_reactivos,
        )

        self._set_text(
            self.procedimiento_experimental,
            informe.procedimiento_experimental,
        )

        self._set_text(
            self.resultados,
            informe.resultados,
        )

        self._set_text(
            self.discusion,
            informe.discusion,
        )

        self._set_text(
            self.conclusiones,
            informe.conclusiones,
        )

        self._set_text(
            self.recomendaciones,
            informe.recomendaciones,
        )

        self._set_text(
            self.bibliografia,
            informe.bibliografia,
        )

        self._set_text(
            self.cuestionario,
            informe.cuestionario,
        )

        self._set_text(
            self.anexos,
            informe.anexos,
        )

        if informe.hoja_datos_url:
            self.lbl_hoja.configure(
                text=(
                    "Hoja de datos existente en Supabase"
                ),
                text_color=TEXT_PRI,
            )

        self.fotos = [
            dict(
                foto
            )
            for foto in (
                informe.fotos
                or []
            )
        ]

        self._refrescar_fotos()

    @staticmethod
    def _set_entry(
        widget,
        valor,
    ):
        widget.delete(
            0,
            "end",
        )

        widget.insert(
            0,
            str(
                valor
                or ""
            ),
        )

    @staticmethod
    def _set_text(
        widget,
        valor,
    ):
        widget.delete(
            "1.0",
            "end",
        )

        widget.insert(
            "1.0",
            str(
                valor
                or ""
            ),
        )

    # ─── Recuperar datos del formulario ──────────────────────────────

    def obtener_informe_formulario(
        self,
        codigo,
        id_informe=None,
    ):
        try:
            semestre = int(
                self.semestre.get().strip()
            )
        except ValueError as error:
            raise ValueError(
                "El semestre debe ser un número entero."
            ) from error

        if semestre <= 0:
            raise ValueError(
                "El semestre debe ser mayor que cero."
            )

        titulo = self.titulo_practica.get().strip()
        autores = self.autores.get().strip()
        asignatura = self.asignatura.get().strip()
        carrera = self.carrera.get().strip()
        docente = self.docente.get().strip()

        if not titulo:
            raise ValueError(
                "Debe ingresar el título de la práctica."
            )

        if not autores:
            raise ValueError(
                "Debe ingresar los autores."
            )

        if not asignatura:
            raise ValueError(
                "Debe ingresar la asignatura."
            )

        if not carrera:
            raise ValueError(
                "Debe ingresar la carrera."
            )

        if not docente:
            raise ValueError(
                "Debe ingresar el docente."
            )

        resumen = self.resumen.get(
            "1.0",
            "end",
        ).strip()

        cantidad_palabras_resumen = len(
            resumen.split()
        )

        if cantidad_palabras_resumen > 150:
            raise ValueError(
                "El resumen no puede superar las 150 palabras. "
                f"Actualmente tiene {cantidad_palabras_resumen}."
            )

        palabras_clave = self.palabras_clave.get().strip()

        lista_palabras_clave = [
            palabra.strip()
            for palabra in palabras_clave.replace(
                ";",
                ",",
            ).split(
                ","
            )
            if palabra.strip()
        ]

        if palabras_clave and not (
            3
            <= len(
                lista_palabras_clave
            )
            <= 5
        ):
            raise ValueError(
                "Debe ingresar entre 3 y 5 palabras clave "
                "separadas por comas."
            )

        # Recuperar las descripciones que el usuario escribió.
        fotos_limpias = []

        for indice, foto in enumerate(
            self.fotos,
            start=1,
        ):
            foto_limpia = dict(
                foto
            )

            entrada_descripcion = (
                foto_limpia.pop(
                    "_entry_descripcion",
                    None,
                )
            )

            if entrada_descripcion is not None:
                foto_limpia[
                    "descripcion"
                ] = entrada_descripcion.get().strip()

            foto_limpia[
                "orden"
            ] = indice

            fotos_limpias.append(
                foto_limpia
            )

        informe = InformeLaboratorio()

        informe.id = id_informe
        informe.codigo = codigo
        informe.titulo = titulo
        informe.autores = autores
        informe.asignatura = asignatura
        informe.carrera = carrera
        informe.semestre = semestre
        informe.docente = docente
        informe.resumen = resumen
        informe.palabras_clave = palabras_clave

        informe.introduccion = self.introduccion.get(
            "1.0",
            "end",
        ).strip()

        informe.objetivo_general = self.objetivo_general.get(
            "1.0",
            "end",
        ).strip()

        informe.objetivos_especificos = self.objetivos_especificos.get(
            "1.0",
            "end",
        ).strip()

        informe.materiales_reactivos = self.materiales_reactivos.get(
            "1.0",
            "end",
        ).strip()

        informe.procedimiento_experimental = (
            self.procedimiento_experimental.get(
                "1.0",
                "end",
            ).strip()
        )

        informe.resultados = self.resultados.get(
            "1.0",
            "end",
        ).strip()

        informe.discusion = self.discusion.get(
            "1.0",
            "end",
        ).strip()

        informe.conclusiones = self.conclusiones.get(
            "1.0",
            "end",
        ).strip()

        informe.recomendaciones = self.recomendaciones.get(
            "1.0",
            "end",
        ).strip()

        informe.bibliografia = self.bibliografia.get(
            "1.0",
            "end",
        ).strip()

        informe.cuestionario = self.cuestionario.get(
            "1.0",
            "end",
        ).strip()

        informe.anexos = self.anexos.get(
            "1.0",
            "end",
        ).strip()

        if self.informe_original:
            informe.hoja_datos_url = (
                self.informe_original.hoja_datos_url
            )

            informe.pdf_url = (
                self.informe_original.pdf_url
            )

            informe.fecha_creacion = (
                self.informe_original.fecha_creacion
            )

        informe.fotos = fotos_limpias

        return informe

    # ─── Método que implementan crear y editar ───────────────────────

    def guardar(self):
        raise NotImplementedError(
            "La clase hija debe implementar el método guardar()."
        )