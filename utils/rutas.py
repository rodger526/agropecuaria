import os
import sys
from pathlib import Path


def ruta_recursos(*partes):
    """
    Obtiene archivos incluidos dentro del ejecutable de PyInstaller.
    """

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent

    return base.joinpath(*partes)


def ruta_datos(*partes):
    """
    Obtiene una carpeta escribible junto al ejecutable.
    """

    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent

    ruta = base.joinpath(*partes)

    if partes and not ruta.suffix:
        ruta.mkdir(parents=True, exist_ok=True)

    return ruta