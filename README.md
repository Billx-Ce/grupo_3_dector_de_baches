# Detector de Baches y Fisuras en Pavimento

Aplicación web desarrollada con Flask y YOLO para la detección de daños en pavimento a partir de imágenes y videos, con soporte adicional para la creación de datasets en formato YOLO.

## Descripción

Este proyecto fue creado para apoyar tareas de inspección visual de pavimento, permitiendo detectar automáticamente fisuras o baches, según el modelo cargado, y generar anotaciones para futuros entrenamientos.

La aplicación ofrece dos funciones principales:

- Detección automática sobre imágenes y videos.
- Construcción de datasets etiquetados en formato YOLO.

## Características

- Interfaz web simple para cargar imágenes y videos.
- Procesamiento automático con modelos YOLO entrenados.
- Generación de resultados visuales con cajas de detección.
- Guardado de anotaciones manuales para `train`, `val` y `test`.
- Exportación del dataset completo en archivo `.zip`.

## Modelos incluidos

El proyecto incluye dos pesos entrenados:

- `exp-2.pt`: modelo orientado a la detección de `crack` (fisuras o grietas).
- `exp.pt`: modelo orientado a la detección de `Pothole` (baches).

## Estado actual del sistema

Actualmente la aplicación no ejecuta ambos modelos al mismo tiempo. En `app.py` solo se carga un modelo por defecto:

```python
model = YOLO("exp-2.pt")
```

En la práctica, esto significa lo siguiente:

- Si se sube una imagen o video, el sistema usa `exp-2.pt`.
- La detección actual queda enfocada en fisuras o grietas.
- El modelo `exp.pt` permanece disponible en el proyecto, pero no se usa automáticamente.

Si deseas trabajar con baches en lugar de fisuras, debes cambiar manualmente la carga del modelo en `app.py`:

```python
model = YOLO("exp.pt")
```

## Flujo de funcionamiento

### Detección automática

La ruta `/detectar` recibe un archivo desde la interfaz y ejecuta inferencia con YOLO.

- Para imágenes, la aplicación guarda temporalmente el archivo en `static/uploads/`, ejecuta el modelo y genera una imagen anotada en `static/resultados/`.
- Para videos, el sistema procesa cada frame y genera un video final con las detecciones dibujadas.
- El nivel de confianza puede ajustarse desde la interfaz.

### Creación de dataset

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

## Instalación

### Windows

1. Clona o copia el proyecto en tu equipo.
2. Abre una terminal en la carpeta raíz.
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

6. Asegúrate de tener en la raíz del proyecto el modelo que deseas usar.
7. Ejecuta la aplicación:

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

### Ejecutar detección

1. Abre la aplicación en el navegador.
2. Carga una imagen o video de pavimento.
3. Ajusta el nivel de confianza si lo necesitas.
4. Ejecuta la detección y revisa el resultado generado.

### Crear dataset

1. Abre la pestaña de creación de dataset.
2. Sube una imagen.
3. Dibuja las cajas manualmente.
4. Asigna la clase correspondiente.
5. Guarda la anotación en `train`, `val` o `test`.

## Cómo cambiar entre modelos

Busca en `app.py` esta línea:

```python
model = YOLO("exp-2.pt")
```

Puedes reemplazarla por:

```python
model = YOLO("exp.pt")
```

Referencia rápida:

- `exp-2.pt`: detección de fisuras.
- `exp.pt`: detección de baches.

## Control de archivos en Git

El proyecto incluye un `.gitignore` para evitar subir:

- Modelos entrenados como `*.pt`, `*.pth` y `*.onnx`.
- Archivos temporales generados en `static/uploads/`.
- Resultados procesados en `static/resultados/`.

Esto permite mantener limpio el repositorio y versionar solo el código y el dataset útil para futuros entrenamientos.

## Consideraciones

- El límite de carga actual es de `300 MB`.
- La aplicación crea y utiliza automáticamente las carpetas necesarias para uploads, resultados y dataset.
- Si los archivos `.pt` no están presentes en la raíz del proyecto, la detección no podrá ejecutarse.

## Mejoras recomendadas

- Permitir seleccionar el modelo desde la interfaz.
- Ejecutar ambos modelos y fusionar resultados.
- Entrenar un solo modelo multiclase para baches y fisuras.
- Incorporar métricas, historial de inferencias o evaluación del modelo.

## Autores

- Billy Cabrera
- Alexander Ramirez
- Anderlin Malpartida
- Lenin Sabino
- Richard Meza

Proyecto orientado al análisis de pavimento mediante visión por computadora y entrenamiento de modelos YOLO para detección de daños superficiales.
