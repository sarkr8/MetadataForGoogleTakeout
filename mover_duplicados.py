import hashlib
import shutil
from pathlib import Path
import subprocess

CARPETA_ANALIZAR = Path("ruta/a/TuCarpetaFotos/con_metadatos")  # <-- cámbialo
CARPETA_REVISION = CARPETA_ANALIZAR.parent / "revisar_duplicados"
CARPETA_REVISION.mkdir(exist_ok=True)

def hash_archivo(path, bloque=65536):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for bloque_data in iter(lambda: f.read(bloque), b""):
            hasher.update(bloque_data)
    return hasher.hexdigest()

def tiene_metadatos(path):
    try:
        result = subprocess.run(
            ["exiftool", "-DateTimeOriginal", str(path)],
            capture_output=True,
            text=True
        )
        return "Date/Time Original" in result.stdout
    except:
        return False

def obtener_fecha_metadatos(path):
    try:
        result = subprocess.run(
            ["exiftool", "-DateTimeOriginal", "-s3", str(path)],
            capture_output=True,
            text=True
        )
        fecha_str = result.stdout.strip()
        return fecha_str if fecha_str else "9999:99:99 99:99:99"
    except:
        return "9999:99:99 99:99:99"

def mover_duplicados():
    hashes = {}
    for archivo in CARPETA_ANALIZAR.iterdir():
        if archivo.is_file():
            h = hash_archivo(archivo)
            hashes.setdefault(h, []).append(archivo)

    for duplicados in hashes.values():
        if len(duplicados) <= 1:
            continue

        # Elegir el mejor (el que tiene metadatos y fecha más antigua)
        duplicados_con_info = sorted(
            duplicados,
            key=lambda f: (
                not tiene_metadatos(f),  # True=1, False=0 → los que sí tienen metadatos primero
                obtener_fecha_metadatos(f)  # menor fecha primero
            )
        )

        conservar = duplicados_con_info[0]
        for archivo in duplicados_con_info[1:]:
            destino = CARPETA_REVISION / archivo.name
            shutil.move(str(archivo), destino)
            print(f"Movido duplicado: {archivo.name}")

if __name__ == "__main__":
    mover_duplicados()
