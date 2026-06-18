import os

def obtener_firma():

    ruta = "firma/firmas/firma_docente.png"

    if os.path.exists(ruta):
        return ruta

    return None