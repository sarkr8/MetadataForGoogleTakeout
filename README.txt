===================================
RESTAURADOR DE METADATOS DE FOTOS GOOGLE TAKEOUT
===================================

Autor: Hiram Martínez Tumalan  
Fecha: 2025  
Requiere: Python 3.8+, exiftool

NOTA: Este repositorio contiene una versiom de exitool para windows 64 bits. 
en caso de que tus sitema operativo sea linux o mac os debes buscarlo desde la pagina de https://exiftool.org/
-----------------------------------
1. ESTRUCTURA INICIAL ESPERADA
-----------------------------------

Coloca tus archivos de Google Takeout así:

  TuCarpetaFotos/
  ├── IMG_1234.jpg
  ├── IMG_1234.jpg.json
  ├── IMG_1235.jpg
  ├── IMG_1235.jpg.json
  └── ...

-----------------------------------
2. INSTALACIÓN DE DEPENDENCIAS
-----------------------------------

Solo necesitas Vscode, Python y exiftool:

- **Windows**
  - Descarga exiftool de https://exiftool.org/
  - Renombra a "exiftool.exe" y agrégalo al PATH del sistema

- **MacOS**
  - brew install exiftool

- **Linux**
  - sudo apt install libimage-exiftool-perl

-----------------------------------
3. SCRIPT 1: insertar_metadatos.py
-----------------------------------

Este script hace lo siguiente:
  ✓ Lee los archivos .json
  ✓ Incrusta los metadatos originales (fecha, ubicación, etc.)
  ✓ Renombra la foto como: IMG_YYYYMMDD_HHMMSS.jpg
  ✓ Evita duplicados con sufijos tipo _01, _02
  ✓ Copia todo lo que tenga metadatos a: con_metadatos/
  ✓ Copia todo lo que no tenga metadatos a: sin_metadatos/
  ✓ hace un reporte final

USO:
  python insertar_metadatos.py

-----------------------------------
4. SCRIPT 2: mover_duplicados.py
-----------------------------------

Este script:
  ✓ Detecta duplicados por hash
  ✓ Compara metadatos (fecha + si los tiene)
  ✓ Conserva la mejor versión (con más metadatos y más antigua)
  ✓ Mueve los duplicados a: revisar_duplicados/

USO:
  python mover_duplicados.py

-----------------------------------
5. ORGANIZACIÓN FINAL
-----------------------------------

Después de ejecutar ambos scripts:

  TuCarpetaFotos/
  ├── con_metadatos/         <- Fotos limpias, con metadatos, renombradas
  ├── revisar_duplicados/    <- Copias duplicadas no necesarias
  ├── insertar_metadatos.py
  ├── mover_duplicados.py
  └── README.txt

-----------------------------------
6. NOTAS
-----------------------------------

- El script nunca modifica los archivos originales.
- Se recomienda revisar la carpeta revisar_duplicados/ antes de borrarla.
- Puedes adaptar los scripts si tienes archivos en otros formatos o carpetas.

