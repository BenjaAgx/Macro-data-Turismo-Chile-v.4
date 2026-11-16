# Proyecto 14: Evolución del Turismo Nacional e Internacional

- **Institución:** Universidad Autónoma de Chile · **Asignatura:** Programación Avanzada
- **Docente:** Alex Flores Fuentealba
- **Integrantes:** Benjamín Aguayo, Enzo Illanes, Jaime Panguinao
- **Repositorio:** https://github.com/BenjaAgx/Macro-data-Turismo-Chile-MDTC-
- **Avance actual:** Avance 4 – Dashboard interactivo y proyección

## Descripción
Análisis de la matriz de movilidad turística comunal (SERNATUR / INE) para identificar tendencias
y estacionalidad del flujo de visitantes. Este avance deja el dataset listo para el análisis
mediante un pipeline reproducible en Python + Pandas.

## Pipeline
```
datos/originales/dataset.csv  (solo lectura)
   ↓ carga.py            Lectura (sep ';', latin-1, decimal ',')
   ↓ validaciones.py     Diagnóstico inicial (nulos, duplicados, fuera de rango)
   ↓ limpieza.py         Nombres de columnas, espacios, categorías, rangos, duplicados
   ↓ limpieza.py         Tratamiento de nulos (estrategia por variable)
   ↓ transformaciones.py Tipos, fecha, total_anual, mes_pico, pct_verano, es_intrarregional, nivel_flujo
   ↓ validaciones.py     Validación de columnas, tipos y rangos
   ↓ carga.py            datos/procesados/dataset_limpio.csv
   ↓ estadisticas.py     resultados/estadisticas.csv
   ↓ indicadores.py      resultados/indicadores.csv (+ estacionalidad_regional.csv)
   ↓ visualizaciones.py  resultados/graficos/grafico_01..04.png
   ↓ informe.py          reportes/avance_3.pdf
```

## Estructura
```
├── datos/
│   ├── originales/            # dataset.csv original (no se versiona ni se modifica)
│   ├── procesados/            # dataset_limpio.csv (+ muestra de 1000 filas)
│   ├── README.md
│   └── instrucciones_descarga.txt
├── resultados/                # estadisticas.csv, indicadores.csv, estacionalidad_regional.csv, graficos/ (autogenerado)
├── reportes/                  # avance_1.pdf, avance_2.pdf, avance_3.pdf (autogenerado), resumen_ejecucion.md
├── src/
│   ├── __init__.py
│   ├── carga.py               # lectura y escritura de archivos
│   ├── limpieza.py            # normalización, duplicados, rangos y nulos
│   ├── transformaciones.py    # conversión de tipos y variables nuevas
│   ├── validaciones.py        # diagnóstico y validación de columnas, tipos y rangos
│   ├── reporte.py             # bitácora de cambios y resumen en Markdown
│   ├── configuracion.py       # (Avance 3) rutas, constantes y carga del dataset limpio
│   ├── estadisticas.py        # (Avance 3) estadística descriptiva y verificación de cálculos
│   ├── indicadores.py         # (Avance 3) indicadores y tabla de estacionalidad regional
│   ├── visualizaciones.py     # (Avance 3) gráficos con Pyplot
│   └── informe.py             # (Avance 3) genera reportes/avance_3.pdf
├── main.py
└── requirements.txt
```

## Requisitos
Python 3.13 (el código no usa nada específico de una versión; las versiones mínimas de `requirements.txt` son las primeras con soporte para 3.13).

## Instrucciones de ejecución
1. Clonar: `git clone https://github.com/BenjaAgx/Macro-data-Turismo-Chile-MDTC-.git && cd Macro-data-Turismo-Chile-MDTC-`
2. Descargar `dataset.csv` (164 MB) desde el enlace de `datos/instrucciones_descarga.txt` y guardarlo en `datos/originales/dataset.csv`.
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar desde la raíz: `python main.py`

Salidas: `datos/procesados/dataset_limpio.csv` y `reportes/resumen_ejecucion.md`
(tablas de diagnóstico, nulos, transformaciones y comparación antes/después para el informe).

## Decisiones de limpieza (resumen)
| Tema | Decisión |
| --- | --- |
| Duplicados exactos | Se elimina la repetición y se conserva la primera |
| Identificadores repetidos (origen-destino-año) | Se informan, no se modifican |
| Flujos negativos / códigos de región fuera de 1-16 | Pasan a nulo y se tratan como nulos |
| Año fuera de 2008-2025 (`ANIO_MIN`/`ANIO_MAX` en `src/validaciones.py`) o nulo | Se elimina la fila |
| Códigos y nombres territoriales nulos | Se recuperan desde su par código↔nombre; si no, `desconocido` o se elimina |
| Meses nulos | Fila sin ningún mes: se elimina. Resto: 0 + columna `n_meses_imputados` |
| Otras columnas con nulos | Mediana (numéricas) o `desconocido` (texto) |

Toda eliminación y corrección queda registrada en `reportes/resumen_ejecucion.md`.

