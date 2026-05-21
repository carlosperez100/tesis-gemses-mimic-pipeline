# Documentación del Mapeo ICD-10 → Anexo 02 EsSalud (GEMSES)

**Autor:** Carlos Pérez Pérez
**Tesis:** Detección automatizada y priorización de eventos adversos en notas clínicas mediante NLP y Matriz GEMSES sobre MIMIC-IV
**Curso:** MIA 303 — Maestría en Inteligencia Artificial, UNI
**Versión del mapeo:** 1.0 — 11 de mayo de 2026
**Archivos asociados:**
- `eventos_adversos_icd10.csv` (149 códigos curados)
- `mapeo_eventos_gemses.py` (módulo Python para integración)

---

## 1. Propósito y alcance

Este mapeo conecta dos esquemas de clasificación de eventos adversos que normalmente operan de forma independiente:

- **ICD-10 / CIE-10** — Clasificación Internacional de Enfermedades (10ª revisión), estándar de la Organización Mundial de la Salud, usado en MIMIC-IV y en la mayoría de sistemas hospitalarios del mundo, incluyendo EsSalud y el MINSA Perú.
- **Anexo 02 de la Directiva GG-ESSALUD-2021** — Taxonomía oficial del Seguro Social de Salud del Perú para clasificar Eventos Relacionados con la Seguridad del Paciente (ERSP). Define 5 categorías operacionales y se conecta directamente con la fórmula de priorización del Modelo GEMSES.

El mapeo permite que el pipeline de la tesis traduzca códigos ICD-10 detectados en notas clínicas (o presentes en la tabla `diagnoses_icd` de MIMIC-IV) a las categorías operativas que usa EsSalud para gestionar el riesgo, alimentando así la dimensión **Calidad (d)** de la fórmula:

```
G = c·0.40 + d·0.20 + e·0.15 + f·0.25
```

---

## 2. Las cinco categorías del Anexo 02 EsSalud

| Categoría | Códigos asignados | Ejemplos representativos |
|---|---|---|
| Procedimiento | 65 | T81.x (complicaciones quirúrgicas), Y60-Y65 (accidentes durante procedimientos), G97.x (complicaciones neurológicas postoperatorias), J95.x (complicaciones respiratorias postoperatorias) |
| Medicación | 28 | T80.3, T80.4 (transfusión incompatible ABO/Rh), T88.6 (shock anafiláctico medicamentoso), Y40-Y49 (efectos adversos por clase terapéutica) |
| Infección nosocomial | 26 | N39.0 (ITU), J18.9 (neumonía), A41.x (sepsis), T81.4 (infección postprocedimiento), T82.6-T85.7 (infección por dispositivos), U82-U83 (resistencia antibiótica) |
| Cuidado del paciente | 22 | W18-W19 (caídas), W06-W08 (caídas de la cama/silla/mueble), L89.x (úlceras por presión por estadio), S00-S72 (traumatismos asociados) |
| Dispositivo médico | 8 | T82.0-T83.0 (complicaciones mecánicas de prótesis y catéteres), Y84.6 (cateterismo urinario adverso), G97.2 (derivación ventricular adversa) |

**Total: 149 códigos** (un código está clasificado simultáneamente en dos categorías por su naturaleza dual).

---

## 3. Criterios de selección de códigos

El CSV NO pretende ser exhaustivo (eso lo cubre el CIE-10 OMS completo con 70 000+ códigos). Es una **selección curada** guiada por tres criterios:

### Criterio 1 — Relevancia operativa para EsSalud
Se priorizaron códigos que aparecen explícita o implícitamente en la **Tabla de Codificación de los ERSP del Anexo 02** de la Directiva GG-ESSALUD-2021. Por ejemplo, "Caída de paciente" (Anexo 02 código 202) se mapea a W06, W18, W19; "Infección urinaria nosocomial" se mapea a N39.0 + T81.4 + T83.5.

### Criterio 2 — Frecuencia en literatura de patient safety
Se incluyeron códigos identificados como Hospital-Acquired Conditions (HACs) por CMS y como Patient Safety Indicators (PSIs) por AHRQ. Estas dos listas constituyen el estándar internacional para identificar eventos adversos en data administrativa.

### Criterio 3 — Trazabilidad en MIMIC-IV
Se confirmó que los códigos elegidos aparecen con frecuencia ≥ 100 ocurrencias en la tabla `diagnoses_icd` de MIMIC-IV v2.x/v3.x (basado en literatura de papers que usan MIMIC). Esto garantiza que el mapeo tendrá señal real al aplicarse al corpus de la tesis.

---

## 4. Calibración de la severidad base

Cada código tiene una severidad base asignada en la escala oficial del Anexo 03 de la Directiva GG-ESSALUD-2021:

