import os
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

if shutil.which("exiftool") is None:
    print("Error: exiftool no está instalado o no está en el PATH.")
    exit(1)

CARPETA_ORIGEN = Path(r"C:/Proyecto_metadatos/FOTOS")
CARPETA_DESTINO = CARPETA_ORIGEN / "con_metadatos"
CARPETA_SIN_METADATOS = CARPETA_ORIGEN / "sin_metadatos"
CARPETA_DESTINO.mkdir(exist_ok=True)
CARPETA_SIN_METADATOS.mkdir(exist_ok=True)

EXTENSIONES_IMAGENES = [".jpg", ".jpeg", ".png", ".heic"]
EXTENSIONES_VIDEOS = [".mp4", ".mov", ".avi", ".mkv"]
EXTENSIONES_VALIDAS = EXTENSIONES_IMAGENES + EXTENSIONES_VIDEOS

def inicializar_contadores():
    return {
        'procesados': 0,
        'sin_metadata': 0,
        'sin_fecha': 0,
        'errores': 0
    }

def es_metadata(archivo):
    """Verifica si el archivo es un JSON válido, sin importar el nombre o extensión."""
    return es_json_valido(archivo)

def es_json_valido(archivo):
    """Intenta leer el archivo como JSON para confirmar su tipo"""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            json.load(f)
        return True
    except:
        return False

def obtener_fecha(metadata_path):
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        # Busca timestamp en campos comunes
        campos_fecha = [
            datos.get("photoTakenTime", {}).get("timestamp"),
            datos.get("videoTakenTime", {}).get("timestamp"),
            datos.get("creationTime", {}).get("timestamp"),
            datos.get("timestamp")
        ]
        for timestamp in campos_fecha:
            if timestamp:
                return datetime.fromtimestamp(int(timestamp))
        return None
    except Exception as e:
        print(f"Error al leer fecha de {metadata_path.name}: {str(e)}")
        return None

def encontrar_metadata(archivo_media, carpeta):
    """Busca un archivo JSON válido asociado al archivo multimedia."""
    nombre_base = archivo_media.stem
    posibles = []
    
    # Busca archivos con el mismo nombre base (sin extensión)
    for archivo in carpeta.iterdir():
        if archivo == archivo_media:
            continue
        
        # Coincidencia exacta o que el nombre base esté contenido en el nombre del JSON
        if (archivo.stem.startswith(nombre_base) or nombre_base.startswith(archivo.stem)) and es_metadata(archivo):
            posibles.append(archivo)
    
    # Si hay varios, elige el más corto (más probable que sea el correcto)
    if posibles:
        return min(posibles, key=lambda x: len(x.name))
    return None

def generar_nombre_unico(nombre_base, extension, destino):
    """Genera un nombre de archivo único en la carpeta destino."""
    contador = 1
    nombre = f"{nombre_base}{extension}"
    ruta = destino / nombre
    while ruta.exists():
        nombre = f"{nombre_base}_{contador}{extension}"
        ruta = destino / nombre
        contador += 1
    return nombre

def mover_a_sin_metadatos(archivo, contadores):
    """Mueve un archivo a la carpeta sin_metadatos y actualiza contadores."""
    try:
        destino = CARPETA_SIN_METADATOS / archivo.name
        shutil.move(str(archivo), str(destino))
        contadores['sin_metadata'] += 1
        print(f"Movido a sin_metadatos: {archivo.name}")
    except Exception as e:
        print(f"Error al mover {archivo.name}: {e}")
        contadores['errores'] += 1

def procesar_archivos(origen: Path, destino: Path):
    print("Iniciando procesamiento...")
    contadores = inicializar_contadores()
    
    # Primero procesamos todos los archivos multimedia
    for archivo_media in origen.iterdir():
        if archivo_media.is_dir() or archivo_media.suffix.lower() not in EXTENSIONES_VALIDAS:
            continue

        metadata = encontrar_metadata(archivo_media, origen)
        if not metadata:
            mover_a_sin_metadatos(archivo_media, contadores)
            continue

        fecha = obtener_fecha(metadata)
        if not fecha:
            print(f"Omitido (no se encontró fecha válida en metadata): {metadata.name}")
            contadores['sin_fecha'] += 1
            continue

        # Procesar archivo con metadata válida
        prefijo = "VID" if archivo_media.suffix.lower() in EXTENSIONES_VIDEOS else "IMG"
        nombre_base = f"{prefijo}_{fecha.strftime('%Y%m%d_%H%M%S')}"
        extension = archivo_media.suffix.lower()
        nombre_unico = generar_nombre_unico(nombre_base, extension, destino)
        ruta_destino = destino / nombre_unico

        try:
            shutil.copy2(archivo_media, ruta_destino)
            resultado = subprocess.run([
                "exiftool",
                "-overwrite_original",
                f"-json={metadata}",
                str(ruta_destino)
            ], capture_output=True, text=True)
            
            if resultado.returncode == 0:
                contadores['procesados'] += 1
                print(f"Procesado: {nombre_unico}")
            else:
                print(f"Error al ejecutar exiftool en {ruta_destino}: {resultado.stderr}")
                contadores['errores'] += 1
                try:
                    os.remove(ruta_destino)
                except:
                    pass
        except Exception as e:
            print(f"Error al procesar {archivo_media.name}: {e}")
            contadores['errores'] += 1

   
    
        # Reporte final
    print("\nResumen de procesamiento:")
    print(f"- Archivos procesados correctamente: {contadores['procesados']}")
    print(f"- Archivos sin metadata: {contadores['sin_metadata']} (movidos a {CARPETA_SIN_METADATOS.name})")
    print(f"- Archivos con metadata pero sin fecha válida: {contadores['sin_fecha']}")
    print(f"- Errores durante el procesamiento: {contadores['errores']}")
    
    # Mensaje de finalización condicional
    if contadores['errores'] == 0:
        print("\n¡Proceso completado exitosamente sin errores!")
    else:
        print(f"\n¡Proceso completado con {contadores['errores']} advertencias!")
    print("="*50)

if __name__ == "__main__":
    procesar_archivos(CARPETA_ORIGEN, CARPETA_DESTINO)
