"""Avance 4: datos agregados para el dashboard, filtros, indicadores dinámicos y modelos de proyección.

Todo el cálculo vive aquí (sin Streamlit) para poder probarlo y reutilizarlo en el informe PDF.
"""
import numpy as np
import pandas as pd

from src.configuracion import RAIZ, RUTA_LIMPIO, RUTA_MUESTRA, VERANO
from src.validaciones import MESES

RUTA_AGREGADO = RAIZ / "datos" / "procesados" / "agregado_dashboard.csv"
CLAVES = ["anio", "region_origen", "region_destino", "es_intrarregional", "nivel_flujo"]
MODELOS = ["Regresión lineal", "Promedio móvil", "Tasa de crecimiento promedio"]

# Valor crítico t de dos colas (95 %) según grados de libertad; con muchos datos se usa 1,96.
_T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26,
        10: 2.23, 12: 2.18, 15: 2.13, 20: 2.09, 30: 2.04}


# ------------------------------------------------------------------ DATOS AGREGADOS
def construir_agregado(df):
    """Reduce el dataset limpio (millones de filas) a una tabla pequeña: un registro por combinación
    de año, región origen, región destino, tipo de viaje y nivel de flujo, con los 12 meses sumados."""
    cols = MESES + ["total_anual"]
    g = df.groupby(CLAVES, observed=True)[cols].sum().reset_index()
    g["n_registros"] = df.groupby(CLAVES, observed=True).size().to_numpy()
    for c in ("region_origen", "region_destino", "nivel_flujo"):
        g[c] = g[c].astype(str)
    return g


def cargar_agregado(forzar=False):
    """Devuelve (tabla agregada, descripción de la fuente).

    Usa datos/procesados/agregado_dashboard.csv si existe (liviano, se puede subir a GitHub).
    Si no, lo construye desde dataset_limpio.csv (o la muestra) y lo guarda para la próxima vez.
    """
    if RUTA_AGREGADO.exists() and not forzar:
        return pd.read_csv(RUTA_AGREGADO, encoding="utf-8"), "agregado_dashboard.csv"
    fuente = RUTA_LIMPIO if RUTA_LIMPIO.exists() else RUTA_MUESTRA
    if not fuente.exists():
        raise FileNotFoundError(
            "No hay datos para el dashboard. Ejecuta antes 'python main.py' (necesita "
            "datos/originales/dataset.csv) o copia datos/procesados/dataset_limpio.csv.")
    cat = ["region_origen", "region_destino", "nivel_flujo"]
    cab = pd.read_csv(fuente, nrows=0).columns
    usar = [c for c in CLAVES + MESES + ["total_anual"] if c in cab]
    df = pd.read_csv(fuente, usecols=usar, dtype={c: "category" for c in cat})
    agg = construir_agregado(df)
    RUTA_AGREGADO.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(RUTA_AGREGADO, index=False, encoding="utf-8")
    return agg, fuente.name + (" (MUESTRA: resultados referenciales)" if fuente == RUTA_MUESTRA else "")


# ------------------------------------------------------------------ FILTROS E INDICADORES
def filtrar(agg, anios=None, regiones_destino=None, regiones_origen=None, tipo_viaje="Todos",
            niveles=None, excluir_desconocido=True):
    """Aplica los filtros del dashboard. Listas vacías o None = sin filtrar."""
    m = pd.Series(True, index=agg.index)
    if anios:
        m &= agg["anio"].between(anios[0], anios[1])
    if regiones_destino:
        m &= agg["region_destino"].isin(regiones_destino)
    if regiones_origen:
        m &= agg["region_origen"].isin(regiones_origen)
    if tipo_viaje == "Intrarregional":
        m &= agg["es_intrarregional"] == 1
    elif tipo_viaje == "Interregional":
        m &= agg["es_intrarregional"] == 0
    if niveles:
        m &= agg["nivel_flujo"].isin(niveles)
    if excluir_desconocido:
        m &= ~agg["region_destino"].str.lower().eq("desconocido")
    return agg[m]


def serie_anual(agg):
    """Total de viajes por año (Serie indexada por año, solo años con datos)."""
    return agg.groupby("anio")["total_anual"].sum().sort_index()


def serie_mensual(agg):
    """Total de viajes por mes del año (suma sobre todos los años filtrados)."""
    return agg[MESES].sum()