| Etiqueta | Score numérico | Criterio de asignación |
|---|---|---|
| Muy alto | 9 | Eventos con riesgo de muerte o daño permanente: sepsis, transfusión incompatible, embolia gaseosa, fractura de fémur, hemorragia intracraneal traumática, anafilaxia, shock séptico. Coincide con la definición de **Evento Centinela** del Anexo 11 de la Directiva. |
| Alto | 6 | Complicaciones serias que requieren intervención inmediata pero generalmente no son mortales: infecciones nosocomiales, caídas con lesión, úlceras estadio III, dehiscencia quirúrgica, hemorragias controlables. |
| Medio | 3 | Eventos sin daño persistente: úlceras estadio I-II, reacciones medicamentosas leves, complicaciones menores de procedimientos, alergias controladas. |
| Bajo | 1 | Eventos sin daño clínico significativo: traumatismos superficiales sin lesión, vómitos postoperatorios autolimitados. |
| Nulo | 0 | Reservado para códigos detectados pero descartados como no-eventos por el panel experto. |

**Importante:** estos valores son **iniciales y revisables**. El Objetivo Específico 4 de la tesis contempla la validación de esta calibración mediante un panel experto independiente (kappa de Cohen ≥ 0.60 como criterio de acuerdo). Si el panel determina que un código fue calibrado incorrectamente, el CSV se actualiza y el pipeline recalcula los scores automáticamente.

---

## 5. Fuentes normativas y referencias

### Fuentes primarias
- **Directiva GG-ESSALUD-2021** — "Registro, Notificación y Gestión de los Eventos Relacionados con la Seguridad del Paciente", aprobada por Gerencia General de EsSalud, marzo 2021. Define el Anexo 02 (Tabla de Codificación de ERSP) y el Anexo 03 (Matriz de Priorización con escala 0-9).
- **CIE-10 OMS** — World Health Organization, *International Statistical Classification of Diseases and Related Health Problems*, 10th revision. https://icd.who.int/browse10/
- **Modelo GEMSES** — Pérez Pérez, C. (2021). *Modelo de Excelencia: Gestión Moderna de los Servicios de Salud — GEMSES*. Lima, ISBN 978-612-00-6235-7.

### Fuentes secundarias para la curación
- **CMS Hospital-Acquired Conditions (HACs)** — Centers for Medicare & Medicaid Services, listado oficial actualizado anualmente. https://www.cms.gov/Medicare/Medicare-Fee-for-Service-Payment/HospitalAcqCond
- **AHRQ Patient Safety Indicators (PSIs)** — Agency for Healthcare Research and Quality, versión 2023. Define los códigos ICD-10 que identifican eventos adversos prevenibles en data administrativa hospitalaria.
- **MIMIC-IV documentation** — Johnson et al. (2023), tabla `diagnoses_icd` y su distribución de códigos.

### Para validación contra normativa peruana
- **CIE-10 PE oficial** — Ministerio de Salud del Perú, Oficina General de Tecnologías de la Información. http://www.minsa.gob.pe/portada/Especiales/2014/cie10/
- **MINSA Norma Técnica de Seguridad del Paciente** — para alinear con políticas nacionales más allá de EsSalud.

---

## 6. Limitaciones reconocidas

### Limitación 1 — Cobertura parcial
El mapeo cubre **149 códigos** seleccionados, no los 70 000+ del CIE-10 completo. Hay eventos adversos que pueden quedar fuera del mapeo si no fueron incluidos en la curación inicial. La función `clasificar_codigo()` retorna `None` para códigos no presentes, lo que permite identificar lagunas para extensiones futuras.

### Limitación 2 — Variantes nacionales de ICD-10
ICD-10 tiene variantes: ICD-10 OMS (original), ICD-10-CM (modificación clínica estadounidense usada en MIMIC-IV), CIE-10 ES (España), CIE-10 PE (Perú). Para códigos a nivel de 3 caracteres (T81, N39, L89) las variantes coinciden. Para códigos a nivel de 4-5 caracteres pueden existir discrepancias menores. El mapeo usa **predominantemente códigos a 3-4 caracteres** para maximizar portabilidad.

### Limitación 3 — Severidad contextual
La severidad base asignada es **promedio típico**. En la realidad clínica, la severidad de un evento depende del contexto del paciente (comorbilidades, edad, fragilidad). El pipeline debería complementar este score base con factores contextuales en futuras versiones — esto está contemplado en la Fase 3 (multimodal) del roadmap experimental.

### Limitación 4 — Validación no realizada aún
Este mapeo no ha sido validado por panel experto. La validación está prevista para la Fase 5 del roadmap (Ene-Mar 2027), con 200 notas estratificadas y revisión por médicos auditores independientes.

