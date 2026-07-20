import requests
from packaging.version import Version, InvalidVersion

from actualizacion.configuracion import (
    URL_API_ULTIMA_VERSION,
    RUTA_VERSION,
    TIEMPO_ESPERA_CONEXION,
    VERSION_POR_DEFECTO
)


def obtener_version_local():
    try:
        if RUTA_VERSION.exists():
            return RUTA_VERSION.read_text(encoding="utf-8").strip()
    except Exception:
        pass

    return VERSION_POR_DEFECTO


def obtener_release_github():
    respuesta = requests.get(
        URL_API_ULTIMA_VERSION,
        timeout=TIEMPO_ESPERA_CONEXION,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "SistemaPlanificacion"
        }
    )

    respuesta.raise_for_status()

    return respuesta.json()


def obtener_version_remota():
    datos = obtener_release_github()

    version = datos.get("tag_name", "").replace("v", "").strip()

    return version, datos


def hay_actualizacion():
    try:

        version_local = obtener_version_local()

        version_remota, datos = obtener_version_remota()

        if Version(version_remota) > Version(version_local):
            return True, version_local, version_remota, datos

        return False, version_local, version_remota, datos

    except (InvalidVersion, Exception):
        return False, obtener_version_local(), None, None


if __name__ == "__main__":

    actualizar, local, remota, datos = hay_actualizacion()

    print("Versión instalada :", local)
    print("Versión GitHub     :", remota)
    print("¿Actualizar?       :", actualizar)