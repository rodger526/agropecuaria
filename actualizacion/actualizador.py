import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def esperar_cierre_archivo(ruta, tiempo_maximo=30):
    """
    Espera hasta que el ejecutable deje de estar bloqueado.
    """
    inicio = time.time()

    while time.time() - inicio < tiempo_maximo:
        try:
            with open(ruta, "ab"):
                return True
        except PermissionError:
            time.sleep(1)

    return False


def reemplazar_ejecutable(ejecutable_actual, ejecutable_nuevo):
    if not esperar_cierre_archivo(ejecutable_actual):
        print("No fue posible actualizar.")
        return False

    try:

        if os.path.exists(ejecutable_actual):
            os.remove(ejecutable_actual)

        shutil.move(ejecutable_nuevo, ejecutable_actual)

        return True

    except Exception as e:
        print(e)
        return False


def actualizar_version(version_file, nueva_version):

    Path(version_file).write_text(
        nueva_version,
        encoding="utf-8"
    )


def iniciar_programa(ejecutable):

    subprocess.Popen(
        [ejecutable],
        shell=False
    )


def main():

    if len(sys.argv) != 5:
        print("Uso incorrecto.")
        return

    ejecutable_actual = sys.argv[1]
    ejecutable_nuevo = sys.argv[2]
    archivo_version = sys.argv[3]
    nueva_version = sys.argv[4]

    correcto = reemplazar_ejecutable(
        ejecutable_actual,
        ejecutable_nuevo
    )

    if not correcto:
        return

    actualizar_version(
        archivo_version,
        nueva_version
    )

    iniciar_programa(ejecutable_actual)


if __name__ == "__main__":
    main()