def indicadores_de_serie(s, verano=None):
    """Indicadores a partir de una serie anual (indexada por año). 'verano' = % dic-feb ya calculado, si se conoce."""
    if s.empty or s.sum() == 0:
        return []
    out = [("Total acumulado", float(s.sum()), f"{int(s.index[0])}-{int(s.index[-1])}"),
           ("Promedio anual", float(s.mean()), "viajes por año"),
           ("Flujo máximo anual", float(s.max()), f"año {int(s.idxmax())}"),
           ("Flujo mínimo anual", float(s.min()), f"año {int(s.idxmin())}")]
    if len(s) >= 2 and s.iloc[-2] > 0:
        out.append(("Variación último año", float((s.iloc[-1] / s.iloc[-2] - 1) * 100),
                    f"{int(s.index[-2])} a {int(s.index[-1])} (%)"))
    if len(s) >= 2 and s.iloc[0] > 0 and s.iloc[-1] > 0 and s.index[-1] > s.index[0]:
        n = s.index[-1] - s.index[0]
        out.append(("Crecimiento anual compuesto", float(((s.iloc[-1] / s.iloc[0]) ** (1 / n) - 1) * 100),
                    f"{int(s.index[0])} a {int(s.index[-1])} (%)"))
    if verano is not None:
        out.append(("Concentración en verano", float(verano), "dic-feb (% del flujo)"))
    return out


def meses_faltantes(agg):
    """Meses sin ningún dato por año (suma nacional = 0). Devuelve {año: [meses]} solo para años incompletos.

    Un año con meses en cero (p. ej. el año en curso, con datos solo hasta octubre) no es comparable con los
    años completos: su total anual aparece artificialmente bajo.
    """
    m = agg.groupby("anio")[MESES].sum()
    return {int(a): [mes for mes in MESES if m.loc[a, mes] <= 0] for a in m.index if (m.loc[a] <= 0).any()}


def anios_incompletos(agg):
    return sorted(meses_faltantes(agg))


def indicadores_dinamicos(agg, incompletos=None):
    """Indicadores que se recalculan con cada filtro, sobre años completos. Devuelve lista de (nombre, valor, detalle)."""
    if incompletos is None:
        incompletos = anios_incompletos(agg)
    completos = agg[~agg["anio"].isin(incompletos)]
    if completos.empty:
        return []
    m = serie_mensual(completos)
    verano = float(m[VERANO].sum() / m.sum() * 100) if m.sum() > 0 else None
    return indicadores_de_serie(serie_anual(completos), verano)


# ------------------------------------------------------------------ MODELOS DE PROYECCIÓN
def _t95(gl):
    if gl < 1:
        return np.nan
    claves = sorted(_T95)
    for k in claves:
        if gl <= k:
            return _T95[k]
    return 1.96


def _resultado(anios_fut, valores, inf=None, sup=None):
    v = np.maximum(np.asarray(valores, dtype=float), 0.0)       # un flujo de viajes no puede ser negativo
    inf = v if inf is None else np.maximum(np.asarray(inf, dtype=float), 0.0)
    sup = v if sup is None else np.maximum(np.asarray(sup, dtype=float), 0.0)
    return pd.DataFrame({"anio": anios_fut, "proyeccion": v, "inferior": inf, "superior": sup})


def proy_lineal(serie, horizonte):
    """Regresión lineal por mínimos cuadrados: y = a + b*año, con intervalo de predicción del 95 %."""
    x, y = serie.index.to_numpy(float), serie.to_numpy(float)
    n = len(x)
    b, a = np.polyfit(x, y, 1)
    fut = np.arange(x[-1] + 1, x[-1] + horizonte + 1)
    pred = a + b * fut
    gl = n - 2
    if gl < 1:
        return _resultado(fut.astype(int), pred)
    s = np.sqrt(np.sum((y - (a + b * x)) ** 2) / gl)
    sxx = np.sum((x - x.mean()) ** 2)
    marg = _t95(gl) * s * np.sqrt(1 + 1 / n + (fut - x.mean()) ** 2 / sxx)
    return _resultado(fut.astype(int), pred, pred - marg, pred + marg)


def proy_promedio_movil(serie, horizonte, ventana=3):
    """Promedio móvil recursivo: cada año proyectado es el promedio de los últimos 'ventana' valores."""
    ventana = int(max(1, min(ventana, len(serie))))
    vals = list(serie.to_numpy(float))
    errores = serie.to_numpy(float)[ventana:] - serie.rolling(ventana).mean().to_numpy()[ventana - 1:-1]
    sigma = np.std(errores, ddof=1) if len(errores) > 1 else np.nan
    pred = []
    for _ in range(horizonte):
        pred.append(np.mean(vals[-ventana:]))
        vals.append(pred[-1])
    fut = np.arange(int(serie.index[-1]) + 1, int(serie.index[-1]) + horizonte + 1)
    pred = np.array(pred)
    if np.isnan(sigma):
        return _resultado(fut, pred)
    marg = 1.96 * sigma * np.sqrt(np.arange(1, horizonte + 1))   # la incertidumbre crece con el horizonte
    return _resultado(fut, pred, pred - marg, pred + marg)


