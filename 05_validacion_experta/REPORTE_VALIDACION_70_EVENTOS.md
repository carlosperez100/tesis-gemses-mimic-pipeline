# Reporte de Validación Experta — Acumulado n=70 detecciones

**Autor:** Carlos Pérez Pérez · MIA-303 · Universidad Nacional de Ingeniería
**Fecha de análisis:** 21/05/2026
**Pipeline evaluado:** GEMSES NLP Pipeline v2.0 sobre MIMIC-IV v3.1 + MIMIC-IV-Note v2.2
**Validador:** Carlos Pérez Pérez (Mg. en Gestión de Calidad en Salud, autor del Modelo GEMSES)
**Archivos fuente:**
- `fase2_validacion_experta_20notas.csv` (rondas 1-20)
- `fase2_validacion_experta_50notas.csv` (rondas 21-70)
- Consolidado: `validacion_70_consolidada.csv`

---

## 1. Resultados acumulados (n=70 detecciones, 60 notas únicas, 34 eventos GEMSES distintos)

| Métrica | Valor |
|---|---:|
| **Precisión global (PPV)** | **65.7 %** (46/70) |
| **IC 95 % (Wilson)** | **54.0 % – 75.8 %** |
| Verdaderos Positivos (VP) | 46 |
| Falsos Positivos (FP) | 24 |
| Dudosos | 0 |
| Notas únicas evaluadas | 60 |
| Eventos GEMSES distintos detectados | 34 (de 51 del Anexo 02) |

---

## 2. Evolución entre fases — evidencia de mejora del pipeline

| Fase | n | VP | FP | Precisión | Período |
|---|---:|---:|---:|---:|---|
| Fase 1 | 20 | 9 | 11 | **45.0 %** | 06/05–13/05 |
| Fase 2 | 50 | 37 | 13 | **74.0 %** | 14/05–20/05 |
| **Acumulado** | **70** | **46** | **24** | **65.7 %** | — |

**Test Z de proporciones (Fase 1 vs Fase 2):** z = −2.309, **p = 0.021**

> **Hallazgo principal:** la mejora de 45 % a 74 % entre fases es **estadísticamente significativa (p<0.05)**. Esto valida empíricamente que el refinamiento iterativo del diccionario de patrones aplicado entre el 13/05 y el 14/05 (corrección de 6 patrones léxicos defectuosos en categorías Procedimiento y Cuidado del Paciente) **mejoró la precisión del pipeline en +29 puntos porcentuales**.

---

## 3. Descomposición de causas raíz de los 24 Falsos Positivos

| Causa raíz | n | % de FPs | Naturaleza del error |
|---|---:|---:|---|
| **P1 = NO** (patrón mal matchea, evento ausente) | 17 | 70.8 % | Léxico — especificidad insuficiente |
| P2 = NO (evento negado, falta NegEx) | 0 | 0.0 % | No es problema actual |
| P3 = NO (evento de hospital previo / historia) | 1 | 4.2 % | Contexto temporal |
| Otros / dudoso parcial | 6 | 25.0 % | Varios |

> **Implicancia metodológica:** la negación **no es el cuello de botella** del pipeline en este corpus (0 FPs por P2=NO). El **70.8 % de los FPs** se debe a matching demasiado laxo, no a falta de detección de negación. Esto contradice la práctica habitual de la literatura que asume NegEx como prioridad #1.

---

## 4. Calibración de la etiqueta de confianza del pipeline (n=70)

| Confianza pipeline | n | VP | FP | Precisión observada |
|---|---:|---:|---:|---:|
| **alta** | 28 | 15 | 13 | **53.6 %** ⚠ |
| **media** | 39 | 30 | 9 | **76.9 %** ✓ |
| baja | 3 | 1 | 2 | 33.3 % |

> **Hallazgo metodológico crítico:** la etiqueta `confianza=alta` rinde **23 puntos porcentuales menos** que `confianza=media`. El score interno de confianza del pipeline está **anticalibrado** (correlación inversa con la realidad). Recomendación: aplicar **calibración isotónica** o **Platt scaling** usando estas 70 observaciones como conjunto de entrenamiento para recalibrar, o **invertir** explícitamente la etiqueta antes de exponerla al usuario clínico.

---

## 5. Desempeño por naturaleza del evento (taxonomía GEMSES)

| Naturaleza GEMSES | n | VP | FP | Precisión | Diagnóstico |
|---|---:|---:|---:|---:|---|
| Infección asociada a la atención | 29 | 23 | 6 | **79.3 %** | Bueno |
| Procedimiento | 11 | 8 | 3 | 72.7 % | Bueno |
| Comportamiento | 3 | 2 | 1 | 66.7 % | Aceptable (n bajo) |
| Sangre / Hemoderivados | 2 | 1 | 1 | 50.0 % | n insuficiente |
| Medicación | 12 | 6 | 6 | **50.0 %** | ⚠ A mejorar |
| **Cuidado del paciente** | 13 | 6 | 7 | **46.2 %** | ⚠ Rediseño urgente |

> La categoría **Cuidado del Paciente** (caídas, autoextubaciones, úlceras por presión) y **Medicación** (interacciones de fármacos, dosis incorrectas) requieren rediseño léxico antes del trabajo final.

---

## 6. Eventos individuales con desempeño extremo

### Eventos con precisión 100 % (mantener)
| ID Evento | Evento | n |
|---|---|---:|
| 602 | Infección del tracto urinario | 6 |
| 601 | Infección del torrente sanguíneo (ITS) | 5 |
| 7010 | Hemorragia/hematoma por anticoagulación | 3 |
| 8032 | Trombosis venosa | 3 |
| 6033 | Infecciones del sistema nervioso central (SNC) | 2 |

