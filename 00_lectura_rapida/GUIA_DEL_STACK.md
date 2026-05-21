# Guía del Stack Tecnológico — Tesis MIA 303

**Para entender qué herramientas se usan y por qué.** Documento de 5 minutos de lectura.

---

## Resumen en una frase

**Python 3.13 + DuckDB + JupyterLab** — tres herramientas gratuitas, ampliamente usadas en la industria, que reemplazan a un stack tradicional de "PostgreSQL + servidor + ETL pesado" con un esfuerzo de instalación 10 veces menor.

---

## Qué hace cada herramienta

### 1. Python 3.13

**Qué es:** Lenguaje de programación de propósito general. Es el estándar de facto en ciencia de datos y machine learning desde hace una década.

**Por qué Python y no otro lenguaje:** porque todas las librerías de procesamiento de lenguaje natural que necesita la tesis (Hugging Face Transformers, BioBERT, ClinicalBERT, spaCy, scikit-learn) están escritas en Python o tienen su mejor API en Python.

**Versión usada:** 3.13.5 (la más reciente al momento del proyecto).

**Instalación:** descarga desde python.org o, más cómodo, vía Anaconda (que incluye Python + cientos de librerías científicas precompiladas).

### 2. DuckDB

**Qué es:** Motor de base de datos analítico, ultraliviano, sin servidor. Funciona como una librería de Python.

**Para qué sirve en esta tesis:** consultar el dataset MIMIC-IV (15+ GB) con SQL sin tener que cargarlo en memoria. DuckDB lee directamente los archivos `.csv.gz` comprimidos, ejecuta queries optimizadas en streaming, y solo carga en memoria el resultado.

**Por qué DuckDB y no PostgreSQL:**

| Aspecto | PostgreSQL | DuckDB |
|---|---|---|
| Instalación | 2-3 días en Windows | `pip install duckdb` en 30 segundos |
| Requiere servicio corriendo | Sí | No |
| Necesita configurar usuarios, permisos, puertos | Sí | No |
| Lee archivos .csv.gz directamente | No (hay que cargarlos primero) | Sí |
| Velocidad en queries analíticas | Rápida con buenos índices | 10-100x más rápida sin configuración |
| Uso de memoria | Alto (necesita buffer pool grande) | Bajo (streaming nativo) |
| Apto para investigación individual | Excesivo | Ideal |

**Versión usada:** 1.5.2.

**Por qué es "la herramienta correcta para esta tesis":** porque permite enfocarse en la INVESTIGACIÓN, no en administración de base de datos. La tesis es de IA aplicada a salud, no de ingeniería de datos.

### 3. JupyterLab

**Qué es:** Entorno de desarrollo basado en notebooks. Mezcla en un mismo documento código, resultados de ejecución, gráficos y texto explicativo en Markdown.

**Para qué sirve en esta tesis:** desarrollar el pipeline NLP de forma iterativa, viendo los resultados de cada celda en tiempo real. Permite separar la lógica en bloques pequeños testeables y conservar la narrativa del análisis junto al código.

**Por qué JupyterLab y no scripts puros:**
- Permite **exploración interactiva** — pruebas una query, ves el resultado, ajustas, sigues. Ideal para investigación.
- **Documenta automáticamente** el proceso — el notebook ES la documentación.
- **Comunica resultados** — un revisor puede leer el notebook como artículo: texto + código + gráficos en orden.
- **Reproducibilidad** — al ejecutar el notebook completo, cualquier persona obtiene los mismos resultados que el autor.

**Versión usada:** 4.5.7.

---

## Cómo se conectan las tres

```
┌─────────────────────────────────────────────────────────┐
│  JupyterLab (interfaz de desarrollo iterativo)          │
│                                                         │
│   ┌──────────────────────────────────────────────────┐  │
│   │ Notebook .ipynb                                  │  │
│   │                                                  │  │
│   │   Celda Markdown — explicación                   │  │
│   │   Celda Python  — código                         │  │
│   │      │                                           │  │
│   │      ▼                                           │  │
│   │   import duckdb                                  │  │
│   │   con = duckdb.connect("mimic.db")               │  │
│   │   resultado = con.sql("SELECT ...").df()         │  │
│   │      │                                           │  │
│   │      ▼                                           │  │
│   │   DataFrame de pandas                            │  │
│   │   gráficos, métricas, NLP, ML...                 │  │
│   └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼ (DuckDB lee los archivos sin copiarlos)
┌─────────────────────────────────────────────────────────┐
│  Disco local                                            │
│   C:\MIMIC\note\note\discharge.csv.gz      (1.14 GB)    │
│   C:\MIMIC\mimiciv\hosp\admissions.csv.gz   (futuro)    │
└─────────────────────────────────────────────────────────┘
```

