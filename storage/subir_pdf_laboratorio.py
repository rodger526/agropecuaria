import mimetypes
import os

from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# Configuración
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

RUTA_ENV = BASE_DIR / ".env"

load_dotenv(
    RUTA_ENV
)


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY"
)

BUCKET = os.getenv(
    "SUPABASE_BUCKET_LABORATORIOS",
    "informes_laboratorio",
)

CARPETA_PDFS = "laboratorios"


# ============================================================
# Cliente de Supabase
# ============================================================

def _crear_cliente():
    """
    Valida las variables de entorno y crea el cliente
    de Supabase.
    """

    if not SUPABASE_URL:
        raise RuntimeError(
            "Falta SUPABASE_URL en el archivo .env."
        )

    if not SUPABASE_KEY:
        raise RuntimeError(
            "Falta SUPABASE_KEY en el archivo .env."
        )

    if not SUPABASE_URL.lower().startswith(
        (
            "http://",
            "https://",
        )
    ):
        raise RuntimeError(
            "SUPABASE_URL no tiene un formato válido."
        )

    if not BUCKET:
        raise RuntimeError(
            "Falta SUPABASE_BUCKET_LABORATORIOS "
            "en el archivo .env."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


# ============================================================
# Funciones auxiliares
# ============================================================

def _validar_pdf(
    ruta_pdf,
):
    """
    Valida que la ruta exista y sea un archivo PDF.
    """

    if not ruta_pdf:
        raise ValueError(
            "La ruta del PDF no puede estar vacía."
        )

    ruta_pdf = Path(
        ruta_pdf
    ).resolve()

    if not ruta_pdf.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo PDF:\n{ruta_pdf}"
        )

    if ruta_pdf.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo del laboratorio debe tener extensión .pdf."
        )

    return ruta_pdf


def _normalizar_url_publica(
    respuesta,
):
    """
    Convierte la respuesta de get_public_url() en texto.
    """

    if isinstance(
        respuesta,
        dict,
    ):
        respuesta = (
            respuesta.get(
                "publicUrl"
            )
            or respuesta.get(
                "public_url"
            )
            or respuesta.get(
                "signedURL"
            )
            or respuesta.get(
                "signed_url"
            )
        )

    url = str(
        respuesta or ""
    ).strip()

    if not url.lower().startswith(
        (
            "http://",
            "https://",
        )
    ):
        raise RuntimeError(
            "Supabase no devolvió una URL pública válida."
        )

    return url


# ============================================================
# Subir PDF
# ============================================================

def subir_pdf_laboratorio(
    ruta_pdf,
):
    """
    Sube el PDF del laboratorio a Supabase Storage.

    El archivo se almacena dentro del bucket configurado en:

        SUPABASE_BUCKET_LABORATORIOS

    y en la carpeta interna:

        laboratorios/

    Devuelve:
        URL pública del PDF.
    """

    ruta_pdf = _validar_pdf(
        ruta_pdf
    )

    nombre_storage = (
        f"{CARPETA_PDFS}/"
        f"{ruta_pdf.stem}_"
        f"{uuid4().hex}"
        f"{ruta_pdf.suffix.lower()}"
    )

    content_type = (
        mimetypes.guess_type(
            str(ruta_pdf)
        )[0]
        or "application/pdf"
    )

    cliente = _crear_cliente()

    try:
        contenido = ruta_pdf.read_bytes()

        cliente.storage.from_(
            BUCKET
        ).upload(
            path=nombre_storage,
            file=contenido,
            file_options={
                "content-type": content_type,
                "upsert": "false",
            },
        )

        respuesta_url = cliente.storage.from_(
            BUCKET
        ).get_public_url(
            nombre_storage
        )

        url_publica = _normalizar_url_publica(
            respuesta_url
        )

        print(
            "PDF de laboratorio subido correctamente:"
        )
        print(
            nombre_storage
        )
        print(
            url_publica
        )

        return url_publica

    except Exception as error:
        raise RuntimeError(
            "No fue posible subir el PDF del laboratorio "
            "a Supabase.\n"
            f"Bucket: {BUCKET}\n"
            f"Ruta: {nombre_storage}\n\n"
            f"{error}"
        ) from error


# ============================================================
# Obtener ruta interna desde URL pública
# ============================================================

def obtener_ruta_storage_laboratorio(
    url_publica,
):
    """
    Obtiene la ruta interna del archivo dentro del bucket.

    Ejemplo:

        URL pública:
        https://proyecto.supabase.co/storage/v1/object/public/
        informes_laboratorio/laboratorios/LAB-001.pdf

        Resultado:
        laboratorios/LAB-001.pdf
    """

    if not url_publica:
        return None

    try:
        ruta_url = unquote(
            urlparse(
                str(
                    url_publica
                )
            ).path
        )

        marcador_publico = (
            f"/storage/v1/object/public/"
            f"{BUCKET}/"
        )

        marcador_firmado = (
            f"/storage/v1/object/sign/"
            f"{BUCKET}/"
        )

        if marcador_publico in ruta_url:
            return ruta_url.split(
                marcador_publico,
                1,
            )[1] or None

        if marcador_firmado in ruta_url:
            return ruta_url.split(
                marcador_firmado,
                1,
            )[1] or None

        return None

    except Exception:
        return None


# ============================================================
# Eliminar PDF
# ============================================================

def eliminar_pdf_laboratorio_por_url(
    url_publica,
):
    """
    Elimina un PDF de laboratorio usando su URL pública.

    Devuelve:
        True si se eliminó o si la URL está vacía.
        False si no se pudo eliminar.
    """

    if not url_publica:
        return True

    ruta_storage = obtener_ruta_storage_laboratorio(
        url_publica
    )

    if not ruta_storage:
        print(
            "No se pudo determinar la ruta interna "
            "del PDF del laboratorio."
        )
        return False

    try:
        cliente = _crear_cliente()

        cliente.storage.from_(
            BUCKET
        ).remove(
            [
                ruta_storage
            ]
        )

        print(
            "PDF de laboratorio eliminado de Supabase:"
        )
        print(
            ruta_storage
        )

        return True

    except Exception as error:
        print(
            "\n===== ERROR ELIMINANDO PDF DE LABORATORIO ====="
        )
        print(error)
        print(
            "================================================\n"
        )

        return False