from database.conexion import obtener_conexion


def eliminar_laboratorio(id_laboratorio):
    """
    Elimina un laboratorio por su ID.

    Las tablas relacionadas se eliminan automáticamente si las
    claves foráneas fueron creadas con ON DELETE CASCADE:

        - laboratorio_materiales
        - laboratorio_reactivos
        - laboratorio_estudiantes

    Devuelve:
        True si el laboratorio fue eliminado.
        False si ocurrió un error.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            raise ValueError(
                "El ID del laboratorio no es válido."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM laboratorios
            WHERE id = %s
            RETURNING id
            """,
            (
                id_laboratorio,
            ),
        )

        fila_eliminada = cursor.fetchone()

        if not fila_eliminada:
            conexion.rollback()

            print(
                f"No existe un laboratorio con ID {id_laboratorio}."
            )

            return False

        conexion.commit()

        print(
            f"Laboratorio {id_laboratorio} eliminado de PostgreSQL."
        )

        return True

    except Exception as error:
        print(
            "\n========== ERROR AL ELIMINAR LABORATORIO =========="
        )
        print(error)
        print(
            "==================================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()