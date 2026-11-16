"""Figuras del dashboard (Avance 4). Las usan app.py (Streamlit) y el informe PDF."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from src.configuracion import MESES_CORTOS, UNIDAD, fmt
from src.validaciones import MESES

AZUL, NARANJA, ROJO, GRIS = "#1f6f9f", "#e08a1e", "#c8372d", "#888888"
COLORES_MODELO = {"Regresión lineal": "#e08a1e", "Promedio móvil": "#2e9e6b",
                  "Tasa de crecimiento promedio": "#8e5ea2"}
_millones = FuncFormatter(lambda x, _: fmt(x / 1e6, 1))


def fig_historico(serie, titulo="Evolución histórica del flujo turístico", excluidos=()):
    """Barras + línea: total anual de la selección. Los años excluidos del modelo se marcan en gris."""
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    x = [int(a) for a in serie.index]
    col = [GRIS if a in excluidos else AZUL for a in x]
    ax.bar(x, serie.to_numpy(), color=col, alpha=0.85, width=0.65, label=f"Total anual de {UNIDAD}")
    ax.plot(x, serie.to_numpy(), color="black", lw=1.4, marker="o", ms=4)
    for xi, yi in zip(x, serie.to_numpy()):
        ax.annotate(fmt(yi / 1e6, 2), (xi, yi), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)
    ax.set_title(titulo)
    ax.set_xlabel("Año")
    ax.set_ylabel(f"{UNIDAD.capitalize()} (millones)")
    ax.set_xticks(x)
    ax.yaxis.set_major_formatter(_millones)
    ax.set_ylim(0, max(serie.max() * 1.15, 1))
    ax.grid(axis="y", alpha=0.3)
    if excluidos:
        ax.bar([], [], color=GRIS, label="Año excluido del modelo")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    return fig


def fig_proyeccion(serie_modelo, serie_excluida, proy, modelo, mostrar_ic=True):
    """Línea histórica + proyección con banda de incertidumbre (95 %)."""
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.plot(serie_modelo.index, serie_modelo.to_numpy(), marker="o", color=AZUL, lw=2, label="Histórico (usado en el modelo)")
    if len(serie_excluida):
        ax.scatter(serie_excluida.index, serie_excluida.to_numpy(), color=GRIS, marker="x", s=50, zorder=3,
                   label="Histórico excluido")
    ux, uy = serie_modelo.index[-1], serie_modelo.iloc[-1]
    c = COLORES_MODELO.get(modelo, NARANJA)
    ax.plot([ux] + list(proy["anio"]), [uy] + list(proy["proyeccion"]), marker="s", ls="--", color=c, lw=2,
            label=f"Proyección: {modelo}")
    if mostrar_ic:
        ax.fill_between(proy["anio"], proy["inferior"], proy["superior"], color=c, alpha=0.18,
                        label="Banda de incertidumbre")
    ax.axvline(ux + 0.5, color=GRIS, lw=0.8, ls=":")
    ax.set_title(f"Proyección del flujo turístico ({int(proy['anio'].iloc[0])}-{int(proy['anio'].iloc[-1])})")
    ax.set_xlabel("Año")
    ax.set_ylabel(f"{UNIDAD.capitalize()} (millones)")
    ax.yaxis.set_major_formatter(_millones)
    ax.set_xticks(sorted(set(int(a) for a in list(serie_modelo.index) + list(serie_excluida.index) + list(proy["anio"]))))
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig


def fig_comparacion(serie_modelo, proyecciones):
    """Compara varios modelos sobre el mismo histórico. proyecciones = {modelo: DataFrame}."""
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.plot(serie_modelo.index, serie_modelo.to_numpy(), marker="o", color=AZUL, lw=2, label="Histórico")
    ux, uy = serie_modelo.index[-1], serie_modelo.iloc[-1]
    for m, p in proyecciones.items():
        ax.plot([ux] + list(p["anio"]), [uy] + list(p["proyeccion"]), marker="s", ls="--", lw=2,
                color=COLORES_MODELO.get(m, NARANJA), label=m)
    ax.set_title("Comparación de métodos de proyección")
    ax.set_xlabel("Año")
    ax.set_ylabel(f"{UNIDAD.capitalize()} (millones)")
    ax.yaxis.set_major_formatter(_millones)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    return fig


def fig_estacionalidad(mensual):
    """Barras: % del flujo en cada mes para la selección actual."""
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    pct = mensual.to_numpy() / mensual.sum() * 100
    colores = [NARANJA if m in ("diciembre", "enero", "febrero") else AZUL for m in MESES]
    ax.bar(MESES_CORTOS, pct, color=colores)
    ax.axhline(100 / 12, color=ROJO, ls="--", lw=1.3, label="Reparto uniforme (8,3 %)")
    ax.set_title("Estacionalidad mensual de la selección (verano en naranjo)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("% del flujo anual")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    return fig
