# Resumen de ejecución del pipeline (insumo para reportes/avance_2.pdf)

## 1. Diagnóstico inicial (dataset original)

| Columna | Tipo | Nulos | % nulos |
| --- | --- | --- | --- |
| CUT Comuna Origen | int64 | 0 | 0.000% |
| Comuna Origen | str | 0 | 0.000% |
| CUT Provincia Origen | int64 | 0 | 0.000% |
| Provincia Origen | str | 0 | 0.000% |
| CUT Región Origen | int64 | 0 | 0.000% |
| Región Origen | str | 0 | 0.000% |
| CUT Comuna Destino | int64 | 0 | 0.000% |
| Comuna Destino | str | 0 | 0.000% |
| Destino Turístico | str | 0 | 0.000% |
| CUT Provincia Destino | int64 | 0 | 0.000% |
| Provincia Destino | str | 0 | 0.000% |
| CUT Región Destino | int64 | 0 | 0.000% |
| Región Destino | str | 0 | 0.000% |
| Anio | int64 | 0 | 0.000% |
| Enero | float64 | 0 | 0.000% |
| Febrero | float64 | 0 | 0.000% |
| Marzo | float64 | 0 | 0.000% |
| Abril | float64 | 0 | 0.000% |
| Mayo | float64 | 0 | 0.000% |
| Junio | float64 | 0 | 0.000% |
| Julio | float64 | 0 | 0.000% |
| Agosto | float64 | 0 | 0.000% |
| Septiembre | float64 | 0 | 0.000% |
| Octubre | float64 | 0 | 0.000% |
| Noviembre | float64 | 0 | 0.000% |
| Diciembre | float64 | 0 | 0.000% |

Fuera de rango por columna: ninguno

## 2. Correcciones

| Corrección aplicada | Valores afectados |
| --- | --- |
| Espacios sobrantes / vacíos en 'destino_turistico' | 2,202 |

## 3. Registros eliminados

| Motivo de eliminación | Filas eliminadas |
| --- | --- |
| (ninguna) | 0 |

## 4. Tratamiento de nulos

| Variable | Nulos iniciales | Estrategia | Justificación | Nulos finales |
| --- | --- | --- | --- | --- |

## 5. Transformaciones

| Variable original | Transformación | Resultado | Tipo final |
| --- | --- | --- | --- |
| anio | Conversión a entero | Año como entero compacto | int16 |
| cut_comuna_origen, cut_region_origen, cut_comuna_destino, cut_region_destino | Conversión a entero | Códigos CUT enteros | int32 |
| enero ... diciembre | Conversión numérica (pd.to_numeric) | Flujos mensuales numéricos | float64 |
| nombres de comuna y región | Normalización de categorías (texto limpio + category) | Nombres únicos por categoría | category |
| anio | pd.to_datetime | fecha_periodo = 1 de enero del año | datetime64[ns] |
| enero ... diciembre | Nueva variable: suma de los 12 meses | total_anual | float64 |
| enero ... diciembre | Nueva variable: mes con mayor flujo | mes_pico | category |
| diciembre, enero, febrero, total_anual | Nueva variable: % del flujo anual en verano (dic-feb) | pct_verano (0-100) | float64 |
| cut_region_origen, cut_region_destino | Nueva variable binaria: viaje dentro de la misma región | es_intrarregional (1 = sí) | int8 |
| total_anual | Clasificación por rangos (terciles de flujo > 0) | nivel_flujo: sin flujo / bajo / medio / alto | category |

## 6. Validaciones finales

| Validación | Resultado | Detalle |
| --- | --- | --- |
| Columnas requeridas presentes | OK | todas |
| Tipos numéricos en meses, año y códigos | OK | correctos |
| Valores dentro de rango | OK | sin fuera de rango |
| Sin nulos en identificadores ni meses | OK | 0 nulos |
| Sin filas duplicadas | OK | 0 duplicadas |
| total_anual coincide con suma de meses | OK | diferencia máx. 5.00e-03 |

## 7. Comparación antes / después

| Indicador | Antes | Después |
| --- | --- | --- |
| Filas | 649,393 | 649,393 |
| Columnas | 26 | 33 |
| Valores nulos | 0 | 0 |
| Filas duplicadas | 0 | 0 |
| Identificadores repetidos (origen-destino-año) | 0 | 0 |
| Valores fuera de rango | 0 | 0 |
| Variables transformadas | 0 | 6 |
| Variables nuevas | 0 | 7 |
