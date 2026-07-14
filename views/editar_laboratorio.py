import os
from datetime import datetime
from tkinter import messagebox

from database.laboratorio.editar_laboratorio import (
    actualizar_laboratorio,
)
from models.laboratorio import Laboratorio
from pdf.generador_pdf_laboratorio import (
    generar_pdf_laboratorio,
)
from storage.subir_pdf_laboratorio import (
    subir_pdf_laboratorio,
)
from views.nueva_laboratorio import (
    RUTA_FIRMA_DOCENTE_LAB,
    RUTA_FIRMA_ENCARGADO_LAB,
    VentanaNuevoLaboratorio,
    _normalizar_hora,
)


class VentanaEditarLaboratorio(
    VentanaNuevoLaboratorio
):
    """
    Ventana para editar un registro de laboratorio existente.

    Reutiliza el formulario de VentanaNuevoLaboratorio y carga:

        - datos informativos;
        - datos académicos;
        - planificación;
        - materiales;
        - reactivos;
        - estudiantes;
        - responsable del laboratorio;
        - firma del docente;
        - firma del encargado;
        - URL anterior del PDF.
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

        # ============================================================
        # Guardar temporalmente las firmas existentes
        # ============================================================

        firma_docente_bytes = self._leer_firma_existente(
            getattr(
                laboratorio,
                "firma_docente_ruta",
                None,
            )
        )

        firma_encargado_bytes = self._leer_firma_existente(
            getattr(
                laboratorio,
                "firma_encargado_ruta",
                None,
            )
        )

        # El constructor padre crea toda la interfaz.
        super().__init__(
            master
        )

        self.title(
            "Editar registro de laboratorio"
        )

        # Restaurar código de sesión existente.
        self._codigo_sesion = (
            getattr(
                laboratorio,
                "codigo_sesion",
                None,
            )
            or self._codigo_sesion
        )

        # Restaurar las firmas que el constructor padre limpia.
        self._restaurar_firma(
            RUTA_FIRMA_DOCENTE_LAB,
            firma_docente_bytes,
        )

        self._restaurar_firma(
            RUTA_FIRMA_ENCARGADO_LAB,
            firma_encargado_bytes,
        )

        # Cargar todos los datos.
        self._cargar_registro(
            laboratorio
        )

        # Cambiar el texto del botón principal.
        self._cambiar_texto_boton_guardar()

        # Mostrar firmas existentes.
        self.after(
            300,
            self._mostrar_firmas_existentes,
        )

    # ================================================================
    # Firmas existentes
    # ================================================================

    @staticmethod
    def _leer_firma_existente(
        ruta,
    ):
        """
        Lee una firma antes de que el constructor padre elimine
        los archivos temporales compartidos.

        Devuelve bytes o None.
        """

        if not ruta:
            return None

        ruta = str(
            ruta
        ).strip()

        if not os.path.isfile(
            ruta
        ):
            return None

        try:
            with open(
                ruta,
                "rb",
            ) as archivo:
                return archivo.read()

        except Exception as error:
            print(
                "No se pudo leer una firma existente:",
                error,
            )
            return None

    @staticmethod
    def _restaurar_firma(
        ruta,
        contenido,
    ):
        """
        Vuelve a escribir una firma conservada en memoria.
        """

        if not contenido:
            return

        try:
            carpeta = os.path.dirname(
                ruta
            )

            if carpeta:
                os.makedirs(
                    carpeta,
                    exist_ok=True,
                )

            with open(
                ruta,
                "wb",
            ) as archivo:
                archivo.write(
                    contenido
                )

        except Exception as error:
            print(
                "No se pudo restaurar una firma:",
                error,
            )

    def _mostrar_firmas_existentes(self):
        """
        Inicia el indicador visual de firmas sin necesidad
        de generar inmediatamente los códigos QR.
        """

        if not self.winfo_exists():
            return

        if os.path.isfile(
            RUTA_FIRMA_DOCENTE_LAB
        ):
            self._lbl_estado_docente_lab.configure(
                text="✔  Firma existente",
                text_color="#4CAF7D",
            )

            self._mostrar_preview_firma(
                RUTA_FIRMA_DOCENTE_LAB,
                self._lbl_preview_docente_lab,
                "preview_docente_laboratorio",
            )

        if os.path.isfile(
            RUTA_FIRMA_ENCARGADO_LAB
        ):
            self._lbl_estado_encargado_lab.configure(
                text="✔  Firma existente",
                text_color="#4CAF7D",
            )

            self._mostrar_preview_firma(
                RUTA_FIRMA_ENCARGADO_LAB,
                self._lbl_preview_encargado_lab,
                "preview_encargado_laboratorio",
            )

    # ================================================================
    # Carga del registro
    # ================================================================

    def _cargar_registro(
        self,
        laboratorio,
    ):
        """
        Coloca en el formulario todos los datos del objeto recibido.
        """

        # Datos generales
        self._set_combo(
            self.laboratorio,
            laboratorio.laboratorio,
        )

        self._actualizar_datos_laboratorio(
            laboratorio.laboratorio
        )

        # Conservar el responsable almacenado en el registro, incluso
        # si posteriormente cambió en laboratorios_tipo.
        if getattr(
            laboratorio,
            "encargado_laboratorio",
            None,
        ):
            self._encargado_actual = str(
                laboratorio.encargado_laboratorio
            ).strip()

            self._lbl_encargado.configure(
                text=self._encargado_actual
            )

            self._lbl_nombre_encargado_firma.configure(
                text=self._encargado_actual
            )

        if getattr(
            laboratorio,
            "cargo_encargado",
            None,
        ):
            self._cargo_encargado_actual = str(
                laboratorio.cargo_encargado
            ).strip()

            self._lbl_cargo_encargado.configure(
                text=self._cargo_encargado_actual
            )

            self._lbl_cargo_encargado_firma.configure(
                text=self._cargo_encargado_actual
            )

        self._set_entry(
            self.numero_estudiantes,
            laboratorio.numero_estudiantes,
        )

        self._set_entry(
            self.asignatura,
            laboratorio.asignatura,
        )

        self._set_entry(
            self.unidad_academica,
            laboratorio.unidad_academica,
        )

        self._set_entry(
            self.semestre,
            laboratorio.semestre,
        )

        self._set_entry(
            self.carrera,
            laboratorio.carrera,
        )

        self._set_entry(
            self.hora_entrada,
            laboratorio.hora_entrada,
        )

        self._set_entry(
            self.hora_salida,
            laboratorio.hora_salida,
        )

        self._set_entry(
            self.institucion,
            laboratorio.institucion,
        )

        self._set_entry(
            self.ciudad,
            laboratorio.ciudad,
        )

        self._set_entry(
            self.docente,
            laboratorio.docente_responsable,
        )

        self._actualizar_nombre_docente_firma()

        # Datos académicos
        self._set_textbox(
            self.tema,
            laboratorio.tema_practica,
        )

        self._set_textbox(
            self.subtema,
            laboratorio.subtema,
        )

        self._set_textbox(
            self.logro,
            laboratorio.logro_aprendizaje,
        )

        # Planificación
        self._set_textbox(
            self.objetivos,
            laboratorio.objetivos,
        )

        self._set_textbox(
            self.metodologia,
            laboratorio.metodologia,
        )

        self._set_textbox(
            self.resultados,
            laboratorio.resultados,
        )

        self._set_textbox(
            self.conclusiones,
            laboratorio.conclusiones,
        )

        self._set_textbox(
            self.observaciones,
            laboratorio.observaciones,
        )

        # Materiales
        self.widget_materiales._items = [
            {
                "nombre": material.get(
                    "nombre"
                ),
                "cantidad": material.get(
                    "cantidad"
                ),
            }
            for material in (
                laboratorio.materiales
                or []
            )
            if isinstance(
                material,
                dict,
            )
        ]

        self.widget_materiales._refrescar()

        # Reactivos
        self.widget_reactivos._items = [
            {
                "nombre": reactivo.get(
                    "nombre"
                ),
                "cantidad": reactivo.get(
                    "cantidad"
                ),
            }
            for reactivo in (
                laboratorio.reactivos
                or []
            )
            if isinstance(
                reactivo,
                dict,
            )
        ]

        self.widget_reactivos._refrescar()

        # Estudiantes guardados anteriormente
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
            }
            for estudiante in (
                laboratorio.estudiantes
                or []
            )
            if isinstance(
                estudiante,
                dict,
            )
        ]

        self._mostrar_estudiantes_cargados()

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

    def _mostrar_estudiantes_cargados(self):
        """
        Muestra los estudiantes recuperados de PostgreSQL.
        """

        total = len(
            self._estudiantes_firmados
        )

        limite = self._limite_estudiantes()

        if limite:
            self._lbl_contador.configure(
                text=(
                    f"{total} / {limite} "
                    "estudiantes registrados"
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
                    f"{total} estudiantes registrados"
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
            texto = "\n".join(
                (
                    f"{indice + 1}. "
                    f"{estudiante.get('nombre') or '—'}"
                    f" — {estudiante.get('cedula') or 'Sin cédula'}"
                )
                for indice, estudiante in enumerate(
                    self._estudiantes_firmados
                )
            )

            self._lista_estudiantes.insert(
                "1.0",
                texto,
            )

        self._lista_estudiantes.configure(
            state="disabled"
        )

    def _cambiar_texto_boton_guardar(self):
        """
        Busca el botón principal creado por la clase padre y cambia
        su texto para indicar que se está editando.
        """

        try:
            for widget in self.scroll.winfo_children():
                if not hasattr(
                    widget,
                    "cget",
                ):
                    continue

                try:
                    texto = widget.cget(
                        "text"
                    )
                except Exception:
                    continue

                if texto == "⬤  GUARDAR REGISTRO":
                    widget.configure(
                        text="⬤  ACTUALIZAR REGISTRO"
                    )
                    break

        except Exception:
            pass

    # ================================================================
    # Guardar actualización
    # ================================================================

    def guardar(self):
        """
        Regenera el PDF, lo sube a Supabase y actualiza PostgreSQL.
        """

        try:
            # ========================================================
            # Validaciones numéricas y horarias
            # ========================================================

            try:
                numero_estudiantes = int(
                    self.numero_estudiantes.get().strip()
                )

                semestre = int(
                    self.semestre.get().strip()
                )

                hora_entrada_normalizada = _normalizar_hora(
                    self.hora_entrada.get()
                )

                hora_salida_normalizada = _normalizar_hora(
                    self.hora_salida.get()
                )

            except ValueError as error:
                messagebox.showerror(
                    "Datos inválidos",
                    (
                        "Revise el semestre, el número de estudiantes "
                        "y los horarios.\n\n"
                        f"{error}"
                    ),
                    parent=self,
                )
                return

            if numero_estudiantes <= 0:
                messagebox.showerror(
                    "Número inválido",
                    (
                        "El número de estudiantes debe ser "
                        "mayor que cero."
                    ),
                    parent=self,
                )
                return

            if semestre <= 0:
                messagebox.showerror(
                    "Semestre inválido",
                    "El semestre debe ser mayor que cero.",
                    parent=self,
                )
                return

            if (
                hora_entrada_normalizada
                >= hora_salida_normalizada
            ):
                messagebox.showerror(
                    "Horario inválido",
                    (
                        "La hora de salida debe ser posterior "
                        "a la hora de entrada."
                    ),
                    parent=self,
                )
                return

            nombre_laboratorio = (
                self.laboratorio.get().strip()
            )

            nombre_docente = (
                self.docente.get().strip()
            )

            if not nombre_laboratorio:
                messagebox.showerror(
                    "Laboratorio requerido",
                    "Debe seleccionar un laboratorio.",
                    parent=self,
                )
                return

            if not self.asignatura.get().strip():
                messagebox.showerror(
                    "Asignatura requerida",
                    "Debe ingresar la asignatura.",
                    parent=self,
                )
                return

            if not nombre_docente:
                messagebox.showerror(
                    "Docente requerido",
                    (
                        "Debe ingresar el nombre del docente "
                        "responsable."
                    ),
                    parent=self,
                )
                return

            if not self._encargado_actual:
                messagebox.showerror(
                    "Encargado requerido",
                    (
                        "El laboratorio seleccionado no tiene "
                        "un encargado configurado."
                    ),
                    parent=self,
                )
                return

            if not self._cargo_encargado_actual:
                messagebox.showerror(
                    "Cargo requerido",
                    (
                        "El encargado del laboratorio no tiene "
                        "un cargo configurado."
                    ),
                    parent=self,
                )
                return

            # ========================================================
            # Materiales y reactivos
            # ========================================================

            materiales = (
                self.widget_materiales.obtener_items()
            )

            reactivos = (
                self.widget_reactivos.obtener_items()
            )

            # ========================================================
            # Estudiantes
            # ========================================================

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
                }
                for estudiante in self._estudiantes_firmados
            ]

            # Agregar líneas manuales nuevas.
            for linea in self.estudiantes.get(
                "1.0",
                "end",
            ).splitlines():
                linea = linea.strip()

                if not linea:
                    continue

                estudiantes.append(
                    {
                        "nombre": linea,
                        "cedula": None,
                        "firma_ruta": None,
                    }
                )

            # ========================================================
            # Firmas responsables
            # ========================================================

            firma_docente = (
                RUTA_FIRMA_DOCENTE_LAB
                if os.path.isfile(
                    RUTA_FIRMA_DOCENTE_LAB
                )
                else getattr(
                    self.registro_original,
                    "firma_docente_ruta",
                    None,
                )
            )

            firma_encargado = (
                RUTA_FIRMA_ENCARGADO_LAB
                if os.path.isfile(
                    RUTA_FIRMA_ENCARGADO_LAB
                )
                else getattr(
                    self.registro_original,
                    "firma_encargado_ruta",
                    None,
                )
            )

            # ========================================================
            # Reconstruir el objeto
            # ========================================================

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

            laboratorio_actualizado = Laboratorio(
                codigo=self.registro_original.codigo,
                laboratorio=nombre_laboratorio,
                numero_estudiantes=numero_estudiantes,
                asignatura=self.asignatura.get().strip(),
                unidad_academica=(
                    self.unidad_academica.get().strip()
                ),
                semestre=semestre,
                carrera=self.carrera.get().strip(),
                hora_entrada=hora_entrada_normalizada,
                hora_salida=hora_salida_normalizada,
                institucion=self.institucion.get().strip(),
                ciudad=self.ciudad.get().strip(),
                docente_responsable=nombre_docente,
                fecha_practica=fecha_practica,
                tema_practica=self.tema.get(
                    "1.0",
                    "end",
                ).strip(),
                subtema=self.subtema.get(
                    "1.0",
                    "end",
                ).strip(),
                logro_aprendizaje=self.logro.get(
                    "1.0",
                    "end",
                ).strip(),
                objetivos=self.objetivos.get(
                    "1.0",
                    "end",
                ).strip(),
                metodologia=self.metodologia.get(
                    "1.0",
                    "end",
                ).strip(),
                resultados=self.resultados.get(
                    "1.0",
                    "end",
                ).strip(),
                conclusiones=self.conclusiones.get(
                    "1.0",
                    "end",
                ).strip(),
                observaciones=self.observaciones.get(
                    "1.0",
                    "end",
                ).strip(),
                pdf_url=self.registro_original.pdf_url,
                materiales=materiales,
                reactivos=reactivos,
                estudiantes=estudiantes,
                encargado_laboratorio=(
                    self._encargado_actual
                ),
                cargo_encargado=(
                    self._cargo_encargado_actual
                ),
                firma_encargado_ruta=firma_encargado,
                firma_docente_ruta=firma_docente,
                codigo_sesion=self._codigo_sesion,
                id=self.registro_original.id,
            )

            # ========================================================
            # Generar nuevo PDF
            # ========================================================

            ruta_pdf = generar_pdf_laboratorio(
                laboratorio_actualizado
            )

            # ========================================================
            # Subir nuevo PDF a Supabase
            # ========================================================

            nueva_url_pdf = subir_pdf_laboratorio(
                ruta_pdf
            )

            laboratorio_actualizado.pdf_url = (
                nueva_url_pdf
            )

            # ========================================================
            # Actualizar base de datos
            # ========================================================

            resultado = actualizar_laboratorio(
                laboratorio_actualizado
            )

            if not resultado:
                raise RuntimeError(
                    "No fue posible actualizar el registro "
                    "en PostgreSQL."
                )

            messagebox.showinfo(
                "Correcto",
                (
                    "Laboratorio actualizado correctamente.\n\n"
                    "El PDF actualizado fue generado y subido "
                    "a Supabase."
                ),
                parent=self,
            )

            self.destroy()

        except Exception as error:
            print(
                "\n========== ERROR EDITANDO LABORATORIO =========="
            )
            print(error)
            print(
                "================================================\n"
            )

            messagebox.showerror(
                "Error",
                (
                    "No fue posible actualizar el laboratorio.\n\n"
                    f"{error}"
                ),
                parent=self,
            )