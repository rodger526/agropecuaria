import socket
import qrcode
import os

os.makedirs("firma/qrs", exist_ok=True)


def _obtener_ip_red() -> str:
    """Devuelve la IP de red local (no 127.0.0.1)."""
    try:
        # Truco: conectar a una IP pública sin enviar datos → el SO elige la interfaz correcta
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


def generar_qr_docente() -> str:
    ip  = _obtener_ip_red()
    url = f"http://{ip}:5000/firma/docente"
    qr  = qrcode.make(url)
    qr.save("firma/qrs/qr_docente.png")
    return url


def generar_qr_comision() -> str:
    ip  = _obtener_ip_red()
    url = f"http://{ip}:5000/firma/comision"
    qr  = qrcode.make(url)
    qr.save("firma/qrs/qr_comision.png")
    return url


def generar_qr() -> str:
    """Compatibilidad con código anterior — devuelve URL base."""
    ip  = _obtener_ip_red()
    url = f"http://{ip}:5000"
    qr  = qrcode.make(url)
    qr.save("firma/qr_firma.png")
    return url