### Limitación 5 — No reemplaza al juicio clínico
El score automatizado es **una sugerencia algorítmica**, no un veredicto. La Oficina de Gestión de la Calidad y Humanización de EsSalud (o equivalente en otra IPRESS) debe mantener un humano-en-el-loop para validar las clasificaciones de alto riesgo antes de tomar acciones institucionales.

---

## 7. Cómo extender el mapeo

El CSV está diseñado para crecer iterativamente. Para añadir nuevos códigos:

### Procedimiento manual (recomendado para alta calidad)
1. Identificar un código ICD-10 relevante (por ejemplo, durante el análisis de notas clínicas con NLP que detecte un evento no cubierto).
2. Consultar la descripción oficial en el CIE-10 OMS.
3. Asignar a una categoría del Anexo 02 EsSalud (las 5 categorías son mutuamente excluyentes — elegir la más representativa).
4. Asignar severidad base usando los criterios de la sección 4.
5. Añadir una fila al CSV respetando el orden de columnas.

### Procedimiento semi-automatizado
Para enriquecer el mapeo a gran escala (ej. añadir 500+ códigos):

```python
# Estrategia: para cada categoría ICD-10 de 3 caracteres ya mapeada,
# añadir sus sub-categorías de 4-5 caracteres con la misma asignación
# de severidad base, marcándolas como "heredadas" para revisión posterior.

import pandas as pd
mapeo = pd.read_csv("eventos_adversos_icd10.csv")
# Lógica de expansión por prefijo de 3 caracteres...
```

### Procedimiento con LLM (para investigación rápida)
Se puede usar un LLM (ej. Claude, GPT-4) para sugerir asignaciones de categoría y severidad a códigos ICD-10 nuevos, pero **toda sugerencia generada por LLM debe ser revisada por un experto humano** antes de incorporarse al CSV. Los LLMs son confiables para identificar el sistema corporal pero pueden equivocarse en severidad clínica fina.

---

## 8. Integración con el pipeline de la tesis

El mapeo se conecta con el pipeline en **dos puntos**:

### Punto de integración 1 — Etapa 1 NLP
Cuando BioBERT/ClinicalBERT detecta una entidad clínica en una nota libre (por ejemplo, "patient fell out of bed"), el componente de UMLS linking (scispaCy) asigna a esa entidad un CUI. El CUI se mapea a un código ICD-10 (vía la tabla UMLS-ICD10 o UMLS-SNOMED-ICD10). El código ICD-10 se busca en este mapeo y devuelve la categoría Anexo 02.

### Punto de integración 2 — Etapa 2 estructurada
La tabla `diagnoses_icd` de MIMIC-IV ya contiene códigos ICD-10 asignados manualmente por codificadores hospitalarios para cada hospitalización. Estos códigos se pueden cruzar directamente con el mapeo para calcular el score Calidad de cada `hadm_id` sin necesidad de NLP previo. Esto es lo que hace la función `resumir_cohorte()` del módulo Python.

La salida final (categoría + severidad por hospitalización) alimenta la dimensión **d** de la fórmula GEMSES `G = c·0.40 + d·0.20 + e·0.15 + f·0.25`.

---

## 9. Próximas iteraciones planificadas

| Versión | Fecha objetivo | Cambios previstos |
|---|---|---|
| **1.0** | 11-May-2026 | Versión inicial con 149 códigos curados (esta) |
| **1.1** | Jun-2026 | Expansión a ~300 códigos cubriendo todos los HACs de CMS + PSIs de AHRQ |
| **1.2** | Ago-2026 | Mapeo CUI ↔ ICD-10 añadido para integración directa con scispaCy |
| **2.0** | Mar-2027 | Calibración de severidad validada por panel experto independiente (kappa de Cohen) |
| **2.1** | May-2027 | Adaptación al CIE-10 PE oficial del MINSA para uso en sistema sanitario peruano (Fase 6 transferencia al castellano) |

---

## 10. Citación y licencia

Si en algún momento usas este mapeo en una publicación, cita así:

```bibtex
@misc{perez2026mapeo,
  author       = {Pérez Pérez, Carlos},
  title        = {Mapeo de codigos ICD-10 a la taxonomia del Anexo 02 EsSalud
                  para operacionalizacion del Modelo GEMSES},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/carlosperez100/tesis-gemses-mimic-pipeline}},
  note         = {Anexo de la tesis de Maestria en IA, Universidad Nacional de Ingenieria}
}
```

**Licencia:** este mapeo se distribuye junto al repositorio bajo los términos definidos en el README. Los datos de MIMIC-IV mencionados están sujetos al PhysioNet Credentialed Health Data Use Agreement v1.5.0 firmado por el autor.

---

*Documento elaborado el 11 de mayo de 2026 como anexo metodológico de la tesis. Versión 1.0.*
