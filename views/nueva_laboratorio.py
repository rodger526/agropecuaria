import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import time
import socket
import uuid

import qrcode
from customtkinter import CTkImage

from models.laboratorio import Laboratorio
from database.laboratorio.guardar_laboratorio import guardar_laboratorio
from pdf.generador_pdf_laboratorio import generar_pdf_laboratorio
from firma.servidor_firma import app as flask_app

# ─── Paleta compartida con el resto del sistema ──────────────────────
BG_DARK     = "#0F1923"
BG_PANEL    = "#1A2535"
BG_CARD     = "#1E2D42"
ACCENT      = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI    = "#E8EDF2"
TEXT_SEC    = "#8A9BB0"
BORDER      = "#2A3A50"


def _label(parent, text):
    return ctk.CTkLabel(
        parent, text=text.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT, anchor="w",
    )


def _entry(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
        font=("Consolas", 13), corner_radius=6, height=38,
    )


def _textbox(parent, height=110):
    return ctk.CTkTextbox(
        parent, height=height,
        fg_color=BG_DARK, border_color=BORDER, border_width=1,
        text_color=TEXT_PRI, font=("Consolas", 13), corner_radius=6,
    )


def _normalizar_hora(texto: str) -> str:
    """
    Convierte una hora escrita sin dos puntos a formato HH:MM.
    Acepta: "830" -> "08:30", "0830" -> "08:30", "8" -> "08:00",
    "08:30" -> "08:30" (se deja igual si ya viene con ':').
    Lanza ValueError si el texto no se puede interpretar como hora válida.
    """
    texto = texto.strip()
    if not texto:
        raise ValueError("La hora no puede estar vacía.")

    # Si ya viene con ':', solo se valida el formato
    if ":" in texto:
        partes = texto.split(":")
        if len(partes) != 2:
            raise ValueError(f"Hora inválida: '{texto}'")
        horas, minutos = partes
    else:
        # Solo dígitos: "8" "830" "0830" "1645"
        if not texto.isdigit():
            raise ValueError(f"Hora inválida: '{texto}'")
        if len(texto) <= 2:
            horas, minutos = texto, "00"
        elif len(texto) == 3:
            horas, minutos = texto[0], texto[1:]
        else:
            horas, minutos = texto[:-2], texto[-2:]

    try:
        h, m = int(horas), int(minutos)
    except ValueError:
        raise ValueError(f"Hora inválida: '{texto}'")

    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Hora fuera de rango: '{texto}'")

    return f"{h:02d}:{m:02d}"


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


