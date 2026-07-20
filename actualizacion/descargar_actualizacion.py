import os
import subprocess
import sys
from pathlib import Path

import requests

from .configuracion import (
    NOMBRE_EJECUTABLE,
    RUTA_ACTUALIZACION_TEMPORAL,
    RUTA_ACTUALIZADOR,
    RUTA_EJECUTABLE,
    RUTA_VERSION,
    TIEMPO_ESPERA_DESCARGA
)


def buscar_url_ejecutable(datos_release):
    """
    Busca dentro de los archivos de la Release el ejecutable
    llamado exactamente: Sistema planificacion.exe
    """

    archivos = datos_release.get("assets", [])

    for archivo in archivos:
        nombre = archivo.get("name", "").strip()

        if nombre.lower() == NOMBRE_EJECUTABLE.lower():
            return archivo.get("browser_download_url")

    return None


def descargar_archivo(url_descarga, ruta_destino):
    """
    Descarga el ejecutable nuevo desde GitHub.
    """

    ruta_destino = Path(ruta_destino)

    try:
        respuesta = requests.get(
            url_descarga,
            stream=True,
            timeout=TIEMPO_ESPERA_DESCARGA,
            headers={
                "Accept": "application/octet-stream",
                "User-Agent": "SistemaPlanificacion"
            }
        )

        respuesta.raise_for_status()

        with open(ruta_destino, "wb") as archivo_destino:
            for bloque in respuesta.iter_content(chunk_size=1024 * 1024):
                if bloque:
                    archivo_destino.write(bloque)

        return True

    except requests.RequestException as error:
        print(f"Error al descargar la actualización: {error}")

        if ruta_destino.exists():
            try:
                ruta_destino.unlink()
            except OSError:
                pass

        return False


def ejecutar_actualizador(nueva_version):
    """
    Ejecuta Actualizador.exe enviando las rutas necesarias.
    """

    if not RUTA_ACTUALIZADOR.exists():
        raise FileNotFoundError(
            f"No se encontró el actualizador en:\n{RUTA_ACTUALIZADOR}"
        )

    if not RUTA_ACTUALIZACION_TEMPORAL.exists():
        raise FileNotFoundError(
            "No se encontró el ejecutable temporal descargado."
        )

    argumentos = [
        str(RUTA_ACTUALIZADOR),
        str(RUTA_EJECUTABLE),
        str(RUTA_ACTUALIZACION_TEMPORAL),
        str(RUTA_VERSION),
        nueva_version
    ]

    subprocess.Popen(
        argumentos,
        cwd=str(RUTA_EJECUTABLE.parent),
        shell=False
    )


def descargar_e_iniciar_actualizacion(datos_release, nueva_version):
    """
    Busca el ejecutable en GitHub, lo descarga y ejecuta
    el actualizador independiente.
    """

    url_descarga = buscar_url_ejecutable(datos_release)

    if not url_descarga:
        raise FileNotFoundError(
            f"La Release no contiene el archivo:\n"
            f"{NOMBRE_EJECUTABLE}"
        )

    descargado = descargar_archivo(
        url_descarga,
        RUTA_ACTUALIZACION_TEMPORAL
    )

    if not descargado:
        return False

    ejecutar_actualizador(nueva_version)

    return True


def cerrar_aplicacion():
    """
    Cierra la aplicación principal para permitir que
    Actualizador.exe reemplace el ejecutable.
    """

    os._exit(0)