# PROYECTO DE TESIS — ESTADO Y MEMORIA DEL PROYECTO

**Autor:** Carlos Pérez Pérez
**Tesis:** Maestría en Inteligencia Artificial — Universidad Nacional de Ingeniería (UNI)
**Curso:** MIA 303 — Proyectos de Investigación I
**Docente:** Mg. Eng. Maria F. Tejada Begazo
**Última actualización del documento:** 10/11 de mayo de 2026

---

## 1. Tema definitivo de tesis

**Título:** *Detección automatizada y priorización de eventos adversos desde notas clínicas no estructuradas mediante un flujo de procesamiento (pipeline) de procesamiento de lenguaje natural y aprendizaje automático — aplicación de la Matriz de Priorización del Modelo GEMSES sobre el dataset MIMIC-IV*

**Pregunta de investigación principal:** ¿En qué medida un flujo de procesamiento integrado de NLP y ML supervisado permite detectar eventos adversos desde notas clínicas no estructuradas de MIMIC-IV y aplicar la Matriz de Priorización del Modelo GEMSES con una concordancia (kappa de Cohen ≥ 0.60) significativamente mayor a la fórmula determinista actual?

**Originalidad:** Cuádruple integración inédita en la literatura 2015-2025: (i) NLP sobre notas clínicas no estructuradas + (ii) dataset público y reproducible (MIMIC-IV) + (iii) arquitectura multimodal texto + tabular + (iv) operacionalización automatizada de un modelo de excelencia institucional adoptado normativamente (GEMSES vía Directiva GG-ESSALUD-2021).

---

## 2. Datos clave (referencia rápida)

| Campo | Valor |
|---|---|
| Repositorio GitHub | https://github.com/carlosperez100/tesis-gemses-mimic-pipeline |
| Carpeta local | C:\MIMIC\tesis |
| Dataset principal | MIMIC-IV v3.1 (PhysioNet) — DOI: 10.13026/kpb9-mt58 |
| Dataset secundario | MIMIC-IV-Note v2.2 — DOI: 10.13026/1n74-ne17 |
| Usuario PhysioNet | carlosperez |
| CITI Institution ID 1 | 1912 (Data or Specimens Only Research) |
| CITI Institution ID 2 | 3641 — Seguro Social de Salud EsSalud |
| CITI Record ID (EsSalud) | 54788726 (vigente hasta 28-Abr-2029) |
| Curso (entregables) | MIA 303 |
| Próximo plazo | Sábado 10 de mayo 2026 — entrega 12 resúmenes (ENTREGADO) |
| Siguiente plazo | Martes 12 y 19 de mayo 2026 — sustentación PPT |
| Examen Parcial | Semana 8 del curso (Junio 2026 estimado) |
| Examen Final | Semana 15 del curso (Septiembre 2026 estimado) |
| Plazo total tesis | Mayo 2026 — Mayo 2027 |

---

## 3. Línea de tiempo de hitos completados

### Semana del 27 abril — 1 mayo 2026
- 27/Abr: Inicio del análisis del material del curso (3 PDFs de clases + paper de Kitchenham + libro GEMSES + proyecto modelo Tejada Begazo).
- 27/Abr: Tema inicial propuesto "Optimización del Control de Gestión en los Servicios de Salud mediante Análisis Predictivo e IA: enfoque basado en GEMSES y Datos de Acceso Abierto".
- 28/Abr: Re-evaluación del tema con la directiva EsSalud GG-ESSALUD-2021 y el Formato 1 GEMSES en mano.
- 28/Abr: Acceso a MIMIC-IV v3.1 conseguido (credentialed user, DUA firmado, módulos hosp + icu disponibles).
- 28/Abr: Certificación CITI bajo EsSalud (ID 3641) completada. Record ID 54788726.

### Semana del 4 — 8 mayo 2026
- Refinamiento del tema con la restricción real: sin acceso a HCE de EsSalud, MIMIC-IV es dataset principal (no plan B).
- Identificación del vacío crítico cuádruple en la literatura.

### Sábado 10 de mayo 2026
- 9 papers iniciales identificados (3 por tema) y ampliados a 12 papers (4 por tema).
- Fichas analíticas completas con formato Tejada (6 subsecciones por paper) + tabla comparativa + desarrollo de la investigación ampliado.
- 11 fórmulas matemáticas formalizadas (F1, F1 ponderado, AUC-ROC, meta-análisis, fusión multimodal, RPN, kappa de Cohen, fórmulas GEMSES G, H, I, J).
- Versiones generadas: Word v3 (citas + fórmulas + comillas latinas), LaTeX completo (compilable en Overleaf), PPT 12 slides para sustentación.