**El detalle clave:** DuckDB nunca carga los 1.14 GB de `discharge.csv.gz` en memoria. Cuando ejecutas una query, DuckDB descomprime sobre la marcha solo las columnas y filas que necesita, y entrega el resultado final como DataFrame a Python. Eso es lo que hace posible procesar 331,793 epicrisis en una laptop sin que se quede sin memoria.

---

## Otras librerías de Python que se instalan junto

Estas son librerías auxiliares que el pipeline usa pero que ya vienen prácticamente en cualquier instalación científica de Python:

| Librería | Función en la tesis |
|---|---|
| **pandas** | Manipulación de DataFrames. Estándar de facto en data science. Cuando DuckDB entrega resultados, los recibe pandas. |
| **pyarrow** | Acelera la conversión entre formatos columnar (DuckDB ↔ pandas). 5-10x más rápido que la conversión nativa. |
| **tqdm** | Barras de progreso bonitas para loops largos. Esencial cuando procesas miles de notas. |
| **matplotlib** | Gráficos básicos (histogramas, líneas, barras) para el análisis exploratorio. |

**Instalación completa de todo el stack en una línea:**

```bash
pip install duckdb pandas pyarrow tqdm jupyterlab matplotlib
```

Total descargado: aproximadamente 200 MB. Tiempo: 2-3 minutos.

---

## Para la Fase 2 (NLP biomédico) se sumarán

Cuando arranque la fase de fine-tuning de modelos transformer, se agregarán a este stack:

| Librería | Para qué |
|---|---|
| **transformers** (Hugging Face) | Carga BioBERT, ClinicalBERT, DistilBERT preentrenados |
| **torch** (PyTorch) | Backend de los modelos de deep learning |
| **scikit-learn** | Métricas estándar (precision, recall, F1, kappa de Cohen) |
| **xgboost** | Modelo tabular para la Etapa 2 multimodal |
| **scispacy** | NER biomédico + linking a UMLS Concept Unique Identifiers |

Esas son opcionales para la fase exploratoria — solo se instalan cuando se necesitan.

---

## Resumen para alguien que solo quiere ejecutar el código

Si recibes este repositorio y quieres correr el `tesis_pipeline.py`:

```bash
# 1. Instalar Python (si no lo tienes) desde python.org

# 2. Instalar las dependencias
pip install duckdb pandas pyarrow tqdm

# 3. Ajustar las rutas en tesis_pipeline.py (sección CONFIGURACIÓN)
#    Cambia PATH_NOTAS para que apunte a tu carpeta con discharge.csv.gz

# 4. Ejecutar
python tesis_pipeline.py
```

Eso es todo. No hay servidores que levantar, no hay puertos que abrir, no hay credenciales que configurar.

---

## Por qué este stack es "lo más simple sin complicarte"

Tres principios de diseño detrás de esta elección:

1. **Cero administración de servicios.** No corres ningún daemon en background. Si apagas la PC, todo queda intacto.

2. **Una sola fuente de verdad.** Los datos viven en su archivo `.csv.gz` original — no se duplican en ninguna base. El archivo de DuckDB (`mimic.db`) solo guarda metadatos y vistas, no copia.

3. **Reversibilidad total.** Si en el futuro decides migrar a PostgreSQL o BigQuery, todo el código DuckDB es código SQL estándar — solo cambias el connector. No hay que reescribir nada.

---

## Cita final

Si necesitas mencionar el stack en tu Capítulo III de la tesis:

> *"El pipeline se implementó en Python 3.13.5 usando DuckDB 1.5.2 como motor analítico para consulta directa de los archivos `.csv.gz` del dataset MIMIC-IV-Note v2.2 sin necesidad de carga previa a memoria. El desarrollo se realizó en JupyterLab 4.5.7. Las dependencias auxiliares (pandas, pyarrow, scikit-learn, Hugging Face Transformers) están especificadas en el archivo `requirements.txt` del repositorio público https://github.com/carlosperez100/tesis-gemses-mimic-pipeline. Esta elección de herramientas privilegia reproducibilidad, simplicidad de despliegue y eficiencia en máquina personal de investigación."*

---

*Documento elaborado el 11 de mayo de 2026 como parte de los entregables de la tesis de Maestría en Inteligencia Artificial.*
