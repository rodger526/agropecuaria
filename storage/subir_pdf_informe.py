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

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ENV = BASE_DIR / ".env"

load_dotenv(RUTA_ENV)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BUCKET = os.getenv(
    "SUPABASE_BUCKET_INFORMES",
    "informes_laboratorio",
)


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
        ("http://", "https://")
    ):
        raise RuntimeError(
            "SUPABASE_URL no tiene un formato válido."
        )

    if not BUCKET:
        raise RuntimeError(
            "Falta SUPABASE_BUCKET_INFORMES en el archivo .env."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


# ============================================================
# Función general de subida
# ============================================================

def subir_archivo(
    ruta_local,
    carpeta,
    nombre_base=None,
):
    """
    Sube cualquier archivo relacionado con el informe.

    Parámetros:
        ruta_local:
            Ruta local del archivo.

        carpeta:
            Carpeta interna dentro del bucket.

        nombre_base:
            Nombre base opcional para el archivo.

    Devuelve:
        URL pública del archivo subido.
    """

    if not ruta_local:
        raise ValueError(
            "La ruta del archivo no puede estar vacía."
        )

    ruta_local = Path(
        ruta_local
    ).resolve()

    if not ruta_local.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo:\n{ruta_local}"
        )

    extension = ruta_local.suffix.lower()

    if not extension:
        raise ValueError(
            "El archivo no tiene una extensión válida."
        )

    nombre_base = str(
        nombre_base or ruta_local.stem
    ).strip()

    if not nombre_base:
        nombre_base = "archivo"

    nombre_storage = (
        f"{carpeta}/"
        f"{nombre_base}_"
        f"{uuid4().hex}"
        f"{extension}"
    )

    content_type = (
        mimetypes.guess_type(
            str(ruta_local)
        )[0]
        or "application/octet-stream"
    )

    cliente = _crear_cliente()

    try:
        contenido = ruta_local.read_bytes()

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

        url_publica = cliente.storage.from_(
            BUCKET
        ).get_public_url(
            nombre_storage
        )

        if isinstance(
            url_publica,
            dict,
        ):
            url_publica = (
                url_publica.get(
                    "publicUrl"
                )
                or url_publica.get(
                    "public_url"
                )
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
            f"Archivo subido correctamente: {nombre_storage}"
        )

        return url_publica

    except Exception as e:
        raise RuntimeError(
            "No fue posible subir el archivo a Supabase:\n"
            f"{e}"
        ) from e


# ============================================================
# Subida del PDF principal
# ============================================================

def subir_pdf_informe(ruta_pdf):
    """
    Sube el PDF principal del informe.

    El archivo quedará en:

        pdfs/
    """

    ruta_pdf = Path(
        ruta_pdf
    )

    if ruta_pdf.suffix.lower() != ".pdf":
        raise ValueError(
            "El archivo principal del informe debe ser PDF."
        )

    return subir_archivo(
        ruta_local=ruta_pdf,
        carpeta="pdfs",
        nombre_base=ruta_pdf.stem,
    )


# ============================================================
# Subida de hoja de datos
# ============================================================

def subir_hoja_datos(
    ruta_archivo,
    codigo_informe,
):
    """
    Sube la hoja de datos escaneada.

    Formatos permitidos:
        PDF, PNG, JPG y JPEG.
    """

    ruta_archivo = Path(
        ruta_archivo
    )

    extensiones_permitidas = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
    }

    if ruta_archivo.suffix.lower() not in extensiones_permitidas:
        raise ValueError(
            "La hoja de datos debe ser PDF, PNG, JPG o JPEG."
        )

    return subir_archivo(
        ruta_local=ruta_archivo,
        carpeta="hojas_datos",
        nombre_base=codigo_informe,
    )


# ============================================================
# Subida de fotografías
# ============================================================

def subir_foto_informe(
    ruta_foto,
    codigo_informe,
):
    """
    Sube una fotografía del informe.

    Formatos permitidos:
        PNG, JPG y JPEG.
    """

    ruta_foto = Path(
        ruta_foto
    )

    extensiones_permitidas = {
        ".png",
        ".jpg",
        ".jpeg",
    }

    if ruta_foto.suffix.lower() not in extensiones_permitidas:
        raise ValueError(
            "La fotografía debe ser PNG, JPG o JPEG."
        )

    return subir_archivo(
        ruta_local=ruta_foto,
        carpeta="fotos",
        nombre_base=codigo_informe,
    )


# ============================================================
# Obtener ruta interna desde una URL pública
# ============================================================

def obtener_ruta_storage_desde_url(
    url_publica,
):
    """
    Obtiene la ruta interna del archivo dentro del bucket.

    Ejemplo:

        URL:
        https://proyecto.supabase.co/storage/v1/object/public/
        informes_laboratorio/pdfs/INF-001.pdf

        Resultado:
        pdfs/INF-001.pdf
    """

    if not url_publica:
        return None

    try:
        ruta_url = unquote(
            urlparse(
                str(url_publica)
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


# ============================================================
# Eliminar archivo
# ============================================================

def eliminar_archivo_por_url(
    url_publica,
):
    """
    Elimina un archivo de Supabase Storage usando su URL pública.

    Devuelve:
        True si se eliminó correctamente.
        False si no se pudo eliminar.
    """

    if not url_publica:
        return True

    ruta_storage = obtener_ruta_storage_desde_url(
        url_publica
    )

    if not ruta_storage:
        print(
            "No se pudo determinar la ruta interna del archivo."
        )
        return False

    try:
        cliente = _crear_cliente()

        cliente.storage.from_(
            BUCKET
        ).remove(
            [ruta_storage]
        )

        print(
            f"Archivo eliminado de Supabase: {ruta_storage}"
        )

        return True

    except Exception as e:
        print(
            "\n===== ERROR ELIMINANDO ARCHIVO DE SUPABASE ====="
        )
        print(e)
        print(
            "=================================================\n"
        )

        return False