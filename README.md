# tesis-gemses-mimic-pipeline

> **Detección automatizada y priorización de eventos adversos en notas clínicas mediante procesamiento de lenguaje natural y aprendizaje automático — aplicación de la Matriz de Priorización del Modelo GEMSES sobre el dataset MIMIC-IV**

Repositorio de la tesis de Maestría en Inteligencia Artificial de la **Universidad Nacional de Ingeniería (UNI)**, curso MIA 303 – Proyectos de Investigación I.

---

## 📌 Tres referencias rápidas

| | |
|---|---|
| 📧 **Email del autor** | [carlosperez100@gmail.com](mailto:carlosperez100@gmail.com) |
| 🐙 **Repositorio GitHub** | [github.com/carlosperez100/tesis-gemses-mimic-pipeline](https://github.com/carlosperez100/tesis-gemses-mimic-pipeline) |
| 🌐 **Sitio oficial Modelo GEMSES** | [sites.google.com/view/gemses](https://sites.google.com/view/gemses/inicio) |

---

## Autor

**Carlos Pérez Pérez**
- Alumno de Maestría en Inteligencia Artificial — UNI
- Asesor — Oficina de Gestión de la Calidad y Humanización, EsSalud
- Autor del Modelo GEMSES (Pérez Pérez, 2021, ISBN 978-612-00-6235-7)

## Docente del curso

Mg. Eng. Maria F. Tejada Begazo

---

## Resumen ejecutivo

Esta tesis propone un flujo de procesamiento (pipeline) automatizado que:

1. **Extrae eventos adversos** desde notas clínicas no estructuradas usando transformers biomédicos preentrenados (BioBERT, ClinicalBERT).
2. **Aplica la Matriz de Priorización del Modelo GEMSES** — un modelo de excelencia sanitaria publicado y patentado en Latinoamérica, adoptado normativamente por EsSalud mediante la Directiva GG-ESSALUD-2021.
3. **Genera clasificaciones accionables** del Nivel de Riesgo (Verde / Amarillo / Rojo) y del Nivel de Gestión (Servicios / Departamento / Director) para cada evento.

**Originalidad:** Es la primera operacionalización documentada del Modelo GEMSES mediante técnicas modernas de inteligencia artificial sobre un dataset clínico público (MIMIC-IV).

---

## Datasets utilizados

- **MIMIC-IV v3.1** (Johnson et al., 2024) — PhysioNet DOI: [10.13026/kpb9-mt58](https://doi.org/10.13026/kpb9-mt58)
- **MIMIC-IV-Note v2.2** (Johnson et al., 2023) — PhysioNet DOI: [10.13026/1n74-ne17](https://doi.org/10.13026/1n74-ne17)

Ambos accedidos bajo PhysioNet Credentialed Health Data Use Agreement v1.5.0 firmado por el autor. **Los datos NO están incluidos en este repositorio** y no pueden redistribuirse conforme al DUA.

---

## Marco ético

El autor completó dos certificaciones independientes en ética de investigación:

- CITI Program **"Data or Specimens Only Research"** — Institution ID 1912
- CITI Program **"Ética en Investigación – Basic Course"** — Seguro Social de Salud EsSalud (Institution ID 3641, Record ID 54788726, vigente hasta 28-Abr-2029)

---

## Estructura del repositorio

```
.
├── README.md                              # Este archivo
├── .gitignore                             # Protección DUA (bloquea archivos de datos)
│
├── docs/                                  # Documentación académica
│   ├── 01_plan_de_tesis/
│   │   └── Plan_Tesis_Cap_I_Carlos_Perez.docx
│   ├── 02_revision_literatura/
│   │   ├── Resumen_12_Articulos_v3_Citas_y_Formulas.docx
│   │   └── Resumen_12_Articulos.tex       # Fuente LaTeX (compilable en Overleaf)
│   ├── 03_metodologia_critica/
│   │   └── Workflow_Lit_Review_Adversarial_Preregistro.docx
│   ├── 04_operativo/
│   │   └── Strings_Busqueda_y_Guia_PhysioNet.docx
│   └── 05_presentaciones/
│       └── Sustentacion_MIA303_GEMSES_MIMIC.pptx
│
└── notebooks/                             # Jupyter notebooks de experimentación
    └── tesis_exploracion_inicial.ipynb    # Exploración inicial con DuckDB
```

---

## Stack tecnológico

| Componente | Propósito |
|---|---|
| **Python 3.13** | Lenguaje principal |
| **DuckDB** | Motor analítico para consultar archivos MIMIC sin servidor |
| **JupyterLab** | Entorno de notebooks |
| **Hugging Face Transformers** | BioBERT, ClinicalBERT (Etapa 1 NLP) |
| **scikit-learn + XGBoost** | Modelos tabulares (Etapa 2) |
| **Snorkel** | Weak supervision para etiquetado inicial |

---

## Cómo reproducir

1. **Solicitar credentialed access a PhysioNet** y firmar los DUAs de MIMIC-IV y MIMIC-IV-Note.
2. **Completar el curso CITI Program** "Data or Specimens Only Research".
3. **Clonar este repositorio:**
   ```bash
   git clone https://github.com/carlosperez100/tesis-gemses-mimic-pipeline.git
   cd tesis-gemses-mimic-pipeline
   ```
4. **Instalar dependencias:**
   ```bash
   pip install duckdb pandas pyarrow jupyterlab matplotlib tqdm transformers torch scikit-learn xgboost
   ```
5. **Descargar los datos MIMIC** a una carpeta local fuera del repositorio.
6. **Ajustar las rutas** en `notebooks/tesis_exploracion_inicial.ipynb` y ejecutar.

---

## Roadmap experimental (6 fases · May 2026 — May 2027)

| Fase | Periodo | Producto |
|---|---|---|
| 1. Corpus etiquetado | May - Jun 2026 | 5000 notas con weak supervision |
| 2. Etapa 1 NLP | Jun - Ago 2026 | BioBERT/ClinicalBERT fine-tuneados |
| 3. Etapa 2 multimodal | Ago - Oct 2026 | Texto + tabular con fusión por atención |
| 4. Matriz GEMSES | Oct - Dic 2026 | Niveles Verde/Amarillo/Rojo aplicados |
| 5. Validación panel experto | Ene - Mar 2027 | 200 notas con anotación independiente |
| 6. Transferencia al castellano | Mar - May 2027 | Piloto con MedLexSp + ClinicalBERT-multilingual |

---

## Sobre el Modelo GEMSES

GEMSES (Gestión Moderna de los Servicios de Salud) es un modelo de excelencia en gestión sanitaria desarrollado por el autor y publicado en 2021. Sus principales características:

- **9 principios rectores**, incluyendo "Automatización de la gestión" e "Investigación"
- **3 macroprocesos:** estratégico, misional y soporte
- **Matriz de Priorización** con fórmula ponderada: G = c·0.40 + d·0.20 + e·0.15 + f·0.25 (Tiempo, Calidad, Costos, Satisfacción)
- **Adopción normativa por EsSalud** mediante la Directiva GG-ESSALUD-2021 (Definición 5.13 cita textualmente al Modelo GEMSES)

**Sitio oficial:** [sites.google.com/view/gemses](https://sites.google.com/view/gemses/inicio)

**Libro original:** Pérez Pérez, C. (2021). *Modelo de Excelencia: Gestión Moderna de los Servicios de Salud — GEMSES*. Lima. ISBN 978-612-00-6235-7.

---

## Cita sugerida (cuando la tesis se complete)

```bibtex
@thesis{perez2027tesis,
  author       = {Pérez Pérez, Carlos},
  title        = {Detección automatizada y priorización de eventos adversos
                  en notas clínicas mediante NLP y la Matriz GEMSES sobre MIMIC-IV},
  school       = {Universidad Nacional de Ingeniería, Facultad de Ingeniería
                  Industrial y de Sistemas, Unidad de Posgrado},
  year         = {2027},
  type         = {Tesis de Maestría en Inteligencia Artificial}
}
```

---

## Conflicto de interés declarado

El autor es Asesor de la Oficina de Gestión de la Calidad y Humanización de EsSalud y autor del Modelo GEMSES (Pérez Pérez, 2021). El estudio no recibe financiamiento ni respaldo institucional de EsSalud y se realiza estrictamente con fines académicos en el marco de la Maestría en IA de la UNI. La validación con panel experto se realizará con profesionales independientes de la Oficina de Gestión de la Calidad y Humanización de EsSalud.

---

## Licencia y uso

Repositorio actualmente privado durante la fase de desarrollo de la tesis. Se hará público al momento de someter el manuscrito a una revista indexada Q1.

---

**Estado del proyecto:** 🟡 En desarrollo — Mayo 2026
