from flask import Flask, render_template, request, jsonify, send_file
from ultralytics import YOLO
from pathlib import Path
from werkzeug.utils import secure_filename
import cv2
import uuid
import json
import zipfile
import tempfile
import time

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # límite 300 MB

# =========================================================
# CARPETAS DEL SISTEMA
# =========================================================
UPLOAD_FOLDER = Path("static/uploads")
RESULTADO_FOLDER = Path("static/resultados")

# Dataset profesional fuera de static
DATASET_ROOT = Path("dataset")
DATASET_IMAGES = DATASET_ROOT / "images"
DATASET_LABELS = DATASET_ROOT / "labels"
DATASET_YAML = DATASET_ROOT / "data.yaml"

SPLITS_VALIDOS = ["train", "val", "test"]

CLASES = {
    0: "crack",
    1: "pothole",
}

EXTENSIONES_IMAGEN = [".jpg", ".jpeg", ".png", ".webp"]
EXTENSIONES_VIDEO = [".mp4", ".avi", ".mov", ".mkv"]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def crear_carpetas():
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    RESULTADO_FOLDER.mkdir(parents=True, exist_ok=True)

    for split in SPLITS_VALIDOS:
        (DATASET_IMAGES / split).mkdir(parents=True, exist_ok=True)
        (DATASET_LABELS / split).mkdir(parents=True, exist_ok=True)


def escribir_data_yaml():
    """
    Genera el archivo dataset/data.yaml para entrenamiento YOLO.
    Comando recomendado:
    yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=50 imgsz=640
    """
    contenido = """path: dataset
train: images/train
val: images/val
test: images/test

names:
  0: crack
  1: pothole
"""
    DATASET_YAML.write_text(contenido, encoding="utf-8")


def nombre_unico(nombre_original):
    nombre_seguro = secure_filename(nombre_original)
    extension = Path(nombre_seguro).suffix.lower()
    identificador = uuid.uuid4().hex[:12]
    return f"{identificador}{extension}"


def contar_archivos_dataset():
    stats = {}

    for split in SPLITS_VALIDOS:
        total_imagenes = 0

        for ext in EXTENSIONES_IMAGEN:
            total_imagenes += len(list((DATASET_IMAGES / split).glob(f"*{ext}")))

        total_labels = len(list((DATASET_LABELS / split).glob("*.txt")))

        stats[split] = {
            "imagenes": total_imagenes,
            "labels": total_labels,
        }

    return stats


crear_carpetas()
escribir_data_yaml()

# =========================================================
# CARGA DEL MODELO
# =========================================================
model = YOLO("exp-2.pt")


# =========================================================
# RUTA PRINCIPAL
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# DETECCIÓN AUTOMÁTICA CON YOLO
# =========================================================
@app.route("/detectar", methods=["POST"])
def detectar():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify({"error": "No se recibió archivo"}), 400

    try:
        confianza = float(request.form.get("confianza", 0.5))
    except ValueError:
        return jsonify({"error": "La confianza debe ser numérica"}), 400

    ext = Path(archivo.filename).suffix.lower()
    nombre_id = uuid.uuid4().hex[:8]

    # ---------------- IMAGEN ----------------
    if ext in EXTENSIONES_IMAGEN:
        ruta_entrada = UPLOAD_FOLDER / f"{nombre_id}{ext}"
        archivo.save(ruta_entrada)

        results = model.predict(str(ruta_entrada), conf=confianza)
        r = results[0]

        print(f"Total detecciones: {len(r.boxes)}")
        for box in r.boxes:
            print(f"Clase: {r.names[int(box.cls)]} | Confianza: {float(box.conf):.2f}")

        imagen_con_detecciones = r.plot()
        ruta_salida = RESULTADO_FOLDER / f"resultado_{nombre_id}.jpg"
        cv2.imwrite(str(ruta_salida), imagen_con_detecciones)

        detecciones = []
        for box in r.boxes:
            detecciones.append({
                "clase": r.names[int(box.cls)],
                "confianza": round(float(box.conf) * 100, 1)
            })

        return jsonify({
            "tipo": "imagen",
            "resultado": f"/static/resultados/resultado_{nombre_id}.jpg",
            "detecciones": detecciones,
            "total": len(detecciones)
        })

    # ---------------- VIDEO ----------------
    if ext in EXTENSIONES_VIDEO:
        ruta_entrada = UPLOAD_FOLDER / f"{nombre_id}{ext}"
        archivo.save(ruta_entrada)

        cap = cv2.VideoCapture(str(ruta_entrada))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if w == 0 or h == 0:
            cap.release()
            return jsonify({"error": "No se pudo leer el video"}), 400

        ruta_salida = RESULTADO_FOLDER / f"resultado_{nombre_id}.mp4"
        out = cv2.VideoWriter(
            str(ruta_salida),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (w, h)
        )

        total_det = 0

        while cap.isOpened():
            ok, frame = cap.read()

            if not ok:
                break

            r = model.predict(frame, conf=confianza, verbose=False)[0]
            total_det += len(r.boxes)
            out.write(r.plot())

        cap.release()
        out.release()

        return jsonify({
            "tipo": "video",
            "resultado": f"/static/resultados/resultado_{nombre_id}.mp4",
            "total": total_det
        })

    return jsonify({"error": "Formato no soportado"}), 400


