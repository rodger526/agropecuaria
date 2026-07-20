from database.conexion import obtener_conexion
from storage.subir_pdf import eliminar_pdf


def obtener_pdf_url(id_practica):
    """Obtiene la URL del PDF asociado a una práctica."""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT pdf_url
            FROM practicas
            WHERE id = %s
            """,
            (id_practica,),
        )

        fila = cursor.fetchone()
        return fila[0] if fila else None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def eliminar_practica(id_practica):
    """
    Elimina una práctica y su PDF.

    Flujo:
        1. Obtiene la URL.
        2. Elimina el PDF de Supabase.
        3. Elimina el registro de PostgreSQL.

    Devuelve:
        (True, mensaje) o (False, mensaje).
    """

    if id_practica is None:
        return False, "El id de la práctica no puede ser None."

    try:
        pdf_url = obtener_pdf_url(id_practica)
    except Exception as error:
        return False, f"No se pudo consultar la práctica:\n{error}"

    if pdf_url:
        if not eliminar_pdf(pdf_url):
            return (
                False,
                "No se eliminó el registro porque primero debe eliminarse "
                "correctamente el PDF de Supabase.",
            )

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM practicas
            WHERE id = %s
            """,
            (id_practica,),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"No existe una práctica con id {id_practica}.")

        conexion.commit()

        return True, "La práctica y su PDF fueron eliminados correctamente."

    except Exception as error:
        if conexion:
            conexion.rollback()

        return (
            False,
            "El PDF pudo haberse eliminado, pero no fue posible borrar "
            f"el registro de PostgreSQL:\n{error}",
        )

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


# Alias para código antiguo.
def eliminar(id_practica):
    exito, _ = eliminar_practica(id_practica)
    return exito