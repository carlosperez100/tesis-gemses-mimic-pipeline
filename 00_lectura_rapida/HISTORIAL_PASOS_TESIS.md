# HISTORIAL DE PASOS DEL PROYECTO DE TESIS

**Autor:** Carlos Pérez Pérez
**Tesis:** Detección automatizada y priorización de eventos adversos en notas clínicas mediante NLP y Matriz GEMSES sobre MIMIC-IV
**Curso:** MIA 303 — Maestría en Inteligencia Artificial, UNI
**Docente:** Mg. Eng. Maria F. Tejada Begazo
**Periodo registrado:** 27 de abril – 11 de mayo de 2026

---

## Resumen ejecutivo

Este documento registra cronológicamente cada paso del proyecto de tesis, organizado por fechas y resultados verificables. Cumple la función de bitácora de investigación y referencia de reproducibilidad.

**Estado al cierre:** 31 hitos completados, 1 dataset operativo (MIMIC-IV-Note v2.2 con 331 793 epicrisis), entorno técnico funcional, repositorio público en GitHub.

---

## ETAPA 1 — Análisis del material académico

### 27 de abril de 2026

**1.1** Lectura completa de los 5 documentos del curso MIA 303:
- Clase 01 — Introducción al curso (57 slides)
- Clase 03 — Revisión de la Literatura (48 slides)
- Clase 04 — Bases de Datos Bibliográficas (52 slides)
- Proyecto modelo de Maria F. Tejada Begazo "Control Visual de un Brazo Manipulador con 7GDL"
- Paper de Kitchenham et al. (2009) sobre revisiones sistemáticas

**1.2** Lectura del libro propio: *Modelo de Excelencia: Gestión Moderna de los Servicios de Salud — GEMSES* (Pérez Pérez, 2021, ISBN 978-612-00-6235-7).

**1.3** Identificación de 5 patrones transversales en el material:
- Convergencia natural GEMSES + IA
- Obsesión por rigurosidad metodológica
- Estructura "9-cosas" recurrente
- Plazos inminentes
- Ventaja competitiva del autor (autor de GEMSES + asesor EsSalud)

**Resultado entregable:** análisis crítico de patrones.

---

## ETAPA 2 — Definición y refinamiento del tema

### 27-28 de abril de 2026

**2.1** Tema inicial propuesto: "Optimización del Control de Gestión en los Servicios de Salud mediante Análisis Predictivo e IA: Un enfoque basado en el Modelo GEMSES y Datos de Acceso Abierto".

**2.2** Re-evaluación tras revisar:
- La directiva oficial **GG-ESSALUD-2021** "Registro, Notificación y Gestión de los Eventos Relacionados con la Seguridad del Paciente"
- El **Formato 1 (Matriz de Priorización de Impactos en Salud)** del Modelo GEMSES con la fórmula: G = c·0.40 + d·0.20 + e·0.15 + f·0.25
- La definición 5.13 de la Directiva que cita literalmente al Modelo GEMSES como herramienta normativa

**2.3** Reformulación del tema a la versión definitiva: *"Detección automatizada y priorización de eventos adversos desde notas clínicas no estructuradas mediante un flujo de procesamiento (pipeline) de NLP y aprendizaje automático — aplicación de la Matriz de Priorización del Modelo GEMSES sobre el dataset MIMIC-IV"*.

**2.4** Clarificación de restricciones reales:
- Sin acceso a Historias Clínicas Electrónicas de EsSalud
- MIMIC-IV se convierte en dataset principal (no plan B)
- Necesidad de capa UMLS como puente idioma-agnóstico

**Resultado entregable:** tema definitivo con marco normativo identificado.

---

## ETAPA 3 — Acceso a datos y certificación ética

### 28 de abril de 2026

**3.1** Solicitud de credentialed access a PhysioNet (usuario: `carlosperez`).

**3.2** Firma del Data Use Agreement v1.5.0 para MIMIC-IV v3.1.

**3.3** Curso CITI Program completado:
- "Data or Specimens Only Research" bajo CITI Institution ID 1912 (afiliación UNI)
- "Curso de Ética en Investigación – Basic Course" bajo Seguro Social de Salud – EsSalud (CITI Institution ID 3641, Record ID 54788726, vigente hasta 28-Abr-2029)

**3.4** Acceso confirmado a MIMIC-IV v3.1 (módulos `hosp` e `icu`) — 364,627 pacientes únicos, 546,028 hospitalizaciones, 94,458 estancias en UCI.

**Resultado entregable:** acceso normativo a datos clínicos de referencia mundial.

---

## ETAPA 4 — Revisión bibliográfica sistemática

### 4-9 de mayo de 2026

**4.1** Definición de 3 temas de búsqueda:
- T1 — NLP en notas clínicas para detección de eventos adversos
- T2 — MIMIC-IV en investigación de seguridad del paciente
- T3 — Modelos de priorización de riesgo (FMEA y variantes)

**4.2** Strings de búsqueda construidos para 8 bases bibliográficas: Scopus, IEEE Xplore, PubMed, ACM Digital Library, Springer, Frontiers, MDPI y ACL Anthology.