# =========================================================
# GUARDAR DATASET EN FORMATO YOLO
# =========================================================
@app.route("/guardar_dataset", methods=["POST"])
def guardar_dataset():
    archivo = request.files.get("archivo")
    split = request.form.get("split", "train")
    anotaciones_json = request.form.get("anotaciones")

    if not archivo:
        return jsonify({"error": "No se recibió imagen"}), 400

    if split not in SPLITS_VALIDOS:
        return jsonify({"error": "División inválida. Usa train, val o test"}), 400

    if not anotaciones_json:
        return jsonify({"error": "No se recibieron anotaciones"}), 400

    ext = Path(archivo.filename).suffix.lower()

    if ext not in EXTENSIONES_IMAGEN:
        return jsonify({"error": "Formato inválido. Usa JPG, JPEG, PNG o WEBP"}), 400

    try:
        anotaciones = json.loads(anotaciones_json)
    except json.JSONDecodeError:
        return jsonify({"error": "Las anotaciones no tienen formato JSON válido"}), 400

    if not isinstance(anotaciones, list) or len(anotaciones) == 0:
        return jsonify({"error": "Debes dibujar al menos una caja"}), 400

    lineas_yolo = []

    for ann in anotaciones:
        try:
            clase = int(ann["clase"])
            x_center = float(ann["x_center"])
            y_center = float(ann["y_center"])
            width = float(ann["width"])
            height = float(ann["height"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Una anotación tiene campos inválidos"}), 400

        if clase not in CLASES:
            return jsonify({"error": f"Clase inválida: {clase}"}), 400

        valores = [x_center, y_center, width, height]

        if not all(0 <= valor <= 1 for valor in valores):
            return jsonify({"error": "Las coordenadas YOLO deben estar entre 0 y 1"}), 400

        if width <= 0 or height <= 0:
            return jsonify({"error": "El ancho y alto de la caja deben ser mayores a 0"}), 400

        lineas_yolo.append(
            f"{clase} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        )

    nombre_imagen = nombre_unico(archivo.filename)
    nombre_base = Path(nombre_imagen).stem
    nombre_label = f"{nombre_base}.txt"

    ruta_imagen = DATASET_IMAGES / split / nombre_imagen
    ruta_label = DATASET_LABELS / split / nombre_label

    archivo.save(ruta_imagen)
    ruta_label.write_text("\n".join(lineas_yolo), encoding="utf-8")

    escribir_data_yaml()

    return jsonify({
        "mensaje": "Dataset guardado correctamente",
        "split": split,
        "imagen_guardada": str(ruta_imagen).replace("\\", "/"),
        "label_guardado": str(ruta_label).replace("\\", "/"),
        "txt": "\n".join(lineas_yolo),
        "total_anotaciones": len(lineas_yolo),
        "estadisticas": contar_archivos_dataset()
    })


@app.route("/estadisticas_dataset", methods=["GET"])
def estadisticas_dataset():
    return jsonify({
        "estadisticas": contar_archivos_dataset()
    })


@app.route("/descargar_dataset_zip", methods=["GET"])
def descargar_dataset_zip():
    """
    Comprime todo el dataset profesional:
    dataset/images/...
    dataset/labels/...
    dataset/data.yaml
    """
    escribir_data_yaml()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_path = Path(tempfile.gettempdir()) / f"dataset_yolo_{timestamp}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for archivo in DATASET_ROOT.rglob("*"):
            if archivo.is_file():
                zipf.write(archivo, archivo.relative_to(DATASET_ROOT.parent))

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=f"dataset_yolo_{timestamp}.zip",
        mimetype="application/zip"
    )


# =========================================================
# EJECUCIÓN LOCAL
# =========================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