class VentanaNuevoLaboratorio(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Registro de Laboratorio")
        self.geometry("1300x950")
        self.configure(fg_color=BG_DARK)

        # Código único de sesión para el QR de estudiantes
        self._codigo_sesion = f"LAB-{uuid.uuid4().hex[:10]}"

        self._servidor_iniciado = False
        self._polling_activo    = False
        self._img_refs          = {}
        self._estudiantes_firmados = []   # se llena vía polling

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="REGISTRO DE PRÁCTICA DE LABORATORIO",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_PRI,
        ).pack(side="left", padx=24)

        self._lbl_fecha = ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%d/%m/%Y  %H:%M"),
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        )
        self._lbl_fecha.pack(side="right", padx=24)

        ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0).pack(fill="x")

        # ── Scroll ────────────────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK,
            scrollbar_button_color=ACCENT,
            scrollbar_button_hover_color=ACCENT_DARK,
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self.crear_campos()

    # ───────────────────────────────────────────────────────────────

    def crear_campos(self):

        # ══ SECCIÓN 1 — DATOS INFORMATIVOS ═══════════════════════════
        s1 = _section_card(self.scroll, "1.  DATOS INFORMATIVOS")

        row1 = ctk.CTkFrame(s1, fg_color="transparent")
        row1.pack(fill="x", pady=(6, 0))
        c1 = ctk.CTkFrame(row1, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(c1, "Laboratorio").pack(anchor="w")
        self.laboratorio = _entry(c1)
        self.laboratorio.pack(fill="x", pady=5)

        c2 = ctk.CTkFrame(row1, fg_color="transparent")
        c2.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(c2, "Número de Estudiantes").pack(anchor="w")
        self.numero_estudiantes = _entry(c2, "Ej: 25")
        self.numero_estudiantes.pack(fill="x", pady=5)

        row2 = ctk.CTkFrame(s1, fg_color="transparent")
        row2.pack(fill="x", pady=(6, 0))
        c3 = ctk.CTkFrame(row2, fg_color="transparent")
        c3.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(c3, "Asignatura").pack(anchor="w")
        self.asignatura = _entry(c3)
        self.asignatura.pack(fill="x", pady=5)

        c4 = ctk.CTkFrame(row2, fg_color="transparent")
        c4.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(c4, "Unidad Académica").pack(anchor="w")
        self.unidad_academica = _entry(c4)
        self.unidad_academica.pack(fill="x", pady=5)

        row3 = ctk.CTkFrame(s1, fg_color="transparent")
        row3.pack(fill="x", pady=(6, 0))
        c5 = ctk.CTkFrame(row3, fg_color="transparent")
        c5.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(c5, "Semestre").pack(anchor="w")
        self.semestre = _entry(c5, "Ej: 3")
        self.semestre.pack(fill="x", pady=5)

        c6 = ctk.CTkFrame(row3, fg_color="transparent")
        c6.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(c6, "Carrera").pack(anchor="w")
        self.carrera = _entry(c6)
        self.carrera.pack(fill="x", pady=5)

        row4 = ctk.CTkFrame(s1, fg_color="transparent")
        row4.pack(fill="x", pady=(6, 0))
        c7 = ctk.CTkFrame(row4, fg_color="transparent")
        c7.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(c7, "Hora Entrada").pack(anchor="w")
        self.hora_entrada = _entry(c7, "Ej: 0830 u 830")
        self.hora_entrada.pack(fill="x", pady=5)

        c8 = ctk.CTkFrame(row4, fg_color="transparent")
        c8.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(c8, "Hora Salida").pack(anchor="w")
        self.hora_salida = _entry(c8, "Ej: 1645 u 1645")
        self.hora_salida.pack(fill="x", pady=5)

        row5 = ctk.CTkFrame(s1, fg_color="transparent")
        row5.pack(fill="x", pady=(6, 0))
        c9 = ctk.CTkFrame(row5, fg_color="transparent")
        c9.pack(side="left", fill="x", expand=True, padx=(0, 8))
        _label(c9, "Institución").pack(anchor="w")
        self.institucion = _entry(c9)
        self.institucion.pack(fill="x", pady=5)

        c10 = ctk.CTkFrame(row5, fg_color="transparent")
        c10.pack(side="left", fill="x", expand=True, padx=(8, 0))
        _label(c10, "Ciudad").pack(anchor="w")
        self.ciudad = _entry(c10)
        self.ciudad.pack(fill="x", pady=5)

        _label(s1, "Docente Responsable").pack(anchor="w", pady=(6, 0))
        self.docente = _entry(s1)
        self.docente.pack(fill="x", pady=5)

        # ══ SECCIÓN 2 — DATOS ACADÉMICOS ═════════════════════════════
        s2 = _section_card(self.scroll, "2.  DATOS ACADÉMICOS")

        _label(s2, "Tema de la Práctica").pack(anchor="w")
        self.tema = _textbox(s2, height=90)
        self.tema.pack(fill="x", pady=5)

        _label(s2, "Subtema").pack(anchor="w", pady=(8, 0))
        self.subtema = _textbox(s2, height=70)
        self.subtema.pack(fill="x", pady=5)

        _label(s2, "Logro de Aprendizaje").pack(anchor="w", pady=(8, 0))
        self.logro = _textbox(s2, height=90)
        self.logro.pack(fill="x", pady=5)

        # ══ SECCIÓN 3 — PLANIFICACIÓN ════════════════════════════════
        s3 = _section_card(self.scroll, "3.  PLANIFICACIÓN")

        _label(s3, "Objetivos").pack(anchor="w")
        self.objetivos = _textbox(s3, height=100)
        self.objetivos.pack(fill="x", pady=5)

        _label(s3, "Metodología").pack(anchor="w", pady=(8, 0))
        self.metodologia = _textbox(s3, height=100)
        self.metodologia.pack(fill="x", pady=5)

        _label(s3, "Resultados").pack(anchor="w", pady=(8, 0))
        self.resultados = _textbox(s3, height=100)
        self.resultados.pack(fill="x", pady=5)

        _label(s3, "Conclusiones").pack(anchor="w", pady=(8, 0))
        self.conclusiones = _textbox(s3, height=100)
        self.conclusiones.pack(fill="x", pady=5)

        _label(s3, "Observaciones").pack(anchor="w", pady=(8, 0))
        self.observaciones = _textbox(s3, height=100)
        self.observaciones.pack(fill="x", pady=5)

        # ══ SECCIÓN 4 — MATERIALES Y REACTIVOS ═══════════════════════
        s4 = _section_card(self.scroll, "4.  MATERIALES Y REACTIVOS")

        _label(s4, "Materiales (uno por línea)").pack(anchor="w")
        self.materiales = _textbox(s4, height=130)
        self.materiales.pack(fill="x", pady=5)

        _label(s4, "Reactivos (uno por línea)").pack(anchor="w", pady=(8, 0))
        self.reactivos = _textbox(s4, height=130)
        self.reactivos.pack(fill="x", pady=5)

        # ══ SECCIÓN 5 — FIRMAS DE ESTUDIANTES ═════════════════════════
        s5 = _section_card(
            self.scroll,
            "5.  FIRMAS DE ESTUDIANTES",
            "Cada estudiante escanea el QR, ingresa nombre y cédula, y firma desde su teléfono",
        )

        self._btn_qr_est = ctk.CTkButton(
            s5,
            text="⬤  Generar QR para estudiantes",
            fg_color=BG_CARD, hover_color="#243348",
            text_color=ACCENT, font=("Consolas", 13, "bold"),
            corner_radius=8, height=42,
            border_width=1, border_color=ACCENT,
            command=self._iniciar_servidor_estudiantes,
        )
        self._btn_qr_est.pack(fill="x", pady=(0, 14))

        contenedor = ctk.CTkFrame(s5, fg_color="transparent")
        contenedor.pack(fill="x")

        # Columna izquierda: QR
        col_qr = ctk.CTkFrame(contenedor, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        col_qr.pack(side="left", padx=(0, 8), pady=4)

        ctk.CTkLabel(
            col_qr, text="ESCANEA PARA FIRMAR",
            font=("Consolas", 10, "bold"), text_color=ACCENT,
        ).pack(pady=(12, 6), padx=20)

        self._lbl_qr_est = ctk.CTkLabel(col_qr, text="Presiona el botón\npara generar el QR", text_color=TEXT_SEC, font=("Consolas", 10))
        self._lbl_qr_est.pack(padx=20, pady=(0, 14))

        # Columna derecha: contador + lista
        col_lista = ctk.CTkFrame(contenedor, fg_color=BG_DARK, corner_radius=8, border_width=1, border_color=BORDER)
        col_lista.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)

        self._lbl_contador = ctk.CTkLabel(
            col_lista, text="0 / —  estudiantes firmados",
            font=("Consolas", 13, "bold"), text_color=ACCENT,
        )
        self._lbl_contador.pack(pady=(14, 4), padx=14, anchor="w")

        self._barra_progreso = ctk.CTkProgressBar(
            col_lista, progress_color=ACCENT, fg_color=BG_PANEL, height=8,
        )
        self._barra_progreso.set(0)
        self._barra_progreso.pack(fill="x", padx=14, pady=(0, 10))

        self._lista_estudiantes = ctk.CTkTextbox(
            col_lista, height=140,
            fg_color=BG_PANEL, border_color=BORDER, border_width=1,
            text_color=TEXT_SEC, font=("Consolas", 11), corner_radius=6,
        )
        self._lista_estudiantes.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._lista_estudiantes.insert("1.0", "Aún no hay firmas registradas.")
        self._lista_estudiantes.configure(state="disabled")

        # ══ SECCIÓN 6 — ESTUDIANTES (lista manual opcional) ═══════════
        s6 = _section_card(
            self.scroll,
            "6.  ESTUDIANTES (lista manual, opcional)",
            "Si prefieres no usar el QR, puedes pegar la lista aquí: una línea por estudiante",
        )

        _label(s6, "Estudiantes (uno por línea)").pack(anchor="w")
        self.estudiantes = _textbox(s6, height=200)
        self.estudiantes.pack(fill="x", pady=5)

        # ══ BOTÓN GUARDAR ════════════════════════════════════════════
        ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR REGISTRO",
            command=self.guardar,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="#0F1923", font=("Consolas", 14, "bold"),
            corner_radius=8, height=48,
        ).pack(pady=24, fill="x")

    # ─── Servidor y QR de estudiantes ──────────────────────────────────

    def _iniciar_servidor_estudiantes(self):
        if not self._servidor_iniciado:
            t = threading.Thread(
                target=lambda: flask_app.run(
                    host="0.0.0.0", port=5000, debug=False, use_reloader=False
                ),
                daemon=True,
            )
            t.start()
            self._servidor_iniciado = True
            time.sleep(0.9)

        self._generar_qr_estudiantes()

        if not self._polling_activo:
            self._polling_activo = True
            self._polling_estudiantes()

        self._btn_qr_est.configure(text="↺  Regenerar QR")

    def _generar_qr_estudiantes(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = socket.gethostbyname(socket.gethostname())

        url = f"http://{ip}:5000/firma/estudiante/{self._codigo_sesion}"
        qr_img = qrcode.make(url).resize((190, 190)).convert("RGB")
        photo  = CTkImage(light_image=qr_img, dark_image=qr_img, size=(190, 190))
        self._img_refs["qr_est"] = photo
        self._lbl_qr_est.configure(image=photo, text="")

    def _limite_estudiantes(self):
        """Devuelve el número máximo de estudiantes esperado, o None si no se ingresó."""
        try:
            n = int(self.numero_estudiantes.get().strip())
            return n if n > 0 else None
        except ValueError:
            return None

    def _polling_estudiantes(self):
        if not self.winfo_exists():
            return

        import json
        ruta_sesion = f"firma/sesiones/{self._codigo_sesion}.json"
        try:
            with open(ruta_sesion, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._estudiantes_firmados = data.get("estudiantes", [])
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # aún no hay firmas registradas, se reintenta en el próximo ciclo

        total   = len(self._estudiantes_firmados)
        limite  = self._limite_estudiantes()

        if limite:
            self._lbl_contador.configure(text=f"{total} / {limite}  estudiantes firmados")
            self._barra_progreso.set(min(total / limite, 1.0))
        else:
            self._lbl_contador.configure(text=f"{total}  estudiantes firmados")
            self._barra_progreso.set(0)

        self._lista_estudiantes.configure(state="normal")
        self._lista_estudiantes.delete("1.0", "end")
        if total == 0:
            self._lista_estudiantes.insert("1.0", "Aún no hay firmas registradas.")
        else:
            texto = "\n".join(
                f"{i+1}. {e['nombre']}  —  {e['cedula']}"
                + (f"   ({e['hora']})" if e.get("hora") else "")
                for i, e in enumerate(self._estudiantes_firmados)
            )
            self._lista_estudiantes.insert("1.0", texto)
        self._lista_estudiantes.configure(state="disabled")

        # Si se alcanzó el límite, detener polling y avisar
        if limite and total >= limite:
            self._lbl_contador.configure(text=f"✔ {total} / {limite}  ¡Completo!")
            self._polling_activo = False
            return

        self.after(2500, self._polling_estudiantes)

    # ─── Guardar ─────────────────────────────────────────────────────

    def guardar(self):

        try:
            codigo = datetime.now().strftime("LAB-%Y%m%d%H%M%S")

            try:
                hora_entrada_norm = _normalizar_hora(self.hora_entrada.get())
                hora_salida_norm  = _normalizar_hora(self.hora_salida.get())
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

            # Materiales y reactivos: una línea por ítem -> dict simple
            materiales_lista = [
                {"nombre": linea.strip(), "cantidad": None}
                for linea in self.materiales.get("1.0", "end").splitlines()
                if linea.strip()
            ]
            reactivos_lista = [
                {"nombre": linea.strip(), "cantidad": None}
                for linea in self.reactivos.get("1.0", "end").splitlines()
                if linea.strip()
            ]

            # Estudiantes: combina los firmados por QR + los de la lista manual
            estudiantes_lista = [
                {
                    "nombre": e["nombre"],
                    "cedula": e["cedula"],
                    "firma_ruta": e.get("firma_ruta"),
                }
                for e in self._estudiantes_firmados
            ]

            for linea in self.estudiantes.get("1.0", "end").splitlines():
                linea = linea.strip()
                if linea:
                    estudiantes_lista.append({
                        "nombre": linea,
                        "cedula": None,
                        "firma_ruta": None,
                    })

            laboratorio = Laboratorio(
                codigo,
                self.laboratorio.get().strip(),
                self.numero_estudiantes.get().strip(),
                self.asignatura.get().strip(),
                self.unidad_academica.get().strip(),
                self.semestre.get().strip(),
                self.carrera.get().strip(),
                hora_entrada_norm,
                hora_salida_norm,
                self.institucion.get().strip(),
                self.ciudad.get().strip(),
                self.docente.get().strip(),
                datetime.now().strftime("%Y-%m-%d"),
                self.tema.get("1.0", "end").strip(),
                self.subtema.get("1.0", "end").strip(),
                self.logro.get("1.0", "end").strip(),
                self.objetivos.get("1.0", "end").strip(),
                self.metodologia.get("1.0", "end").strip(),
                self.resultados.get("1.0", "end").strip(),
                self.conclusiones.get("1.0", "end").strip(),
                self.observaciones.get("1.0", "end").strip(),
                materiales=materiales_lista,
                reactivos=reactivos_lista,
                estudiantes=estudiantes_lista,
            )

            guardar_laboratorio(laboratorio)
            generar_pdf_laboratorio(laboratorio)

            messagebox.showinfo("Correcto", "Registro guardado correctamente.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))