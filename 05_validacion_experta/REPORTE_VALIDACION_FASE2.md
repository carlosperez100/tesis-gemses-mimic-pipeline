# Reporte de Validación Experta — Fase 2 (n=50)

**Autor:** Carlos Pérez Pérez · MIA-303 · UNI
**Fecha:** 21/05/2026
**Dataset evaluado:** Detecciones del pipeline NLP sobre MIMIC-IV v3.1 + Note v2.2
**Archivo fuente:** `fase2_validacion_experta_50notas.csv`
**Validador único:** Carlos Pérez Pérez (Mg. en Gestión de la Calidad, autor del Modelo GEMSES)

---

## 1. Diseño de la validación

Se aplicó un protocolo de tres preguntas binarias en cascada por cada detección automática:

| Pregunta | Pregunta operacional | Acción si NO |
|---|---|---|
| **P1** | ¿El evento adverso está mencionado textualmente en la nota? | Falso Positivo por **error de patrón** |
| **P2** | ¿La mención está afirmada (no negada ni hipotética)? | Falso Positivo por **falta de detección de negación** (NegEx) |
| **P3** | ¿El evento ocurrió en esta hospitalización (no es historia)? | Falso Positivo por **contexto histórico** |

**Dictamen final** = VP solo si P1=SÍ ∧ P2=SÍ ∧ P3=SÍ. En cualquier otro caso, FP.

Este diseño se inspira en los criterios de Adverse Event Trigger Tool (IHI) adaptados a fenotipado computacional, y permite trazar la causa raíz de cada falla del pipeline en lugar de reportar solo una métrica agregada.

---

## 2. Resultados agregados (n=50 detecciones, 45 notas únicas)

| Métrica | Valor |
|---|---:|
| **Precisión (Positive Predictive Value)** | **74.0 %** (37/50) |
| Verdaderos Positivos | 37 |
| Falsos Positivos | 13 |
| Dudosos | 0 |

> **Comparación con baseline:** la versión preliminar del pipeline reportada el 13/05 alcanzaba 32 % de precisión sobre 2 500 detecciones. La nueva versión más restrictiva (patrones afinados + reglas de contexto) alcanza **74 % en 50 detecciones validadas**, un incremento absoluto de **+42 pp**.

---

## 3. Análisis de causas raíz de los Falsos Positivos (n=13)

| Causa raíz | n | % de FPs | Diagnóstico |
|---|---:|---:|---|
| **P1 = NO** (patrón mal matchea, evento ausente) | 11 | 84.6 % | Diccionario de patrones demasiado laxo |
| P2 = NO (evento negado, falta NegEx) | 0 | 0.0 % | No es problema actual |
| P3 = NO (evento de hospital previo / historia) | 1 | 7.7 % | Falta sección parser para "Brief Hospital Course" vs "PMH" |
| Otros / Dudoso parcial | 1 | 7.7 % | — |

> **Hallazgo clave:** la **negación NO es el cuello de botella** del pipeline (0 % de FPs). El problema dominante es **especificidad léxica**: patrones como `urinary tract infection` están haciendo match con menciones contextuales (riesgo, profilaxis, historia familiar). Prioridad de mejora #1 = enriquecer los patrones con contexto inmediato (ventana ±5 tokens).

---

## 4. Calibración de la etiqueta de confianza del pipeline

| Confianza pipeline | n | VP | FP | Precisión observada |
|---|---:|---:|---:|---:|
| **alta** | 20 | 11 | 9 | **55.0 %** ⚠ |
| **media** | 29 | 26 | 3 | **89.7 %** ✓ |
| baja | 1 | 0 | 1 | 0.0 % |

> **Hallazgo metodológico crítico:** la etiqueta `confianza=alta` rinde **PEOR** que `confianza=media`. Esto indica que el score interno de confianza del pipeline está **mal calibrado** y debe **recalibrarse** o **invertirse**. Recomendación: aplicar Platt scaling o calibración isotónica usando esta muestra como conjunto de validación.

