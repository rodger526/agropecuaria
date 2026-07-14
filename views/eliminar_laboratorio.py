from database.laboratorio.buscar_laboratorio import (
    buscar_laboratorio_por_id,
)
from database.laboratorio.eliminar_laboratorio import (
    eliminar_laboratorio,
)
from storage.subir_pdf_laboratorio import (
    eliminar_pdf_laboratorio_por_url,
)


def eliminar(id_laboratorio):
    """
    Elimina un laboratorio de PostgreSQL y, si tiene un PDF
    almacenado en Supabase, intenta eliminarlo también.

    Flujo:
        1. Busca el laboratorio para recuperar su pdf_url.
        2. Elimina el registro de PostgreSQL.
        3. Si la eliminación fue correcta, elimina el PDF de Supabase.

    Devuelve:
        True si el registro se eliminó correctamente.
        False si ocurrió algún error.
    """

    if not id_laboratorio:
        print(
            "No se recibió un ID válido para eliminar."
        )
        return False

    try:
        # ========================================================
        # 1. Recuperar datos antes de borrar
        # ========================================================

        fila = buscar_laboratorio_por_id(
            id_laboratorio
        )

        pdf_url = None

        if fila:
            # Según el orden de buscar_laboratorio_por_id():
            # índice 22 = pdf_url
            if len(fila) > 22:
                pdf_url = fila[22]

        # ========================================================
        # 2. Eliminar registro de PostgreSQL
        # ========================================================

        resultado = eliminar_laboratorio(
            id_laboratorio
        )

        if not resultado:
            print(
                "No fue posible eliminar el laboratorio "
                "de PostgreSQL."
            )
            return False

        # ========================================================
        # 3. Eliminar PDF de Supabase
        # ========================================================

        if pdf_url:
            eliminado_storage = (
                eliminar_pdf_laboratorio_por_url(
                    pdf_url
                )
            )

            if not eliminado_storage:
                print(
                    "El laboratorio fue eliminado de PostgreSQL, "
                    "pero no se pudo eliminar su PDF de Supabase."
                )

        print(
            f"Laboratorio {id_laboratorio} eliminado correctamente."
        )

        return True

    except Exception as error:
        print(
            "\n========== ERROR ELIMINANDO LABORATORIO =========="
        )
        print(error)
        print(
            "==================================================\n"
        )

        return False