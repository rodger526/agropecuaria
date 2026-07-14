from datetime import datetime


def generar_codigo_informe():
    """
    Genera un código único para identificar cada informe.

    Ejemplo:

        INF-20260713221543
    """

    fecha = datetime.now()

    return f"INF-{fecha.strftime('%Y%m%d%H%M%S')}"