**4.3** Identificación inicial de 9 papers (3 por tema), luego ampliados a **12 papers definitivos** (4 por tema):

| # | Tema | Cita | Tipo |
|---|---|---|---|
| 1 | T1 | Modi & Feldman (2024) | Revisión sistemática |
| 2 | T1 | Wang, Coiera, Magrabi (2024) | Empírico |
| 3 | T1 | Mahendran et al. (2025) | Scoping review |
| 4 | T1 | Campillos-Llanos (2023) MedLexSp | Recurso lingüístico |
| 5 | T2 | Johnson et al. (2023) MIMIC-IV | Dataset paper |
| 6 | T2 | van Aken et al. (2024) | Benchmarking |
| 7 | T2 | Hu et al. (2024) | Meta-análisis |
| 8 | T2 | Liu X. et al. (2024) | Multimodal |
| 9 | T3 | Liu H.C. et al. (2023) FMEA | Revisión narrativa |
| 10 | T3 | Kovačević et al. (2024) | DSS híbrido |
| 11 | T3 | Khan et al. (2025) | Revisión sistemática |
| 12 | T3 | Ferrara et al. (2024) | Revisión sistemática |

**4.4** Fichas analíticas elaboradas según el formato oficial de la docente Tejada (6 subsecciones por paper):
- Objetivo del artículo
- Metodología
- Resultados Principales
- Conclusiones
- Crítica Personal
- Palabras Claves

**Total:** 12 papers × 6 subsecciones = 72 subsecciones analíticas.

**4.5** Formalización de 11 ecuaciones matemáticas:
- F1-score, F1 ponderado, AUC-ROC, meta-análisis (efectos aleatorios)
- Fusión multimodal por atención
- RPN (Risk Priority Number), kappa de Cohen
- Fórmulas GEMSES: G (Impacto), H (Nivel de Riesgo), I (Índice de Gestión), J (Nivel de Gestión × 100)

**Resultado entregable:** revisión bibliográfica completa en formato Word + LaTeX.

---

## ETAPA 5 — Operacionalización GEMSES → MIMIC-IV

### 9 de mayo de 2026

**5.1** Aporte original (no aparece en ninguno de los 12 papers revisados): mapeo de las 4 dimensiones de la Matriz GEMSES a variables proxy de MIMIC-IV.

| Dimensión GEMSES | Peso | Variable proxy en MIMIC-IV |
|---|---|---|
| Tiempo (c) | 0.40 | Length of Stay vs mediana del DRG |
| Calidad (d) | 0.20 | ICD-9/10 de complicaciones + NER de eventos en notas |
| Costos (e) | 0.15 | DRG weight + procedimientos invasivos adicionales |
| Satisfacción (f) | 0.25 | Readmisión a 30 días + AMA discharge |

**Resultado entregable:** tabla de operacionalización publicable como contribución metodológica.

---

## ETAPA 6 — Generación de entregables académicos

### 10 de mayo de 2026

**6.1** Cap I del Plan de Tesis: planteamiento, hipótesis (causal con kappa ≥ 0.60), objetivo general + 5 específicos, justificación cuádruple (teórica, metodológica, aplicada, social), alcances con plan B explícito.

**6.2** Resumen de 12 artículos con citas latinas «...», fórmulas formales, tabla comparativa y desarrollo ampliado de la investigación. Generado en Word (.docx) y LaTeX (.tex compilable en Overleaf).

**6.3** Workflow estilo Sant'Anna ejecutado:
- `/lit-review` — síntesis crítica de 12 papers
- `/devils-advocate` — registro adversarial de 7 riesgos con mitigaciones
- `/preregister` — preregistro formal estilo OSF con hipótesis, variables, plan analítico, criterios de detención

**6.4** Presentación de sustentación: PPT de 12 slides para 12 o 19 de mayo 2026, con QA visual de 2 rondas.

**Resultado entregable:** 7 documentos académicos definitivos.

---

## ETAPA 7 — Infraestructura técnica

### 10-11 de mayo de 2026

**7.1** Acceso adicional a **MIMIC-IV-Note v2.2** — DUA específico firmado en PhysioNet (DOI: 10.13026/1n74-ne17).

**7.2** Descarga de MIMIC-IV-Note: 4 archivos `.csv.gz` totalizando 1.96 GB:
- `discharge.csv.gz` — 1.14 GB (epicrisis)
- `discharge_detail.csv.gz` — 789 KB (metadatos)
- `radiology.csv.gz` — 781 MB (informes radiológicos)
- `radiology_detail.csv.gz` — 39 MB (metadatos)

**7.3** Stack técnico instalado y verificado en máquina local Windows:
- Python 3.13.5
- DuckDB 1.5.2
- Pandas, pyarrow, JupyterLab 4.5.7, Matplotlib, tqdm
- Git 2.53.0 con autenticación GitHub

