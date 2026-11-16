## ¿Qué medida estadística resultó más útil?
La comparación entre media y mediana junto con el coeficiente de variación. Mostró que total_anual es muy asimétrica (la media es 10,4 veces la mediana y el CV es 522%), por lo que el promedio simple engaña y conviene trabajar con totales agregados. Para estacionalidad, el promedio de pct_verano (37,7%) fue la medida más directa.

## ¿Qué indicador ayuda mejor a responder el problema?
Para la tendencia, la variación del flujo total entre el primer y el último año: -5,1% (tasa anual compuesta -0,9%); para la estacionalidad regional, el índice de estacionalidad y la concentración estival (pct_verano entre 25,5% y 55,8% según la región), porque resumen en una cifra comparable lo que la pregunta pide.

## ¿Qué gráfico comunica mejor los resultados?
El gráfico 02 (estacionalidad mensual por región), porque muestra en una sola figura la forma del año de cada región, el total nacional y el reparto uniforme de referencia. Para la tendencia, el gráfico 01 es el más claro.

## ¿Cómo verificaron los cálculos?
El programa ejecuta 7 comprobaciones automáticas en cada corrida (6 aprobadas en esta ejecución): contrasta media y mediana con NumPy, verifica que la suma por año, por región y por mes sea igual al total general, que los 12 meses sumen total_anual en cada fila, que pct_verano esté entre 0 y 100 y que los porcentajes mensuales de cada región sumen 100. El detalle está en la sección 5.

## ¿Qué resultado fue inesperado?
Lo más inesperado fue una media 10,4 veces mayor que la mediana, la caída de 58,5% del flujo total en 2020 y el pico fuera del verano en Ñuble y Antofagasta.

## ¿Qué análisis deberían realizar después?
Un análisis de series de tiempo mensuales por región (medias móviles y descomposición estacional) para proyectar el flujo, como plantea el objetivo del proyecto; comparar regiones de origen y destino; medir el efecto de eventos puntuales (por ejemplo la pandemia) sobre la tendencia; estudiar las rutas críticas a nivel comunal y contrastar con pruebas de hipótesis si las diferencias de estacionalidad entre regiones son estadísticamente significativas.

## Conclusión del avance
En este avance se calcularon estadísticas descriptivas para 15 variables numéricas y las frecuencias de 6 variables categóricas, se programaron 12 indicadores y se generaron 4 gráficos, todo exportado automáticamente con python main.py a la carpeta resultados/. Tendencia: el flujo nacional disminuyó 5,1% entre 2019 y 2025, con caídas en 2020, 2022 y 2025. Estacionalidad: a nivel nacional 37,1% del flujo ocurre entre diciembre y febrero, pero entre regiones la concentración estival va de 25,5% (Antofagasta) a 55,8% (Coquimbo), es decir, la estacionalidad varía de forma importante entre regiones. Las estadísticas descriptivas aportan el contexto (distribución asimétrica y muchos pares sin flujo) que obliga a analizar totales agregados en lugar de registros individuales. Como limitaciones, el análisis agrega registros de una matriz origen-destino muy dispersa y asimétrica, por lo que las conclusiones se basan en totales y porcentajes agregados; el siguiente avance puede profundizar con modelos de series de tiempo y proyección del flujo.
