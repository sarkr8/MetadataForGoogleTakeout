# Google Takeout Photo Metadata Restorer & Deduplicator

Herramienta de automatización basada en Python 3 y ExifTool diseñada para resolver la pérdida de metadatos en las exportaciones de Google Takeout. El sistema procesa los archivos JSON laterales (sidecar files), incrusta de forma nativa la información cronológica y geográfica en los archivos binarios de las imágenes, y ejecuta un pipeline de depuración de duplicados mediante análisis de hashes criptográficos.

## Características Principales

* Inyección Nativa de Metadatos: Recuperación e incrustación de fechas de captura (EXIF/IPTC) y coordenadas geográficas (GPS) mapeadas desde los esquemas JSON de Google.
* Pipeline de Deduplicación Inteligente: Identificación de archivos duplicados mediante hashing criptográfico. El algoritmo compara la densidad de metadatos y la antigüedad del archivo para preservar de forma automática la versión con mayor integridad de datos.
* Estandarización de Naming: Renombrado sistemático de archivos bajo el estándar de la industria: IMG_YYYYMMDD_HHMMSS.jpg, gestionando colisiones de nombres mediante sufijos incrementales controlados (_01, _02).
* Operación Segura e Idempotente: Procesamiento no destructivo. Los archivos originales se segregan en estructuras de directorios aisladas sin alterar las fuentes de entrada.

---

## Stack Tecnológico y Dependencias

* Lenguaje: Python 3.8+ (Librerías nativas: os, json, hashlib, shutil)
* Core Engine: ExifTool by Phil Harvey (Utilidad CLI de bajo nivel para manipulación de metadatos binarios)

### Instalación de ExifTool por Sistema Operativo

El script interactúa directamente con la interfaz de línea de comandos de ExifTool. Asegúrate de tenerlo disponible en el entorno:

* Windows (64-bits): El repositorio incluye el binario precompilado para entornos Windows. Para uso global, se sugiere renombrar a exiftool.exe y añadirlo a las Variables de Entorno (PATH) del sistema.
* macOS: Ejecutar "brew install exiftool" desde la terminal.
* Linux (Debian/Ubuntu): Ejecutar "sudo apt update && sudo apt install libimage-exiftool-perl" desde la terminal.

---

## Arquitectura de Directorios y Workflow

### 1. Estado Inicial Esperado y Requisito de Ubicación
Para que el script pueda mapear correctamente la información, es estrictamente obligatorio consolidar y colocar tanto los archivos de imagen (.jpg, .png, etc.) como sus archivos de metadatos correspondientes (.json) exactamente en la misma carpeta raíz, ubicados en el mismo nivel que los scripts de procesamiento. No deben estar en subcarpetas separadas.

Estructura requerida en el mismo directorio:

TuCarpetaFotos

├── insertar_metadatos.py     # Script de inyección de metadatos

├── mover_duplicados.py       # Script de deduplicación

├── IMG_1234.jpg             # Archivo de imagen

├── IMG_1234.jpg.json        # Archivo JSON lateral con los metadatos originales de Google

├── IMG_1235.jpg             # Archivo de imagen

└── IMG_1235.jpg.json        # Archivo JSON lateral con los metadatos originales de Google

### 2. Ejecución del Pipeline de Procesamiento

#### Paso A: Restauración y Clasificación
El primer módulo parsea los esquemas JSON, reinyecta los metadatos y realiza una segregación inicial basada en el éxito de la operación. Se ejecuta con el comando: "python insertar_metadatos.py"
* Resultados: Genera los directorios organizados /con_metadatos y /sin_metadatos, emitiendo un reporte analítico en consola al finalizar.

#### Paso B: Deduplicación Criptográfica
El segundo módulo analiza el directorio resultante para eliminar redundancias físicas de almacenamiento basándose en firmas digitales uniques. Se ejecuta con el comando: "python mover_duplicados.py"

### 3. Organización Final del Workspace
Tras completar la ejecución de los módulos, el espacio de trabajo se reestructura de la siguiente manera:

TuCarpetaFotos
├── con_metadatos/          # Archivos optimizados, con metadatos incrustados y renombrados

├── revisar_duplicados/     # Copias redundantes aisladas para auditoría manual previa al purgado

├── insertar_metadatos.py

├── mover_duplicados.py

└── README.md

---

## Consideraciones de Diseño e Ingeniería

* Integridad de Datos: Los algoritmos de movimiento de archivos operan bajo confirmación de copia previa (shutil.copy2 / shutil.move) para evitar pérdidas de información ante interrupciones del sistema (pánicos de ejecución o fallos de energía).
* Auditoría de Duplicados: La carpeta revisar_duplicados/ actúa como un búfer de seguridad. Se recomienda una inspección visual o validación de logs antes de proceder con el borrado físico definitivo de las estructuras redundantes.

---

**Desarrollado por:** Hiram Martínez  
**Contacto / Portafolio:** [Inserta tu enlace aquí]
