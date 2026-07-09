import customtkinter as ctk
from tkinter import messagebox

from database.laboratorio.editar_laboratorio import actualizar_laboratorio
from models.laboratorio import Laboratorio

# ─── Paleta compartida ───────────────────────────────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_CARD     = "#1E2D42"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"
RED         = "#E05252"
RED_DARK    = "#B83C3C"


def _label(parent, text):
    return ctk.CTkLabel(
        parent, text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT, anchor="w",
    )


def _entry(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
        placeholder_text=placeholder,
        font=("Consolas", 13), corner_radius=6, height=38,
    )


def _textbox(parent, height=110):
    return ctk.CTkTextbox(
        parent, height=height,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, font=("Consolas", 13), corner_radius=6,
    )


def _section_card(parent, title, subtitle=""):
    outer = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=10)
    outer.pack(fill="x", pady=(0, 16))
    ctk.CTkFrame(outer, width=4, fg_color=ACCENT, corner_radius=2).pack(side="left", fill="y")
    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
    ctk.CTkLabel(
        inner, text=title, font=("Consolas", 13, "bold"),
        text_color=ACCENT, anchor="w",
    ).pack(anchor="w", pady=(0, 2))
    if subtitle:
        ctk.CTkLabel(
            inner, text=subtitle, font=("Consolas", 10),
            text_color=TEXT_SEC, anchor="w",
        ).pack(anchor="w", pady=(0, 8))
    return inner