def proy_tasa_crecimiento(serie, horizonte):
    """Proyección compuesta usando tasas logarítmicas anualizadas.

    La banda es una aproximación basada en la dispersión histórica de las tasas,
    no un intervalo de confianza formal.
    """
    y, x = serie.to_numpy(dtype=float), serie.index.to_numpy(dtype=float)
    fut = np.arange(int(x[-1]) + 1, int(x[-1]) + horizonte + 1)
    if len(y) < 2 or np.any(y <= 0):
        return _resultado(fut, np.repeat(max(float(y[-1]), 0.0), horizonte))
    tasas_log = np.log(y[1:] / y[:-1]) / np.diff(x)
    media = float(np.mean(tasas_log))
    sd = float(np.std(tasas_log, ddof=1)) if len(tasas_log) > 1 else 0.0
    k = np.arange(1, horizonte + 1, dtype=float)
    pred = y[-1] * np.exp(media * k)
    inferior = y[-1] * np.exp((media - 1.96 * sd) * k)
    superior = y[-1] * np.exp((media + 1.96 * sd) * k)
    return _resultado(fut, pred, inferior, superior)

def proyectar(serie, modelo, horizonte, ventana=3):
    """Despacha al modelo elegido. 'serie' = Serie anual indexada por año (mínimo 3 años)."""
    if not isinstance(serie, pd.Series) or len(serie) < 3:
        raise ValueError("Se necesitan al menos 3 años de datos para proyectar.")
    if int(horizonte) < 1 or int(horizonte) > 10:
        raise ValueError("El horizonte debe estar entre 1 y 10 años.")
    serie = serie.sort_index().astype(float)
    if serie.index.has_duplicates or not np.isfinite(serie.to_numpy()).all():
        raise ValueError("La serie debe tener años únicos y valores numéricos finitos.")
    if (serie < 0).any():
        raise ValueError("Los flujos históricos no pueden ser negativos.")
    if modelo == "Regresión lineal":
        return proy_lineal(serie, horizonte)
    if modelo == "Promedio móvil":
        return proy_promedio_movil(serie, horizonte, ventana)
    if modelo == "Tasa de crecimiento promedio":
        return proy_tasa_crecimiento(serie, horizonte)
    raise ValueError(f"Modelo desconocido: {modelo}")


def backtest(serie, ventana=3, max_pruebas=5):
    """Validación de origen móvil: evalúa cada modelo en varios años históricos.

    En cada corte el modelo solo recibe información anterior al año evaluado.
    Devuelve métricas agregadas por método (MAE, RMSE y MAPE).
    """
    if len(serie) < 5:
        return pd.DataFrame(columns=["modelo", "n_pruebas", "mae", "rmse", "mape"])
    n_pruebas = min(int(max_pruebas), len(serie) - 3)
    filas = []
    for modelo in MODELOS:
        reales, predichos = [], []
        for corte in range(len(serie) - n_pruebas, len(serie)):
            entrenamiento = serie.iloc[:corte]
            real = float(serie.iloc[corte])
            pred = float(proyectar(entrenamiento, modelo, 1, ventana)["proyeccion"].iloc[0])
            reales.append(real)
            predichos.append(pred)
        reales = np.asarray(reales, dtype=float)
        predichos = np.asarray(predichos, dtype=float)
        errores = predichos - reales
        validos = reales != 0
        mape = float(np.mean(np.abs(errores[validos] / reales[validos])) * 100) if validos.any() else np.nan
        filas.append({"modelo": modelo, "n_pruebas": len(reales),
                      "mae": float(np.mean(np.abs(errores))),
                      "rmse": float(np.sqrt(np.mean(errores ** 2))), "mape": mape})
    return pd.DataFrame(filas).sort_values("mae").reset_index(drop=True)

def r2_lineal(serie):
    """R² del ajuste lineal sobre la serie histórica (qué tan 'recta' es la tendencia)."""
    x, y = serie.index.to_numpy(float), serie.to_numpy(float)
    if len(x) < 3 or np.var(y) == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1] ** 2)
