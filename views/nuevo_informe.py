from pathlib import Path
from tkinter import messagebox

from database.informe.guardar_informe import guardar_informe
from pdf.generador_pdf_informe import generar_pdf_informe
from storage.subir_pdf_informe import (
    subir_foto_informe,
    subir_hoja_datos,
    subir_pdf_informe,
)
from utils.generar_codigo_informe import generar_codigo_informe
from views.formulario_informe import FormularioInformeBase


class VentanaNuevoInforme(FormularioInformeBase):
    """
    Ventana para crear un nuevo informe de laboratorio.

    Flujo:
        1. Valida los datos del formulario.
        2. Genera el código del informe.
        3. Sube la hoja de datos a Supabase.
        4. Sube las fotografías a Supabase.
        5. Genera el PDF local.
        6. Sube el PDF a Supabase.
        7. Guarda todo en PostgreSQL.
    """

    def __init__(self, master):
        super().__init__(
            master=master,
            titulo_ventana="Nuevo informe de laboratorio",
            texto_boton="GUARDAR INFORME",
            informe=None,
        )

    def guardar(self):
        """
        Guarda el informe completo en Supabase y PostgreSQL.
        """

        archivos_subidos = []

        try:
            # ========================================================
            # 1. Generar código y obtener datos del formulario
            # ========================================================

            codigo = generar_codigo_informe()

            informe = self.obtener_informe_formulario(
                codigo=codigo,
                id_informe=None,
            )

            # ========================================================
            # 2. Subir hoja de datos
            # ========================================================

            if self.ruta_hoja_datos_local:
                hoja_datos_url = subir_hoja_datos(
                    ruta_archivo=self.ruta_hoja_datos_local,
                    codigo_informe=codigo,
                )

                informe.hoja_datos_url = hoja_datos_url

                archivos_subidos.append(
                    hoja_datos_url
                )

            # ========================================================
            # 3. Subir fotografías
            # ========================================================

            fotos_subidas = []

            for indice, foto in enumerate(
                informe.fotos or [],
                start=1,
            ):
                ruta_local = foto.get(
                    "ruta_local"
                )

                if not ruta_local:
                    continue

                foto_url = subir_foto_informe(
                    ruta_foto=ruta_local,
                    codigo_informe=codigo,
                )

                archivos_subidos.append(
                    foto_url
                )

                fotos_subidas.append(
                    {
                        "foto_url": foto_url,
                        "ruta_local": ruta_local,
                        "descripcion": foto.get(
                            "descripcion"
                        ),
                        "orden": foto.get(
                            "orden",
                            indice,
                        ),
                    }
                )

            informe.fotos = fotos_subidas

            # ========================================================
            # 4. Generar PDF local
            # ========================================================

            carpeta_pdf = Path(
                "pdfs_informes"
            )

            carpeta_pdf.mkdir(
                parents=True,
                exist_ok=True,
            )

            ruta_pdf = carpeta_pdf / (
                f"{codigo}.pdf"
            )

            ruta_pdf_generado = generar_pdf_informe(
                informe=informe,
                ruta_pdf=ruta_pdf,
            )

            # ========================================================
            # 5. Subir PDF a Supabase
            # ========================================================

            pdf_url = subir_pdf_informe(
                ruta_pdf_generado
            )

            informe.pdf_url = pdf_url

            archivos_subidos.append(
                pdf_url
            )

            # ========================================================
            # 6. Guardar registro en PostgreSQL
            # ========================================================

            resultado = guardar_informe(
                informe
            )

            if not resultado:
                raise RuntimeError(
                    "No fue posible guardar el informe "
                    "en la base de datos."
                )

            # ========================================================
            # 7. Confirmación
            # ========================================================

            messagebox.showinfo(
                "Correcto",
                (
                    "Informe guardado correctamente.\n\n"
                    f"Código: {codigo}\n"
                    "El PDF y los archivos fueron subidos "
                    "a Supabase."
                ),
                parent=self,
            )

            self.destroy()

        except Exception as e:
            print(
                "\n========== ERROR CREANDO INFORME =========="
            )
            print(e)
            print(
                "============================================\n"
            )

            messagebox.showerror(
                "Error",
                (
                    "No fue posible guardar el informe.\n\n"
                    f"{e}"
                ),
                parent=self,
            )