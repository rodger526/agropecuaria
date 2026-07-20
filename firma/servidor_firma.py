import base64
import json
import os
import re
import shutil
import threading
import uuid

from datetime import datetime

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
)

from utils.rutas_app import ruta_datos


# ============================================================
# CONFIGURACIÓN DE FLASK
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
# CARPETAS TEMPORALES
# ============================================================

CARPETA_DATOS_FIRMA = ruta_datos(
    "firmas_temporales"
)

CARPETA_FIRMAS_RESPONSABLES = os.path.join(
    CARPETA_DATOS_FIRMA,
    "responsables",
)

CARPETA_FIRMAS_ESTUDIANTES = os.path.join(
    CARPETA_DATOS_FIRMA,
    "estudiantes",
)

CARPETA_SESIONES = os.path.join(
    CARPETA_DATOS_FIRMA,
    "sesiones",
)


os.makedirs(
    CARPETA_FIRMAS_RESPONSABLES,
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
# ROLES DE FIRMA PERMITIDOS
# ============================================================

ROLES_FIRMA = {
    "docente": {
        "archivo": "firma_docente.png",
        "titulo": "Firma del Docente Responsable",
    },
    "comision": {
        "archivo": "firma_comision.png",
        "titulo": "Firma de la Comisión Académica",
    },
    "docente_laboratorio": {
        "archivo": "firma_docente_laboratorio.png",
        "titulo": "Firma del Docente Responsable",
    },
    "encargado_laboratorio": {
        "archivo": "firma_encargado_laboratorio.png",
        "titulo": "Firma del Encargado del Laboratorio",
    },
}


# Sesión usada únicamente para conservar compatibilidad
# con formularios antiguos que todavía no envían código de sesión.
SESION_GENERAL = "general"

# Protege la lectura/escritura del JSON cuando varios estudiantes
# firman al mismo tiempo.
_LOCK_SESIONES = threading.RLock()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def _normalizar_codigo_sesion(codigo_sesion):
    """
    Limpia y valida un código de sesión.

    Solo permite:
        - letras
        - números
        - guiones
        - guiones bajos

    Si no se proporciona código, devuelve 'general' para conservar
    compatibilidad con las rutas antiguas.
    """

    codigo = str(
        codigo_sesion or ""
    ).strip()

    if not codigo:
        return SESION_GENERAL

    codigo = re.sub(
        r"[^A-Za-z0-9_-]",
        "",
        codigo,
    )

    if not codigo:
        return SESION_GENERAL

    return codigo[:100]


def _crear_codigo_sesion():
    """
    Genera un identificador único para una nueva sesión de firmas.
    """

    return uuid.uuid4().hex


def _carpeta_sesion_responsables(codigo_sesion):
    """
    Devuelve la carpeta temporal de firmas responsables
    correspondiente a una sesión.
    """

    codigo = _normalizar_codigo_sesion(
        codigo_sesion
    )

    carpeta = os.path.join(
        CARPETA_FIRMAS_RESPONSABLES,
        codigo,
    )

    os.makedirs(
        carpeta,
        exist_ok=True,
    )

    return carpeta


def _ruta_firma_rol(
    rol,
    codigo_sesion=None,
):
    """
    Devuelve la ruta absoluta de una firma responsable.

    Cada sesión utiliza su propia carpeta para evitar que las firmas
    de dos formularios diferentes se mezclen.
    """

    configuracion = ROLES_FIRMA.get(
        rol
    )

    if not configuracion:
        return None

    carpeta = _carpeta_sesion_responsables(
        codigo_sesion
    )

    return os.path.join(
        carpeta,
        configuracion["archivo"],
    )


def _ruta_sesion_estudiantes(
    codigo_sesion,
):
    """
    Devuelve la ruta del archivo JSON de estudiantes
    perteneciente a una sesión.
    """

    codigo = _normalizar_codigo_sesion(
        codigo_sesion
    )

    return os.path.join(
        CARPETA_SESIONES,
        f"{codigo}.json",
    )


def _leer_sesion_estudiantes(
    codigo_sesion,
):
    """
    Lee la información de estudiantes de una sesión.

    Si todavía no existe, devuelve una estructura vacía.
    """

    ruta = _ruta_sesion_estudiantes(
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

        estudiantes = datos.get(
            "estudiantes"
        )

        if not isinstance(
            estudiantes,
            list,
        ):
            datos["estudiantes"] = []

        return datos

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {
            "estudiantes": [],
        }


def _guardar_sesion_estudiantes(
    codigo_sesion,
    datos,
):
    """
    Guarda los estudiantes registrados en una sesión.
    """

    ruta = _ruta_sesion_estudiantes(
        codigo_sesion
    )

    ruta_temporal = f"{ruta}.tmp"

    with _LOCK_SESIONES:
        with open(
            ruta_temporal,
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=2,
            )

        os.replace(
            ruta_temporal,
            ruta,
        )




def obtener_ruta_sesion_estudiantes(codigo_sesion):
    """
    Devuelve la ruta absoluta del JSON de estudiantes de una sesión.

    Se expone para que las ventanas de escritorio utilicen exactamente
    la misma carpeta que el servidor Flask.
    """

    return _ruta_sesion_estudiantes(codigo_sesion)


def obtener_estudiantes_sesion(codigo_sesion):
    """
    Devuelve una copia de la lista de estudiantes registrados.
    """

    with _LOCK_SESIONES:
        datos = _leer_sesion_estudiantes(codigo_sesion)
        return [
            dict(estudiante)
            for estudiante in datos.get("estudiantes", [])
            if isinstance(estudiante, dict)
        ]


def _decodificar_imagen_base64(
    contenido,
):
    """
    Convierte una imagen Base64 enviada por el navegador
    en bytes.

    Formato esperado:

        data:image/png;base64,AAAA...
    """

    contenido = str(
        contenido or ""
    ).strip()

    if not contenido:
        raise ValueError(
            "No se recibió ninguna firma."
        )

    if "," not in contenido:
        raise ValueError(
            "La firma enviada no contiene datos válidos."
        )

    encabezado, datos_base64 = contenido.split(
        ",",
        1,
    )

    if not encabezado.lower().startswith(
        "data:image/"
    ):
        raise ValueError(
            "El contenido recibido no corresponde a una imagen."
        )

    try:
        imagen = base64.b64decode(
            datos_base64,
            validate=True,
        )

    except Exception as error:
        raise ValueError(
            "No fue posible decodificar la firma."
        ) from error

    if not imagen:
        raise ValueError(
            "La firma recibida está vacía."
        )

    # Evita que se reciban archivos excesivamente grandes.
    limite_bytes = 5 * 1024 * 1024

    if len(imagen) > limite_bytes:
        raise ValueError(
            "La firma supera el tamaño máximo permitido."
        )

    return imagen


def _eliminar_archivo(ruta):
    """
    Elimina un archivo sin generar error cuando no existe.
    """

    if not ruta:
        return

    try:
        if os.path.isfile(
            ruta
        ):
            os.remove(
                ruta
            )

    except OSError as error:
        print(
            f"No se pudo eliminar el archivo temporal "
            f"{ruta}: {error}"
        )


def _eliminar_carpeta_vacia(ruta):
    """
    Elimina una carpeta únicamente si está vacía.
    """

    if not ruta:
        return

    try:
        if (
            os.path.isdir(ruta)
            and not os.listdir(ruta)
        ):
            os.rmdir(
                ruta
            )

    except OSError:
        pass


def obtener_ruta_firma(
    rol,
    codigo_sesion=None,
):
    """
    Función pública para obtener una firma temporal desde otros módulos.

    Devuelve:
        Ruta absoluta, si la firma existe.
        None, si la firma todavía no existe.

    Ejemplo:

        ruta = obtener_ruta_firma(
            "docente",
            codigo_sesion,
        )
    """

    if rol not in ROLES_FIRMA:
        return None

    ruta = _ruta_firma_rol(
        rol,
        codigo_sesion,
    )

    if os.path.isfile(
        ruta
    ):
        return ruta

    return None


def eliminar_firmas_sesion(
    codigo_sesion,
    incluir_estudiantes=False,
):
    """
    Elimina todos los archivos temporales asociados a una sesión.

    Esta función debe ejecutarse después de:

        1. Generar correctamente el PDF.
        2. Subir correctamente el PDF a Supabase.
        3. Guardar correctamente la URL del PDF en PostgreSQL.

    Parámetros:
        codigo_sesion:
            Código único utilizado por el formulario.

        incluir_estudiantes:
            Si es True, también elimina firmas y JSON
            de estudiantes.
    """

    codigo = _normalizar_codigo_sesion(
        codigo_sesion
    )

    carpeta_responsables = os.path.join(
        CARPETA_FIRMAS_RESPONSABLES,
        codigo,
    )

    if os.path.isdir(
        carpeta_responsables
    ):
        try:
            shutil.rmtree(
                carpeta_responsables
            )

        except OSError as error:
            print(
                "No se pudo eliminar la carpeta temporal "
                f"de responsables: {error}"
            )

    if incluir_estudiantes:
        sesion = _leer_sesion_estudiantes(
            codigo
        )

        for estudiante in sesion.get(
            "estudiantes",
            [],
        ):
            _eliminar_archivo(
                estudiante.get(
                    "firma_ruta"
                )
            )

        _eliminar_archivo(
            _ruta_sesion_estudiantes(
                codigo
            )
        )

        carpeta_estudiantes = os.path.join(
            CARPETA_FIRMAS_ESTUDIANTES,
            codigo,
        )

        if os.path.isdir(carpeta_estudiantes):
            try:
                shutil.rmtree(carpeta_estudiantes)
            except OSError as error:
                print(
                    "No se pudo eliminar la carpeta temporal "
                    f"de estudiantes: {error}"
                )

    return True


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.route("/")
def inicio():
    """
    Redirige a la firma del docente responsable.
    """

    codigo_sesion = request.args.get(
        "sesion",
        SESION_GENERAL,
    )

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion
    )

    return redirect(
        f"/firma/docente?sesion={codigo_sesion}"
    )


# ============================================================
# CREAR SESIÓN
# ============================================================

@app.route(
    "/crear_sesion",
    methods=["GET", "POST"],
)
def crear_sesion():
    """
    Genera un código único para una nueva sesión de firmas.
    """

    codigo_sesion = _crear_codigo_sesion()

    _carpeta_sesion_responsables(
        codigo_sesion
    )

    return jsonify(
        {
            "ok": True,
            "codigo_sesion": codigo_sesion,
        }
    )


# ============================================================
# FORMULARIOS DE FIRMAS RESPONSABLES
# ============================================================

def _mostrar_formulario_firma(
    rol,
):
    """
    Renderiza el formulario correspondiente a un rol.
    """

    configuracion = ROLES_FIRMA.get(
        rol
    )

    if not configuracion:
        return (
            "Rol de firma no válido.",
            404,
        )

    codigo_sesion = _normalizar_codigo_sesion(
        request.args.get(
            "sesion",
            SESION_GENERAL,
        )
    )

    return render_template(
        "firma.html",
        rol=rol,
        titulo=configuracion["titulo"],
        codigo_sesion=codigo_sesion,
    )


@app.route("/firma/docente")
def firma_docente():
    """
    Firma del docente responsable de planificación.
    """

    return _mostrar_formulario_firma(
        "docente"
    )


@app.route("/firma/comision")
def firma_comision():
    """
    Firma de la comisión académica.
    """

    return _mostrar_formulario_firma(
        "comision"
    )


@app.route("/firma/docente_laboratorio")
def firma_docente_laboratorio():
    """
    Firma del docente responsable del registro de laboratorio.
    """

    return _mostrar_formulario_firma(
        "docente_laboratorio"
    )


@app.route("/firma/encargado_laboratorio")
def firma_encargado_laboratorio():
    """
    Firma del encargado o técnico responsable del laboratorio.
    """

    return _mostrar_formulario_firma(
        "encargado_laboratorio"
    )


# ============================================================
# GUARDAR FIRMA DE RESPONSABLE
# ============================================================

@app.route(
    "/guardar_firma",
    methods=["POST"],
)
def guardar_firma():
    """
    Guarda temporalmente una firma de planificación
    o laboratorio.

    Datos JSON esperados:

        {
            "firma": "data:image/png;base64,...",
            "rol": "docente",
            "codigo_sesion": "..."
        }

    Para conservar compatibilidad, también acepta:

        "sesion": "..."
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

    codigo_sesion = datos_json.get(
        "codigo_sesion"
    )

    if not codigo_sesion:
        codigo_sesion = datos_json.get(
            "sesion"
        )

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion
    )

    if rol not in ROLES_FIRMA:
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
            rol,
            codigo_sesion,
        )

        if not ruta:
            return jsonify(
                {
                    "ok": False,
                    "error": (
                        "No se pudo determinar la ruta "
                        "temporal de la firma."
                    ),
                }
            ), 400

        # Reemplaza una firma previa del mismo rol
        # dentro de la misma sesión.
        _eliminar_archivo(
            ruta
        )

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
                "codigo_sesion": codigo_sesion,
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
# ESTADO DE LAS FIRMAS
# ============================================================

@app.route("/estado")
def estado():
    """
    Devuelve el estado de todas las firmas responsables
    pertenecientes a una sesión.

    Ejemplo:

        /estado?sesion=ABC123
    """

    codigo_sesion = _normalizar_codigo_sesion(
        request.args.get(
            "sesion",
            SESION_GENERAL,
        )
    )

    resultado = {
        "ok": True,
        "codigo_sesion": codigo_sesion,
        "firmas": {},
    }

    for rol in ROLES_FIRMA:
        ruta = _ruta_firma_rol(
            rol,
            codigo_sesion,
        )

        resultado["firmas"][rol] = bool(
            ruta
            and os.path.isfile(
                ruta
            )
        )

        # También conserva las claves antiguas en el nivel principal.
        resultado[rol] = resultado["firmas"][rol]

    return jsonify(
        resultado
    )


@app.route("/estado/<rol>")
def estado_por_rol(
    rol,
):
    """
    Devuelve el estado de una firma específica.

    Ejemplo:

        /estado/docente?sesion=ABC123
    """

    if rol not in ROLES_FIRMA:
        return jsonify(
            {
                "ok": False,
                "error": "Rol no válido.",
            }
        ), 404

    codigo_sesion = _normalizar_codigo_sesion(
        request.args.get(
            "sesion",
            SESION_GENERAL,
        )
    )

    ruta = _ruta_firma_rol(
        rol,
        codigo_sesion,
    )

    return jsonify(
        {
            "ok": True,
            "rol": rol,
            "codigo_sesion": codigo_sesion,
            "firmado": bool(
                ruta
                and os.path.isfile(
                    ruta
                )
            ),
        }
    )


# ============================================================
# ELIMINAR FIRMA ESPECÍFICA
# ============================================================

@app.route(
    "/eliminar_firma/<rol>",
    methods=["POST"],
)
def eliminar_firma(
    rol,
):
    """
    Elimina una firma responsable específica.

    Puede recibir la sesión mediante:

        JSON:
            {"codigo_sesion": "..."}

        Query:
            ?sesion=...
    """

    if rol not in ROLES_FIRMA:
        return jsonify(
            {
                "ok": False,
                "error": "Rol no válido.",
            }
        ), 404

    datos_json = request.get_json(
        silent=True
    ) or {}

    codigo_sesion = (
        datos_json.get(
            "codigo_sesion"
        )
        or datos_json.get(
            "sesion"
        )
        or request.args.get(
            "sesion"
        )
        or SESION_GENERAL
    )

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion
    )

    ruta = _ruta_firma_rol(
        rol,
        codigo_sesion,
    )

    try:
        _eliminar_archivo(
            ruta
        )

        carpeta = os.path.dirname(
            ruta
        )

        _eliminar_carpeta_vacia(
            carpeta
        )

        return jsonify(
            {
                "ok": True,
                "rol": rol,
                "codigo_sesion": codigo_sesion,
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
# ELIMINAR TODAS LAS FIRMAS DE UNA SESIÓN
# ============================================================

@app.route(
    "/eliminar_sesion/<codigo_sesion>",
    methods=["POST"],
)
def eliminar_sesion(
    codigo_sesion,
):
    """
    Elimina todos los archivos temporales relacionados
    con una sesión.
    """

    datos_json = request.get_json(
        silent=True
    ) or {}

    incluir_estudiantes = bool(
        datos_json.get(
            "incluir_estudiantes",
            False,
        )
    )

    try:
        eliminar_firmas_sesion(
            codigo_sesion,
            incluir_estudiantes=incluir_estudiantes,
        )

        return jsonify(
            {
                "ok": True,
                "codigo_sesion": _normalizar_codigo_sesion(
                    codigo_sesion
                ),
            }
        )

    except Exception as error:
        print(
            f"Error eliminando sesión: {error}"
        )

        return jsonify(
            {
                "ok": False,
                "error": (
                    "No fue posible eliminar los archivos "
                    "temporales de la sesión."
                ),
            }
        ), 500


# ============================================================
# FIRMA DE ESTUDIANTES
# ============================================================

@app.route(
    "/firma/estudiante/<codigo_sesion>"
)
def firma_estudiante(
    codigo_sesion,
):
    """
    Muestra el formulario para que un estudiante ingrese
    nombre, cédula y firma.
    """

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion
    )

    if codigo_sesion == SESION_GENERAL:
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
    Guarda temporalmente la firma de un estudiante
    y la agrega al archivo JSON de su sesión.
    """

    datos_json = request.get_json(
        silent=True
    ) or {}

    codigo_sesion_original = str(
        datos_json.get(
            "codigo_sesion",
            "",
        )
    ).strip()

    if not codigo_sesion_original:
        return jsonify(
            {
                "ok": False,
                "error": "La sesión no es válida.",
            }
        ), 400

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion_original
    )

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

    if not nombre:
        return jsonify(
            {
                "ok": False,
                "error": "El nombre es obligatorio.",
            }
        ), 400

    if len(nombre) > 200:
        return jsonify(
            {
                "ok": False,
                "error": (
                    "El nombre supera la longitud permitida."
                ),
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
                "error": (
                    "La cédula debe contener exactamente "
                    "10 dígitos."
                ),
            }
        ), 400

    try:
        imagen_bytes = _decodificar_imagen_base64(
            firma_base64
        )

        with _LOCK_SESIONES:
            sesion = _leer_sesion_estudiantes(
                codigo_sesion
            )

            estudiantes = sesion.get(
                "estudiantes",
                [],
            )

            # Evita registrar dos veces la misma cédula
            # dentro de una misma sesión.
            for estudiante in estudiantes:
                if str(
                    estudiante.get(
                        "cedula",
                        ""
                    )
                ).strip() == cedula:
                    return jsonify(
                        {
                            "ok": False,
                            "error": (
                                "Esta cédula ya fue registrada "
                                "en la sesión."
                            ),
                        }
                    ), 409

        carpeta_estudiantes_sesion = os.path.join(
            CARPETA_FIRMAS_ESTUDIANTES,
            codigo_sesion,
        )

        os.makedirs(
            carpeta_estudiantes_sesion,
            exist_ok=True,
        )

        nombre_archivo = (
            f"{cedula}_"
            f"{uuid.uuid4().hex[:8]}.png"
        )

        ruta_firma = os.path.join(
            carpeta_estudiantes_sesion,
            nombre_archivo,
        )

        with open(
            ruta_firma,
            "wb",
        ) as archivo:
            archivo.write(
                imagen_bytes
            )

        with _LOCK_SESIONES:
            # Se vuelve a leer para no perder firmas que hayan llegado
            # mientras se escribía la imagen.
            sesion = _leer_sesion_estudiantes(
                codigo_sesion
            )
            estudiantes = sesion.get(
                "estudiantes",
                [],
            )

            for estudiante in estudiantes:
                if str(
                    estudiante.get("cedula", "")
                ).strip() == cedula:
                    _eliminar_archivo(ruta_firma)
                    return jsonify(
                        {
                            "ok": False,
                            "error": (
                                "Esta cédula ya fue registrada "
                                "en la sesión."
                            ),
                        }
                    ), 409

            estudiantes.append(
                {
                    "nombre": nombre,
                    "cedula": cedula,
                    "firma_ruta": ruta_firma,
                    "hora": datetime.now().strftime(
                        "%H:%M:%S"
                    ),
                    "fecha": datetime.now().strftime(
                        "%d/%m/%Y"
                    ),
                }
            )

            sesion["estudiantes"] = estudiantes

            _guardar_sesion_estudiantes(
                codigo_sesion,
                sesion,
            )

        return jsonify(
            {
                "ok": True,
                "codigo_sesion": codigo_sesion,
                "total": len(
                    estudiantes
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
    registrados en una sesión.
    """

    codigo_sesion = _normalizar_codigo_sesion(
        codigo_sesion
    )

    if codigo_sesion == SESION_GENERAL:
        return jsonify(
            {
                "ok": False,
                "error": "Sesión inválida.",
            }
        ), 400

    sesion = _leer_sesion_estudiantes(
        codigo_sesion
    )

    estudiantes = sesion.get(
        "estudiantes",
        [],
    )

    return jsonify(
        {
            "ok": True,
            "codigo_sesion": codigo_sesion,
            "total": len(
                estudiantes
            ),
            "estudiantes": [
                {
                    "nombre": estudiante.get(
                        "nombre",
                        "",
                    ),
                    "cedula": estudiante.get(
                        "cedula",
                        "",
                    ),
                    "hora": estudiante.get(
                        "hora",
                        "",
                    ),
                    "fecha": estudiante.get(
                        "fecha",
                        "",
                    ),
                }
                for estudiante in estudiantes
            ],
        }
    )


# ============================================================
# EJECUTAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True,
    )