from pathlib import Path
from tkinter import messagebox

from database.informe.editar_informe import actualizar_informe
from pdf.generador_pdf_informe import generar_pdf_informe
from storage.subir_pdf_informe import (
    eliminar_archivo_por_url,
    subir_foto_informe,
    subir_hoja_datos,
    subir_pdf_informe,
)
from views.formulario_informe import FormularioInformeBase


class VentanaEditarInforme(FormularioInformeBase):
    """
    Ventana para editar un informe de laboratorio existente.

    Flujo:
        1. Recupera los datos actuales.
        2. Conserva archivos que no fueron modificados.
        3. Sube una nueva hoja de datos, si se seleccionó.
        4. Sube las fotografías nuevas.
        5. Regenera el PDF.
        6. Sube el PDF actualizado.
        7. Actualiza PostgreSQL.
        8. Intenta eliminar de Supabase los archivos antiguos
           que fueron reemplazados o retirados.
    """

    def __init__(
        self,
        master,
        informe,
    ):
        if informe is None:
            raise ValueError(
                "No se recibió un informe válido para editar."
            )

        if not getattr(
            informe,
            "id",
            None,
        ):
            raise ValueError(
                "El informe no tiene un ID válido."
            )

        super().__init__(
            master=master,
            titulo_ventana="Editar informe de laboratorio",
            texto_boton="ACTUALIZAR INFORME",
            informe=informe,
        )

    def guardar(self):
        """
        Actualiza el informe completo en PostgreSQL y Supabase.
        """

        urls_nuevas_subidas = []

        hoja_antigua_url = (
            self.informe_original.hoja_datos_url
        )

        pdf_antiguo_url = (
            self.informe_original.pdf_url
        )

        fotos_antiguas = [
            dict(
                foto
            )
            for foto in (
                self.informe_original.fotos
                or []
            )
        ]

        try:
            # ========================================================
            # 1. Obtener los datos actuales del formulario
            # ========================================================

            informe = self.obtener_informe_formulario(
                codigo=self.informe_original.codigo,
                id_informe=self.informe_original.id,
            )

            # Mantener fecha original
            informe.fecha_creacion = (
                self.informe_original.fecha_creacion
            )

            # ========================================================
            # 2. Actualizar hoja de datos, si se seleccionó otra
            # ========================================================

            if self.ruta_hoja_datos_local:
                nueva_hoja_url = subir_hoja_datos(
                    ruta_archivo=self.ruta_hoja_datos_local,
                    codigo_informe=informe.codigo,
                )

                informe.hoja_datos_url = (
                    nueva_hoja_url
                )

                urls_nuevas_subidas.append(
                    nueva_hoja_url
                )

            # Si no se eligió otra hoja, conservar la anterior
            elif hoja_antigua_url:
                informe.hoja_datos_url = (
                    hoja_antigua_url
                )

            # ========================================================
            # 3. Procesar fotografías
            # ========================================================

            fotos_finales = []

            for indice, foto in enumerate(
                informe.fotos or [],
                start=1,
            ):
                if not isinstance(
                    foto,
                    dict,
                ):
                    continue

                foto_url_existente = str(
                    foto.get(
                        "foto_url"
                    )
                    or ""
                ).strip()

                ruta_local = str(
                    foto.get(
                        "ruta_local"
                    )
                    or ""
                ).strip()

                descripcion = str(
                    foto.get(
                        "descripcion"
                    )
                    or ""
                ).strip()

                try:
                    orden = int(
                        foto.get(
                            "orden",
                            indice,
                        )
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    orden = indice

                # Fotografía que ya estaba en Supabase
                if foto_url_existente:
                    fotos_finales.append(
                        {
                            "foto_url": foto_url_existente,
                            "descripcion": descripcion,
                            "orden": orden,
                        }
                    )
                    continue

                # Fotografía nueva seleccionada desde la computadora
                if ruta_local:
                    nueva_foto_url = subir_foto_informe(
                        ruta_foto=ruta_local,
                        codigo_informe=informe.codigo,
                    )

                    urls_nuevas_subidas.append(
                        nueva_foto_url
                    )

                    fotos_finales.append(
                        {
                            "foto_url": nueva_foto_url,
                            "ruta_local": ruta_local,
                            "descripcion": descripcion,
                            "orden": orden,
                        }
                    )

            informe.fotos = fotos_finales

            # ========================================================
            # 4. Generar nuevamente el PDF
            # ========================================================

            carpeta_pdf = Path(
                "pdfs_informes"
            )

            carpeta_pdf.mkdir(
                parents=True,
                exist_ok=True,
            )

            ruta_pdf = (
                carpeta_pdf
                / f"{informe.codigo}.pdf"
            )

            ruta_generada = generar_pdf_informe(
                informe=informe,
                ruta_pdf=ruta_pdf,
            )

            # ========================================================
            # 5. Subir PDF actualizado
            # ========================================================

            nuevo_pdf_url = subir_pdf_informe(
                ruta_generada
            )

            informe.pdf_url = nuevo_pdf_url

            urls_nuevas_subidas.append(
                nuevo_pdf_url
            )

            # ========================================================
            # 6. Actualizar PostgreSQL
            # ========================================================

            resultado = actualizar_informe(
                informe
            )

            if not resultado:
                raise RuntimeError(
                    "No fue posible actualizar el informe "
                    "en la base de datos."
                )

            # ========================================================
            # 7. Eliminar archivos antiguos reemplazados
            # ========================================================

            if (
                self.ruta_hoja_datos_local
                and hoja_antigua_url
                and hoja_antigua_url
                != informe.hoja_datos_url
            ):
                eliminar_archivo_por_url(
                    hoja_antigua_url
                )

            if (
                pdf_antiguo_url
                and pdf_antiguo_url
                != informe.pdf_url
            ):
                eliminar_archivo_por_url(
                    pdf_antiguo_url
                )

            # URLs antiguas de fotografías
            urls_fotos_antiguas = {
                str(
                    foto.get(
                        "foto_url"
                    )
                    or ""
                ).strip()
                for foto in fotos_antiguas
                if isinstance(
                    foto,
                    dict,
                )
            }

            # URLs que todavía permanecen en el informe
            urls_fotos_actuales = {
                str(
                    foto.get(
                        "foto_url"
                    )
                    or ""
                ).strip()
                for foto in informe.fotos
                if isinstance(
                    foto,
                    dict,
                )
            }

            fotos_eliminadas = (
                urls_fotos_antiguas
                - urls_fotos_actuales
            )

            for foto_url in fotos_eliminadas:
                if foto_url:
                    eliminar_archivo_por_url(
                        foto_url
                    )

            # ========================================================
            # 8. Confirmación
            # ========================================================

            messagebox.showinfo(
                "Correcto",
                (
                    "Informe actualizado correctamente.\n\n"
                    "El nuevo PDF fue generado y subido "
                    "a Supabase."
                ),
                parent=self,
            )

            self.destroy()

        except Exception as e:
            print(
                "\n========== ERROR EDITANDO INFORME =========="
            )
            print(e)
            print(
                "============================================\n"
            )

            # Si algo falló antes de actualizar la base de datos,
            # intenta retirar los archivos nuevos para no dejar
            # archivos huérfanos.
            for url_nueva in urls_nuevas_subidas:
                try:
                    eliminar_archivo_por_url(
                        url_nueva
                    )
                except Exception:
                    pass

            messagebox.showerror(
                "Error",
                (
                    "No fue posible actualizar el informe.\n\n"
                    f"{e}"
                ),
                parent=self,
            )