"""Genera reportes/avance_4.pdf (informe técnico del Avance 4) siguiendo la estructura del enunciado (7.1 a 7.6).

Fuente de cifras (en este orden):
  1. Datos agregados reales del dashboard (datos/procesados/agregado_dashboard.csv o dataset_limpio.csv).
  2. Si no existen, la serie anual nacional publicada en el Avance 3 (redondeada a 0,1 millones).
Capturas: si existen reportes/capturas/vista_historica.png, vista_proyectada.png e indicadores.png se insertan;
si no, se usan figuras generadas con las mismas funciones del dashboard y el PDF lo indica.
Uso:  python generar_informe4.py
"""
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import KeepTogether, PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

from src import graficos_dashboard as gd
from src import proyeccion as pr
from src.configuracion import RAIZ, URL_REPOSITORIO, fmt, nombre_corto
from src.informe import CURSO, GRUPO, P, PBullet, _imagen, _pagina, _portada, _tabla, _tabla_portada
from src.validaciones import MESES

RUTA_PDF = RAIZ / "reportes" / "avance_4.pdf"
DIR_CAPTURAS = RAIZ / "reportes" / "capturas"
DIR_TMP = RAIZ / "resultados" / "graficos"
RUTA_TEXTOS = RAIZ / "reportes" / "textos_avance4.md"
MARCA = "<!-- BORRADOR"
HORIZONTE, VENTANA = 3, 3

# Serie anual nacional publicada en el Informe Nº3 (Gráfico 01), en viajes, redondeada a 0,1 millones.
SERIE_AVANCE3 = {2018: 17.7e6, 2019: 17.3e6, 2020: 6.3e6, 2021: 13.5e6, 2022: 19.9e6, 2023: 17.2e6,
                 2024: 19.8e6, 2025: 22.1e6}
# Estacionalidad publicada en el Informe Nº3 (se usa solo si no hay datos agregados).
YOY_AVANCE3 = {2019: -2.4, 2020: -63.4, 2023: -13.7}   # variaciones interanuales publicadas (%)
ESTAC_AVANCE3 = {"verano": 46.9, "mes_max": ("diciembre", 15.8), "mes_min": ("noviembre", 5.9),
                 "reg_max": ("Tarapacá", 55.5), "reg_min": ("Magallanes", 29.9)}


# ----------------------------------------------------------------------------- UTILIDADES
def _p(valor, dec=1):
    return f"{valor:+.{dec}f}".replace(".", ",") + " %"


def _m(v, dec=1):
    """Viajes en millones con formato chileno."""
    return fmt(v / 1e6, dec) + " millones"