class VentanaEditarLaboratorio(ctk.CTkToplevel):

    def __init__(self, master, registro: Laboratorio):
        super().__init__(master)

        self.registro = registro
        self.id_lab   = registro.id
        self.codigo   = registro.codigo
        self.pdf_url  = registro.pdf_url

        self._filas_materiales   = []
        self._filas_reactivos    = []
        self._filas_estudiantes  = []

        self.title("Editar Laboratorio")
        self.geometry("1100x900")
        self.configure(fg_color=BG_DARK)

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="✏  EDITAR LABORATORIO",
            font=("Consolas", 15, "bold"), text_color=TEXT_PRI,
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header, text=f"ID #{self.id_lab}",
            font=("Consolas", 12, "bold"), text_color=ACCENT,
        ).pack(side="right", padx=20)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Scroll ────────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ══ SECCIÓN 1 — DATOS INFORMATIVOS ═══════════════════════════
        s1 = _section_card(scroll, "1.  DATOS INFORMATIVOS")

        row1 = ctk.CTkFrame(s1, fg_color="transparent")
        row1.pack(fill="x", pady=(6, 0))
        col_a = ctk.CTkFrame(row1, fg_color="transparent")
        col_a.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_a, "Laboratorio").pack(anchor="w")
        self.laboratorio = _entry(col_a)
        self.laboratorio.insert(0, registro.laboratorio or "")
        self.laboratorio.pack(fill="x", pady=5)

        col_b = ctk.CTkFrame(row1, fg_color="transparent")
        col_b.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_b, "N° Estudiantes").pack(anchor="w")
        self.numero_estudiantes = _entry(col_b)
        self.numero_estudiantes.insert(0, str(registro.numero_estudiantes or ""))
        self.numero_estudiantes.pack(fill="x", pady=5)

        row2 = ctk.CTkFrame(s1, fg_color="transparent")
        row2.pack(fill="x", pady=(6, 0))
        col_c = ctk.CTkFrame(row2, fg_color="transparent")
        col_c.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_c, "Asignatura").pack(anchor="w")
        self.asignatura = _entry(col_c)
        self.asignatura.insert(0, registro.asignatura or "")
        self.asignatura.pack(fill="x", pady=5)

        col_d = ctk.CTkFrame(row2, fg_color="transparent")
        col_d.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_d, "Unidad Académica").pack(anchor="w")
        self.unidad_academica = _entry(col_d)
        self.unidad_academica.insert(0, registro.unidad_academica or "")
        self.unidad_academica.pack(fill="x", pady=5)

        row3 = ctk.CTkFrame(s1, fg_color="transparent")
        row3.pack(fill="x", pady=(6, 0))
        col_e = ctk.CTkFrame(row3, fg_color="transparent")
        col_e.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_e, "Semestre").pack(anchor="w")
        self.semestre = _entry(col_e)
        self.semestre.insert(0, str(registro.semestre or ""))
        self.semestre.pack(fill="x", pady=5)

        col_f = ctk.CTkFrame(row3, fg_color="transparent")
        col_f.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_f, "Carrera").pack(anchor="w")
        self.carrera = _entry(col_f)
        self.carrera.insert(0, registro.carrera or "")
        self.carrera.pack(fill="x", pady=5)

        row4 = ctk.CTkFrame(s1, fg_color="transparent")
        row4.pack(fill="x", pady=(6, 0))
        col_g = ctk.CTkFrame(row4, fg_color="transparent")
        col_g.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_g, "Hora Entrada").pack(anchor="w")
        self.hora_entrada = _entry(col_g, "HH:MM")
        self.hora_entrada.insert(0, str(registro.hora_entrada or ""))
        self.hora_entrada.pack(fill="x", pady=5)

        col_h = ctk.CTkFrame(row4, fg_color="transparent")
        col_h.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_h, "Hora Salida").pack(anchor="w")
        self.hora_salida = _entry(col_h, "HH:MM")
        self.hora_salida.insert(0, str(registro.hora_salida or ""))
        self.hora_salida.pack(fill="x", pady=5)

        row5 = ctk.CTkFrame(s1, fg_color="transparent")
        row5.pack(fill="x", pady=(6, 0))
        col_i = ctk.CTkFrame(row5, fg_color="transparent")
        col_i.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_i, "Institución").pack(anchor="w")
        self.institucion = _entry(col_i)
        self.institucion.insert(0, registro.institucion or "")
        self.institucion.pack(fill="x", pady=5)

        col_j = ctk.CTkFrame(row5, fg_color="transparent")
        col_j.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_j, "Ciudad").pack(anchor="w")
        self.ciudad = _entry(col_j)
        self.ciudad.insert(0, registro.ciudad or "")
        self.ciudad.pack(fill="x", pady=5)

        row6 = ctk.CTkFrame(s1, fg_color="transparent")
        row6.pack(fill="x", pady=(6, 0))
        col_k = ctk.CTkFrame(row6, fg_color="transparent")
        col_k.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(col_k, "Docente Responsable").pack(anchor="w")
        self.docente_responsable = _entry(col_k)
        self.docente_responsable.insert(0, registro.docente_responsable or "")
        self.docente_responsable.pack(fill="x", pady=5)

        col_l = ctk.CTkFrame(row6, fg_color="transparent")
        col_l.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(col_l, "Fecha Práctica").pack(anchor="w")
        self.fecha_practica = _entry(col_l, "DD/MM/AAAA")
        self.fecha_practica.insert(0, str(registro.fecha_practica or ""))
        self.fecha_practica.pack(fill="x", pady=5)

        # ══ SECCIÓN 2 — DATOS ACADÉMICOS ═════════════════════════════
        s2 = _section_card(scroll, "2.  DATOS ACADÉMICOS")

        _label(s2, "Tema de la Práctica").pack(anchor="w")
        self.tema = _textbox(s2, height=90)
        self.tema.pack(fill="x", pady=5)
        self.tema.insert("1.0", registro.tema_practica or "")

        _label(s2, "Subtema").pack(anchor="w", pady=(8, 0))
        self.subtema = _entry(s2)
        self.subtema.insert(0, registro.subtema or "")
        self.subtema.pack(fill="x", pady=5)

        _label(s2, "Logro de Aprendizaje").pack(anchor="w", pady=(8, 0))
        self.logro_aprendizaje = _textbox(s2, height=90)
        self.logro_aprendizaje.pack(fill="x", pady=5)
        self.logro_aprendizaje.insert("1.0", registro.logro_aprendizaje or "")

        # ══ SECCIÓN 3 — PLANIFICACIÓN ════════════════════════════════
        s3 = _section_card(scroll, "3.  PLANIFICACIÓN")

        _label(s3, "Objetivos").pack(anchor="w")
        self.objetivos = _textbox(s3, height=100)
        self.objetivos.pack(fill="x", pady=5)
        self.objetivos.insert("1.0", registro.objetivos or "")

        _label(s3, "Metodología").pack(anchor="w", pady=(8, 0))
        self.metodologia = _textbox(s3, height=100)
        self.metodologia.pack(fill="x", pady=5)
        self.metodologia.insert("1.0", registro.metodologia or "")

        _label(s3, "Resultados").pack(anchor="w", pady=(8, 0))
        self.resultados = _textbox(s3, height=100)
        self.resultados.pack(fill="x", pady=5)
        self.resultados.insert("1.0", registro.resultados or "")

        _label(s3, "Conclusiones").pack(anchor="w", pady=(8, 0))
        self.conclusiones = _textbox(s3, height=100)
        self.conclusiones.pack(fill="x", pady=5)
        self.conclusiones.insert("1.0", registro.conclusiones or "")

        _label(s3, "Observaciones").pack(anchor="w", pady=(8, 0))
        self.observaciones = _textbox(s3, height=90)
        self.observaciones.pack(fill="x", pady=5)
        self.observaciones.insert("1.0", registro.observaciones or "")

        # ══ SECCIÓN 4 — MATERIALES ═══════════════════════════════════
        s4 = _section_card(scroll, "4.  MATERIALES")
        self._cont_materiales = ctk.CTkFrame(s4, fg_color="transparent")
        self._cont_materiales.pack(fill="x")
        for m in (registro.materiales or []):
            self._agregar_fila_material(m.get("nombre", ""), m.get("cantidad", ""))
        ctk.CTkButton(
            s4, text="+  Agregar material",
            fg_color=BG_CARD, hover_color="#243348", text_color=ACCENT,
            font=("Consolas", 11, "bold"), corner_radius=6, height=32,
            border_width=1, border_color=ACCENT,
            command=lambda: self._agregar_fila_material(),
        ).pack(anchor="w", pady=(8, 0))

        # ══ SECCIÓN 5 — REACTIVOS ═════════════════════════════════════
        # NOTA: laboratorio_reactivos solo tiene columnas (nombre, cantidad),
        # sin 'unidad', según database/laboratorio/buscar_laboratorio.py
        s5 = _section_card(scroll, "5.  REACTIVOS")
        self._cont_reactivos = ctk.CTkFrame(s5, fg_color="transparent")
        self._cont_reactivos.pack(fill="x")
        for r in (registro.reactivos or []):
            self._agregar_fila_reactivo(r.get("nombre", ""), r.get("cantidad", ""))
        ctk.CTkButton(
            s5, text="+  Agregar reactivo",
            fg_color=BG_CARD, hover_color="#243348", text_color=ACCENT,
            font=("Consolas", 11, "bold"), corner_radius=6, height=32,
            border_width=1, border_color=ACCENT,
            command=lambda: self._agregar_fila_reactivo(),
        ).pack(anchor="w", pady=(8, 0))

        # ══ SECCIÓN 6 — ESTUDIANTES ═══════════════════════════════════
        # NOTA: laboratorio_estudiantes usa 'cedula', no 'codigo'.
        s6 = _section_card(scroll, "6.  ESTUDIANTES")
        self._cont_estudiantes = ctk.CTkFrame(s6, fg_color="transparent")
        self._cont_estudiantes.pack(fill="x")
        for e in (registro.estudiantes or []):
            self._agregar_fila_estudiante(e.get("nombre", ""), e.get("cedula", ""))
        ctk.CTkButton(
            s6, text="+  Agregar estudiante",
            fg_color=BG_CARD, hover_color="#243348", text_color=ACCENT,
            font=("Consolas", 11, "bold"), corner_radius=6, height=32,
            border_width=1, border_color=ACCENT,
            command=lambda: self._agregar_fila_estudiante(),
        ).pack(anchor="w", pady=(8, 0))

        # ══ BOTÓN ACTUALIZAR ═════════════════════════════════════════
        ctk.CTkButton(
            scroll,
            text="⬤  ACTUALIZAR LABORATORIO",
            command=self.actualizar,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="#0F1923", font=("Consolas", 14, "bold"),
            corner_radius=8, height=48,
        ).pack(pady=24, fill="x")

    # ─── Filas dinámicas: materiales / reactivos / estudiantes ───────

    def _fila_generica(self, contenedor, campos_placeholders, lista_filas, valores):
        """
        Crea una fila con N entries + botón de eliminar, y la registra en
        `lista_filas` como dict {"frame": ..., "entries": [entry, entry, ...]}.
        `valores` es una tupla con el valor inicial de cada entry (o "").
        """
        fila = ctk.CTkFrame(contenedor, fg_color=BG_DARK, corner_radius=6)
        fila.pack(fill="x", pady=3)

        entries = []
        for i, placeholder in enumerate(campos_placeholders):
            e = ctk.CTkEntry(
                fila, placeholder_text=placeholder,
                fg_color=BG_DARK, border_color=BORDER, border_width=1,
                text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
                font=("Consolas", 12), corner_radius=6, height=34,
            )
            valor = valores[i] if i < len(valores) else ""
            if valor not in (None, ""):
                e.insert(0, str(valor))
            e.pack(side="left", fill="x", expand=True, padx=(6, 4), pady=6)
            entries.append(e)

        registro_fila = {"frame": fila, "entries": entries}

        def _quitar():
            fila.destroy()
            lista_filas.remove(registro_fila)

        ctk.CTkButton(
            fila, text="✕", width=32, height=34,
            fg_color=RED, hover_color=RED_DARK, text_color=TEXT_PRI,
            font=("Consolas", 12, "bold"), corner_radius=6,
            command=_quitar,
        ).pack(side="left", padx=(0, 6), pady=6)

        lista_filas.append(registro_fila)
        return registro_fila

    def _agregar_fila_material(self, nombre="", cantidad=""):
        self._fila_generica(
            self._cont_materiales,
            ["Nombre del material", "Cantidad"],
            self._filas_materiales,
            (nombre, cantidad),
        )

    def _agregar_fila_reactivo(self, nombre="", cantidad=""):
        self._fila_generica(
            self._cont_reactivos,
            ["Nombre del reactivo", "Cantidad"],
            self._filas_reactivos,
            (nombre, cantidad),
        )

    def _agregar_fila_estudiante(self, nombre="", cedula=""):
        self._fila_generica(
            self._cont_estudiantes,
            ["Nombre del estudiante", "Cédula"],
            self._filas_estudiantes,
            (nombre, cedula),
        )

    def _leer_filas(self, lista_filas, claves):
        """Convierte las filas de entries en una lista de dicts, ignorando filas vacías."""
        resultado = []
        for f in lista_filas:
            valores = [e.get().strip() for e in f["entries"]]
            if not any(valores):
                continue
            resultado.append({clave: val for clave, val in zip(claves, valores)})
        return resultado

    # ─── Guardar cambios ─────────────────────────────────────────────

    def actualizar(self):
        try:
            laboratorio         = self.laboratorio.get().strip()
            numero_estudiantes  = int(self.numero_estudiantes.get().strip())
            asignatura          = self.asignatura.get().strip()
            unidad_academica    = self.unidad_academica.get().strip()
            semestre            = int(self.semestre.get().strip())
            carrera              = self.carrera.get().strip()
            hora_entrada         = self.hora_entrada.get().strip()
            hora_salida           = self.hora_salida.get().strip()
            institucion           = self.institucion.get().strip()
            ciudad                = self.ciudad.get().strip()
            docente_responsable   = self.docente_responsable.get().strip()
            fecha_practica         = self.fecha_practica.get().strip()
            tema_practica          = self.tema.get("1.0", "end").strip()
            subtema                = self.subtema.get().strip()
            logro_aprendizaje      = self.logro_aprendizaje.get("1.0", "end").strip()
            objetivos              = self.objetivos.get("1.0", "end").strip()
            metodologia            = self.metodologia.get("1.0", "end").strip()
            resultados             = self.resultados.get("1.0", "end").strip()
            conclusiones           = self.conclusiones.get("1.0", "end").strip()
            observaciones          = self.observaciones.get("1.0", "end").strip()
        except ValueError:
            messagebox.showerror("Error", "Semestre y N° de Estudiantes deben ser números.")
            return

        materiales  = self._leer_filas(self._filas_materiales, ("nombre", "cantidad"))
        reactivos   = self._leer_filas(self._filas_reactivos, ("nombre", "cantidad"))
        estudiantes = self._leer_filas(self._filas_estudiantes, ("nombre", "cedula"))

        lab = Laboratorio(
            codigo=self.codigo,
            laboratorio=laboratorio,
            numero_estudiantes=numero_estudiantes,
            asignatura=asignatura,
            unidad_academica=unidad_academica,
            semestre=semestre,
            carrera=carrera,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            institucion=institucion,
            ciudad=ciudad,
            docente_responsable=docente_responsable,
            fecha_practica=fecha_practica,
            tema_practica=tema_practica,
            subtema=subtema,
            logro_aprendizaje=logro_aprendizaje,
            objetivos=objetivos,
            metodologia=metodologia,
            resultados=resultados,
            conclusiones=conclusiones,
            observaciones=observaciones,
            materiales=materiales,
            reactivos=reactivos,
            estudiantes=estudiantes,
            id=self.id_lab,
            pdf_url=self.pdf_url,
        )

        exito = actualizar_laboratorio(lab)

        if not exito:
            messagebox.showerror("Error", "No fue posible actualizar el laboratorio.")
            return

        # ── Regenerar el PDF físico con los datos editados ─────────────
        # NOTA: ajusta este bloque según cómo generes el PDF de laboratorio
        # (por ejemplo pdf.generador_pdf.generar_pdf_laboratorio). Si aún
        # no existe esa función, puedes comentar este bloque por ahora.
        try:
            if self.pdf_url:
                from pdf.generador_pdf import generar_pdf_laboratorio
                generar_pdf_laboratorio(lab, self.pdf_url)
        except ImportError:
            pass
        except Exception as e:
            messagebox.showwarning(
                "Advertencia",
                f"El laboratorio se actualizó en la base de datos,\n"
                f"pero no fue posible regenerar el PDF:\n\n{e}"
            )
            self.destroy()
            return

        messagebox.showinfo(
            "Correcto",
            "Laboratorio actualizado correctamente."
        )
        self.destroy()