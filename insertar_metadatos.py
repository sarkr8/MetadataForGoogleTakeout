import os
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime

CARPETA_ORIGEN = Path("ruta/a/TuCarpetaFotos")  # <-- cámbialo
CARPETA_DESTINO = CARPETA_ORIGEN / "con_metadatos"
CARPETA_DESTINO.mkdir(exist_ok=True)

EXTENSIONES_VALIDAS = [".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov"]

def obtener_fecha(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        timestamp = int(datos.get("photoTakenTime", {}).get("timestamp", 0))
        return datetime.fromtimestamp(timestamp)
    except:
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

        base_nombre = f"IMG_{fecha.strftime('%Y%m%d_%H%M%S')}"
        extension = archivo_multimedia.suffix.lower()
        nombre_unico = generar_nombre_unico(base_nombre, extension, destino)
        ruta_destino = destino / nombre_unico

        shutil.copy2(archivo_multimedia, ruta_destino)

        comando = [
            "exiftool",
            f"-json={archivo_json}",
            str(ruta_destino)
        ]

        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Procesado: {nombre_unico}")

if __name__ == "__main__":
    procesar_archivos(CARPETA_ORIGEN, CARPETA_DESTINO)
