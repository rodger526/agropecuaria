import sys
from pathlib import Path


def carpeta_recursos() -> Path:
    """
    Carpeta que contiene los recursos empaquetados.
    """

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent


def carpeta_aplicacion() -> Path:
    """
    Carpeta donde está el ejecutable o el proyecto.
    Se utiliza para archivos que la aplicación crea o modifica.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


def ruta_recurso(*partes) -> Path:
    return carpeta_recursos().joinpath(*partes)


def ruta_datos(*partes) -> Path:
    ruta = carpeta_aplicacion().joinpath(*partes)

    if ruta.suffix:
        ruta.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
    else:
        ruta.mkdir(
            parents=True,
            exist_ok=True,
        )

    return ruta