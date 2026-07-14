import base64
import json
import os
import uuid

from datetime import datetime

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
)


# ============================================================
# Configuración de Flask
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

app = Flask(
    __name__,
    template_folder=os.path.join(
        BASE_DIR,
        "templates",
    ),
)


# ============================================================
# Rutas de almacenamiento
# ============================================================

CARPETA_FIRMAS = os.path.join(
    BASE_DIR,
    "firmas",
)

CARPETA_FIRMAS_ESTUDIANTES = os.path.join(
    CARPETA_FIRMAS,
    "estudiantes",
)

CARPETA_SESIONES = os.path.join(
    BASE_DIR,
    "sesiones",
)


os.makedirs(
    CARPETA_FIRMAS,
    exist_ok=True,
)

os.makedirs(
    CARPETA_FIRMAS_ESTUDIANTES,
    exist_ok=True,
)

os.makedirs(
    CARPETA_SESIONES,
    exist_ok=True,
)


# ============================================================
# Archivos de firma
# ============================================================

ARCHIVOS_FIRMA = {
    # Planificación de prácticas
    "docente": "firma_docente.png",
    "comision": "firma_comision.png",

    # Registro de laboratorio
    "docente_laboratorio": "firma_docente_laboratorio.png",
    "encargado_laboratorio": "firma_encargado_laboratorio.png",
}


# ============================================================
# Funciones auxiliares
# ============================================================

def _ruta_sesion(codigo_sesion):
    """
    Devuelve la ruta del archivo JSON de una sesión.
    """

    codigo_sesion = str(
        codigo_sesion or ""
    ).strip()

    return os.path.join(
        CARPETA_SESIONES,
        f"{codigo_sesion}.json",
    )


def _leer_sesion(codigo_sesion):
    """
    Lee los estudiantes registrados en una sesión.

    Si la sesión aún no existe, devuelve una estructura vacía.
    """

    ruta = _ruta_sesion(
        codigo_sesion
    )

    if not os.path.isfile(
        ruta
    ):
        return {
            "estudiantes": [],
        }

    try:
        with open(
            ruta,
            "r",
            encoding="utf-8",
        ) as archivo:
            datos = json.load(
                archivo
            )

        if not isinstance(
            datos,
            dict,
        ):
            return {
                "estudiantes": [],
            }

        if "estudiantes" not in datos:
            datos["estudiantes"] = []

        return datos

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {
            "estudiantes": [],
        }


def _guardar_sesion(
    codigo_sesion,
    datos,
):
    """
    Guarda la información de una sesión en un archivo JSON.
    """

    ruta = _ruta_sesion(
        codigo_sesion
    )

    with open(
        ruta,
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=2,
        )


def _decodificar_imagen_base64(
    contenido,
):
    """
    Convierte una imagen Base64 recibida desde el navegador
    en bytes.

    El valor esperado tiene este formato:

        data:image/png;base64,AAAA...
    """

    contenido = str(
        contenido or ""
    ).strip()

    if "," not in contenido:
        raise ValueError(
            "La firma enviada no contiene datos válidos."
        )

    _encabezado, datos_base64 = contenido.split(
        ",",
        1,
    )

    try:
        return base64.b64decode(
            datos_base64
        )

    except Exception as error:
        raise ValueError(
            "No fue posible decodificar la firma."
        ) from error


def _ruta_firma_rol(
    rol,
):
    """
    Devuelve la ruta absoluta de la firma correspondiente
    al rol indicado.
    """

    nombre_archivo = ARCHIVOS_FIRMA.get(
        rol
    )

    if not nombre_archivo:
        return None

    return os.path.join(
        CARPETA_FIRMAS,
        nombre_archivo,
    )


# ============================================================
# Página inicial
# ============================================================

@app.route("/")
def inicio():
    """
    Redirige por defecto a la firma del docente
    de planificación.
    """

    return redirect(
        "/firma/docente"
    )


# ============================================================
# Firmas de planificación
# ============================================================

@app.route("/firma/docente")
def firma_docente():
    """
    Firma del docente responsable de la planificación.
    """

    return render_template(
        "firma.html",
        rol="docente",
        titulo="Firma del Docente Responsable",
    )


@app.route("/firma/comision")
def firma_comision():
    """
    Firma de la comisión académica.
    """

    return render_template(
        "firma.html",
        rol="comision",
        titulo="Firma de la Comisión Académica",
    )


