import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# Cargar configuración desde el .env de la raíz
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ENV = BASE_DIR / ".env"

load_dotenv(RUTA_ENV)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")

CARPETA = "practicas"


def _validar_configuracion():
    """
    Comprueba que existan las variables necesarias para utilizar
    Supabase Storage.
    """

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
    """
    Crea el cliente de Supabase después de validar la configuración.
    """

    _validar_configuracion()

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


def subir_pdf(ruta_pdf):
    """
    Sube un PDF al bucket configurado en Supabase Storage.

    El archivo se almacena dentro de:

        practicas/nombre_archivo.pdf

    Devuelve:
        URL pública del PDF.

    Lanza:
        FileNotFoundError si el archivo local no existe.
        ValueError si el archivo no es PDF.
        RuntimeError si la subida o la URL pública fallan.
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
            "El archivo seleccionado no tiene extensión PDF."
        )

    cliente = _crear_cliente()

    nombre_archivo = ruta_pdf.name
    ruta_storage = f"{CARPETA}/{nombre_archivo}"

    try:
        with ruta_pdf.open("rb") as archivo:
            contenido = archivo.read()

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
        ).get_public_url(ruta_storage)

        if isinstance(url_publica, dict):
            url_publica = (
                url_publica.get("publicUrl")
                or url_publica.get("public_url")
            )

        url_publica = str(url_publica or "").strip()

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

    except Exception as e:
        raise RuntimeError(
            f"No fue posible subir el PDF a Supabase:\n{e}"
        ) from e


def obtener_ruta_storage_desde_url(pdf_url):
    """
    Extrae la ruta interna de Storage desde una URL pública.

    Ejemplo:

        URL:
        https://proyecto.supabase.co/storage/v1/object/public/
        pdfs/practicas/PRA-001.pdf

        Resultado:
        practicas/PRA-001.pdf
    """

    if not pdf_url:
        return None

    pdf_url = str(pdf_url).strip()

    try:
        ruta_url = unquote(urlparse(pdf_url).path)

        marcador = f"/storage/v1/object/public/{BUCKET}/"

        if marcador not in ruta_url:
            return None

        ruta_storage = ruta_url.split(
            marcador,
            1,
        )[1]

        return ruta_storage or None

    except Exception:
        return None


def eliminar_pdf(pdf_url):
    """
    Elimina de Supabase Storage un PDF mediante su URL pública.

    Devuelve:
        True  -> archivo eliminado o URL vacía.
        False -> no se pudo determinar o eliminar el archivo.
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

    except Exception as e:
        print("\n====== ERROR ELIMINANDO PDF DE SUPABASE ======")
        print(e)
        print("==============================================\n")

        return False