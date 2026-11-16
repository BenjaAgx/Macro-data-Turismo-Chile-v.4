# Validación técnica de la revisión del Avance 4

## Comprobaciones realizadas
- Compilación sintáctica de los módulos Python: correcta.
- Los tres modelos generan tres períodos futuros en una serie de control.
- Proyecciones y bandas finitas y no negativas en la serie de control.
- Backtesting de origen móvil: métricas MAE, RMSE y MAPE para los tres métodos.

## Resultados de ejemplo (serie sintética, no datos oficiales)
- Regresión lineal: [18843214, 19571845, 20300476]
- Promedio móvil: [18070000, 19726667, 19968889]
- Tasa de crecimiento promedio: [22823958, 23560970, 24321781]

## Limitación
No se recibió el dataset oficial ni el dataset procesado dentro del ZIP. No se certificó la ejecución integrada de Streamlit ni se calcularon proyecciones reales.