# ============================================================
# Firmas del registro de laboratorio
# ============================================================

@app.route("/firma/docente_laboratorio")
def firma_docente_laboratorio():
    """
    Firma del docente responsable del registro
    de laboratorio.
    """

    return render_template(
        "firma.html",
        rol="docente_laboratorio",
        titulo="Firma del Docente Responsable",
    )


@app.route("/firma/encargado_laboratorio")
def firma_encargado_laboratorio():
    """
    Firma del encargado o técnico responsable
    del laboratorio.
    """

    return render_template(
        "firma.html",
        rol="encargado_laboratorio",
        titulo="Firma del Encargado del Laboratorio",
    )


# ============================================================
# Guardar firmas de responsables
# ============================================================

@app.route(
    "/guardar_firma",
    methods=["POST"],
)
def guardar_firma():
    """
    Guarda una firma de planificación o laboratorio.

    Roles permitidos:
        docente
        comision
        docente_laboratorio
        encargado_laboratorio
    """

    datos_json = request.get_json(
        silent=True
    ) or {}

    firma_base64 = datos_json.get(
        "firma",
        "",
    )

    rol = str(
        datos_json.get(
            "rol",
            "",
        )
    ).strip()

    if rol not in ARCHIVOS_FIRMA:
        return jsonify(
            {
                "ok": False,
                "error": "El rol de firma no es válido.",
            }
        ), 400

    try:
        imagen_bytes = _decodificar_imagen_base64(
            firma_base64
        )

        ruta = _ruta_firma_rol(
            rol
        )

        if not ruta:
            return jsonify(
                {
                    "ok": False,
                    "error": "No se encontró la ruta de la firma.",
                }
            ), 400

        with open(
            ruta,
            "wb",
        ) as archivo:
            archivo.write(
                imagen_bytes
            )

        return jsonify(
            {
                "ok": True,
                "rol": rol,
                "archivo": os.path.basename(
                    ruta
                ),
            }
        )

    except ValueError as error:
        return jsonify(
            {
                "ok": False,
                "error": str(error),
            }
        ), 400

    except Exception as error:
        print(
            "\n========== ERROR GUARDANDO FIRMA =========="
        )
        print(error)
        print(
            "===========================================\n"
        )

        return jsonify(
            {
                "ok": False,
                "error": "No fue posible guardar la firma.",
            }
        ), 500


# ============================================================
# Estado de firmas
# ============================================================

@app.route("/estado")
def estado():
    """
    Devuelve el estado de todas las firmas de responsables.
    """

    resultado = {}

    for rol in ARCHIVOS_FIRMA:
        ruta = _ruta_firma_rol(
            rol
        )

        resultado[rol] = bool(
            ruta
            and os.path.isfile(
                ruta
            )
        )

    return jsonify(
        resultado
    )


@app.route("/estado/<rol>")
def estado_por_rol(
    rol,
):
    """
    Devuelve el estado de una firma específica.
    """

    if rol not in ARCHIVOS_FIRMA:
        return jsonify(
            {
                "ok": False,
                "error": "Rol no válido.",
            }
        ), 404

    ruta = _ruta_firma_rol(
        rol
    )

    return jsonify(
        {
            "ok": True,
            "rol": rol,
            "firmado": bool(
                ruta
                and os.path.isfile(
                    ruta
                )
            ),
        }
    )


# ============================================================
# Eliminar una firma específica
# ============================================================

@app.route(
    "/eliminar_firma/<rol>",
    methods=["POST"],
)
def eliminar_firma(
    rol,
):
    """
    Elimina una firma concreta.

    Puede utilizarse al abrir un formulario nuevo para evitar
    reutilizar una firma anterior.
    """

    if rol not in ARCHIVOS_FIRMA:
        return jsonify(
            {
                "ok": False,
                "error": "Rol no válido.",
            }
        ), 404

    ruta = _ruta_firma_rol(
        rol
    )

    try:
        if ruta and os.path.isfile(
            ruta
        ):
            os.remove(
                ruta
            )

        return jsonify(
            {
                "ok": True,
                "rol": rol,
            }
        )

    except Exception as error:
        print(
            f"Error eliminando firma {rol}: {error}"
        )

        return jsonify(
            {
                "ok": False,
                "error": "No fue posible eliminar la firma.",
            }
        ), 500


# ============================================================
# Firmas de estudiantes
# ============================================================

