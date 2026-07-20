import os
import socket
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
from tkinter import messagebox
from urllib.parse import quote

import customtkinter as ctk
import qrcode
from customtkinter import CTkImage
from PIL import Image

from database.editar import (
    actualizar_con_firma_comision,
    actualizar_datos_practica,
    obtener_estado_firmas,
    obtener_ultimo_error,
)
from firma.servidor_firma import (
    app as flask_app,
    eliminar_firmas_sesion,
    obtener_ruta_firma,
)

from pdf.agregar_firma_comision import agregar_firma_comision
from storage.subir_firma import eliminar_firma, subir_firma
from storage.subir_pdf import eliminar_pdf, subir_pdf


BG_DARK = "#0F1923"
BG_PANEL = "#1A2535"
BG_CARD = "#1E2D42"
ACCENT = "#4CAF7D"
ACCENT_DARK = "#3A9166"
TEXT_PRI = "#E8EDF2"
TEXT_SEC = "#8A9BB0"
BORDER = "#2A3A50"
WARNING = "#E7A93B"

PUERTO_FIRMAS = 5000

_SERVIDOR_LOCK = threading.Lock()
_SERVIDOR_INICIADO = False


# Ajusta únicamente estos índices si buscar_por_id() usa otro orden.
IDX_ID = 0
IDX_CODIGO = 1
IDX_CARRERA = 2
IDX_SEMESTRE = 3
IDX_ASIGNATURA = 4
IDX_UNIDAD = 5
IDX_TIPO = 6
IDX_LUGAR = 7
IDX_SEMANA = 8
IDX_TEMA = 9
IDX_RESULTADO = 10
IDX_ARTICULACION = 11
IDX_OBJETIVO = 12
IDX_MATERIALES = 13
IDX_DESCRIPCION = 14
IDX_EVIDENCIAS = 15
IDX_PDF = 16
IDX_FECHA_REGISTRO = 17
IDX_DOCENTE = 18
IDX_FECHA_CREACION = 19
IDX_FIRMA_DOCENTE = 20
IDX_FIRMA_COMISION = 21


def _col(registro, indice, default=""):
    try:
        valor = registro[indice]
        return default if valor is None else valor
    except (IndexError, TypeError):
        return default


def _tiene_valor(valor):
    return bool(str(valor or "").strip())


def _servidor_escuchando():
    try:
        with socket.create_connection(
            ("127.0.0.1", PUERTO_FIRMAS),
            timeout=0.4,
        ):
            return True
    except OSError:
        return False


def _asegurar_servidor():
    global _SERVIDOR_INICIADO

    with _SERVIDOR_LOCK:
        if _SERVIDOR_INICIADO or _servidor_escuchando():
            _SERVIDOR_INICIADO = True
            return

        threading.Thread(
            target=lambda: flask_app.run(
                host="0.0.0.0",
                port=PUERTO_FIRMAS,
                debug=False,
                use_reloader=False,
                threaded=True,
            ),
            daemon=True,
            name="ServidorFirmaComision",
        ).start()

        _SERVIDOR_INICIADO = True


def _entry(parent):
    return ctk.CTkEntry(
        parent,
        fg_color=BG_DARK,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRI,
        font=("Consolas", 13),
        corner_radius=6,
        height=38,
    )


def _textbox(parent, height=100):
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


def _label(parent, texto):
    return ctk.CTkLabel(
        parent,
        text=texto.upper(),
        font=("Consolas", 11, "bold"),
        text_color=ACCENT,
        anchor="w",
    )


def _obtener_ventana_raiz(widget):
    """
    Devuelve la ventana raíz real para que la edición no dependa
    de la vida útil de VentanaBuscar.
    """

    actual = widget

    while getattr(actual, "master", None) is not None:
        actual = actual.master

    return actual


