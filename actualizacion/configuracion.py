from pathlib import Path
import sys


# ============================================================
# Datos de GitHub
# ============================================================

USUARIO_GITHUB = "rodger526"
REPOSITORIO_GITHUB = "agropecuaria"

URL_API_ULTIMA_VERSION = (
    f"https://api.github.com/repos/"
    f"{USUARIO_GITHUB}/{REPOSITORIO_GITHUB}/releases/latest"
)


# ============================================================
# Nombre de la aplicación
# ============================================================

NOMBRE_APLICACION = "Sistema planificacion"
NOMBRE_EJECUTABLE = "Sistema planificacion.exe"


# ============================================================
# Rutas de la aplicación
# ============================================================

def obtener_directorio_aplicacion():
    """
    Devuelve la carpeta donde se encuentra el programa.

    Cuando se ejecuta como código Python:
        devuelve la raíz del proyecto.

    Cuando se ejecuta como archivo .exe:
        devuelve la carpeta donde está el ejecutable.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


DIRECTORIO_APLICACION = obtener_directorio_aplicacion()

RUTA_VERSION = DIRECTORIO_APLICACION / "version.txt"

RUTA_EJECUTABLE = DIRECTORIO_APLICACION / NOMBRE_EJECUTABLE

RUTA_ACTUALIZACION_TEMPORAL = (
    DIRECTORIO_APLICACION / "actualizacion_temporal.exe"
)

RUTA_ACTUALIZADOR = (
    DIRECTORIO_APLICACION / "Actualizador.exe"
)


# ============================================================
# Configuración de conexión
# ============================================================

TIEMPO_ESPERA_CONEXION = 10
TIEMPO_ESPERA_DESCARGA = 60


# ============================================================
# Configuración de versión
# ============================================================

VERSION_POR_DEFECTO = "1.0.0"