**7.4** Estructura de carpetas creada:
```
C:\MIMIC\
├── note\note\          (MIMIC-IV-Note v2.2 extraído)
├── mimiciv\            (MIMIC-IV principal — pendiente descarga)
└── tesis\              (repositorio Git local)
    ├── .gitignore      (protección DUA)
    ├── README.md
    ├── index.html      (showcase HTML, sirve GitHub Pages)
    ├── docs\           (documentos académicos versionados)
    └── notebooks\      (notebooks Jupyter)
```

**Resultado entregable:** entorno técnico 100 % funcional.

---

## ETAPA 8 — Repositorio GitHub público

### 11 de mayo de 2026

**8.1** Repositorio creado: `https://github.com/carlosperez100/tesis-gemses-mimic-pipeline`.

**8.2** Configuración inicial:
- Branch `main` activo
- `.gitignore` con protección DUA (bloquea CSV, parquet, DB, sample_*.csv)
- Commits:
  - Initial commit (README + gitignore)
  - Agrega 7 documentos definitivos (940 líneas insertadas)
  - Add HTML showcase index (940 líneas)

**8.3** GitHub Pages activado — sitio público en:
`https://carlosperez100.github.io/tesis-gemses-mimic-pipeline/`

**Resultado entregable:** versionamiento académico profesional con sitio web público.

---

## ETAPA 9 — Validación con datos reales

### 11 de mayo de 2026 (continuación)

**9.1** Notebook `tesis_exploracion_inicial.ipynb` ejecutado celda por celda con DuckDB sobre MIMIC-IV-Note:

| Paso | Verificación | Resultado |
|---|---|---|
| Imports y versiones | Python + DuckDB + Pandas | OK |
| Configuración de rutas | `note: existe: True` | OK |
| Verificación de archivos | 4/4 archivos detectados | OK |
| Conexión DuckDB | Vistas `discharge` y `discharge_detail` registradas | OK |
| **Patrón 1: COUNT(*)** | Total de epicrisis en el corpus | **331 793 notas** |
| Patrón 2: GROUP BY | Tipo de nota | 100 % "DS" (Discharge Summary) |
| Patrón 4: SAMPLE 10 | 10 epicrisis al azar | OK (subject_id, hadm_id, charttime) |

**9.2** Hallazgo metodológico: las notas están en inglés, mientras el Modelo GEMSES y la taxonomía del Anexo 02 EsSalud están en español. Decisión arquitectónica: introducir capa UMLS (Concept Unique Identifiers) para hacer el pipeline idioma-agnóstico.

**Resultado entregable:** infraestructura validada sobre datos reales + arquitectura UMLS documentada para Fase 2 del roadmap.

---

## RESUMEN CUANTITATIVO DEL TRABAJO REALIZADO

| Indicador | Valor |
|---|---|
| Días de trabajo intensivo | 15 (27 abril – 11 mayo 2026) |
| Hitos completados y verificados | 31 |
| Papers científicos analizados | 12 |
| Ecuaciones matemáticas formalizadas | 11 |
| Subsecciones analíticas redactadas | 72 |
| Bases bibliográficas consultadas | 8 |
| Datasets credentialed obtenidos | 2 (MIMIC-IV v3.1 + Note v2.2) |
| Certificaciones CITI Program | 2 (UNI + EsSalud) |
| Documentos académicos generados | 10 |
| Líneas de código Python (notebook) | ~250 |
| Tamaño del corpus de trabajo | 331 793 epicrisis (1.14 GB) |
| Commits Git | 3 |
| Sitio web público | github.io activo |

---

## PRÓXIMOS PASOS (ROADMAP)

| Fase | Periodo | Producto verificable |
|---|---|---|
| Fase 1 — Corpus etiquetado | May-Jun 2026 | 5000 notas con weak supervision (Snorkel) + 300 anotadas manualmente |
| Fase 2 — NLP Etapa 1 | Jun-Ago 2026 | BioBERT, ClinicalBERT, DistilBERT fine-tuneados |
| Fase 3 — Pipeline multimodal | Ago-Oct 2026 | Texto + tabular con fusión por atención |
| Fase 4 — Matriz GEMSES | Oct-Dic 2026 | Niveles Verde/Amarillo/Rojo aplicados a cohorte |
| Fase 5 — Panel experto | Ene-Mar 2027 | 200 notas con validación experta independiente |
| Fase 6 — Transferencia castellano | Mar-May 2027 | Piloto con MedLexSp + ClinicalBERT-multilingual |
| **Hito final** | **May 2027** | **Tesis defendida + paper Q1 sometido** |

---

## REFERENCIAS DEL AUTOR

- Email: carlosperez100@gmail.com
- Repositorio: https://github.com/carlosperez100/tesis-gemses-mimic-pipeline
- Sitio del Modelo GEMSES: https://sites.google.com/view/gemses/inicio
- Libro original GEMSES: Pérez Pérez, C. (2021), Lima, ISBN 978-612-00-6235-7
- ORCID: (a registrar para sometimiento a revistas Q1)

---

*Bitácora cerrada el 11 de mayo de 2026, lista para anexar al expediente del curso MIA 303 y al material suplementario del paper Q1 futuro.*