class VentanaEditarPractica(ctk.CTkToplevel):
    """
    Edición protegida.

    Reglas:
    1. Nunca sustituye pdf_url.
    2. Nunca modifica firma_docente.
    3. Nunca reemplaza firma_comision.
    4. La firma de comisión solo se registra si estaba vacía.
    5. Editar datos no regenera ni elimina el PDF firmado anterior.
    """

    def __init__(self, master, registro):
        self.ventana_busqueda = master
        raiz = _obtener_ventana_raiz(master)
        super().__init__(raiz)

        self.id_practica = _col(registro, IDX_ID, None)
        self.codigo = _col(registro, IDX_CODIGO, "")
        self.codigo_sesion = uuid.uuid4().hex

        estado_real = obtener_estado_firmas(
            self.id_practica
        )

        self.codigo = (
            estado_real.get("codigo")
            or self.codigo
        )

        self.pdf_url_anterior = (
            estado_real.get("pdf_url")
            or _col(registro, IDX_PDF, None)
        )

        self.firma_docente_existente = (
            estado_real.get("firma_docente")
            or _col(registro, IDX_FIRMA_DOCENTE, None)
        )

        self.firma_comision_existente = (
            estado_real.get("firma_comision")
            or _col(registro, IDX_FIRMA_COMISION, None)
        )

        self.comision_ya_firmo = _tiene_valor(
            self.firma_comision_existente
        )

        self._polling_activo = False
        self._after_polling = None
        self._guardando = False
        self._cerrando = False
        self._img_refs = {}

        self.title("Editar práctica")
        self.geometry("1150x900")
        self.minsize(950, 700)
        self.configure(fg_color=BG_DARK)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

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
            text="✏  EDITAR PRÁCTICA",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_PRI,
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header,
            text=f"ID #{self.id_practica}",
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        ).pack(side="right", padx=20)

        ctk.CTkFrame(
            self,
            height=3,
            fg_color=ACCENT,
            corner_radius=0,
        ).pack(fill="x")

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

        self._crear_campos(registro)
        self._crear_panel_comision()

        self._btn_guardar = ctk.CTkButton(
            self.scroll,
            text="⬤  GUARDAR CAMBIOS",
            command=self.guardar,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=BG_DARK,
            font=("Consolas", 14, "bold"),
            height=48,
        )
        self._btn_guardar.pack(fill="x", pady=24)

    def _seccion(self, titulo):
        frame = ctk.CTkFrame(
            self.scroll,
            fg_color=BG_PANEL,
            corner_radius=10,
        )
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text=titulo,
            font=("Consolas", 13, "bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        cuerpo = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        cuerpo.pack(fill="x", padx=16, pady=(0, 14))
        return cuerpo

    def _campo_doble(
        self,
        parent,
        titulo_1,
        valor_1,
        titulo_2,
        valor_2,
    ):
        fila = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        fila.pack(fill="x", pady=5)

        izquierda = ctk.CTkFrame(
            fila,
            fg_color="transparent",
        )
        izquierda.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        derecha = ctk.CTkFrame(
            fila,
            fg_color="transparent",
        )
        derecha.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        _label(izquierda, titulo_1).pack(anchor="w")
        entrada_1 = _entry(izquierda)
        entrada_1.insert(0, str(valor_1 or ""))
        entrada_1.pack(fill="x", pady=4)

        _label(derecha, titulo_2).pack(anchor="w")
        entrada_2 = _entry(derecha)
        entrada_2.insert(0, str(valor_2 or ""))
        entrada_2.pack(fill="x", pady=4)

        return entrada_1, entrada_2

    def _campo_texto(
        self,
        parent,
        titulo,
        valor,
        altura,
    ):
        _label(parent, titulo).pack(
            anchor="w",
            pady=(8, 0),
        )

        caja = _textbox(parent, altura)
        caja.insert("1.0", str(valor or ""))
        caja.pack(fill="x", pady=4)
        return caja

    def _crear_campos(self, registro):
        s1 = self._seccion("1. DATOS INFORMATIVOS")

        self.carrera, self.semestre = self._campo_doble(
            s1,
            "Carrera",
            _col(registro, IDX_CARRERA),
            "Semestre",
            _col(registro, IDX_SEMESTRE),
        )

        self.asignatura, self.unidad = self._campo_doble(
            s1,
            "Asignatura",
            _col(registro, IDX_ASIGNATURA),
            "Unidad del sílabo",
            _col(registro, IDX_UNIDAD),
        )

        self.tipo, self.semana = self._campo_doble(
            s1,
            "Tipo de práctica",
            _col(registro, IDX_TIPO),
            "Semana planificada",
            _col(registro, IDX_SEMANA),
        )

        self.docente, self.lugar = self._campo_doble(
            s1,
            "Docente responsable",
            _col(registro, IDX_DOCENTE),
            "Lugar de ejecución",
            _col(registro, IDX_LUGAR),
        )

        s2 = self._seccion("2. DATOS ACADÉMICOS")

        self.tema = self._campo_texto(
            s2,
            "Tema de la práctica",
            _col(registro, IDX_TEMA),
            85,
        )

        self.resultado = self._campo_texto(
            s2,
            "Resultado de aprendizaje",
            _col(registro, IDX_RESULTADO),
            85,
        )

        _label(
            s2,
            "Articulación curricular",
        ).pack(anchor="w")

        self.articulacion = _entry(s2)
        self.articulacion.insert(
            0,
            str(_col(registro, IDX_ARTICULACION)),
        )
        self.articulacion.pack(fill="x", pady=4)

        s3 = self._seccion("3. PLANIFICACIÓN")

        self.objetivo = self._campo_texto(
            s3,
            "Objetivo general",
            _col(registro, IDX_OBJETIVO),
            100,
        )

        self.materiales = self._campo_texto(
            s3,
            "Materiales y equipos",
            _col(registro, IDX_MATERIALES),
            100,
        )

        self.descripcion = self._campo_texto(
            s3,
            "Descripción de la actividad",
            _col(registro, IDX_DESCRIPCION),
            120,
        )

        _label(s3, "Evidencias").pack(anchor="w")

        self.evidencias = _entry(s3)
        self.evidencias.insert(
            0,
            str(_col(registro, IDX_EVIDENCIAS)),
        )
        self.evidencias.pack(fill="x", pady=4)

    def _crear_panel_comision(self):
        s4 = self._seccion(
            "4. REVISIÓN Y FIRMA DE COMISIÓN"
        )

        panel = ctk.CTkFrame(
            s4,
            fg_color=BG_DARK,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
        )
        panel.pack(fill="x")

        ctk.CTkLabel(
            panel,
            text="COMISIÓN ACADÉMICA",
            font=("Consolas", 12, "bold"),
            text_color=ACCENT,
        ).pack(pady=(14, 6))

        self._lbl_qr = ctk.CTkLabel(
            panel,
            text="",
            text_color=TEXT_SEC,
        )
        self._lbl_qr.pack()

        self._lbl_estado = ctk.CTkLabel(
            panel,
            text="",
            font=("Consolas", 11, "bold"),
        )
        self._lbl_estado.pack(pady=6)

        self._lbl_preview = ctk.CTkLabel(
            panel,
            text="",
        )
        self._lbl_preview.pack(pady=(0, 8))

        self._btn_qr = ctk.CTkButton(
            panel,
            width=320,
            height=40,
            fg_color=BG_CARD,
            hover_color="#243348",
            text_color=ACCENT,
            border_width=1,
            border_color=ACCENT,
            command=self._iniciar_firma,
        )
        self._btn_qr.pack(pady=(4, 14))

        if self.comision_ya_firmo:
            self._lbl_qr.configure(
                text=(
                    "Esta práctica ya tiene firma de comisión."
                )
            )
            self._lbl_estado.configure(
                text="✔ FIRMA REGISTRADA — NO SE PUEDE CAMBIAR",
                text_color=ACCENT,
            )
            self._btn_qr.configure(
                text="✔ FIRMA BLOQUEADA",
                state="disabled",
            )
        else:
            self._lbl_qr.configure(
                text=(
                    "La comisión todavía no ha firmado."
                )
            )
            self._lbl_estado.configure(
                text="⏳ PENDIENTE",
                text_color=WARNING,
            )
            self._btn_qr.configure(
                text="⬤ GENERAR QR PARA COMISIÓN",
                state="normal",
            )

    def _iniciar_firma(self):
        if self.comision_ya_firmo:
            return

        try:
            _asegurar_servidor()

            self._btn_qr.configure(
                state="disabled",
                text="GENERANDO QR...",
            )

            self.after(
                700,
                self._mostrar_qr,
            )

        except Exception as error:
            messagebox.showerror(
                "Firma de comisión",
                f"No se pudo iniciar el servidor:\n{error}",
                parent=self,
            )

    def _mostrar_qr(self):
        if self._cerrando or not self.winfo_exists():
            return

        ip = self._obtener_ip()
        sesion = quote(
            self.codigo_sesion,
            safe="",
        )

        url = (
            f"http://{ip}:{PUERTO_FIRMAS}"
            f"/firma/comision?sesion={sesion}"
        )

        imagen = qrcode.make(url)
        imagen = imagen.resize((180, 180)).convert("RGB")

        imagen_ctk = CTkImage(
            light_image=imagen,
            dark_image=imagen,
            size=(180, 180),
        )

        self._img_refs["qr"] = imagen_ctk

        self._lbl_qr.configure(
            image=imagen_ctk,
            text="",
        )

        self._lbl_estado.configure(
            text="⏳ ESPERANDO FIRMA...",
            text_color=WARNING,
        )

        self._btn_qr.configure(
            state="disabled",
            text="ESPERANDO FIRMA...",
        )

        self._polling_activo = True
        self._polling_firma()

    def _obtener_ip(self):
        sock = None

        try:
            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
            )
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]

        except OSError:
            return socket.gethostbyname(
                socket.gethostname()
            )

        finally:
            if sock:
                sock.close()

    def _polling_firma(self):
        if (
            self._cerrando
            or not self._polling_activo
            or not self.winfo_exists()
        ):
            return

        ruta = obtener_ruta_firma(
            "comision",
            self.codigo_sesion,
        )

        if ruta and os.path.isfile(ruta):
            self._polling_activo = False
            self._after_polling = None

            self._lbl_estado.configure(
                text="✔ FIRMA RECIBIDA",
                text_color=ACCENT,
            )

            self._btn_qr.configure(
                text="✔ FIRMA RECIBIDA",
                state="disabled",
            )

            self._mostrar_preview(ruta)
            return

        self._after_polling = self.after(
            2000,
            self._polling_firma,
        )

    def _mostrar_preview(self, ruta):
        try:
            with Image.open(ruta) as original:
                imagen = original.convert("RGBA")

                fondo = Image.new(
                    "RGBA",
                    imagen.size,
                    (255, 255, 255, 255),
                )

                fondo.paste(
                    imagen,
                    mask=imagen.getchannel("A"),
                )

                fondo = fondo.convert("RGB")
                fondo.thumbnail((250, 95))

            vista = CTkImage(
                light_image=fondo,
                dark_image=fondo,
                size=(
                    max(1, fondo.width),
                    max(1, fondo.height),
                ),
            )

            self._img_refs["preview"] = vista

            if self._lbl_preview.winfo_exists():
                self._lbl_preview.configure(
                    image=vista,
                    text="",
                )

        except Exception as error:
            print(
                "No se pudo mostrar la firma:",
                error,
            )

    def _texto(self, widget):
        return widget.get("1.0", "end").strip()

    def _descargar_pdf_anterior(self):
        """
        Descarga temporalmente el PDF ya firmado por el docente.
        """

        url = str(self.pdf_url_anterior or "").strip()

        if not url.lower().startswith(
            ("http://", "https://")
        ):
            raise RuntimeError(
                "La práctica no tiene una URL válida del PDF anterior."
            )

        carpeta = (
            Path(tempfile.gettempdir())
            / "sistema_practicas_edicion"
        )
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        destino = carpeta / (
            f"original-{self.id_practica}-"
            f"{uuid.uuid4().hex[:8]}.pdf"
        )

        urllib.request.urlretrieve(
            url,
            destino,
        )

        if not destino.is_file():
            raise RuntimeError(
                "No se pudo descargar el PDF anterior."
            )

        return destino

    def _crear_pdf_con_firma_comision(
        self,
        pdf_anterior,
        firma_comision,
    ):
        """
        Inserta la comisión sobre el PDF anterior.

        Así la firma del docente permanece exactamente igual.
        """

        carpeta = (
            Path(tempfile.gettempdir())
            / "sistema_practicas_edicion"
        )
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        salida = carpeta / (
            f"{self.codigo or 'practica'}-"
            f"comision-{uuid.uuid4().hex[:8]}.pdf"
        )

        agregar_firma_comision(
            str(pdf_anterior),
            str(firma_comision),
            str(salida),
        )

        return salida

    def guardar(self):
        if self._guardando:
            return

        try:
            semestre = int(
                self.semestre.get().strip()
            )
            semana = int(
                self.semana.get().strip()
            )

            if semestre <= 0 or semana <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Datos inválidos",
                (
                    "Semestre y semana deben ser "
                    "números mayores que cero."
                ),
                parent=self,
            )
            return

        self._guardando = True
        self._btn_guardar.configure(
            state="disabled",
            text="GUARDANDO...",
        )

        threading.Thread(
            target=self._procesar_guardado,
            args=(semestre, semana),
            daemon=True,
            name="GuardarEdicionSegura",
        ).start()

    def _procesar_guardado(
        self,
        semestre,
        semana,
    ):
        pdf_anterior_local = None
        pdf_nuevo_local = None
        nueva_pdf_url = None
        nueva_firma_url = None
        actualizacion_bd = False

        try:
            firma_nueva = None

            if not self.comision_ya_firmo:
                posible_firma = obtener_ruta_firma(
                    "comision",
                    self.codigo_sesion,
                )

                if (
                    posible_firma
                    and os.path.isfile(posible_firma)
                ):
                    firma_nueva = posible_firma

            if firma_nueva:
                # 1. Descargar el PDF anterior. Este ya contiene
                #    la firma original del docente.
                pdf_anterior_local = (
                    self._descargar_pdf_anterior()
                )

                # 2. Insertar únicamente la firma de comisión.
                pdf_nuevo_local = (
                    self._crear_pdf_con_firma_comision(
                        pdf_anterior_local,
                        firma_nueva,
                    )
                )

                # 3. Subir la firma de comisión de forma permanente.
                nueva_firma_url = subir_firma(
                    firma_nueva,
                    self.id_practica,
                    rol="comision",
                )

                # 4. Subir el PDF actualizado.
                nueva_pdf_url = subir_pdf(
                    str(pdf_nuevo_local)
                )

                # 5. Actualizar PostgreSQL en una sola transacción.
                actualizacion_bd = actualizar_con_firma_comision(
                    self.id_practica,
                    self.carrera.get().strip(),
                    semestre,
                    self.asignatura.get().strip(),
                    self.unidad.get().strip(),
                    self.tipo.get().strip(),
                    self.docente.get().strip(),
                    self.lugar.get().strip(),
                    semana,
                    self._texto(self.tema),
                    self._texto(self.resultado),
                    self.articulacion.get().strip(),
                    self._texto(self.objetivo),
                    self._texto(self.materiales),
                    self._texto(self.descripcion),
                    self.evidencias.get().strip(),
                    nueva_pdf_url,
                    nueva_firma_url,
                )

                if not actualizacion_bd:
                    raise RuntimeError(
                        obtener_ultimo_error()
                        or (
                            "PostgreSQL no confirmó la "
                            "actualización."
                        )
                    )

                # 6. Solo después de actualizar PostgreSQL se elimina
                #    el PDF remoto anterior.
                if (
                    self.pdf_url_anterior
                    and self.pdf_url_anterior
                    != nueva_pdf_url
                ):
                    if not eliminar_pdf(
                        self.pdf_url_anterior
                    ):
                        print(
                            "Advertencia: no se pudo eliminar "
                            "el PDF anterior de Supabase."
                        )

                self.pdf_url_anterior = nueva_pdf_url
                self.firma_comision_existente = (
                    nueva_firma_url
                )
                self.comision_ya_firmo = True

            else:
                # Sin firma nueva: se actualizan únicamente los datos.
                actualizacion_bd = actualizar_datos_practica(
                    self.id_practica,
                    self.codigo,
                    self.carrera.get().strip(),
                    semestre,
                    self.asignatura.get().strip(),
                    self.unidad.get().strip(),
                    self.tipo.get().strip(),
                    self.docente.get().strip(),
                    self.lugar.get().strip(),
                    semana,
                    self._texto(self.tema),
                    self._texto(self.resultado),
                    self.articulacion.get().strip(),
                    self._texto(self.objetivo),
                    self._texto(self.materiales),
                    self._texto(self.descripcion),
                    self.evidencias.get().strip(),
                )

                if not actualizacion_bd:
                    raise RuntimeError(
                        obtener_ultimo_error()
                        or (
                            "PostgreSQL no confirmó la "
                            "actualización."
                        )
                    )

            self.after(
                0,
                self._guardado_exitoso,
            )

        except Exception as error:
            # Rollback de archivos subidos cuando PostgreSQL falló.
            if nueva_pdf_url and not actualizacion_bd:
                eliminar_pdf(nueva_pdf_url)

            if nueva_firma_url and not actualizacion_bd:
                eliminar_firma(nueva_firma_url)

            detalle = (
                str(error).strip()
                or error.__class__.__name__
            )

            self.after(
                0,
                lambda mensaje=detalle: (
                    self._guardado_fallido(mensaje)
                ),
            )

        finally:
            for temporal in (
                pdf_anterior_local,
                pdf_nuevo_local,
            ):
                if temporal:
                    try:
                        Path(temporal).unlink(
                            missing_ok=True
                        )
                    except OSError:
                        pass

    def _guardado_exitoso(self):
        self._guardando = False
        self._detener_polling()

        messagebox.showinfo(
            "Cambios guardados",
            (
                "Los datos fueron actualizados correctamente.\n\n"
                "La firma de comisión fue incorporada al PDF "
                "sin modificar la firma anterior del docente."
            ),
            parent=self,
        )

        self._cerrar(
            confirmar=False,
            eliminar_temporales=False,
        )

    def _guardado_fallido(self, detalle):
        self._guardando = False

        if not self.winfo_exists():
            return

        self._btn_guardar.configure(
            state="normal",
            text="⬤  GUARDAR CAMBIOS",
        )

        messagebox.showerror(
            "Error al guardar",
            (
                "No se completó la actualización:\n\n"
                f"{detalle}"
            ),
            parent=self,
        )

    def _detener_polling(self):
        self._polling_activo = False

        if self._after_polling is not None:
            try:
                self.after_cancel(
                    self._after_polling
                )
            except Exception:
                pass

            self._after_polling = None

    def _cerrar(
        self,
        confirmar=True,
        eliminar_temporales=True,
    ):
        if self._cerrando:
            return

        if self._guardando:
            messagebox.showwarning(
                "Guardado en proceso",
                (
                    "Espere a que termine el guardado."
                ),
                parent=self,
            )
            return

        if confirmar:
            respuesta = messagebox.askyesno(
                "Cerrar edición",
                "¿Desea cerrar la ventana de edición?",
                parent=self,
            )

            if not respuesta:
                return

        self._cerrando = True
        self._detener_polling()

        if eliminar_temporales:
            try:
                eliminar_firmas_sesion(
                    self.codigo_sesion
                )
            except Exception:
                pass

        self.destroy()