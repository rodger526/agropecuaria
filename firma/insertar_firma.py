from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_FIRMA_DOCENTE = (
    BASE_DIR
    / "firma"
    / "firmas"
    / "firma_docente.png"
)


def obtener_firma():
    """
    Devuelve la ruta absoluta de la firma del docente si existe.

    Devuelve:
        str: ruta absoluta de la firma.
        None: si la firma todavía no existe.
    """

    if RUTA_FIRMA_DOCENTE.is_file():
        return str(RUTA_FIRMA_DOCENTE)

    return None