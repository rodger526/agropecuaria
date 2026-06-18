from flask import Flask, request, render_template, jsonify, redirect
import base64
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
)

PASTA_FIRMAS = "firma/firmas"
os.makedirs(PASTA_FIRMAS, exist_ok=True)

# ─── Raíz → redirige a docente por defecto ───────────────────────────
@app.route("/")
def inicio():
    return redirect("/firma/docente")

# ─── Páginas de firma ─────────────────────────────────────────────────
@app.route("/firma/docente")
def firma_docente():
    return render_template("firma.html", rol="docente", titulo="Firma del Docente")

@app.route("/firma/comision")
def firma_comision():
    return render_template("firma.html", rol="comision", titulo="Firma de la Comisión")

# ─── Guardar firma ────────────────────────────────────────────────────
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

# ─── Estado para polling ──────────────────────────────────────────────
@app.route("/estado")
def estado():
    return jsonify({
        "docente":  os.path.exists(os.path.join(PASTA_FIRMAS, "firma_docente.png")),
        "comision": os.path.exists(os.path.join(PASTA_FIRMAS, "firma_comision.png")),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)