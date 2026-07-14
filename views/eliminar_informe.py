from database.informe.buscar_informe import (
    buscar_fotos_por_informe,
    buscar_informe_por_id,
)
from database.informe.eliminar_informe import eliminar_informe
from storage.subir_pdf_informe import eliminar_archivo_por_url


# Índices de la fila devuelta por buscar_informe_por_id()
IDX_ID = 0
IDX_HOJA_DATOS_URL = 22
IDX_PDF_URL = 23


def eliminar(id_informe):
    """
    Elimina completamente un informe.

    Proceso:
        1. Consulta las URLs antes de borrar el registro.
        2. Elimina el informe de PostgreSQL.
        3. Elimina el PDF de Supabase Storage.
        4. Elimina la hoja de datos.
        5. Elimina todas las fotografías.

    Devuelve:
        True si el registro fue eliminado correctamente.
        False si ocurrió un error al eliminarlo de PostgreSQL.

    Nota:
        Si PostgreSQL se elimina correctamente, pero algún archivo no
        puede borrarse de Supabase, la función seguirá devolviendo True
        y mostrará el error en la consola.
    """

    if id_informe is None:
        print(
            "[eliminar_informe] "
            "El ID del informe no puede ser None."
        )
        return False

    # ============================================================
    # 1. Obtener información antes de eliminar
    # ============================================================

    fila_informe = buscar_informe_por_id(
        id_informe
    )

    if not fila_informe:
        print(
            f"[eliminar_informe] "
            f"No existe el informe con ID {id_informe}."
        )
        return False

    pdf_url = fila_informe[
        IDX_PDF_URL
    ]

    hoja_datos_url = fila_informe[
        IDX_HOJA_DATOS_URL
    ]

    fotografias = buscar_fotos_por_informe(
        id_informe
    )

    # ============================================================
    # 2. Eliminar el registro de PostgreSQL
    # ============================================================

    eliminado_bd = eliminar_informe(
        id_informe
    )

    if not eliminado_bd:
        return False

    # ============================================================
    # 3. Eliminar el PDF principal de Supabase
    # ============================================================

    if pdf_url:
        resultado_pdf = eliminar_archivo_por_url(
            pdf_url
        )

        if not resultado_pdf:
            print(
                "[eliminar_informe] "
                "El registro se eliminó, pero no se pudo "
                "eliminar el PDF de Supabase."
            )

    # ============================================================
    # 4. Eliminar la hoja de datos
    # ============================================================

    if hoja_datos_url:
        resultado_hoja = eliminar_archivo_por_url(
            hoja_datos_url
        )

        if not resultado_hoja:
            print(
                "[eliminar_informe] "
                "El registro se eliminó, pero no se pudo "
                "eliminar la hoja de datos de Supabase."
            )

    # ============================================================
    # 5. Eliminar fotografías
    # ============================================================

    for fotografia in fotografias or []:
        if not isinstance(
            fotografia,
            dict,
        ):
            continue

        foto_url = fotografia.get(
            "foto_url"
        )

        if not foto_url:
            continue

        resultado_foto = eliminar_archivo_por_url(
            foto_url
        )

        if not resultado_foto:
            print(
                "[eliminar_informe] "
                f"No se pudo eliminar la fotografía: {foto_url}"
            )

    print(
        f"Informe {id_informe} y sus archivos "
        "relacionados fueron procesados correctamente."
    )

    return True