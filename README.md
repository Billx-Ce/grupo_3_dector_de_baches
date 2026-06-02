# Detector de Baches y Fisuras en Pavimento

Aplicacion web desarrollada con Flask y YOLO para la deteccion de danos en pavimento a partir de imagenes y videos, con soporte adicional para la creacion de datasets en formato YOLO.

## Descripcion

Este proyecto fue creado para apoyar tareas de inspeccion visual de pavimento, permitiendo detectar automaticamente fisuras o baches, segun el modelo cargado, y generar anotaciones para futuros entrenamientos.

La aplicacion ofrece dos funciones principales:

- Deteccion automatica sobre imagenes y videos.
- Construccion de datasets etiquetados en formato YOLO.

## Caracteristicas

- Interfaz web simple para cargar imagenes y videos.
- Procesamiento automatico con modelos YOLO entrenados.
- Generacion de resultados visuales con cajas de deteccion.
- Guardado de anotaciones manuales para `train`, `val` y `test`.
- Exportacion del dataset completo en archivo `.zip`.

## Modelos incluidos

El proyecto incluye dos pesos entrenados:

- `exp-2.pt`: modelo orientado a la deteccion de `crack` (fisuras o grietas).
- `exp.pt`: modelo orientado a la deteccion de `Pothole` (baches).

## Estado actual del sistema

Actualmente la aplicacion no ejecuta ambos modelos al mismo tiempo. En `app.py` solo se carga un modelo por defecto:

```python
model = YOLO("exp-2.pt")
```

En la practica, esto significa lo siguiente:

- Si se sube una imagen o video, el sistema usa `exp-2.pt`.
- La deteccion actual queda enfocada en fisuras o grietas.
- El modelo `exp.pt` permanece disponible en el proyecto, pero no se usa automaticamente.

Si deseas trabajar con baches en lugar de fisuras, debes cambiar manualmente la carga del modelo en `app.py`:

```python
model = YOLO("exp.pt")
```

## Flujo de funcionamiento

### Deteccion automatica

La ruta `/detectar` recibe un archivo desde la interfaz y ejecuta inferencia con YOLO.

- Para imagenes, la aplicacion guarda temporalmente el archivo en `static/uploads/`, ejecuta el modelo y genera una imagen anotada en `static/resultados/`.
- Para videos, el sistema procesa cada frame y genera un video final con las detecciones dibujadas.
- El nivel de confianza puede ajustarse desde la interfaz.

### Creacion de dataset

La ruta `/guardar_dataset` permite almacenar anotaciones manuales en formato YOLO para construir un nuevo conjunto de entrenamiento.

La estructura usada es la siguiente:

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

Las clases configuradas para el dataset son:

- `0: crack`
- `1: pothole`

Esto permite preparar un dataset propio con ambas clases para entrenar, en una siguiente etapa, un modelo unificado.

### Descarga del dataset

La ruta `/descargar_dataset_zip` comprime la carpeta `dataset/` y permite descargarla como archivo `.zip`.

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

## Instalacion

### Windows

1. Clona o copia el proyecto en tu equipo.
2. Abre una terminal en la carpeta raiz.
3. Crea un entorno virtual:

```powershell
python -m venv .venv
```

4. Activa el entorno:

```powershell
.venv\Scripts\Activate.ps1
```

5. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

6. Asegurate de tener en la raiz del proyecto el modelo que deseas usar.
7. Ejecuta la aplicacion:

```powershell
python app.py
```

8. Abre el navegador en:

```text
http://127.0.0.1:5000
```

### Linux o macOS

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

## Uso

### Ejecutar deteccion

1. Abre la aplicacion en el navegador.
2. Carga una imagen o video de pavimento.
3. Ajusta el nivel de confianza si lo necesitas.
4. Ejecuta la deteccion y revisa el resultado generado.

### Crear dataset

1. Abre la pestana de creacion de dataset.
2. Sube una imagen.
3. Dibuja las cajas manualmente.
4. Asigna la clase correspondiente.
5. Guarda la anotacion en `train`, `val` o `test`.

## Como cambiar entre modelos

Busca en `app.py` esta linea:

```python
model = YOLO("exp-2.pt")
```

Puedes reemplazarla por:

```python
model = YOLO("exp.pt")
```

Referencia rapida:

- `exp-2.pt`: deteccion de fisuras.
- `exp.pt`: deteccion de baches.

## Control de archivos en Git

El proyecto incluye un `.gitignore` para evitar subir:

- Modelos entrenados como `*.pt`, `*.pth` y `*.onnx`.
- Archivos temporales generados en `static/uploads/`.
- Resultados procesados en `static/resultados/`.

Esto permite mantener limpio el repositorio y versionar solo el codigo y el dataset util para futuros entrenamientos.

## Consideraciones

- El limite de carga actual es de `300 MB`.
- La aplicacion crea y utiliza automaticamente las carpetas necesarias para uploads, resultados y dataset.
- Si los archivos `.pt` no estan presentes en la raiz del proyecto, la deteccion no podra ejecutarse.

## Mejoras recomendadas

- Permitir seleccionar el modelo desde la interfaz.
- Ejecutar ambos modelos y fusionar resultados.
- Entrenar un solo modelo multiclase para baches y fisuras.
- Incorporar metricas, historial de inferencias o evaluacion del modelo.

## Autor

Proyecto orientado al analisis de pavimento mediante vision por computadora y entrenamiento de modelos YOLO para deteccion de danos superficiales.
