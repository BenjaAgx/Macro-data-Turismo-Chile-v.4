"""Genera reportes/avance_4.pdf.   Uso:  python generar_informe4.py

Usa los datos agregados del dashboard si existen; si no, usa la serie anual publicada en el Avance 3.
"""
from src.informe_avance4 import construir_informe4
from src.proyeccion import cargar_agregado

if __name__ == "__main__":
    try:
        agg, fuente = cargar_agregado()
    except FileNotFoundError:
        agg, fuente = None, "serie anual del Avance 3"
    print(f"Datos: {fuente}")
    print(f"-> {construir_informe4(agg, fuente)}")
