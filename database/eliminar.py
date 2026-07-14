from database.conexion import obtener_conexion


def eliminar_practica(id_practica):
    """
    Elimina una práctica de la tabla practicas.

    Devuelve:
        True  -> si el registro fue eliminado.
        False -> si no existe o ocurrió un error.
    """

    conexion = None
    cursor = None

    try:
        if id_practica is None:
            raise ValueError(
                "El id de la práctica no puede ser None."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM practicas
            WHERE id = %s
        """, (
            id_practica,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe una práctica con id {id_practica}."
            )

        conexion.commit()

        print(
            f"Práctica {id_practica} eliminada correctamente."
        )

        return True

    except Exception as e:
        print("\n========== ERROR AL ELIMINAR PRÁCTICA ==========")
        print(e)
        print("=================================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()