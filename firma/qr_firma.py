import os
import socket

import qrcode


# ============================================================
# Rutas
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CARPETA_QRS = os.path.join(
    BASE_DIR,
    "qrs",
)

os.makedirs(
    CARPETA_QRS,
    exist_ok=True,
)


# ============================================================
# IP local
# ============================================================

def obtener_ip_red():
    """
    Obtiene la IP local real del equipo.

    Evita devolver 127.0.0.1 para que el teléfono pueda abrir
    el servidor Flask desde la misma red Wi-Fi.
    """

    socket_red = None

    try:
        socket_red = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        socket_red.connect(
            (
                "8.8.8.8",
                80,
            )
        )

        ip = socket_red.getsockname()[0]

        return ip

    except Exception:
        try:
            return socket.gethostbyname(
                socket.gethostname()
            )

        except Exception:
            return "127.0.0.1"

    finally:
        if socket_red:
            try:
                socket_red.close()
            except Exception:
                pass


# ============================================================
# Generador general
# ============================================================

def generar_qr_url(
    url,
    nombre_archivo,
):
    """
    Genera un QR para una URL y lo guarda dentro de firma/qrs.

    Devuelve:
        {
            "url": "...",
            "ruta_qr": "..."
        }
    """

    url = str(
        url or ""
    ).strip()

    nombre_archivo = str(
        nombre_archivo or ""
    ).strip()

    if not url:
        raise ValueError(
            "La URL del código QR está vacía."
        )

    if not nombre_archivo:
        raise ValueError(
            "El nombre del archivo QR está vacío."
        )

    if not nombre_archivo.lower().endswith(
        ".png"
    ):
        nombre_archivo += ".png"

    ruta_qr = os.path.join(
        CARPETA_QRS,
        nombre_archivo,
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(
        url
    )

    qr.make(
        fit=True
    )

    imagen = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    imagen.save(
        ruta_qr
    )

    return {
        "url": url,
        "ruta_qr": ruta_qr,
    }


# ============================================================
# Planificación
# ============================================================

def generar_qr_docente():
    """
    Genera el QR para la firma del docente de planificación.
    """

    ip = obtener_ip_red()

    url = (
        f"http://{ip}:5000/"
        "firma/docente"
    )

    return generar_qr_url(
        url,
        "qr_docente.png",
    )


def generar_qr_comision():
    """
    Genera el QR para la firma de la comisión.
    """

    ip = obtener_ip_red()

    url = (
        f"http://{ip}:5000/"
        "firma/comision"
    )

    return generar_qr_url(
        url,
        "qr_comision.png",
    )


# ============================================================
# Laboratorio
# ============================================================

def generar_qr_docente_laboratorio():
    """
    Genera el QR para la firma del docente responsable
    del registro de laboratorio.
    """

    ip = obtener_ip_red()

    url = (
        f"http://{ip}:5000/"
        "firma/docente_laboratorio"
    )

    return generar_qr_url(
        url,
        "qr_docente_laboratorio.png",
    )


def generar_qr_encargado_laboratorio():
    """
    Genera el QR para la firma del encargado
    del laboratorio.
    """

    ip = obtener_ip_red()

    url = (
        f"http://{ip}:5000/"
        "firma/encargado_laboratorio"
    )

    return generar_qr_url(
        url,
        "qr_encargado_laboratorio.png",
    )


# ============================================================
# Estudiantes
# ============================================================

def generar_qr_estudiante(
    codigo_sesion,
):
    """
    Genera el QR para una sesión de firmas de estudiantes.
    """

    codigo_sesion = str(
        codigo_sesion or ""
    ).strip()

    if not codigo_sesion:
        raise ValueError(
            "El código de sesión no puede estar vacío."
        )

    ip = obtener_ip_red()

    url = (
        f"http://{ip}:5000/"
        f"firma/estudiante/{codigo_sesion}"
    )

    nombre_archivo = (
        f"qr_estudiante_{codigo_sesion}.png"
    )

    return generar_qr_url(
        url,
        nombre_archivo,
    )


# ============================================================
# Compatibilidad con código anterior
# ============================================================

def generar_qr():
    """
    Mantiene compatibilidad con código anterior.

    Genera un QR que apunta a la raíz del servidor.
    """

    ip = obtener_ip_red()

    url = f"http://{ip}:5000"

    return generar_qr_url(
        url,
        "qr_firma.png",
    )


# ============================================================
# Prueba manual
# ============================================================

if __name__ == "__main__":
    resultados = [
        generar_qr_docente(),
        generar_qr_comision(),
        generar_qr_docente_laboratorio(),
        generar_qr_encargado_laboratorio(),
    ]

    for resultado in resultados:
        print(
            "\nQR generado"
        )
        print(
            "URL:",
            resultado["url"],
        )
        print(
            "Archivo:",
            resultado["ruta_qr"],
        )