def _guardar(fig, nombre):
    DIR_TMP.mkdir(parents=True, exist_ok=True)
    ruta = DIR_TMP / nombre
    fig.savefig(ruta, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return ruta


def _palabras(t):
    return len(t.split())


def _fig_tarjetas(inds):
    """Figura con los indicadores en formato de tarjetas, como se ven en el dashboard."""
    n, cols = len(inds), 4
    filas = -(-n // cols)
    fig, axs = plt.subplots(filas, cols, figsize=(8.6, 1.5 * filas + 0.3))
    axs = axs.ravel()
    for ax in axs:
        ax.axis("off")
    for ax, (nom, val, det) in zip(axs, inds):
        ax.add_patch(plt.Rectangle((0.02, 0.05), 0.96, 0.9, transform=ax.transAxes, fc="#f4f7fa", ec="#c9d6e2"))
        txt = (fmt(val, 1) + " %") if "%" in det else fmt(val, 0)
        ax.text(0.5, 0.74, nom, ha="center", va="center", fontsize=8.5, color="#444444", transform=ax.transAxes)
        ax.text(0.5, 0.46, txt, ha="center", va="center", fontsize=13, fontweight="bold", color="#1f6f9f",
                transform=ax.transAxes)
        ax.text(0.5, 0.18, det, ha="center", va="center", fontsize=7.5, color="#777777", transform=ax.transAxes)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- CÁLCULOS
def _calcular(agg=None):
    """Escenario del informe: total nacional. Se proyecta con y sin 2020-2021 (pandemia).

    Los años incompletos (meses sin datos) se muestran en el gráfico, pero quedan fuera de los modelos y de los
    indicadores anuales: su total anual sería artificialmente bajo.
    """
    faltan = {}
    if agg is not None:
        datos = pr.filtrar(agg)
        faltan = pr.meses_faltantes(agg)
        s_all = pr.serie_anual(datos)
        s = s_all.drop(index=[a for a in faltan if a in s_all.index])
        comp = datos[~datos["anio"].isin(faltan)]
        mensual = pr.serie_mensual(comp)
        verano = float(mensual[["diciembre", "enero", "febrero"]].sum() / mensual.sum() * 100)
        reg = comp.groupby("region_destino")[MESES].sum()
        reg = reg[reg.sum(axis=1) > 0]
        rv = reg[["diciembre", "enero", "febrero"]].sum(axis=1) / reg.sum(axis=1) * 100
        estac = {"verano": verano, "mes_max": (mensual.idxmax(), float(mensual.max() / mensual.sum() * 100)),
                 "mes_min": (mensual.idxmin(), float(mensual.min() / mensual.sum() * 100)),
                 "reg_max": (nombre_corto(rv.idxmax()), float(rv.max())),
                 "reg_min": (nombre_corto(rv.idxmin()), float(rv.min()))}
        origen = "datos"
    else:
        s = pd.Series(SERIE_AVANCE3, dtype=float).sort_index()
        s.index.name = "anio"
        s_all, estac, origen = s, ESTAC_AVANCE3, "avance3"
    exc = [a for a in (2020, 2021) if a in s.index and a != s.index[-1]]
    ss = s.drop(index=exc)
    c = {"origen": origen, "serie": s, "serie_all": s_all, "faltan": faltan, "exc": exc, "serie_sin": ss,
         "estac": estac, "inds": pr.indicadores_de_serie(s, estac["verano"]), "r2": pr.r2_lineal(s),
         "r2_sin": pr.r2_lineal(ss)}
    c["proy_sin"] = {m: pr.proyectar(ss, m, HORIZONTE, VENTANA) for m in pr.MODELOS}
    c["proy_todo"] = {m: pr.proyectar(s, m, HORIZONTE, VENTANA) for m in pr.MODELOS}
    # La validación retrospectiva necesita al menos 5 años: se hace con todos los años completos.
    c["bt"] = pr.backtest(s, VENTANA)
    return c


def _figuras(c):
    """Devuelve dict clave -> (ruta, es_captura_real)."""
    reales = {k: DIR_CAPTURAS / f"{n}.png" for k, n in (("historica", "vista_historica"),
              ("proyectada", "vista_proyectada"), ("indicadores", "indicadores"))}
    auto = {"historica": lambda: gd.fig_historico(c["serie_all"], excluidos=c["exc"] + list(c["faltan"])),
            "proyectada": lambda: gd.fig_proyeccion(c["serie_sin"], c["serie_all"].loc[c["exc"] + [a for a in c["faltan"] if a in c["serie_all"].index]],
                                                    c["proy_sin"]["Regresión lineal"], "Regresión lineal"),
            "indicadores": lambda: _fig_tarjetas(c["inds"]),
            "comparacion": lambda: gd.fig_comparacion(c["serie_sin"], c["proy_sin"])}
    out = {k: (r, True) for k, r in reales.items() if r.exists()}
    for k, f in auto.items():
        if k not in out:
            out[k] = (_guardar(f(), f"av4_{k}.png"), False)
    return out


# ----------------------------------------------------------------------------- TEXTOS
def _textos(c):
    s, e = c["serie"], c["estac"]
    a0, a1 = int(s.index[0]), int(s.index[-1])
    var_tot = (s.iloc[-1] / s.iloc[0] - 1) * 100
    cagr = ((s.iloc[-1] / s.iloc[0]) ** (1 / (a1 - a0)) - 1) * 100
    yoy = (s.pct_change() * 100).dropna()
    caidas = [(int(a), v) for a, v in yoy.items() if v < 0]
    aprox = ""
    if c["origen"] == "avance3":      # con la serie redondeada se usan las variaciones exactas ya publicadas
        caidas = sorted(YOY_AVANCE3.items())
        aprox = "aprox. "
    mayor_caida = min(caidas, key=lambda t: t[1]) if caidas else None
    mayor_alza = (int(yoy.idxmax()), float(yoy.max()))
    exc = " y ".join(str(a) for a in c["exc"])
    lin, mm, tc = (c["proy_sin"][m] for m in pr.MODELOS)
    fin = {n: float(p["proyeccion"].iloc[-1]) for n, p in zip(pr.MODELOS, (lin, mm, tc))}
    anio_f = int(lin["anio"].iloc[-1])
    ult = float(s.iloc[-1])
    bt = c["bt"]
    mejor = bt.iloc[0] if len(bt) else None
    ancho = float(lin["superior"].iloc[-1] - lin["inferior"].iloc[-1])

    caidas_txt = " y ".join(f"{a} ({_p(v)})" for a, v in caidas) if caidas else "ningún año"
    parcial = ""
    for a, ms in sorted(c["faltan"].items()):
        parcial += (f" El año {a} se excluyó del análisis anual porque no tiene datos de {' y '.join(ms)}: su total "
                    "sería artificialmente bajo y no es comparable con los años completos.")
    extra = ""
    if mayor_caida and mayor_caida[0] in (2020, 2021):
        extra = (("La mayor fue la de " + str(mayor_caida[0]) + f" ({_p(mayor_caida[1])}), " if len(caidas) > 1 else
                  "Es ") + "coherente con el efecto de la pandemia de COVID-19 sobre la movilidad, y fue seguida de la mayor "
                 f"alza ({mayor_alza[0]}: {aprox}{_p(mayor_alza[1], 0)}) al recuperarse el viaje. ")
    tendencia = (f"El flujo nacional pasó de {_m(s.iloc[0])} en {a0} a {_m(s.iloc[-1])} en {a1} ({_p(var_tot)}; "
                 f"crecimiento anual compuesto de {_p(cagr)}), pero la trayectoria no es lineal: hubo {'una caída' if len(caidas) == 1 else 'caídas'} en {caidas_txt}. "
                 + extra +
                 f"En estacionalidad, {e['mes_max'][0]} concentra el {fmt(e['mes_max'][1], 1)} % del flujo anual y "
                 f"{e['mes_min'][0]} el {fmt(e['mes_min'][1], 1)} %; el verano (dic-feb) reúne el {fmt(e['verano'], 1)} %, con "
                 f"diferencias entre regiones desde {fmt(e['reg_min'][1], 1)} % ({e['reg_min'][0]}) hasta "
                 f"{fmt(e['reg_max'][1], 1)} % ({e['reg_max'][0]})." + parcial)
    proyecta = (f"Al ajustar los modelos sin {exc} (años atípicos), la proyección para {anio_f} es de "
                f"{_m(fin[pr.MODELOS[0]])} con regresión lineal ({_p((fin[pr.MODELOS[0]] / ult - 1) * 100)} respecto de {a1}), "
                f"{_m(fin[pr.MODELOS[1]])} con promedio móvil ({_p((fin[pr.MODELOS[1]] / ult - 1) * 100)}) y "
                f"{_m(fin[pr.MODELOS[2]])} con tasa de crecimiento promedio ({_p((fin[pr.MODELOS[2]] / ult - 1) * 100)}). "
                f"Los métodos difieren en {_m(max(fin.values()) - min(fin.values()))} hacia {anio_f}: esa dispersión es una "
                "medida directa de la incertidumbre del escenario. "
                + (f"Como sensibilidad, si se incluyen {exc} en el ajuste las proyecciones para {anio_f} pasan a "
                   + ", ".join(f"{_m(float(c['proy_todo'][m]['proyeccion'].iloc[-1]))} ({n})"
                               for m, n in zip(pr.MODELOS, ("regresión lineal", "promedio móvil", "tasa de crecimiento")))
                   + ": el tratamiento de la pandemia cambia el resultado." if c["exc"] else ""))
    conf = (f"La confiabilidad es baja a moderada. La serie tiene solo {len(s)} observaciones anuales ({len(c['serie_sin'])} sin "
            f"los años atípicos); el coeficiente de determinación (R cuadrado) de la tendencia lineal es {fmt(c['r2'], 2)} con todos los años y {fmt(c['r2_sin'], 2)} "
            f"sin ellos, y el intervalo de predicción de la regresión para {anio_f} abarca {_m(ancho)} de ancho. ")
    if mejor is not None:
        conf += (f"En la validación retrospectiva (origen móvil sobre los {len(s)} años completos, {int(mejor['n_pruebas'])} años de prueba) el menor error "
                 f"absoluto medio lo obtuvo {mejor['modelo']} (MAE de {_m(mejor['mae'])}; MAPE {fmt(mejor['mape'], 1)} %). "
                 "Aun así, con tan pocos puntos la comparación es orientativa, y ningún modelo anticipa por sí solo "
                 "un shock como el de 2020.")
    falta = ("Mejorarían los resultados: (1) series mensuales o trimestrales, que multiplican los puntos de datos y "
             "permiten modelos estacionales como Holt-Winters o SARIMA; (2) variables explicativas como PIB, tipo de cambio, "
             "feriados largos, conectividad aérea y terrestre, precio de combustibles y eventos climáticos o sanitarios; "
             "(3) más años de historia y el cierre completo de los años en curso; y (4) datos de gasto y pernoctaciones, que permiten "
             "pasar de contar viajes a medir demanda económica.")
    n_mejor = mejor["modelo"] if mejor is not None else pr.MODELOS[0]
    base = (f"Según la validación retrospectiva, el método más razonable para esta serie es {n_mejor}, porque fue el que "
            "cometió menor error al predecir años que no conocía. " if mejor is not None else
            "La serie es demasiado corta para una validación retrospectiva, por lo que la elección se basa solo en los "
            "supuestos de cada método. ")
    final = (base + "Sin embargo, no conviene usar un único número: "
             "recomendamos presentar el método elegido como escenario central y los otros dos como escenarios de rango, "
             "explicitando que ninguno incorpora shocks externos. La regresión lineal es la más fácil de explicar y la única "
             "con un intervalo estadístico formal; el promedio móvil es el más conservador; y la tasa de crecimiento "
             "es la más sensible a los años de rebote posteriores a la pandemia.")
    concl = ("Se construyó un dashboard interactivo en Streamlit que permite explorar la matriz de movilidad turística de "
             "Chile con cinco filtros, siete indicadores que se recalculan automáticamente, gráficos históricos, "
             "estacionales y de proyección, y tres modelos matemáticos configurables por el usuario, junto con una "
             f"comparación entre métodos mediante validación retrospectiva. Entre {a0} y {a1} el flujo nacional varió "
             f"{_p(var_tot)}, con una caída marcada en {int(s.idxmin())} y una recuperación posterior, y una concentración "
             f"estival del {fmt(e['verano'], 1)} %" + (f" (se excluyó {', '.join(str(a) for a in c['faltan'])} por estar incompleto)" if c["faltan"] else "") + f". Para {anio_f}, los modelos proyectan entre {_m(min(fin.values()))} y "
             f"{_m(max(fin.values()))}, lo que muestra que el resultado depende del método y de los supuestos. La herramienta "
             "es útil porque permite a un analista cambiar el período, la región y el modelo sin tocar el código, y porque "
             "expone la incertidumbre en lugar de ocultarla. Sus limitaciones son la corta longitud de la serie anual, la "
             "ausencia de variables externas y la imposibilidad de representar la estacionalidad intra-anual. Como mejoras "
             "futuras se propone incorporar datos mensuales, modelos estacionales, variables macroeconómicas y una "
             "validación con más años de prueba.")
    return {"tendencia": tendencia, "proyecta": proyecta, "conf": conf, "falta": falta, "final": final,
            "conclusion": concl}


CLAVES_TEXTO = [("tendencia", "¿Qué tendencia histórica se observa?"), ("proyecta", "¿Qué proyecta el modelo?"),
                ("conf", "¿Qué tan confiable es la proyección?"),
                ("falta", "¿Qué información faltante podría mejorar los resultados?"),
                ("final", "¿Qué método entrega resultados más razonables y por qué?"), ("conclusion", "Conclusión")]


def _cargar_textos(c):
    """Lee reportes/textos_avance4.md; si no existe lo crea como borrador para que el equipo lo reescriba."""
    auto = _textos(c)
    if not RUTA_TEXTOS.exists():
        lin = [MARCA + ": reescriban cada respuesta con sus palabras y BORREN esta línea. Vuelvan a ejecutar "
               "python generar_informe4.py para actualizar el PDF. -->", ""]
        for k, t in CLAVES_TEXTO:
            lin += [f"## {t}", auto[k], ""]
        RUTA_TEXTOS.parent.mkdir(parents=True, exist_ok=True)
        RUTA_TEXTOS.write_text("\n".join(lin), encoding="utf-8")
        return auto
    inv = {t: k for k, t in CLAVES_TEXTO}
    cuerpo, actual = {}, None
    for l in RUTA_TEXTOS.read_text(encoding="utf-8").splitlines():
        if l.startswith("<!--"):
            continue
        if l.startswith("## "):
            actual = inv.get(l[3:].strip())
            cuerpo[actual] = []
        elif actual and l.strip():
            cuerpo[actual].append(l.strip())
    out = dict(auto)
    out.update({k: " ".join(v) for k, v in cuerpo.items() if k and v})
    return out


# ----------------------------------------------------------------------------- PDF
def _caja(texto):
    t = Table([[P(texto, "c")]], colWidths=[16 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F7")),
                           ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9d6e2")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def _figura(titulo, ruta, real, nota=""):
    pie = "Captura real del dashboard." if real else (
        "Figura generada con las mismas funciones de graficos_dashboard.py que usa el dashboard.")
    return KeepTogether([P(titulo, "h3"), _imagen(ruta, 12.5), P(pie + (" " + nota if nota else ""), "c")])


def construir_informe4(agg=None, fuente="", ruta_pdf=RUTA_PDF):
    c = _calcular(agg)
    figs = _figuras(c)
    tx = _cargar_textos(c)
    s = c["serie"]
    a0, a1 = int(s.index[0]), int(s.index[-1])
    anio_f = int(c["proy_sin"][pr.MODELOS[0]]["anio"].iloc[-1])
    exc = " y ".join(str(a) for a in c["exc"])

    ruta_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(ruta_pdf), pagesize=LETTER, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            topMargin=3.0 * cm, bottomMargin=2.2 * cm,
                            title="Informe Nº4: Dashboard interactivo y proyección de datos",
                            author=f"{GRUPO} - {CURSO}")
    st = [Spacer(1, 353), _tabla_portada(), PageBreak(), P("INFORME Nº4", "t")]
    st.append(P("Dashboard interactivo y proyección de datos", "h2"))
    if "MUESTRA" in fuente:
        st.append(P("ADVERTENCIA: informe generado con la muestra del dataset; las cifras son solo referenciales.", "aviso"))
    st.append(P("Resumen del Avance: se transformó el análisis de los avances anteriores en una aplicación interactiva "
                "(Python, Pandas y Streamlit) que permite filtrar la matriz de movilidad turística, calcular indicadores "
                "automáticos, visualizar la serie histórica y proyectar el flujo futuro con tres modelos matemáticos "
                "ajustables, comparándolos con validación retrospectiva."))
    if c["origen"] == "avance3":
        st.append(_caja(
            f"Nota sobre los datos: las cifras de este informe usan la serie anual nacional del Informe Nº3 "
            f"({a0}-{a1}, redondeada a 0,1 millones de viajes) y sus indicadores de estacionalidad. Al ejecutar "
            "generar_informe4.py con el dataset procesado completo, todas las cifras se recalculan con los valores exactos."))

    if c["faltan"]:
        det = "; ".join(f"{a} (sin {', '.join(ms)})" for a, ms in sorted(c["faltan"].items()))
        st.append(_caja(f"Nota sobre los datos: el dataset cubre {int(c['serie_all'].index[0])}-{int(c['serie_all'].index[-1])} e incluye años incompletos: {det}. Se muestran en gris en los "
                        "gráficos, pero se excluyen de los modelos y de los indicadores anuales, que usan solo años completos "
                        f"({int(s.index[0])}-{int(s.index[-1])})."))

    # ---------------- 7.1
    st.append(P("7.1 Objetivo del Dashboard", "h1"))
    st.append(PBullet("Problema que resuelve:", "la matriz de movilidad turística comunal origen-destino tiene decenas de "
                      "miles de registros, por lo que no puede leerse directamente. El dashboard resume esa información, "
                      "permite compararla por región, período y tipo de viaje, y la proyecta hacia el futuro."))
    st.append(PBullet("Usuario:", "analistas de turismo de gobiernos regionales y municipios, y gestores de servicios "
                      "turísticos que necesitan consultar datos sin programar."))
    st.append(PBullet("Decisiones que apoya:", "dotación de personal y refuerzo de servicios en los meses de mayor demanda, "
                      "priorización de regiones destino, y planificación de capacidad e inversión según distintos escenarios "
                      "de crecimiento."))
    st.append(PBullet("Pregunta orientadora:", "¿qué tendencia presenta el flujo de turismo en los últimos años y cómo "
                      "varía la estacionalidad entre las distintas regiones de Chile?"))

    # ---------------- 7.2
    st.append(P("7.2 Componentes Implementados", "h1"))
    st.append(_tabla([["Elemento", "Implementación"],
                      ["Filtros (5)", "Rango de años; región destino; región origen; tipo de viaje (todos, intrarregional o "
                                      "interregional); nivel de flujo (bajo, medio, alto)."],
                      ["Indicadores (7)", "Total acumulado; promedio anual; flujo máximo anual; flujo mínimo anual; variación "
                                          "del último año; crecimiento anual compuesto; concentración en verano. Se recalculan con cada filtro."],
                      ["Gráficos (4)", "Evolución histórica anual (barras y línea); estacionalidad mensual; proyección con banda "
                                       "de incertidumbre; comparación entre modelos."],
                      ["Modelo de proyección", "Regresión lineal, promedio móvil y tasa de crecimiento promedio, seleccionables "
                                               "desde el dashboard, más comparación entre métodos (desafío extra)."],
                      ["Parámetros ajustables", "Modelo; horizonte de 1 a 10 años; ventana del promedio móvil; años excluidos del "
                                                "ajuste; mostrar u ocultar la banda de incertidumbre."],
                      ["Exportación", "Descarga de la serie anual filtrada en CSV."]], [4.0, 12.0]))
    st.append(P("Tabla 1. Componentes del dashboard.", "c"))
    st.append(_tabla([["Módulo", "Responsabilidad"],
                      ["app.py", "Interfaz Streamlit: filtros, indicadores, pestañas y descarga."],
                      ["src/proyeccion.py", "Agregación, filtros, indicadores, modelos y validación retrospectiva."],
                      ["src/graficos_dashboard.py", "Figuras reutilizables por el dashboard y el informe."],
                      ["src/informe_avance4.py", "Generación automática de este informe."]], [5.0, 11.0]))
    st.append(P("Tabla 2. Organización modular del código. Repositorio: " + URL_REPOSITORIO, "c"))

    # ---------------- 7.3
    st.append(P("7.3 Modelo Utilizado", "h1"))
    st.append(P("Variable proyectada: total anual de viajes turísticos (suma de los doce meses) de la selección filtrada, "
                "agregado por año. El usuario elige uno de tres métodos; en las fórmulas, t es el año, h los años hacia "
                "adelante e y(t) el último valor observado."))
    st.append(_tabla([["Método", "Fórmula", "Supuestos", "Limitaciones"],
                      ["Regresión lineal", "y(t) = a + b·t, con a y b por mínimos cuadrados. Banda: intervalo de predicción de 95 % (t de Student).",
                       "Tendencia constante; errores independientes.", "Sensible a años atípicos; extrapola sin límite."],
                      ["Promedio móvil", "y(t+1) = promedio de los últimos k valores (k = 3 por defecto), aplicado en forma recursiva.",
                       "El nivel reciente predice el siguiente año.", "No captura tendencia; la proyección se aplana."],
                      ["Tasa de crecimiento promedio", "y(t+h) = y(t)·exp(g·h), con g = promedio de las tasas logarítmicas anualizadas, ln(y1/y0) / años entre datos.",
                       "El crecimiento medio histórico se mantiene.", "Amplifica el rebote posterior a una caída; muy sensible a la base."]],
                     [2.8, 6.2, 3.6, 3.4], chica=True))
    st.append(P("Tabla 3. Modelos de proyección.", "c"))
    st.append(P("Supuestos generales: la serie anual es representativa del comportamiento futuro y los años atípicos "
                f"({exc}, pandemia) pueden excluirse del ajuste sin dejar de mostrarse en el gráfico histórico. "
                "Los años con meses sin datos se excluyen siempre del ajuste. Como un flujo no puede ser negativo, las proyecciones y sus bandas se truncan en cero. Para promedio móvil y "
                "tasa de crecimiento la banda es una estimación orientativa de la incertidumbre, no un intervalo de confianza formal."))
    st.append(P("Limitaciones generales: la serie anual tiene pocos puntos, no incluye variables externas y la "
                "agregación anual oculta la estacionalidad dentro del año."))

    # ---------------- 7.4
    st.append(KeepTogether([P("7.4 Resultados", "h1"), _figura("Vista histórica", *figs["historica"],
                      nota=("Las barras grises ("
                            + ", ".join(str(a) for a in c["exc"] + list(c["faltan"])) +
                            ") no se usan en el ajuste de los modelos." if (c["exc"] or c["faltan"]) else ""))]))
    st.append(_figura("Vista proyectada (regresión lineal, 3 años)", *figs["proyectada"]))
    st.append(_figura("Indicadores calculados (total nacional, todos los años)", *figs["indicadores"]))
    filas = [["Indicador", "Valor", "Detalle"]]
    for n, v, d in c["inds"]:
        filas.append([n, (fmt(v, 1) + " %") if "%" in d else fmt(v, 0), d])
    st.append(_tabla(filas, [6.0, 3.5, 6.5]))
    st.append(P("Tabla 4. Indicadores dinámicos con el filtro por defecto.", "c"))

    st.append(KeepTogether([P("Comparación de métodos (desafío extra)", "h3"), _imagen(figs["comparacion"][0], 12.5),
                            P(f"Figura. Proyección a {anio_f} con los tres métodos, ajustados sin {exc}.", "c")]))
    fil = [["Año"] + pr.MODELOS]
    for i, anio in enumerate(c["proy_sin"][pr.MODELOS[0]]["anio"]):
        fil.append([str(int(anio))] + [fmt(c["proy_sin"][m]["proyeccion"].iloc[i], 0) for m in pr.MODELOS])
    st.append(KeepTogether([_tabla(fil, [3.0, 4.3, 4.3, 4.4]), P("Tabla 5. Viajes proyectados por método.", "c")]))
    lin = c["proy_sin"][pr.MODELOS[0]]
    st.append(P(f"Intervalo de predicción de 95 % de la regresión lineal para {anio_f}: entre "
                f"{fmt(lin['inferior'].iloc[-1], 0)} y {fmt(lin['superior'].iloc[-1], 0)} viajes."))
    if c["exc"]:
        fil = [["Año"] + pr.MODELOS]
        for i, anio in enumerate(c["proy_todo"][pr.MODELOS[0]]["anio"]):
            fil.append([str(int(anio))] + [fmt(c["proy_todo"][m]["proyeccion"].iloc[i], 0) for m in pr.MODELOS])
        st.append(KeepTogether([_tabla(fil, [3.0, 4.3, 4.3, 4.4]),
                                P(f"Tabla 5b. Sensibilidad: proyección incluyendo {exc} en el ajuste.", "c")]))
    if len(c["bt"]):
        fil = [["Modelo", "Años de prueba", "MAE", "RMSE", "MAPE (%)"]]
        for _, r in c["bt"].iterrows():
            fil.append([r["modelo"], str(int(r["n_pruebas"])), fmt(r["mae"], 0), fmt(r["rmse"], 0), fmt(r["mape"], 1)])
        st.append(_tabla(fil, [5.0, 2.5, 3.0, 3.0, 2.5]))
        st.append(P("Tabla 6. Validación retrospectiva de origen móvil: en cada año de prueba el modelo usa solo datos "
                    "anteriores (se usan todos los años completos). MAE: error absoluto medio; RMSE: raíz del error cuadrático medio, penaliza errores grandes; "
                    "MAPE: error porcentual medio. Ordenado de menor a mayor MAE.", "c"))

    # ---------------- 7.5
    st.append(P("7.5 Interpretación", "h1"))
    for k, t in CLAVES_TEXTO[:4]:
        st.append(PBullet(t, tx[k]))
    st.append(KeepTogether([P("Pregunta final del desafío extra", "h3"), PBullet(CLAVES_TEXTO[4][1], tx["final"])]))

    # ---------------- 7.6
    st.append(P("7.6 Conclusión", "h1"))
    n = _palabras(tx["conclusion"])
    st.append(P(tx["conclusion"]))
    st.append(P(f"Extensión de la conclusión: {n} palabras.", "c"))
    if not 150 <= n <= 250:
        print(f"AVISO: la conclusión tiene {n} palabras; el enunciado pide entre 150 y 250.")

    # ---------------- ejecución y referencias
    st.append(P("8. Ejecución del Proyecto", "h1"))
    st.append(P("Desde la raíz del repositorio: (1) pip install -r requirements.txt; (2) python main.py, que genera "
                "datos/procesados/dataset_limpio.csv a partir de datos/originales/dataset.csv; (3) streamlit run app.py para "
                "abrir el dashboard; (4) python generar_informe4.py para regenerar este informe."))
    st.append(P("Referencias", "h1"))
    for r in ("Hyndman, R. J., y Athanasopoulos, G. (2021). Forecasting: Principles and Practice (3.ª ed.). OTexts. "
              "https://otexts.com/fpp3/",
              "McKinney, W. (2022). Python for Data Analysis (3.ª ed.). O'Reilly Media.",
              "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90-95.",
              "Harris, C. R., et al. (2020). Array programming with NumPy. Nature, 585, 357-362."):
        st.append(PBullet("", r))
    doc.build(st, onFirstPage=_portada, onLaterPages=_pagina)
    return ruta_pdf
