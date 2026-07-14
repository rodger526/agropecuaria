from database.eliminar import eliminar_practica


def eliminar(id_practica):
    """
    Elimina una práctica mediante la capa de base de datos.

    La confirmación y los mensajes visuales deben manejarse desde
    views/buscar_practica.py para evitar mostrar dos confirmaciones.

    Devuelve:
        True  -> se eliminó correctamente.
        False -> no se pudo eliminar.
    """

    if id_practica is None:
        return False

    return eliminar_practica(id_practica)