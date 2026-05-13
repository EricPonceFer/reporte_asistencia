from pathlib import Path
import sys


def obtener_ruta_base():

    # Ejecutable
    if getattr(sys, 'frozen', False):

        return Path(sys.executable).parent

    # Proyecto normal
    return Path(__file__).resolve().parent.parent.parent


BASE_DIR = obtener_ruta_base()

# =====================================================
# CARPETA DATA
# =====================================================

DATA_DIR = BASE_DIR / "data"

# =====================================================
# ARCHIVOS
# =====================================================

RUTA_CODIGOS = (
    DATA_DIR / "Identificacion Operadores.csv"
)

RUTA_VELADA = (
    DATA_DIR / "Personal Velada.csv"
)
