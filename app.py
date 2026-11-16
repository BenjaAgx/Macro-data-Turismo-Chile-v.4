"""Avance 4: dashboard interactivo de turismo. Ejecutar desde la raíz:  streamlit run app.py"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src import graficos_dashboard as gd
from src import proyeccion as pr
from src.configuracion import UNIDAD, fmt, nombre_corto

st.set_page_config(page_title="Turismo Chile - Dashboard", page_icon="📊", layout="wide")


@st.cache_data(show_spinner="Cargando datos...")
def cargar():
    return pr.cargar_agregado()


def mostrar(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


try:
    agg, fuente = cargar()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

st.title("📊 Evolución del turismo nacional e internacional - Chile")
st.caption(f"Fuente: matriz de movilidad turística comunal (SERNATUR / INE) · datos: {fuente}")
if "MUESTRA" in fuente:
    st.warning("Se está usando una muestra del dataset: los resultados son solo referenciales.")

# ------------------------------------------------------------------ BARRA LATERAL: FILTROS Y PARÁMETROS
anios_disp = sorted(agg["anio"].unique())
regiones = sorted(r for r in agg["region_destino"].unique() if r.lower() != "desconocido")
orig = sorted(r for r in agg["region_origen"].unique() if r.lower() != "desconocido")
nombre = {r: nombre_corto(r) for r in set(regiones) | set(orig)}

with st.sidebar:
    st.header("🔎 Filtros")
    rango = st.slider("Rango de años", int(anios_disp[0]), int(anios_disp[-1]),
                      (int(anios_disp[0]), int(anios_disp[-1])))
    sel_dest = st.multiselect("Región destino", regiones, format_func=nombre.get,
                              placeholder="Todas las regiones")
    sel_orig = st.multiselect("Región origen", orig, format_func=nombre.get,
                              placeholder="Todas las regiones")
    tipo = st.radio("Tipo de viaje", ["Todos", "Intrarregional", "Interregional"], horizontal=True)
    niveles = st.multiselect("Nivel de flujo del registro", ["bajo", "medio", "alto", "sin flujo"],
                             default=["bajo", "medio", "alto"],
                             help="Tercil del total anual de cada par origen-destino (calculado en el Avance 2).")

    st.header("⚙️ Proyección")
    modelo = st.selectbox("Modelo", pr.MODELOS)
    horizonte = st.slider("Años a proyectar", 1, 10, 3)
    ventana = 3
    if modelo == "Promedio móvil":
        ventana = st.slider("Ventana del promedio móvil (años)", 2, 5, 3)
    mostrar_ic = st.checkbox("Mostrar banda de incertidumbre", value=True)

datos = pr.filtrar(agg, rango, sel_dest, sel_orig, tipo, niveles)
serie = pr.serie_anual(datos)
faltan = pr.meses_faltantes(agg)                      # años con meses sin datos (p. ej. el año en curso)
incompletos = [a for a in faltan if a in serie.index]
serie_comp = serie.drop(index=incompletos)           # solo años completos: base de modelos e indicadores

with st.sidebar:
    candidatos = [int(a) for a in serie_comp.index[:-1]]  # el último año completo no se puede excluir
    excluir = st.multiselect("Excluir años del ajuste del modelo", candidatos,
                             help="Útil para años atípicos (p. ej. 2020-2021 por la pandemia). "
                                  "Siguen visibles en el gráfico histórico.")

if serie.empty or serie.sum() == 0:
    st.warning("Los filtros no dejan datos. Amplía la selección.")
    st.stop()

serie_modelo = serie_comp.drop(index=excluir, errors="ignore")
for a in incompletos:
    st.warning(f"{a} es un año incompleto (sin datos de {', '.join(faltan[a])}). Se muestra en gris, pero no se usa "
               "para ajustar los modelos ni para los indicadores anuales, porque su total sería artificialmente bajo.")

# ------------------------------------------------------------------ INDICADORES
st.subheader("Indicadores de la selección")
inds = pr.indicadores_dinamicos(datos, incompletos)
cols = st.columns(len(inds)) if inds else []
for col, (nom, val, det) in zip(cols, inds):
    es_pct = "%" in det
    texto = (fmt(val, 1) + " %") if es_pct else fmt(val, 0)
    col.metric(nom, texto, help=det)
    col.caption(det)

# ------------------------------------------------------------------ PESTAÑAS
tab_hist, tab_proy, tab_comp, tab_datos = st.tabs(
    ["📈 Vista histórica", "🔮 Proyección", "⚖️ Comparar métodos", "🗂️ Datos"])

with tab_hist:
    c1, c2 = st.columns([3, 2])
    with c1:
        mostrar(gd.fig_historico(serie, excluidos=list(excluir) + incompletos))
    with c2:
        mostrar(gd.fig_estacionalidad(pr.serie_mensual(datos)))
    if len(serie) >= 2:
        var = (serie_comp.pct_change() * 100).reindex(serie.index)     # sin variación para años incompletos
        tabla = pd.DataFrame({"Año": serie.index.astype(int), f"Total ({UNIDAD})": serie.to_numpy(),
                              "Variación anual (%)": var.to_numpy()})
        st.dataframe(tabla.style.format({f"Total ({UNIDAD})": "{:,.0f}", "Variación anual (%)": "{:+.1f}"},
                                        na_rep="-"), hide_index=True, use_container_width=True)

with tab_proy:
    if len(serie_modelo) < 3:
        st.warning("Se necesitan al menos 3 años para proyectar: amplía el rango o quita exclusiones.")
    else:
        proy = pr.proyectar(serie_modelo, modelo, horizonte, ventana)
        mostrar(gd.fig_proyeccion(serie_modelo, serie.loc[[a for a in serie.index if a in excluir or a in incompletos]],
                                  proy, modelo, mostrar_ic))
        ult = serie_modelo.iloc[-1]
        fin = proy["proyeccion"].iloc[-1]
        k1, k2, k3 = st.columns(3)
        k1.metric(f"Proyección {int(proy['anio'].iloc[0])}", fmt(proy["proyeccion"].iloc[0], 0))
        k2.metric(f"Proyección {int(proy['anio'].iloc[-1])}", fmt(fin, 0),
                  f"{(fin / ult - 1) * 100:+.1f} % vs. {int(serie_modelo.index[-1])}".replace(".", ","))
        r2 = pr.r2_lineal(serie_modelo)
        k3.metric("R² de la tendencia lineal", fmt(r2, 2) if r2 == r2 else "-",
                  help="Qué parte de la variación histórica explica una recta. Cerca de 0 = tendencia débil.")
        st.dataframe(proy.rename(columns={"anio": "Año", "proyeccion": "Proyección",
                                          "inferior": "Límite inferior 95 %", "superior": "Límite superior 95 %"})
                     .style.format({"Proyección": "{:,.0f}", "Límite inferior 95 %": "{:,.0f}",
                                    "Límite superior 95 %": "{:,.0f}"}), hide_index=True, use_container_width=True)
        if modelo == "Regresión lineal":
            st.info("La banda corresponde a un intervalo de predicción aproximado del 95 % bajo los supuestos del modelo lineal. "
                    "No incorpora cambios económicos, sanitarios ni políticas turísticas.")
        else:
            st.info("La banda es una estimación orientativa de incertidumbre basada en la variabilidad histórica; "
                    "no es un intervalo de confianza estadístico formal.")

with tab_comp:
    if len(serie_modelo) < 3:
        st.warning("Se necesitan al menos 3 años para comparar métodos.")
    else:
        proys = {m: pr.proyectar(serie_modelo, m, horizonte, ventana) for m in pr.MODELOS}
        mostrar(gd.fig_comparacion(serie_modelo, proys))
        fin = pd.DataFrame({m: p["proyeccion"].to_numpy() for m, p in proys.items()},
                           index=proys[pr.MODELOS[0]]["anio"].to_numpy())
        fin.index.name = "Año"
        st.dataframe(fin.style.format("{:,.0f}"), use_container_width=True)
        bt = pr.backtest(serie_modelo, ventana)
        if len(bt):
            st.markdown("**Validación retrospectiva de origen móvil:** cada modelo se prueba en varios años; "
                        "para cada año solo utiliza los datos anteriores. Menores MAE/RMSE indican menor error.")
            bt = bt.rename(columns={"modelo": "Modelo", "n_pruebas": "Años de prueba", "mae": "MAE",
                                    "rmse": "RMSE", "mape": "MAPE (%)"})
            st.dataframe(bt.style.format({"MAE": "{:,.0f}", "RMSE": "{:,.0f}", "MAPE (%)": "{:.1f}"}),
                         hide_index=True, use_container_width=True)
            mejor = bt.iloc[0]["Modelo"]
            st.success(f"En esta selección, **{mejor}** obtuvo el menor MAE en la validación retrospectiva. "
                       "La comparación es orientativa y depende del período evaluado.")

with tab_datos:
    st.write(f"{fmt(len(datos), 0)} combinaciones año-origen-destino en la selección.")
    resumen = datos.groupby("region_destino")["total_anual"].sum().sort_values(ascending=False).reset_index()
    resumen["region_destino"] = resumen["region_destino"].map(nombre)
    resumen["% del total"] = resumen["total_anual"] / resumen["total_anual"].sum() * 100
    resumen.columns = ["Región destino", f"Total ({UNIDAD})", "% del total"]
    st.dataframe(resumen.style.format({f"Total ({UNIDAD})": "{:,.0f}", "% del total": "{:.1f}"}),
                 hide_index=True, use_container_width=True)
    st.download_button("⬇️ Descargar serie anual (CSV)",
                       serie.rename("total_anual").reset_index().to_csv(index=False).encode("utf-8"),
                       file_name="serie_anual_seleccion.csv", mime="text/csv")
