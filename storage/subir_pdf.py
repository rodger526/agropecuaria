import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# Configuración
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ENV = BASE_DIR / ".env"

load_dotenv(RUTA_ENV)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")

CARPETA = "practicas"


def _validar_configuracion():
    faltantes = []

    if not SUPABASE_URL:
        faltantes.append("SUPABASE_URL")

    if not SUPABASE_KEY:
        faltantes.append("SUPABASE_KEY")

    if not BUCKET:
        faltantes.append("SUPABASE_BUCKET")

    if faltantes:
        raise RuntimeError(
            "Faltan variables de Supabase en el archivo .env: "
            + ", ".join(faltantes)
        )

    if not SUPABASE_URL.lower().startswith(
        ("http://", "https://")
    ):
        raise RuntimeError(
            "SUPABASE_URL no tiene un formato válido."
        )


def _crear_cliente():
    _validar_configuracion()

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


# ============================================================
# Subir PDF
# ============================================================

def subir_pdf(ruta_pdf):
    """
    Sube un PDF a Supabase Storage.

    Devuelve la URL pública.
    """

    if not ruta_pdf:
        raise ValueError(
            "La ruta del PDF no puede estar vacía."
        )

    ruta_pdf = Path(ruta_pdf).resolve()

    if not ruta_pdf.is_file():
        raise FileNotFoundError(
            f"No se encontró el PDF:\n{ruta_pdf}"
        )

    if ruta_pdf.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo seleccionado no es un PDF."
        )

    cliente = _crear_cliente()

    nombre_archivo = ruta_pdf.name
    ruta_storage = f"{CARPETA}/{nombre_archivo}"

    try:
        contenido = ruta_pdf.read_bytes()

        cliente.storage.from_(BUCKET).upload(
            path=ruta_storage,
            file=contenido,
            file_options={
                "content-type": "application/pdf",
                "upsert": "true",
            },
        )

        url_publica = cliente.storage.from_(
            BUCKET
        ).get_public_url(
            ruta_storage
        )

        if isinstance(url_publica, dict):
            url_publica = (
                url_publica.get("publicUrl")
                or url_publica.get("public_url")
            )

        url_publica = str(
            url_publica or ""
        ).strip()

        if not url_publica.lower().startswith(
            ("http://", "https://")
        ):
            raise RuntimeError(
                "Supabase no devolvió una URL pública válida."
            )

        print(
            f"PDF subido correctamente: {ruta_storage}"
        )

        return url_publica

    except Exception as error:
        raise RuntimeError(
            f"No fue posible subir el PDF a Supabase:\n{error}"
        ) from error


# ============================================================
# Obtener ruta interna desde URL
# ============================================================

def obtener_ruta_storage_desde_url(pdf_url):
    """
    Convierte una URL pública de Supabase en su ruta interna.

    Ejemplo:

    URL:
    https://xxxxx.supabase.co/storage/v1/object/public/
    pdfs/practicas/PRA-001.pdf

    Resultado:
    practicas/PRA-001.pdf
    """

    if not pdf_url:
        return None

    try:
        ruta_url = unquote(
            urlparse(
                str(pdf_url).strip()
            ).path
        )

        marcador = (
            f"/storage/v1/object/public/{BUCKET}/"
        )

        if marcador not in ruta_url:
            return None

        ruta_storage = ruta_url.split(
            marcador,
            1,
        )[1]

        return ruta_storage or None

    except Exception:
        return None


# ============================================================
# Eliminar PDF
# ============================================================

def eliminar_pdf(pdf_url):
    """
    Elimina un PDF de Supabase Storage mediante su URL pública.

    Devuelve:
        True si fue eliminado.
        False si ocurrió un error.
    """

    if not pdf_url:
        return True

    ruta_storage = obtener_ruta_storage_desde_url(
        pdf_url
    )

    if not ruta_storage:
        print(
            "No se pudo determinar la ruta interna del PDF."
        )
        return False

    try:
        cliente = _crear_cliente()

        cliente.storage.from_(BUCKET).remove(
            [ruta_storage]
        )

        print(
            f"PDF eliminado de Supabase: {ruta_storage}"
        )

        return True

    except Exception as error:
        print(
            "\n====== ERROR ELIMINANDO PDF DE SUPABASE ======"
        )
        print(error)
        print(
            "==============================================\n"
        )

        return False