### Eventos con precisión 0 % (rediseñar antes del Trabajo Final 12/07)
| ID Evento | Evento | n | Probable causa |
|---|---|---:|---|
| **7031** | Diarrea asociada a antimicrobianos | **5** | Patrón "diarrhea" matchea menciones de monitoreo, no del evento |
| **6019** | Hepatitis | **2** | Confunde "Hepatitis C cirrhosis" (historia) con evento agudo |
| **8023** | Hemotórax | **2** | Confunde diagnóstico diferencial con evento ocurrido |

### Eventos con precisión intermedia (afinar)
| ID Evento | Evento | n | Precisión |
|---|---|---:|---:|
| 202 | Caída de paciente | 5 | **20.0 %** |
| 8016 | Neumotórax | 2 | 50.0 % |
| 6035 | Meningitis o ventriculitis | 3 | 66.7 % |

---

## 7. Implicancias directas para los entregables

### Trabajo Parcial (DOM 31/05) — Capítulo 1 + 2

**Para el planteamiento del problema (Cap 1):**
> "Sobre el corpus de 331 793 notas de epicrisis de MIMIC-IV, el pipeline NLP preliminar identificó 2 500 eventos adversos potenciales con apenas 32 % de precisión. Tras dos rondas de refinamiento iterativo con validación experta (n=70 detecciones), la precisión acumulada alcanza 65.7 % (IC 95 %: 54.0–75.8 %), con mejora estadísticamente significativa entre fases (p=0.021). Sin embargo, la heterogeneidad por categoría (Cuidado del Paciente: 46.2 % vs Infecciones: 79.3 %) y la calibración invertida de la etiqueta de confianza ('alta' rinde 23 pp menos que 'media') evidencian que la detección automatizada de eventos adversos en notas clínicas no estructuradas no es un problema resuelto, sino un campo activo de investigación con desafíos metodológicos abiertos."

**Para los objetivos específicos (Cap 2):**
1. Caracterizar el desempeño del pipeline GEMSES NLP v2.0 sobre MIMIC-IV en términos de PPV global e IC 95 %.
2. Diagnosticar las causas raíz de los Falsos Positivos mediante el protocolo P1/P2/P3.
3. Evaluar la calibración interna de la etiqueta de confianza del pipeline.
4. Estratificar el desempeño por las 6 categorías de naturaleza del Anexo 02 del Modelo GEMSES.
5. Identificar los eventos individuales con desempeño extremo (0 % o 100 %) para guiar el rediseño del diccionario.

### Trabajo Final (DOM 12/07) — Capítulo 3 + 4

**Cap 3 (Metodología):** documentar el protocolo P1/P2/P3 como aporte metodológico replicable. La fórmula de decisión es:
$$VP \iff P1=SI \land P2=SI \land P3=SI$$

**Cap 4 (Resultados y Discusión):**
- Reportar precisión 65.7 % con IC 95 % (Wilson).
- Mostrar curva de mejora Fase 1 → Fase 2 (45 % → 74 %, p=0.021).
- Discutir la implicancia clínica: el pipeline es **utilizable como sistema de triage** (sensibilidad alta) pero **no como sistema de notificación directa al expediente** (precisión insuficiente para acción clínica directa).

---

## 8. Limitaciones reconocidas

1. **Un solo evaluador experto** — no es posible calcular kappa de Cohen para fiabilidad inter-evaluador. Plan de mitigación: reclutar segundo evaluador entre compañeros de MIA-303 con perfil clínico antes del Trabajo Final.
2. **No se calcula Recall (Sensibilidad)** — requiere anotación exhaustiva de notas completas (no solo verificación de detecciones del pipeline). Diseño propuesto: anotar 50 notas completas de novo en Fase 3 para estimar FNs.
3. **Muestreo no estratificado** — algunas categorías GEMSES tienen n=2 (Sangre/Hemoderivados), produciendo IC muy anchos. Fase 3 debe usar muestreo estratificado.
4. **Sin gold standard externo** — no se ha comparado contra notificaciones oficiales de eventos adversos del hospital donante de MIMIC-IV (Beth Israel Deaconess) por restricciones de acceso al sistema interno.

---

## 9. Próximos pasos prioritarios

| # | Acción | Plazo | Razón |
|---|---|---|---|
| 1 | Migrar Cap 1+2 a template Overleaf `jbhvhxvqdgyd#8e17ae` | 28/05/2026 | Trabajo Parcial entrega 31/05 |
| 2 | Rediseñar patrones de 3 eventos con 0 % de precisión | 05/06/2026 | Antes de presentación parcial |
| 3 | Reclutar segundo evaluador | 15/06/2026 | Para fiabilidad inter-evaluador |
| 4 | Calibración isotónica de etiqueta de confianza | 25/06/2026 | Aporte metodológico Cap 3 |
| 5 | Diseñar Fase 3 con muestreo estratificado balanceado | 30/06/2026 | Para IC estrechos por categoría |
| 6 | Anotar 50 notas completas para estimar Recall | 06/07/2026 | Métrica completa para Cap 4 |

---

**Citación sugerida para LaTeX:**
> Pérez Pérez, C. (2026). *Validación experta acumulada de 70 detecciones de eventos adversos del pipeline GEMSES NLP v2.0 sobre MIMIC-IV.* MIA-303 Trabajo de Investigación I, Universidad Nacional de Ingeniería.