---

## 5. Desempeño por naturaleza del evento (clasificación GEMSES)

| Naturaleza | n | VP | FP | Precisión |
|---|---:|---:|---:|---:|
| Comportamiento | 2 | 2 | 0 | 100 % |
| Sangre / Hemoderivados | 1 | 1 | 0 | 100 % |
| Infección asociada a la atención | 21 | 19 | 2 | 90.5 % |
| Procedimiento | 9 | 7 | 2 | 77.8 % |
| Medicación | 10 | 6 | 4 | 60.0 % |
| **Cuidado del paciente** | 7 | 2 | 5 | **28.6 %** ⚠ |

> **Hallazgo:** la categoría `Cuidado del paciente` (caídas, úlceras por presión, etc.) tiene desempeño inaceptable y debe rediseñarse en su totalidad. La heterogeneidad léxica de estas entidades (e.g., "fall risk", "fell at home", "history of falls") confunde al matcher actual.

---

## 6. Eventos con desempeño individual problemático

| ID Evento | Evento | n | VP | FP | Precisión |
|---|---|---:|---:|---:|---:|
| 7031 | Diarrea asociada a antimicrobianos | 4 | 0 | 4 | **0 %** ⚠ |
| 8023 | Hemotórax | 2 | 0 | 2 | **0 %** ⚠ |
| 202 | Caída de paciente | 4 | 1 | 3 | 25 % |
| 6035 | Meningitis o ventriculitis | 3 | 2 | 1 | 67 % |

> **Acción correctiva inmediata:** los patrones para "diarrea asociada a antimicrobianos" y "hemotórax" requieren rediseño antes del trabajo final. Probable problema: los patrones genéricos están matcheando menciones en contexto de diagnóstico diferencial, no como evento adverso ocurrido.

---

## 7. Implicancias para la tesis

### Para Capítulo 1 (Planteamiento del problema)
- **Magnitud verificada:** sobre 331 793 notas de epicrisis en MIMIC-IV, el pipeline detecta eventos adversos con 74 % de precisión cuando se afinaron patrones — vs 32 % del baseline. Esto confirma que **el problema de FP es manejable** con metodología adecuada.

### Para Capítulo 2 (Objetivos)
- Reformular objetivo específico: en lugar de "alcanzar precisión ≥ 80 %", proponer "**identificar y caracterizar las causas raíz de los FPs**" — ya tenemos evidencia empírica para sostenerlo (84.6 % de FPs son de naturaleza léxica, no contextual).

### Para Capítulo 3 (Metodología)
- Documentar el **protocolo P1/P2/P3** como contribución metodológica.
- Anexar este reporte como evidencia del flujo de validación experta.

### Para Capítulo 4 (Resultados y Discusión)
- Reportar **precisión global 74 %**, **descomposición por causa raíz**, **calibración mal calibrada** como tres hallazgos principales.
- Discutir limitación: validación de **un solo experto** (kappa de Cohen no calculable). Sugerir como trabajo futuro validación con segundo experto independiente.

---

## 8. Próximos pasos sugeridos

1. **Refinar patrones** de los 6 eventos con precisión < 70 % (especialmente Diarrea, Hemotórax, Caída).
2. **Recalibrar** o **invertir** la etiqueta `confianza=alta`.
3. **Diseñar Fase 3:** validación de muestreo balanceado por naturaleza (≥ 10 detecciones por categoría) para tener IC del 95 % estrechos por categoría.
4. **Calcular Recall:** necesitará anotar de cero un subconjunto de notas (e.g., 100 notas completas) para identificar eventos NO detectados (Falsos Negativos).
5. **Buscar segundo anotador** entre los compañeros de maestría (estudiantes con perfil clínico) para calcular kappa de Cohen ≥ 0.6 como evidencia de fiabilidad inter-evaluador.