### Domingo 11 de mayo 2026 (madrugada)
- Acceso a MIMIC-IV-Note v2.2 conseguido (DUA específico firmado).
- Descarga de Note iniciada en Chrome (1.8 GB, en progreso).
- Entorno técnico instalado y verificado: Python 3.13.5 + DuckDB 1.5.2 + Pandas + JupyterLab.
- Notebook inicial `tesis_exploracion_inicial.ipynb` generado con DuckDB conectado a MIMIC.
- Repositorio Git inicializado en C:\MIMIC\tesis con .gitignore protegiendo DUA.
- Repositorio publicado en GitHub privado.
- Estructura `docs/` + `notebooks/` poblada con 7 documentos definitivos.
- Dos commits: (1) Initial commit con README + gitignore, (2) Agrega 7 documentos definitivos.

---

## 4. Estado actual al cierre de esta sesión

### Lo que está funcionando
- Repositorio GitHub con todos los entregables académicos hasta la fecha
- Entorno Python local listo para arrancar la Etapa 1 NLP
- Mini-notebook de prueba ejecutado exitosamente
- 12 papers definitivos seleccionados y analizados con formato oficial
- Doble certificación CITI vigente

### Lo que falta por completar (corto plazo)
- Terminar la descarga de MIMIC-IV-Note (1.8 GB) — en progreso en Chrome
- Extraer el ZIP de Note en `C:\MIMIC\note\`
- Reanudar descarga de MIMIC-IV principal (9.8 GB, pausada)
- Ejecutar `tesis_exploracion_inicial.ipynb` con datos reales
- Generar primer sample de 100 notas etiquetadas

---

## 5. Stack técnico configurado

| Componente | Versión | Propósito |
|---|---|---|
| Python | 3.13.5 | Entorno de desarrollo |
| DuckDB | 1.5.2 | Motor analítico (sustituye a PostgreSQL) |
| Pandas | 2.x | Manipulación de DataFrames |
| pyarrow | latest | Aceleración DuckDB ↔ Pandas |
| JupyterLab | 4.5.7 | Entorno de notebooks |
| Matplotlib | latest | Gráficos básicos |
| tqdm | latest | Barras de progreso |
| Git | 2.53.0 | Control de versiones |

### Pendientes de instalar (para Fase 2 NLP)
- `transformers` (Hugging Face) — para BioBERT y ClinicalBERT
- `torch` o `tensorflow` — backend de transformers
- `scikit-learn` — métricas y modelos clásicos
- `xgboost` — modelo tabular comparativo
- `snorkel` — para weak supervision en el etiquetado

---

## 6. Estructura del repositorio

```
tesis-gemses-mimic-pipeline/
├── README.md
├── .gitignore                                  (protege datos bajo DUA)
├── docs/
│   ├── 01_plan_de_tesis/
│   │   └── Plan_Tesis_Cap_I_Carlos_Perez.docx
│   ├── 02_revision_literatura/
│   │   ├── Resumen_12_Articulos_MIA303_v3_Citas_y_Formulas.docx
│   │   └── Resumen_12_Articulos_MIA303.tex
│   ├── 03_metodologia_critica/
│   │   └── Workflow_Lit_Review_Adversarial_Preregistro.docx
│   ├── 04_operativo/
│   │   └── Strings_Busqueda_y_Guia_PhysioNet.docx
│   └── 05_presentaciones/
│       └── Sustentacion_MIA303_GEMSES_MIMIC.pptx
└── notebooks/
    └── tesis_exploracion_inicial.ipynb
