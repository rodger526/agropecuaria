from database.conexion import obtener_conexion


def eliminar_laboratorio(id_laboratorio):
    """
    Elimina el laboratorio con el id dado.
    Las tablas relacionadas (laboratorio_materiales, laboratorio_reactivos,
    laboratorio_estudiantes) se borran automáticamente por ON DELETE CASCADE.
    Devuelve True si se eliminó correctamente, False si hubo error.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM laboratorios
            WHERE id = %s
        """, (id_laboratorio,))

        conexion.commit()
        return True

    except Exception as e:
        print("ERROR AL ELIMINAR LABORATORIO")
        print(e)
        if conexion:
            conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()