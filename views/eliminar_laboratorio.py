from database.laboratorio.eliminar_laboratorio import eliminar_laboratorio


def eliminar(id_laboratorio):
    """
    Wrapper delgado usado por la vista de búsqueda.
    Delega en database.laboratorio.eliminar_laboratorio.eliminar_laboratorio,
    que ya maneja la transacción y el borrado en cascada (ON DELETE CASCADE).
    Devuelve True/False.
    """
    return eliminar_laboratorio(id_laboratorio)