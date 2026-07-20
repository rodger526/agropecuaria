import mimetypes
import os
import uuid
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv
from supabase import create_client


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ENV = BASE_DIR / ".env"

load_dotenv(RUTA_ENV)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")

CARPETA = "firmas/practicas"


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


def _crear_cliente():
    _validar_configuracion()

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


def subir_firma(
    ruta_firma,
    id_practica,
    rol="comision",
):
    """
    Sube una firma a Supabase Storage.

    Devuelve la URL pública permanente.
    """

    if not ruta_firma:
        raise ValueError(
            "La ruta de la firma no puede estar vacía."
        )

    ruta_firma = Path(ruta_firma).resolve()

    if not ruta_firma.is_file():
        raise FileNotFoundError(
            f"No se encontró la firma:\n{ruta_firma}"
        )

    extension = ruta_firma.suffix.lower()

    if extension not in (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    ):
        raise ValueError(
            "La firma debe ser una imagen PNG, JPG, JPEG o WEBP."
        )

    cliente = _crear_cliente()

    nombre_archivo = (
        f"{rol}-{id_practica}-"
        f"{uuid.uuid4().hex}{extension}"
    )

    ruta_storage = (
        f"{CARPETA}/{nombre_archivo}"
    )

    tipo_mime = (
        mimetypes.guess_type(
            str(ruta_firma)
        )[0]
        or "image/png"
    )

    try:
        contenido = ruta_firma.read_bytes()

        cliente.storage.from_(BUCKET).upload(
            path=ruta_storage,
            file=contenido,
            file_options={
                "content-type": tipo_mime,
                "upsert": "false",
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
            f"Firma subida correctamente: {ruta_storage}"
        )

        return url_publica

    except Exception as error:
        raise RuntimeError(
            "No fue posible subir la firma a Supabase:\n"
            f"{error}"
        ) from error


def obtener_ruta_storage_desde_url(
    firma_url,
):
    """
    Convierte una URL pública de Supabase
    en su ruta interna de Storage.
    """

    if not firma_url:
        return None

    try:
        ruta_url = unquote(
            urlparse(
                str(firma_url).strip()
            ).path
        )

        marcador = (
            f"/storage/v1/object/public/"
            f"{BUCKET}/"
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


def eliminar_firma(
    firma_url,
):
    """
    Elimina una firma de Supabase mediante su URL pública.

    Se usa principalmente para rollback si falla
    la actualización de PostgreSQL.
    """

    if not firma_url:
        return True

    ruta_storage = obtener_ruta_storage_desde_url(
        firma_url
    )

    if not ruta_storage:
        print(
            "No se pudo determinar la ruta interna "
            "de la firma."
        )
        return False

    try:
        cliente = _crear_cliente()

        cliente.storage.from_(BUCKET).remove(
            [ruta_storage]
        )

        print(
            f"Firma eliminada de Supabase: "
            f"{ruta_storage}"
        )

        return True

    except Exception as error:
        print(
            "\n====== ERROR ELIMINANDO FIRMA ======"
        )
        print(error)
        print(
            "====================================\n"
        )

        return False