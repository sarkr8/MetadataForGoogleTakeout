import os
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime

CARPETA_ORIGEN = Path("C:\Proyecto_metadatos\FOTOS")  # <-- cámbialo
CARPETA_DESTINO = CARPETA_ORIGEN / "con_metadatos"
CARPETA_DESTINO.mkdir(exist_ok=True)

EXTENSIONES_IMAGENES = [".jpg", ".jpeg", ".png", ".heic"]
EXTENSIONES_VIDEOS = [".mp4", ".mov", ".avi", ".mkv"]
EXTENSIONES_VALIDAS = EXTENSIONES_IMAGENES + EXTENSIONES_VIDEOS

def obtener_fecha(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        # Intentar obtener fecha para fotos
        if "photoTakenTime" in datos:
            timestamp = int(datos.get("photoTakenTime", {}).get("timestamp", 0))
            return datetime.fromtimestamp(timestamp)
        # Intentar obtener fecha para videos
        elif "videoTakenTime" in datos:
            timestamp = int(datos.get("videoTakenTime", {}).get("timestamp", 0))
            return datetime.fromtimestamp(timestamp)
        # Alternativa para otros formatos
        elif "creationTime" in datos:
            timestamp = int(datos.get("creationTime", {}).get("timestamp", 0))
            return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"Error al leer fecha de {json_path}: {e}")
        return None

def generar_nombre_unico(base_name, extension, carpeta):
    nombre_final = f"{base_name}{extension}"
    contador = 1
    while (carpeta / nombre_final).exists():
        nombre_final = f"{base_name}_{contador:02d}{extension}"
        contador += 1
    return nombre_final

def procesar_archivos(origen: Path, destino: Path):
    for archivo_json in origen.glob("*.json"):
        nombre_base = archivo_json.stem
        archivo_multimedia = None

        # Buscar archivo multimedia correspondiente
        for ext in EXTENSIONES_VALIDAS:
            posible = origen / f"{nombre_base}{ext}"
            if posible.exists():
                archivo_multimedia = posible
                break

        if not archivo_multimedia:
            continue

        fecha = obtener_fecha(archivo_json)
        if not fecha:
            continue

        # Determinar prefijo según tipo de archivo
        if archivo_multimedia.suffix.lower() in EXTENSIONES_IMAGENES:
            prefijo = "IMG"
        else:
            prefijo = "VID"

        base_nombre = f"{prefijo}_{fecha.strftime('%Y%m%d_%H%M%S')}"
        extension = archivo_multimedia.suffix.lower()
        nombre_unico = generar_nombre_unico(base_nombre, extension, destino)
        ruta_destino = destino / nombre_unico

        # Copiar archivo al destino
        shutil.copy2(archivo_multimedia, ruta_destino)

        # Procesar metadatos con exiftool
        comando = [
            "exiftool",
            f"-json={archivo_json}",
            str(ruta_destino)
        ]

        try:
            subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Procesado: {nombre_unico}")
        except subprocess.CalledProcessError as e:
            print(f"Error al procesar metadatos de {nombre_unico}: {e}")
            # Eliminar archivo si falló el procesamiento de metadatos
            try:
                ruta_destino.unlink()
            except OSError:
                pass

if __name__ == "__main__":
    procesar_archivos(CARPETA_ORIGEN, CARPETA_DESTINO)
