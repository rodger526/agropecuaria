from flask import Flask, request, render_template, jsonify, redirect
import base64
import os
import json
import uuid
from datetime import datetime

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
)

PASTA_FIRMAS    = "firma/firmas"
PASTA_ESTUD     = "firma/firmas/estudiantes"   # PNGs de firma por estudiante
PASTA_SESIONES  = "firma/sesiones"             # JSON con la lista de estudiantes firmados por sesión

os.makedirs(PASTA_FIRMAS, exist_ok=True)
os.makedirs(PASTA_ESTUD, exist_ok=True)
os.makedirs(PASTA_SESIONES, exist_ok=True)


def _ruta_sesion(codigo_sesion):
    return os.path.join(PASTA_SESIONES, f"{codigo_sesion}.json")


def _leer_sesion(codigo_sesion):
    ruta = _ruta_sesion(codigo_sesion)
    if not os.path.exists(ruta):
        return {"estudiantes": []}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_sesion(codigo_sesion, datos):
    with open(_ruta_sesion(codigo_sesion), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ─── Raíz ──────────────────────────────────────────────────────────────
@app.route("/")
def inicio():
    return redirect("/firma/docente")


# ─── Firmas de práctica de campo (docente / comisión) ───────────────────
@app.route("/firma/docente")
def firma_docente():
    return render_template("firma.html", rol="docente", titulo="Firma del Docente")


@app.route("/firma/comision")
def firma_comision():
    return render_template("firma.html", rol="comision", titulo="Firma de la Comisión")


@app.route("/guardar_firma", methods=["POST"])
def guardar_firma():
    datos = request.json.get("firma", "")
    rol   = request.json.get("rol", "docente")

    if "," not in datos:
        return jsonify({"ok": False, "error": "Datos inválidos"}), 400

    _, imagen = datos.split(",", 1)
    imagen_bytes = base64.b64decode(imagen)

    nombre = "firma_docente.png" if rol == "docente" else "firma_comision.png"
    ruta   = os.path.join(PASTA_FIRMAS, nombre)

    with open(ruta, "wb") as f:
        f.write(imagen_bytes)

    return jsonify({"ok": True})


@app.route("/estado")
def estado():
    return jsonify({
        "docente":  os.path.exists(os.path.join(PASTA_FIRMAS, "firma_docente.png")),
        "comision": os.path.exists(os.path.join(PASTA_FIRMAS, "firma_comision.png")),
    })


# ─── Firmas de estudiantes (laboratorio) ────────────────────────────────

@app.route("/firma/estudiante/<codigo_sesion>")
def firma_estudiante(codigo_sesion):
    return render_template(
        "firma_estudiante.html",
        codigo_sesion=codigo_sesion,
    )


@app.route("/guardar_firma_estudiante", methods=["POST"])
def guardar_firma_estudiante():
    data = request.json or {}

    codigo_sesion = data.get("codigo_sesion", "").strip()
    nombre        = data.get("nombre", "").strip()
    cedula        = data.get("cedula", "").strip()
    firma_b64     = data.get("firma", "")

    if not codigo_sesion:
        return jsonify({"ok": False, "error": "Sesión inválida"}), 400
    if not nombre or not cedula:
        return jsonify({"ok": False, "error": "Nombre y cédula son obligatorios"}), 400
    if "," not in firma_b64:
        return jsonify({"ok": False, "error": "Firma inválida"}), 400

    # Validación simple de cédula ecuatoriana: 10 dígitos numéricos
    if not (cedula.isdigit() and len(cedula) == 10):
        return jsonify({"ok": False, "error": "La cédula debe tener 10 dígitos"}), 400

    sesion = _leer_sesion(codigo_sesion)

    # Nota: no se valida cédula duplicada a propósito. Esta sesión se usa
    # para tomar asistencia diaria en distintas materias, por lo que la
    # misma persona puede (y debe poder) firmar varias veces.

    # Guardar imagen de firma
    _, imagen = firma_b64.split(",", 1)
    imagen_bytes = base64.b64decode(imagen)

    nombre_archivo = f"{codigo_sesion}_{cedula}_{uuid.uuid4().hex[:6]}.png"
    ruta_firma = os.path.join(PASTA_ESTUD, nombre_archivo)

    with open(ruta_firma, "wb") as f:
        f.write(imagen_bytes)

    sesion["estudiantes"].append({
        "nombre": nombre,
        "cedula": cedula,
        "firma_ruta": ruta_firma,
        "hora": datetime.now().strftime("%H:%M:%S"),
    })
    _guardar_sesion(codigo_sesion, sesion)

    return jsonify({"ok": True, "total": len(sesion["estudiantes"])})


@app.route("/estado_sesion/<codigo_sesion>")
def estado_sesion(codigo_sesion):
    sesion = _leer_sesion(codigo_sesion)
    return jsonify({
        "total": len(sesion["estudiantes"]),
        "estudiantes": [
            {"nombre": e["nombre"], "cedula": e["cedula"]}
            for e in sesion["estudiantes"]
        ],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)