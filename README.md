# Macro-data Turismo Chile (MDTC) — Proyecto 14: Evolución del Turismo Nacional e Internacional 🇨🇱

- **Institución:** Universidad Autónoma de Chile (Sede Temuco) · **Asignatura:** Programación Avanzada
- **Docente:** Alex Flores Fuentealba
- **Equipo de Desarrollo:** Benjamín Aguayo, Enzo Illanes, Jaime Panguinao
- **Repositorio:** https://github.com/BenjaAgx/Macro-data-Turismo-Chile-MDTC-
- **Avance actual:** Avance 4 – Dashboard interactivo, proyección y ejecutable independiente (`.exe`)

---

## 📊 Descripción del Proyecto
Análisis de la matriz de movilidad turística comunal (SERNATUR / INE, período 2008–2025) sobre un volumen de **649.393 registros históricos** para identificar tendencias, estacionalidad del flujo de visitantes y proyecciones futuras.

### Evolución del Desarrollo
* **Avance 1 y 2:** Ingesta, diagnóstico, limpieza y transformación del dataset original mediante un pipeline reproducible en Python y Pandas.
* **Avance 3:** Modularización en `src/`, cálculo automatizado de estadísticas descriptivas (`estadisticas.csv`), 12 indicadores clave (`indicadores.csv`), estacionalidad regional, gráficos analíticos y reporte ejecutivo (`avance_3.pdf`).
* **Avance 4 (Entrega Final):** Dashboard interactivo en Streamlit (`app.py`) con 5 filtros dinámicos, 7 KPIs, modelos de proyección (Regresión Lineal OLS, Promedio Móvil y Tasa de Crecimiento) y empaquetado como aplicación portátil para Windows (`Macro-data_Turismo_Chile.exe`).

---

## Pipeline de Procesamiento
```text
datos/originales/dataset.csv  (solo lectura - 649.393 registros)
   ↓ carga.py             Lectura (sep ';', latin-1, decimal ',')
   ↓ validaciones.py      Diagnóstico inicial (nulos, duplicados, fuera de rango)
   ↓ limpieza.py          Nombres de columnas, espacios, categorías, rangos, duplicados
   ↓ limpieza.py          Tratamiento de nulos (estrategia por variable)
   ↓ transformaciones.py  Tipos, fecha, total_anual, mes_pico, pct_verano, es_intrarregional, nivel_flujo
   ↓ validaciones.py      Validación de columnas, tipos y rangos
   ↓ carga.py             datos/procesados/dataset_limpio.csv
   ↓ estadisticas.py      resultados/estadisticas.csv
   ↓ indicadores.py       resultados/indicadores.csv (+ estacionalidad_regional.csv)
   ↓ visualizaciones.py   resultados/graficos/grafico_01..04.png
   ↓ informe.py           reportes/avance_3.pdf
   ↓ app.py / lanzador.py Dashboard interactivo Streamlit + Ejecutable Windows (.exe)


## Estructura del Repositorio

├── datos/
│   ├── originales/            # dataset.csv original (no se versiona ni se modifica)
│   ├── procesados/            # dataset_limpio.csv y agregado_dashboard.csv
│   ├── README.md
│   └── instrucciones_descarga.txt
├── resultados/                # estadisticas.csv, indicadores.csv, estacionalidad_regional.csv, graficos/ (autogenerado)
├── reportes/                  # avance_1.pdf, avance_2.pdf, avance_3.pdf, avance_4.pdf, resumen_ejecucion.md
├── src/
│   ├── __init__.py
│   ├── carga.py               # Lectura y escritura de archivos
│   ├── limpieza.py            # Normalización, duplicados, rangos y nulos
│   ├── transformaciones.py    # Conversión de tipos y variables nuevas
│   ├── validaciones.py        # Diagnóstico y validación de columnas, tipos y rangos
│   ├── reporte.py             # Bitácora de cambios y resumen en Markdown
│   ├── configuracion.py       # (Avance 3) Rutas, constantes y carga del dataset limpio
│   ├── estadisticas.py        # (Avance 3) Estadística descriptiva y verificación de cálculos
│   ├── indicadores.py         # (Avance 3) Indicadores y tabla de estacionalidad regional
│   ├── visualizaciones.py     # (Avance 3) Gráficos con Pyplot
│   ├── informe.py             # (Avance 3) Genera reportes/avance_3.pdf
│   ├── proyeccion.py          # (Avance 4) Agregación, filtros, indicadores dinámicos y modelos
│   ├── graficos_dashboard.py  # (Avance 4) Figuras del dashboard e informe
│   └── informe_avance4.py     # (Avance 4) Genera reportes/avance_4.pdf
├── app.py                     # Interfaz principal del dashboard en Streamlit
├── lanzador.py                # Script puente para empaquetado independiente con PyInstaller
├── main.py                    # Ejecución completa del pipeline (Avances 2 y 3)
├── generar_informe4.py        # Generación del reporte final Avance 4
├── verificar_entrega.py       # Validación automática de requisitos de entrega (11 checks)
└── requirements.txt           # Dependencias (pandas, numpy, matplotlib, streamlit)

## Instrucciones de Ejecución

Opción 1: Ejecutable Independiente para Windows (.exe)
El proyecto fue empaquetado mediante PyInstaller (--onefile) junto con lanzador.py, congelando el intérprete de Python, librerías, módulos src/ y datos agregados (agregado_dashboard.csv) en un único archivo autocontenido:

Ubicar el archivo Macro-data_Turismo_Chile.exe (generado en la carpeta dist/).

Hacer doble clic sobre el archivo; levanta automáticamente el servidor local de Streamlit y abre el dashboard en el navegador sin requerir Python ni dependencias instaladas.

Opción 2: Ejecución desde Código Fuente
Requisitos: Python 3.13 (compatible con versiones anteriores soportadas por:

git clone [https://github.com/BenjaAgx/Macro-data-Turismo-Chile-MDTC-.git](https://github.com/BenjaAgx/Macro-data-Turismo-Chile-MDTC-.git) && cd Macro-data-Turismo-Chile-MDTC-

Descargar el dataset: Obtener dataset.csv (164 MB) desde el enlace indicado en datos/instrucciones_descarga.txt y guardarlo en datos/originales/dataset.csv.

Instalar dependencias:

pip install -r requirements.txt

Ejecutar el pipeline de datos (Avances 2 y 3):

python main.py

Iniciar el dashboard interactivo (Avance 4):

streamlit run app.py

##   Decisiones de Limpieza (Resumen)

## Decisiones de Limpieza (Resumen)
TemaDecisiónDuplicados exactosSe elimina la repetición y se conserva la primeraIdentificadores repetidos (origen-destino-año)Se informan, no se modificanFlujos negativos / códigos de región fuera de 1-16Pasan a nulo y se tratan como nulosAño fuera de 2008-2025 (ANIO_MIN/ANIO_MAX en src/validaciones.py) o nuloSe elimina la filaCódigos y nombres territoriales nulosSe recuperan desde su par código↔nombre; si no, desconocido o se eliminaMeses nulosFila sin ningún mes: se elimina. Resto: 0 + columna n_meses_imputadosOtras columnas con nulosMediana (numéricas) o desconocido (texto)Toda eliminación y corrección queda registrada en reportes/resumen_ejecucion.md.

##   Tecnologías Utilizadas
Lenguaje: Python 3.13

Procesamiento y Análisis: Pandas, NumPy

Visualización e Interfaz: Streamlit, Matplotlib

Empaquetado y Control de Versiones: PyInstaller (--onefile), Git
