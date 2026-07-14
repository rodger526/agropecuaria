from datetime import datetime


def generar_codigo():
    """
    Genera un código prácticamente único para una planificación.

    Ejemplo:
        PRA-20260713224530123456
    """

    fecha = datetime.now()

    return f"PRA-{fecha.strftime('%Y%m%d%H%M%S%f')}"