@app.route(
    "/firma/estudiante/<codigo_sesion>"
)
def firma_estudiante(
    codigo_sesion,
):
    """
    Muestra el formulario para que un estudiante
    ingrese su nombre, cédula y firma.
    """

    codigo_sesion = str(
        codigo_sesion or ""
    ).strip()

    if not codigo_sesion:
        return (
            "Código de sesión inválido.",
            400,
        )

    return render_template(
        "firma_estudiante.html",
        codigo_sesion=codigo_sesion,
    )


@app.route(
    "/guardar_firma_estudiante",
    methods=["POST"],
)
def guardar_firma_estudiante():
    """
    Guarda la firma de un estudiante y la agrega
    al archivo JSON de la sesión.
    """

    datos_json = request.get_json(
        silent=True
    ) or {}

    codigo_sesion = str(
        datos_json.get(
            "codigo_sesion",
            "",
        )
    ).strip()

    nombre = str(
        datos_json.get(
            "nombre",
            "",
        )
    ).strip()

    cedula = str(
        datos_json.get(
            "cedula",
            "",
        )
    ).strip()

    firma_base64 = str(
        datos_json.get(
            "firma",
            "",
        )
    ).strip()

    if not codigo_sesion:
        return jsonify(
            {
                "ok": False,
                "error": "La sesión no es válida.",
            }
        ), 400

    if not nombre:
        return jsonify(
            {
                "ok": False,
                "error": "El nombre es obligatorio.",
            }
        ), 400

    if not cedula:
        return jsonify(
            {
                "ok": False,
                "error": "La cédula es obligatoria.",
            }
        ), 400

    if not (
        cedula.isdigit()
        and len(cedula) == 10
    ):
        return jsonify(
            {
                "ok": False,
                "error": "La cédula debe contener 10 dígitos.",
            }
        ), 400

    try:
        imagen_bytes = _decodificar_imagen_base64(
            firma_base64
        )

        sesion = _leer_sesion(
            codigo_sesion
        )

        nombre_archivo = (
            f"{codigo_sesion}_"
            f"{cedula}_"
            f"{uuid.uuid4().hex[:8]}.png"
        )

        ruta_firma = os.path.join(
            CARPETA_FIRMAS_ESTUDIANTES,
            nombre_archivo,
        )

        with open(
            ruta_firma,
            "wb",
        ) as archivo:
            archivo.write(
                imagen_bytes
            )

        sesion["estudiantes"].append(
            {
                "nombre": nombre,
                "cedula": cedula,
                "firma_ruta": ruta_firma,
                "hora": datetime.now().strftime(
                    "%H:%M:%S"
                ),
            }
        )

        _guardar_sesion(
            codigo_sesion,
            sesion,
        )

        return jsonify(
            {
                "ok": True,
                "total": len(
                    sesion["estudiantes"]
                ),
            }
        )

    except ValueError as error:
        return jsonify(
            {
                "ok": False,
                "error": str(error),
            }
        ), 400

    except Exception as error:
        print(
            "\n===== ERROR GUARDANDO FIRMA DE ESTUDIANTE ====="
        )
        print(error)
        print(
            "================================================\n"
        )

        return jsonify(
            {
                "ok": False,
                "error": (
                    "No fue posible guardar la firma "
                    "del estudiante."
                ),
            }
        ), 500


@app.route(
    "/estado_sesion/<codigo_sesion>"
)
def estado_sesion(
    codigo_sesion,
):
    """
    Devuelve la lista y el total de estudiantes
    que han firmado en una sesión.
    """

    codigo_sesion = str(
        codigo_sesion or ""
    ).strip()

    if not codigo_sesion:
        return jsonify(
            {
                "ok": False,
                "error": "Sesión inválida.",
            }
        ), 400

    sesion = _leer_sesion(
        codigo_sesion
    )

    estudiantes = sesion.get(
        "estudiantes",
        [],
    )

    return jsonify(
        {
            "ok": True,
            "total": len(
                estudiantes
            ),
            "estudiantes": [
                {
                    "nombre": estudiante.get(
                        "nombre"
                    ),
                    "cedula": estudiante.get(
                        "cedula"
                    ),
                    "hora": estudiante.get(
                        "hora"
                    ),
                }
                for estudiante in estudiantes
            ],
        }
    )


# ============================================================
# Ejecutar servidor
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
    )