## Avance 3: estadística, indicadores y gráficos
`python main.py` ejecuta **todo** desde la raíz: el pipeline del Avance 2 (si existe `datos/originales/dataset.csv`)
y luego el Avance 3 sobre `datos/procesados/dataset_limpio.csv`. Si el archivo completo no está, usa la muestra
`dataset_limpio_muestra.csv` (con aviso). Opción: `python main.py --solo-avance3` omite el Avance 2.

| Salida | Contenido |
| --- | --- |
| `resultados/estadisticas.csv` | n, media, mediana, mín, máx, rango, desv. estándar, cuartiles, CV, % ceros y frecuencias |
| `resultados/indicadores.csv` | 12 indicadores: método de cálculo, resultado e interpretación |
| `resultados/estacionalidad_regional.csv` | % mensual, % de verano e índice de estacionalidad por región destino |
| `resultados/graficos/grafico_01..04.png` | evolución anual, estacionalidad por región, % de verano por región, distribución |
| `reportes/avance_3.pdf` | informe con tablas, gráficos, interpretaciones, verificación y evidencia de ejecución |
| `reportes/ejecucion_avance3.txt` | salida completa de consola de la última ejecución |

| Módulo | Responsabilidad |
| --- | --- |
| `src/estadisticas.py` | Estadísticas descriptivas y verificación cruzada de cálculos |
| `src/indicadores.py` | Indicadores del proyecto (tendencia y estacionalidad) |
| `src/visualizaciones.py` | Crear y guardar los gráficos |
| `main.py` | Ejecutar todo el proceso |

### Respuestas finales y verificación de entrega
- La primera vez que se ejecuta `python main.py` se crea `reportes/respuestas_finales.md` con un **borrador** de las preguntas
  finales y la conclusión. El equipo lo reescribe con sus propias palabras, borra la línea `<!-- BORRADOR ... -->` y vuelve a
  ejecutar `python main.py` (o `python main.py --solo-avance3`) para regenerar `reportes/avance_3.pdf`.
- `python verificar_entrega.py` revisa la lista final de entrega del enunciado (archivos, módulos, README, commits, informe
  generado con el dataset completo y respuestas ya escritas).

## Avance 4: dashboard interactivo y proyección
```
streamlit run app.py
```
Requiere `datos/procesados/dataset_limpio.csv` (se genera con `python main.py`). La primera vez, el dashboard crea
`datos/procesados/agregado_dashboard.csv` (tabla liviana, **sí se puede subir a GitHub**) y desde entonces arranca sin el
dataset de 164 MB.

| Elemento | Implementación |
| --- | --- |
| Filtros (5) | Rango de años, región destino, región origen, tipo de viaje (intra/interregional), nivel de flujo |
| Indicadores (7) | Total acumulado, promedio anual, año máximo, año mínimo, variación último año, crecimiento anual compuesto, concentración en verano |
| Gráficos | Histórico anual, estacionalidad mensual, proyección con intervalo 95 %, comparación de métodos |
| Modelos | Regresión lineal, promedio móvil, tasa de crecimiento promedio (selección y comparación en el dashboard) |
| Parámetros | Modelo, años a proyectar, ventana del promedio móvil, años excluidos del ajuste, intervalo on/off |

| Módulo | Responsabilidad |
| --- | --- |
| `app.py` | Interfaz Streamlit |
| `src/proyeccion.py` | Agregación, filtros, indicadores dinámicos, modelos y validación retrospectiva |
| `src/graficos_dashboard.py` | Figuras (las usan el dashboard y el informe) |
| `src/informe_avance4.py` + `generar_informe4.py` | Genera `reportes/avance_4.pdf` |

### Informe del Avance 4
1. Ejecuta el dashboard y guarda capturas en `reportes/capturas/` como `vista_historica.png`, `vista_proyectada.png` e `indicadores.png`.
2. `python generar_informe4.py` crea `reportes/avance_4.pdf` y, la primera vez, `reportes/textos_avance4.md` con un **borrador** de
   las interpretaciones y la conclusión (150-250 palabras). Reescríbanlo con sus palabras, borren la línea `<!-- BORRADOR ... -->`
   y vuelvan a ejecutar el comando.


## Mejoras de calidad incorporadas en la revisión del Avance 4

- Validación de horizonte, años únicos, valores finitos y flujos no negativos antes de proyectar.
- Tasa de crecimiento calculada con tasas logarítmicas anualizadas, lo que permite manejar años no consecutivos.
- Validación retrospectiva de origen móvil en varios años, con MAE, RMSE y MAPE, en lugar de evaluar solo el último año.
- Diferenciación entre el intervalo de predicción del modelo lineal y las bandas orientativas de los otros métodos.
- Etiquetas de indicadores corregidas: flujo máximo y mínimo anual, indicando el año correspondiente.

### Ejecución

```bash
pip install -r requirements.txt
python main.py
streamlit run app.py
```

El archivo original `dataset.csv` debe estar en `datos/originales/dataset.csv` para generar el dataset procesado. El ZIP de revisión recibido no incluía el CSV original ni el dataset limpio, por lo que las pruebas incluidas validan los modelos con una serie sintética de control y no reemplazan la prueba de integración con los datos oficiales.
