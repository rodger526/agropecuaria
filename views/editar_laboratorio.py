import os
from datetime import datetime
from tkinter import messagebox
from urllib.parse import quote

import qrcode
from customtkinter import CTkImage

from database.laboratorio.editar_laboratorio import (
    actualizar_laboratorio,
)
from firma.servidor_firma import (
    eliminar_firmas_sesion,
    obtener_ruta_firma,
)
from models.laboratorio import Laboratorio
from pdf.generador_pdf_laboratorio import (
    generar_pdf_laboratorio,
)
from storage.subir_pdf_laboratorio import (
    subir_pdf_laboratorio,
)
from utils.rutas_app import ruta_datos
from views.nueva_laboratorio import (
    ACCENT,
    BG_CARD,
    BG_CARD_HOV,
    BG_DARK,
    TEXT_PRI,
    TEXT_SEC,
    PUERTO_FIRMAS,
    VentanaNuevoLaboratorio,
)


class VentanaEditarLaboratorio(
    VentanaNuevoLaboratorio
):
    """
    Ventana para editar un registro de laboratorio existente.

    Comportamiento de firmas durante la edición:

        - Las firmas de estudiantes se conservan sin cambios.
        - La firma del docente se conserva sin cambios.
        - Solamente el encargado del laboratorio puede firmar.
        - La nueva firma del encargado reemplaza su firma anterior.
        - Las firmas se almacenan permanentemente antes de generar
          el nuevo PDF.
    """

    def __init__(
        self,
        master,
        laboratorio,
    ):
        if laboratorio is None:
            raise ValueError(
                "No se recibió un laboratorio válido."
            )

        if not getattr(
            laboratorio,
            "id",
            None,
        ):
            raise ValueError(
                "El laboratorio no tiene un ID válido."
            )

        self.registro_original = laboratorio

        # Guardar las rutas originales antes de construir
        # la ventana de edición.
        self._firma_docente_original = self._ruta_existente(
            getattr(
                laboratorio,
                "firma_docente_ruta",
                None,
            )
        )

        self._firma_encargado_original = self._ruta_existente(
            getattr(
                laboratorio,
                "firma_encargado_ruta",
                None,
            )
        )

        # Crear toda la interfaz reutilizando la ventana nueva.
        super().__init__(
            master
        )

        self.title(
            "Editar registro de laboratorio"
        )

        # La sesión creada por la clase padre será utilizada únicamente
        # para recibir la nueva firma del encargado.
        self._sesion_edicion = self._codigo_sesion

        # Eliminar cualquier firma temporal previa asociada a esta
        # nueva sesión de edición.
        try:
            eliminar_firmas_sesion(
                self._codigo_sesion,
                incluir_estudiantes=True,
            )
        except Exception:
            pass

        # Cargar los datos almacenados.
        self._cargar_registro(
            laboratorio
        )

        # Configurar el formulario para modo edición.
        self._configurar_modo_edicion()

        # Mostrar las firmas existentes.
        self.after(
            300,
            self._mostrar_firmas_existentes,
        )

    # ================================================================
    # Utilidades de rutas
    # ================================================================

    @staticmethod
    def _ruta_existente(
        ruta,
    ):
        """
        Devuelve la ruta absoluta si el archivo existe.

        Si la ruta no existe o está vacía, devuelve None.
        """

        if not ruta:
            return None

        ruta = os.path.abspath(
            str(
                ruta
            ).strip()
        )

        if not os.path.isfile(
            ruta
        ):
            return None

        return ruta

    # ================================================================
    # Configuración de la interfaz de edición
    # ================================================================

    def _configurar_modo_edicion(self):
        """
        Ajusta la interfaz para que en la edición:

            - no se puedan solicitar nuevas firmas de estudiantes;
            - no se pueda volver a firmar como docente;
            - solo se genere el QR del encargado;
            - los estudiantes cargados permanezcan sin cambios.
        """

        # Botón principal.
        if hasattr(
            self,
            "_btn_guardar",
        ):
            self._btn_guardar.configure(
                text="⬤  ACTUALIZAR REGISTRO"
            )

        # No permitir nuevas firmas de estudiantes.
        if hasattr(
            self,
            "_btn_qr_est",
        ):
            self._btn_qr_est.configure(
                state="disabled",
                text=(
                    "✔  FIRMAS DE ESTUDIANTES CONSERVADAS"
                ),
                fg_color=BG_CARD,
                hover_color=BG_CARD,
                text_color=TEXT_SEC,
                border_color=BG_CARD_HOV,
            )

        # Detener cualquier polling de estudiantes.
        self._polling_estudiantes_activo = False

        if self._after_estudiantes:
            try:
                self.after_cancel(
                    self._after_estudiantes
                )
            except Exception:
                pass

            self._after_estudiantes = None

        # La lista manual tampoco debe modificarse durante la edición,
        # porque los estudiantes anteriores deben conservarse.
        if hasattr(
            self,
            "estudiantes",
        ):
            self.estudiantes.delete(
                "1.0",
                "end",
            )

            self.estudiantes.insert(
                "1.0",
                (
                    "Las firmas y los datos de estudiantes se "
                    "conservan automáticamente durante la edición."
                ),
            )

            self.estudiantes.configure(
                state="disabled"
            )

        # Cambiar el botón de responsables para indicar que solamente
        # firmará el encargado.
        if hasattr(
            self,
            "_btn_qr_responsables",
        ):
            self._btn_qr_responsables.configure(
                text="⬤  GENERAR QR DEL ENCARGADO",
                command=self._iniciar_firmas_responsables,
            )

        # El docente no genera un QR nuevo.
        if hasattr(
            self,
            "_lbl_qr_docente_lab",
        ):
            self._lbl_qr_docente_lab.configure(
                text=(
                    "La firma del docente se conserva\n"
                    "sin modificaciones."
                ),
                image=None,
            )

        if hasattr(
            self,
            "_lbl_estado_docente_lab",
        ):
            self._lbl_estado_docente_lab.configure(
                text=(
                    "✔  Firma protegida"
                    if self._firma_docente_original
                    else "Sin firma registrada"
                ),
                text_color=(
                    ACCENT
                    if self._firma_docente_original
                    else TEXT_SEC
                ),
            )

        # El encargado debe firmar nuevamente para autorizar
        # la actualización.
        if hasattr(
            self,
            "_lbl_estado_encargado_lab",
        ):
            self._lbl_estado_encargado_lab.configure(
                text="⏳  Nueva firma requerida",
                text_color=TEXT_SEC,
            )

        if hasattr(
            self,
            "_lbl_qr_encargado_lab",
        ):
            self._lbl_qr_encargado_lab.configure(
                text="Presiona «Generar QR del encargado»",
                image=None,
            )

    # ================================================================
    # Carga del registro
    # ================================================================

    def _cargar_registro(
        self,
        laboratorio,
    ):
        """
        Coloca en el formulario todos los datos del registro recibido.
        """

        # ============================================================
        # Datos generales
        # ============================================================

        self._set_combo(
            self.laboratorio,
            getattr(
                laboratorio,
                "laboratorio",
                "",
            ),
        )

        self._actualizar_datos_laboratorio(
            getattr(
                laboratorio,
                "laboratorio",
                "",
            )
        )

        # Conservar el encargado almacenado en el registro.
        encargado_guardado = str(
            getattr(
                laboratorio,
                "encargado_laboratorio",
                "",
            )
            or ""
        ).strip()

        cargo_guardado = str(
            getattr(
                laboratorio,
                "cargo_encargado",
                "",
            )
            or ""
        ).strip()

        if encargado_guardado:
            self._encargado_actual = encargado_guardado

            self._lbl_encargado.configure(
                text=encargado_guardado
            )

            self._lbl_nombre_encargado_firma.configure(
                text=encargado_guardado
            )

        if cargo_guardado:
            self._cargo_encargado_actual = cargo_guardado

            self._lbl_cargo_encargado.configure(
                text=cargo_guardado
            )

            self._lbl_cargo_encargado_firma.configure(
                text=cargo_guardado
            )

        self._set_entry(
            self.numero_estudiantes,
            getattr(
                laboratorio,
                "numero_estudiantes",
                "",
            ),
        )

        self._set_entry(
            self.asignatura,
            getattr(
                laboratorio,
                "asignatura",
                "",
            ),
        )

        self._set_combo(
            self.unidad_academica,
            getattr(
                laboratorio,
                "unidad_academica",
                "",
            ),
        )

        self._set_entry(
            self.semestre,
            getattr(
                laboratorio,
                "semestre",
                "",
            ),
        )

        self._set_combo(
            self.carrera,
            getattr(
                laboratorio,
                "carrera",
                "",
            ),
        )

        self._set_entry(
            self.hora_entrada,
            getattr(
                laboratorio,
                "hora_entrada",
                "",
            ),
        )

        self._set_entry(
            self.hora_salida,
            getattr(
                laboratorio,
                "hora_salida",
                "",
            ),
        )

        self._set_entry(
            self.institucion,
            getattr(
                laboratorio,
                "institucion",
                "",
            ),
        )

        self._set_combo(
            self.ciudad,
            getattr(
                laboratorio,
                "ciudad",
                "",
            ),
        )

        self._set_entry(
            self.docente,
            getattr(
                laboratorio,
                "docente_responsable",
                "",
            ),
        )

        self._actualizar_nombre_docente_firma()

        # ============================================================
        # Datos académicos
        # ============================================================

        self._set_textbox(
            self.tema,
            getattr(
                laboratorio,
                "tema_practica",
                "",
            ),
        )

        self._set_textbox(
            self.subtema,
            getattr(
                laboratorio,
                "subtema",
                "",
            ),
        )

        self._set_textbox(
            self.logro,
            getattr(
                laboratorio,
                "logro_aprendizaje",
                "",
            ),
        )

        # ============================================================
        # Planificación
        # ============================================================

        self._set_textbox(
            self.objetivos,
            getattr(
                laboratorio,
                "objetivos",
                "",
            ),
        )

        self._set_textbox(
            self.metodologia,
            getattr(
                laboratorio,
                "metodologia",
                "",
            ),
        )

        self._set_textbox(
            self.resultados,
            getattr(
                laboratorio,
                "resultados",
                "",
            ),
        )

        self._set_textbox(
            self.conclusiones,
            getattr(
                laboratorio,
                "conclusiones",
                "",
            ),
        )

        self._set_textbox(
            self.observaciones,
            getattr(
                laboratorio,
                "observaciones",
                "",
            ),
        )

        # ============================================================
        # Materiales
        # ============================================================

        materiales_originales = (
            getattr(
                laboratorio,
                "materiales",
                None,
            )
            or []
        )

        self.widget_materiales._items = [
            {
                "nombre": material.get(
                    "nombre"
                ),
                "cantidad": material.get(
                    "cantidad"
                ),
            }
            for material in materiales_originales
            if isinstance(
                material,
                dict,
            )
        ]

        self.widget_materiales._refrescar()

        # ============================================================
        # Reactivos
        # ============================================================

        reactivos_originales = (
            getattr(
                laboratorio,
                "reactivos",
                None,
            )
            or []
        )

        self.widget_reactivos._items = [
            {
                "nombre": reactivo.get(
                    "nombre"
                ),
                "cantidad": reactivo.get(
                    "cantidad"
                ),
            }
            for reactivo in reactivos_originales
            if isinstance(
                reactivo,
                dict,
            )
        ]

        self.widget_reactivos._refrescar()

        # ============================================================
        # Estudiantes
        # ============================================================

        estudiantes_originales = (
            getattr(
                laboratorio,
                "estudiantes",
                None,
            )
            or []
        )

        self._estudiantes_firmados = [
            {
                "nombre": estudiante.get(
                    "nombre"
                ),
                "cedula": estudiante.get(
                    "cedula"
                ),
                "firma_ruta": estudiante.get(
                    "firma_ruta"
                ),
                "hora": estudiante.get(
                    "hora"
                ),
                "fecha": estudiante.get(
                    "fecha"
                ),
            }
            for estudiante in estudiantes_originales
            if isinstance(
                estudiante,
                dict,
            )
        ]

        self._mostrar_estudiantes_cargados()

    # ================================================================
    # Asignación de valores a widgets
    # ================================================================

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
                if valor is not None
                else ""
            ),
        )

    @staticmethod
    def _set_combo(
        widget,
        valor,
    ):
        widget.set(
            str(
                valor
                if valor is not None
                else ""
            )
        )

    @staticmethod
    def _set_textbox(
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
                if valor is not None
                else ""
            ),
        )

    # ================================================================
    # Mostrar estudiantes almacenados
    # ================================================================

    def _mostrar_estudiantes_cargados(self):
        """
        Muestra los estudiantes recuperados del registro.

        No permite agregar ni modificar estudiantes durante la edición.
        """

        total = len(
            self._estudiantes_firmados
        )

        limite = self._limite_estudiantes()

        if limite:
            self._lbl_contador.configure(
                text=(
                    f"{total} / {limite} "
                    "estudiantes conservados"
                )
            )

            self._barra_progreso.set(
                min(
                    total / limite,
                    1.0,
                )
            )

        else:
            self._lbl_contador.configure(
                text=(
                    f"{total} estudiantes conservados"
                )
            )

            self._barra_progreso.set(
                0
            )

        self._lista_estudiantes.configure(
            state="normal"
        )

        self._lista_estudiantes.delete(
            "1.0",
            "end",
        )

        if total == 0:
            self._lista_estudiantes.insert(
                "1.0",
                "No hay estudiantes registrados.",
            )

        else:
            lineas = []

            for indice, estudiante in enumerate(
                self._estudiantes_firmados,
                start=1,
            ):
                nombre = (
                    estudiante.get(
                        "nombre"
                    )
                    or "Sin nombre"
                )

                cedula = (
                    estudiante.get(
                        "cedula"
                    )
                    or "Sin cédula"
                )

                hora = estudiante.get(
                    "hora"
                )

                firma_ruta = estudiante.get(
                    "firma_ruta"
                )

                tiene_firma = bool(
                    firma_ruta
                    and os.path.isfile(
                        str(
                            firma_ruta
                        )
                    )
                )

                estado_firma = (
                    "✔ Firma"
                    if tiene_firma
                    else "Sin firma"
                )

                texto = (
                    f"{indice}. {nombre}"
                    f" — {cedula}"
                    f" — {estado_firma}"
                )

                if hora:
                    texto += (
                        f" — {hora}"
                    )

                lineas.append(
                    texto
                )

            self._lista_estudiantes.insert(
                "1.0",
                "\n".join(
                    lineas
                ),
            )

        self._lista_estudiantes.configure(
            state="disabled"
        )

    # ================================================================
    # Mostrar firmas existentes
    # ================================================================

    def _mostrar_firmas_existentes(self):
        """
        Muestra la firma original del docente y la firma anterior
        del encargado.

        La firma del docente permanece protegida.
        La firma anterior del encargado se muestra solamente como
        referencia hasta que firme nuevamente.
        """

        if not self.winfo_exists():
            return

        # Firma original del docente.
        if (
            self._firma_docente_original
            and os.path.isfile(
                self._firma_docente_original
            )
        ):
            self._lbl_estado_docente_lab.configure(
                text="✔  Firma protegida",
                text_color=ACCENT,
            )

            self._mostrar_preview_firma(
                self._firma_docente_original,
                self._lbl_preview_docente_lab,
                "preview_docente_edicion",
            )

        else:
            self._lbl_estado_docente_lab.configure(
                text="Sin firma registrada",
                text_color=TEXT_SEC,
            )

        # Firma anterior del encargado.
        if (
            self._firma_encargado_original
            and os.path.isfile(
                self._firma_encargado_original
            )
        ):
            self._mostrar_preview_firma(
                self._firma_encargado_original,
                self._lbl_preview_encargado_lab,
                "preview_encargado_anterior",
            )

            self._lbl_estado_encargado_lab.configure(
                text="⏳  Debe firmar nuevamente",
                text_color=TEXT_SEC,
            )

    # ================================================================
    # QR del encargado
    # ================================================================

    def _iniciar_firmas_responsables(self):
        """
        En modo edición solo se permite generar el QR del encargado.
        """

        if self._cerrando:
            return

        if not self._encargado_actual:
            messagebox.showwarning(
                "Encargado pendiente",
                (
                    "El laboratorio seleccionado no tiene un "
                    "encargado configurado."
                ),
                parent=self,
            )
            return

        if not self._cargo_encargado_actual:
            messagebox.showwarning(
                "Cargo pendiente",
                (
                    "El encargado seleccionado no tiene un "
                    "cargo configurado."
                ),
                parent=self,
            )
            return

        try:
            self._asegurar_servidor()

            self._btn_qr_responsables.configure(
                state="disabled",
                text="GENERANDO QR DEL ENCARGADO...",
            )

            self.after(
                700,
                self._activar_qr_encargado,
            )

        except Exception as error:
            self._btn_qr_responsables.configure(
                state="normal",
                text="⬤  GENERAR QR DEL ENCARGADO",
            )

            messagebox.showerror(
                "Servidor de firmas",
                (
                    "No se pudo iniciar el servidor de firmas.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    def _activar_qr_encargado(self):
        if (
            self._cerrando
            or not self.winfo_exists()
        ):
            return

        try:
            self._generar_qr_encargado()

            if not self._polling_responsables_activo:
                self._polling_responsables_activo = True
                self._polling_firmas_responsables()

            self._btn_qr_responsables.configure(
                state="normal",
                text="↺  REGENERAR QR DEL ENCARGADO",
            )

        except Exception as error:
            self._btn_qr_responsables.configure(
                state="normal",
                text="⬤  GENERAR QR DEL ENCARGADO",
            )

            messagebox.showerror(
                "Código QR",
                (
                    "No se pudo generar el QR del encargado.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    def _generar_qr_encargado(self):
        """
        Genera únicamente el QR para la firma del encargado.
        """

        ip = self._obtener_ip_red()

        sesion = quote(
            self._codigo_sesion,
            safe="",
        )

        url = (
            f"http://{ip}:{PUERTO_FIRMAS}"
            f"/firma/encargado_laboratorio"
            f"?sesion={sesion}"
        )

        imagen_qr = qrcode.make(
            url
        ).resize(
            (
                170,
                170,
            )
        ).convert(
            "RGB"
        )

        photo = CTkImage(
            light_image=imagen_qr,
            dark_image=imagen_qr,
            size=(
                170,
                170,
            ),
        )

        self._img_refs[
            "qr_encargado_edicion"
        ] = photo

        self._lbl_qr_encargado_lab.configure(
            image=photo,
            text="",
        )

    def _generar_qrs_responsables(self):
        """
        Sobrescribe el método de la ventana nueva.

        En edición no se genera QR para el docente.
        """

        self._generar_qr_encargado()

    def _polling_firmas_responsables(self):
        """
        Comprueba únicamente la nueva firma del encargado.
        """

        if (
            self._cerrando
            or not self._polling_responsables_activo
            or not self.winfo_exists()
        ):
            return

        ruta_encargado = obtener_ruta_firma(
            "encargado_laboratorio",
            self._codigo_sesion,
        )

        if (
            ruta_encargado
            and os.path.isfile(
                ruta_encargado
            )
        ):
            self._lbl_estado_encargado_lab.configure(
                text="✔  Nueva firma recibida",
                text_color=ACCENT,
            )

            self._mostrar_preview_firma(
                ruta_encargado,
                self._lbl_preview_encargado_lab,
                "preview_encargado_nuevo",
            )

        else:
            self._lbl_estado_encargado_lab.configure(
                text="⏳  Nueva firma requerida",
                text_color=TEXT_SEC,
            )

        self._after_responsables = self.after(
            800,
            self._polling_firmas_responsables,
        )

    # ================================================================
    # Persistencia de la firma del encargado
    # ================================================================

    def _persistir_nueva_firma_encargado(
        self,
    ):
        """
        Copia la firma temporal del encargado a la carpeta permanente
        del registro.

        La firma del docente y las firmas de los estudiantes no se
        modifican.
        """

        ruta_temporal = obtener_ruta_firma(
            "encargado_laboratorio",
            self._codigo_sesion,
        )

        if not (
            ruta_temporal
            and os.path.isfile(
                ruta_temporal
            )
        ):
            raise ValueError(
                "El encargado del laboratorio debe firmar "
                "antes de actualizar el registro."
            )

        codigo = str(
            getattr(
                self.registro_original,
                "codigo",
                "",
            )
            or ""
        ).strip()

        if not codigo:
            raise ValueError(
                "El registro no tiene un código válido."
            )

        carpeta_registro = str(
            ruta_datos(
                "datos",
                "firmas_laboratorios",
                codigo,
            )
        )

        ruta_permanente = (
            self._copiar_firma_persistente(
                ruta_temporal,
                carpeta_registro,
                "firma_encargado.png",
            )
        )

        if not ruta_permanente:
            raise RuntimeError(
                "No fue posible guardar permanentemente "
                "la firma del encargado."
            )

        return ruta_permanente

    # ================================================================
    # Construcción del objeto actualizado
    # ================================================================

    def _crear_objeto_actualizado(
        self,
        numero_estudiantes,
        semestre,
        hora_entrada,
        hora_salida,
        firma_encargado,
    ):
        """
        Construye el objeto Laboratorio que se enviará al generador
        de PDF y a PostgreSQL.
        """

        # Copiar la lista para no alterar el objeto original.
        estudiantes = [
            {
                "nombre": estudiante.get(
                    "nombre"
                ),
                "cedula": estudiante.get(
                    "cedula"
                ),
                "firma_ruta": estudiante.get(
                    "firma_ruta"
                ),
                "hora": estudiante.get(
                    "hora"
                ),
                "fecha": estudiante.get(
                    "fecha"
                ),
            }
            for estudiante in self._estudiantes_firmados
        ]

        fecha_practica = (
            getattr(
                self.registro_original,
                "fecha_practica",
                None,
            )
            or datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        codigo_sesion_original = getattr(
            self.registro_original,
            "codigo_sesion",
            None,
        )

        return Laboratorio(
            id=self.registro_original.id,
            codigo=self.registro_original.codigo,
            laboratorio=self.laboratorio.get().strip(),
            numero_estudiantes=numero_estudiantes,
            asignatura=self.asignatura.get().strip(),
            unidad_academica=(
                self.unidad_academica.get().strip()
            ),
            semestre=semestre,
            carrera=self.carrera.get().strip(),
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            institucion=self.institucion.get().strip(),
            ciudad=self.ciudad.get().strip(),
            docente_responsable=(
                self.docente.get().strip()
            ),
            fecha_practica=fecha_practica,
            tema_practica=self._texto_textbox(
                self.tema
            ),
            subtema=self._texto_textbox(
                self.subtema
            ),
            logro_aprendizaje=self._texto_textbox(
                self.logro
            ),
            objetivos=self._texto_textbox(
                self.objetivos
            ),
            metodologia=self._texto_textbox(
                self.metodologia
            ),
            resultados=self._texto_textbox(
                self.resultados
            ),
            conclusiones=self._texto_textbox(
                self.conclusiones
            ),
            observaciones=self._texto_textbox(
                self.observaciones
            ),
            materiales=(
                self.widget_materiales.obtener_items()
            ),
            reactivos=(
                self.widget_reactivos.obtener_items()
            ),
            estudiantes=estudiantes,
            encargado_laboratorio=(
                self._encargado_actual
            ),
            cargo_encargado=(
                self._cargo_encargado_actual
            ),
            firma_docente_ruta=(
                self._firma_docente_original
            ),
            firma_encargado_ruta=firma_encargado,
            pdf_url=getattr(
                self.registro_original,
                "pdf_url",
                None,
            ),
            codigo_sesion=(
                codigo_sesion_original
                or self._codigo_sesion
            ),
        )

    # ================================================================
    # Guardar actualización
    # ================================================================

    def guardar(self):
        """
        Valida los datos, exige la firma del encargado, genera el nuevo
        PDF, lo sube a Supabase y actualiza PostgreSQL.
        """

        if self._guardando:
            return

        try:
            (
                numero_estudiantes,
                semestre,
                hora_entrada,
                hora_salida,
            ) = self._validar_formulario()

            # Verificar obligatoriamente la nueva firma.
            ruta_firma_temporal = obtener_ruta_firma(
                "encargado_laboratorio",
                self._codigo_sesion,
            )

            if not (
                ruta_firma_temporal
                and os.path.isfile(
                    ruta_firma_temporal
                )
            ):
                messagebox.showwarning(
                    "Firma requerida",
                    (
                        "El encargado del laboratorio debe firmar "
                        "para autorizar la actualización.\n\n"
                        "Presione «Generar QR del encargado» y "
                        "realice la firma desde el teléfono."
                    ),
                    parent=self,
                )
                return

            self._guardando = True

            self._btn_guardar.configure(
                state="disabled",
                text="ACTUALIZANDO REGISTRO...",
            )

            self.update_idletasks()

            # Guardar permanentemente la nueva firma del encargado.
            firma_encargado = (
                self._persistir_nueva_firma_encargado()
            )

            # Crear el objeto actualizado.
            laboratorio_actualizado = (
                self._crear_objeto_actualizado(
                    numero_estudiantes,
                    semestre,
                    hora_entrada,
                    hora_salida,
                    firma_encargado,
                )
            )

            # Generar el nuevo PDF.
            ruta_pdf = generar_pdf_laboratorio(
                laboratorio_actualizado
            )

            if not ruta_pdf:
                raise RuntimeError(
                    "El generador no devolvió la ruta del PDF."
                )

            if not os.path.isfile(
                ruta_pdf
            ):
                raise FileNotFoundError(
                    "El PDF actualizado no fue creado correctamente."
                )

            # Subir el PDF a Supabase.
            nueva_url_pdf = subir_pdf_laboratorio(
                ruta_pdf
            )

            if not nueva_url_pdf:
                raise RuntimeError(
                    "Supabase no devolvió la URL del PDF actualizado."
                )

            laboratorio_actualizado.pdf_url = (
                nueva_url_pdf
            )

            # Actualizar PostgreSQL.
            resultado = actualizar_laboratorio(
                laboratorio_actualizado
            )

            if not resultado:
                raise RuntimeError(
                    "No fue posible actualizar el registro "
                    "en PostgreSQL."
                )

            # Limpiar solamente la sesión temporal de edición.
            try:
                eliminar_firmas_sesion(
                    self._codigo_sesion,
                    incluir_estudiantes=True,
                )
            except Exception:
                pass

            messagebox.showinfo(
                "Registro actualizado",
                (
                    "El laboratorio fue actualizado correctamente.\n\n"
                    "• Se conservaron las firmas de estudiantes.\n"
                    "• Se conservó la firma del docente.\n"
                    "• Se registró la nueva firma del encargado.\n"
                    "• Se generó y subió el nuevo PDF."
                ),
                parent=self,
            )

            self._cerrando = True

            try:
                self.destroy()
            except Exception:
                pass

        except ValueError as error:
            messagebox.showerror(
                "Datos inválidos",
                str(
                    error
                ),
                parent=self,
            )

            self._restaurar_boton_guardar()

        except Exception as error:
            print(
                "\n"
                "========== ERROR EDITANDO LABORATORIO =========="
            )
            print(
                error
            )
            print(
                "================================================"
                "\n"
            )

            messagebox.showerror(
                "Error",
                (
                    "No fue posible actualizar el laboratorio.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

            self._restaurar_boton_guardar()

    def _restaurar_boton_guardar(self):
        """
        Reactiva el botón después de un error durante la actualización.
        """

        self._guardando = False

        try:
            if (
                self.winfo_exists()
                and hasattr(
                    self,
                    "_btn_guardar",
                )
            ):
                self._btn_guardar.configure(
                    state="normal",
                    text="⬤  ACTUALIZAR REGISTRO",
                )
        except Exception:
            pass

    # ================================================================
    # Cierre de ventana
    # ================================================================

    def _cerrar_ventana(self):
        """
        Cierra la ventana y elimina únicamente las firmas temporales
        creadas durante esta edición.

        No elimina firmas permanentes del docente, estudiantes
        ni encargado.
        """

        if self._cerrando:
            return

        self._cerrando = True
        self._polling_estudiantes_activo = False
        self._polling_responsables_activo = False

        if self._after_estudiantes:
            try:
                self.after_cancel(
                    self._after_estudiantes
                )
            except Exception:
                pass

            self._after_estudiantes = None

        if self._after_responsables:
            try:
                self.after_cancel(
                    self._after_responsables
                )
            except Exception:
                pass

            self._after_responsables = None

        try:
            eliminar_firmas_sesion(
                self._codigo_sesion,
                incluir_estudiantes=True,
            )
        except Exception:
            pass

        try:
            self.destroy()
        except Exception:
            pass