from database.conexion import obtener_conexion


def eliminar_informe(id_informe):
    """
    Elimina un informe y todas las fotografías asociadas.

    Si la tabla informe_laboratorio_fotos tiene una FK con
    ON DELETE CASCADE, el DELETE de las fotos se realiza
    automáticamente.

    Si no existe dicha restricción, este código igualmente
    las elimina manualmente antes del informe.
    """

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # ==========================================
        # Eliminar fotografías asociadas
        # ==========================================

        cursor.execute("""
            DELETE FROM informe_laboratorio_fotos
            WHERE informe_id = %s
        """, (
            id_informe,
        ))

        # ==========================================
        # Eliminar informe
        # ==========================================

        cursor.execute("""
            DELETE FROM informes_laboratorio
            WHERE id = %s
        """, (
            id_informe,
        ))

        if cursor.rowcount == 0:
            raise Exception(
                "No existe el informe solicitado."
            )

        conexion.commit()

        print(
            f"Informe {id_informe} eliminado correctamente."
        )

        return True

    except Exception as e:

        print(
            "\n========== ERROR ELIMINANDO INFORME =========="
        )
        print(e)
        print(
            "==============================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()