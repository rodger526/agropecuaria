from database.conexion import obtener_conexion


def eliminar_practica(id_practica):

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM practicas
            WHERE id = %s
        """, (id_practica,))

        conexion.commit()

        return True

    except Exception as e:

        print("ERROR AL ELIMINAR:")
        print(e)

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()