```

---

## 7. Decisiones clave tomadas

1. **DuckDB en lugar de PostgreSQL** — para evitar instalar servidor y manejar dependencias pesadas en Windows. DuckDB se comporta como librería Python, lee CSVs comprimidos directamente.

2. **MIMIC-IV como dataset principal** (no como plan B) — porque no hay acceso a HCE de EsSalud, MIMIC-IV es el activo real. Datos abiertos, reproducibles, validados internacionalmente.

3. **Arquitectura multimodal (texto + tabular)** — siguiendo a Liu X. et al. 2024 (JMIR). La Matriz GEMSES requiere tanto entrada textual (descripción del evento) como tabular (estancia, complicaciones, costos, satisfacción).

4. **Comillas latinas «...» para citas de autores** — separación visible entre lo que dicen los autores (citas en cursiva azul) y mi análisis crítico (texto plano).

5. **"Flujo de procesamiento (pipeline)" en la primera mención** — convención académica formal para introducir el anglicismo con su traducción y luego usarlos indistintamente.

6. **Declaración honesta de conflicto de interés** — no inflar relaciones con EsSalud que no existen. El aval institucional EsSalud para la tesis NO existe; solo existe la afiliación CITI Program. La tesis es estrictamente académica.

7. **Repositorio privado en GitHub** — durante la fase de desarrollo. Se hará público al momento de someter el paper Q1.

---

## 8. Credenciales y accesos

### PhysioNet
- Usuario: `carlosperez`
- Email: carlosperez100@gmail.com
- Datasets autorizados: MIMIC-IV v3.1, MIMIC-IV-Note v2.2

### CITI Program
- Afiliación 1: Institution ID 1912 — curso "Data or Specimens Only Research"
- Afiliación 2: Institution ID 3641 (Seguro Social de Salud — EsSalud) — curso "Ética en Investigación"
- Record ID EsSalud: 54788726 (vencimiento 28-Abr-2029)

### GitHub
- Usuario: carlosperez100
- Repositorio: https://github.com/carlosperez100/tesis-gemses-mimic-pipeline (privado por ahora)
- Branch principal: main

---

## 9. Los 12 papers del marco teórico

### Tema 1 — NLP en notas clínicas (artículos 1-4)
1. Modi & Feldman (2024) — *Extracting adverse drug events from clinical Notes: A systematic review*. J Biomed Inform 151. **CITA PIVOTE.**
2. Wang, Coiera, Magrabi (2024) — *Improving Patient Safety Event Report Classification with ML*. MEDINFO.
3. Mahendran et al. (2025) — *Leveraging NLP and ML for ADE Detection — Scoping Review*. Drug Safety.
4. Campillos-Llanos (2023) — *MedLexSp medical lexicon for Spanish NLP*. J Biomed Semantics.

### Tema 2 — MIMIC-IV (artículos 5-8)
5. Johnson et al. (2023) — *MIMIC-IV dataset paper*. Sci Data. **CITA TÉCNICA OBLIGATORIA.**
6. van Aken et al. (2024) — *Revisiting Clinical Outcome Prediction for MIMIC-IV*. ClinicalNLP NAACL.
7. Hu et al. (2024) — *ML to predict ADE — systematic review + meta-analysis*. J Int Med Res.
8. Liu X. et al. (2024) — *Multimodal Deep Learning for Heart Failure (MIMIC)*. JMIR. **ANTECEDENTE METODOLÓGICO DIRECTO.**

### Tema 3 — Priorización de riesgo (artículos 9-12)
9. Liu H.C. et al. (2023) — *Overview of FMEA: Patient Safety Tool*. GJQSH.
10. Kovačević et al. (2024) — *DSS Fuzzy+ANN+SVM for risk management*. Int J Med Inform.
11. Khan et al. (2025) — *AI in healthcare patient safety — SR*. Frontiers Med.
12. Ferrara et al. (2024) — *Risk Management and Patient Safety in the AI Era — SR*. Healthcare MDPI.

---

## 10. Roadmap experimental (6 fases)

| Fase | Periodo | Producto |
|---|---|---|
| 1. Construcción del corpus etiquetado | May - Jun 2026 | Corpus de 5000 notas con weak supervision Snorkel |
| 2. Etapa 1 NLP (transformers biomédicos) | Jun - Ago 2026 | BioBERT, ClinicalBERT, DistilBERT fine-tuneados; F1, kappa |
| 3. Etapa 2 multimodal (texto + tabular) | Ago - Oct 2026 | Arquitectura con fusión por atención; AUC-ROC |
| 4. Cálculo Matriz GEMSES | Oct - Dic 2026 | Niveles Verde/Amarillo/Rojo aplicados a la cohorte |
| 5. Validación con panel experto | Ene - Mar 2027 | 200 notas estratificadas con anotación experta independiente |
| 6. Transferencia al castellano | Mar - May 2027 | Piloto con CodiEsp + MedLexSp + ClinicalBERT-multilingual |

---

## 11. Operacionalización GEMSES → MIMIC-IV

Aporte original que NO aparece en ninguno de los 12 papers revisados:

| Dimensión GEMSES | Peso | Variable proxy MIMIC-IV |
|---|---|---|
| Tiempo (c) | 0.40 | Length of Stay (LOS) prolongado vs mediana DRG |
| Calidad (d) | 0.20 | ICD-9/10 de complicaciones intrahospitalarias + NER de eventos en notas |
| Costos (e) | 0.15 | DRG weight + procedimientos invasivos adicionales |
| Satisfacción (f) | 0.25 | Readmisión 30 días + alta contra recomendación médica (AMA discharge) |

Fórmula GEMSES: **G = c·0.40 + d·0.20 + e·0.15 + f·0.25**

Derivadas: H = B·G (Nivel de Riesgo); I = H÷Σh (Índice de Gestión); J = I×100 (Nivel de Gestión final, mapeado a P25/P50/P75 → Verde/Amarillo/Rojo).

---

## 12. Próximos pasos prioritarios (al retomar la próxima sesión)

1. **Confirmar descarga MIMIC-IV-Note completa** y extraída en `C:\MIMIC\note\`.
2. **Reanudar descarga MIMIC-IV principal** (9.8 GB) en background.
3. **Ejecutar `tesis_exploracion_inicial.ipynb`** y validar que las 4 queries de exploración funcionan sobre datos reales.
4. **Capturar resultados de Sección 4.1 y 4.2** del notebook (distribución de notas, longitud) para calibrar el segundo notebook.
5. **Generar `02_etiquetado_inicial.ipynb`** con weak supervision para construir el primer corpus de 300 notas etiquetadas manualmente.
6. **Preparar sustentación PPT del 12 o 19 de mayo** — el PPT ya está en `docs/05_presentaciones/`.

---

## 13. Riesgos identificados y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| R1: Notas MIMIC en inglés vs sistema sanitario hispanohablante | Alta | Alto | Fase 6 con MedLexSp + CodiEsp + ClinicalBERT-multilingual |
| R2: Etiquetado de eventos requiere anotación manual | Alta | Alto | Weak supervision Snorkel + validación 300 notas |
| R3: Proxies GEMSES sobre MIMIC son aproximación | Media | Medio | Justificación teórica + análisis de sensibilidad ±20% en pesos |
| R4: Alcance ambicioso para 9-12 meses | Media | Alto | Fast-track 60/100 quality gate; defender Etapa 1 si Etapa 2 no llega |
| R5: Conflicto de intereses (autor GEMSES + asesor EsSalud) | Media | Medio | Declaración honesta + panel experto independiente |

---

## 14. Cómo retomar la sesión

Cuando Carlos vuelva a este proyecto en una sesión futura, debe:

1. Subir el archivo **PROYECTO_TESIS_ESTADO.md** al chat O instalar el **skill `tesis-gemses-mimic`** que genere el contexto automáticamente.
2. Mencionar palabras clave: "tesis", "MIMIC-IV", "GEMSES", "evento adverso", "ERSP", "pipeline NLP".
3. Indicar el estado actual (qué hito está en curso) para que el asistente sepa por dónde continuar.

Comando rápido para retomar: *"Estoy retomando mi proyecto de tesis MIA 303 sobre GEMSES + MIMIC-IV. Aquí tienes el documento de estado actualizado, sigue desde [última acción completada]."*

---

## 15. Contacto del autor y referencias

### Contacto
- Email: **carlosperez100@gmail.com**
- GitHub: https://github.com/carlosperez100
- Repositorio de la tesis: **https://github.com/carlosperez100/tesis-gemses-mimic-pipeline**

### Sobre el Modelo GEMSES
- Sitio oficial del modelo: **https://sites.google.com/view/gemses/inicio**
- Autor del modelo: Carlos Pérez Pérez (mismo autor de esta tesis)
- Año de publicación del libro: 2021
- ISBN: 978-612-00-6235-7
- Adopción normativa: Directiva GG-ESSALUD-2021 (Definición 5.13 cita textualmente al Modelo GEMSES como herramienta de priorización oficial)

### Cómo citar este trabajo
- **Tesis (cuando se complete):** Pérez Pérez, C. (2027). *Detección automatizada y priorización de eventos adversos en notas clínicas mediante NLP y la Matriz GEMSES sobre MIMIC-IV* [Tesis de Maestría]. Universidad Nacional de Ingeniería, Facultad de Ingeniería Industrial y de Sistemas, Unidad de Posgrado.
- **Modelo GEMSES:** Pérez Pérez, C. (2021). *Modelo de Excelencia: Gestión Moderna de los Servicios de Salud — GEMSES*. Lima. ISBN 978-612-00-6235-7.

---

*Documento generado al cierre de la sesión del 11 de mayo de 2026 como memoria externa del proyecto.*
