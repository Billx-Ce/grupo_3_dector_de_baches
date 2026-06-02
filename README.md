# MI Detector

Aplicacion web en Flask para detectar danos en pavimento con YOLO y para crear un dataset en formato YOLO a partir de anotaciones manuales.

El proyecto permite:

- Subir imagenes o videos para ejecutar deteccion.
- Dibujar cajas manualmente y guardar etiquetas YOLO.
- Organizar el dataset en `train`, `val` y `test`.
- Descargar el dataset generado en un archivo `.zip`.

## Modelos incluidos

En la carpeta raiz hay dos pesos de YOLO:

- `exp-2.pt`: modelo entrenado para detectar `crack` (fisuras o grietas).
- `exp.pt`: modelo entrenado para detectar `Pothole` (baches).

Importante:

Actualmente la aplicacion no usa ambos modelos al mismo tiempo. En el codigo solo se carga uno:

```python
model = YOLO("exp-2.pt")
```

Eso significa que en el estado actual:

- Si subes una imagen o video, se usa `exp-2.pt`.
- Las detecciones estan orientadas a fisuras/grietas.
- `exp.pt` queda como modelo alternativo, pero no entra automaticamente en el flujo.

Si quieres usar el modelo de baches, debes cambiar esa linea en `app.py` por:

```python
model = YOLO("exp.pt")
```

Si en el futuro quieres detectar ambas clases al mismo tiempo, hay tres caminos:

1. Entrenar un solo modelo con ambas clases.
2. Agregar un selector en la interfaz para elegir el modelo.
3. Ejecutar los dos modelos y combinar resultados.

## Como funciona

### 1. Deteccion automatica

La ruta `/detectar` recibe una imagen o video desde la interfaz web.

- Si el archivo es imagen (`.jpg`, `.jpeg`, `.png`, `.webp`), el sistema guarda temporalmente el archivo en `static/uploads/`, ejecuta YOLO y genera una imagen con cajas en `static/resultados/`.
- Si el archivo es video (`.mp4`, `.avi`, `.mov`, `.mkv`), procesa frame por frame y genera un video anotado en `static/resultados/`.
- La confianza se puede ajustar desde la interfaz.

### 2. Creacion de dataset YOLO

La ruta `/guardar_dataset` permite subir una imagen y guardar anotaciones manuales en formato YOLO.

El proyecto organiza el dataset asi:

```text
dataset/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  data.yaml
```

Las clases definidas en el proyecto para el dataset son:

- `0: crack`
- `1: pothole`

Esto sirve para construir un dataset nuevo y luego entrenar un modelo que detecte ambas clases en una sola red.

### 3. Descarga del dataset

La ruta `/descargar_dataset_zip` comprime la carpeta `dataset/` y la descarga como un `.zip`.

## Estructura del proyecto

```text
mi_detector/
  app.py
  requirements.txt
  exp-2.pt
  exp.pt
  templates/
    index.html
  static/
    uploads/
    resultados/
  dataset/
    images/
    labels/
    data.yaml
```

## Requisitos

- Python 3.10 o superior
- `pip`

Dependencias principales:

- Flask
- Ultralytics
- OpenCV
- NumPy
- Werkzeug

## Instalacion en otra maquina

### Opcion 1: Windows

1. Instala Python 3.10 o superior.
2. Clona o copia este proyecto en tu equipo.
3. Abre una terminal dentro de la carpeta del proyecto.
4. Crea un entorno virtual:

```powershell
python -m venv .venv
```

5. Activalo:

```powershell
.venv\Scripts\Activate.ps1
```

6. Instala dependencias:

```powershell
pip install -r requirements.txt
```

7. Ejecuta la app:

```powershell
python app.py
```

8. Abre en el navegador:

```text
http://127.0.0.1:5000
```

### Opcion 2: Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Luego abre:

```text
http://127.0.0.1:5000
```

## Como cambiar de modelo

Edita `app.py` y busca esta linea:

```python
model = YOLO("exp-2.pt")
```

Puedes cambiarla por:

```python
model = YOLO("exp.pt")
```

Resumen rapido:

- `exp-2.pt` para grietas o fisuras.
- `exp.pt` para baches.

## Archivos que no se suben a Git

El proyecto incluye un `.gitignore` para evitar subir:

- Modelos entrenados (`*.pt`, `*.pth`, `*.onnx`)
- Archivos temporales subidos por usuarios
- Resultados generados por la app

## Notas

- El limite de subida actual es de `300 MB`.
- Las carpetas `static/uploads/` y `static/resultados/` se crean y usan automaticamente.
- Si faltan los modelos `.pt`, la app no podra ejecutar deteccion hasta que vuelvas a copiarlos a la raiz del proyecto.

## Posibles mejoras

- Seleccionar el modelo desde la interfaz.
- Cargar ambos modelos y combinar resultados.
- Entrenar un solo modelo multiclase para `crack` y `pothole`.
- Agregar una pagina de metricas o historial de inferencias.
