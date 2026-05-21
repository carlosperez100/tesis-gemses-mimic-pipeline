# 📋 INVENTARIO MAESTRO — Tesis GEMSES × MIMIC-IV

**Autor:** Carlos Pérez Pérez · MIA-303 UNI
**Última reorganización:** 21/05/2026 16:00
**Fuente única de verdad:** esta carpeta OneDrive
**Repositorio Git destino:** `C:\MIMIC\tesis` (sincronizado vía `.bat`)
**Sitio público:** https://carlosperez100.github.io/tesis-gemses-mimic-pipeline/

---

## 🚀 INICIO RÁPIDO

1. **Para ver el panorama del proyecto** → abrir `00_lectura_rapida/PROYECTO_TESIS_ESTADO.md`
2. **Para conocer las fechas y criterios del curso** → abrir `08_administracion_curso/CRONOGRAMA_OFICIAL_MIA303.md`
3. **Para subir todo a GitHub** → doble clic en `_scripts_sincronizacion/SINCRONIZAR_TESIS_v3.bat`

---

## 📁 ESTRUCTURA DE CARPETAS (10 carpetas, 46 archivos, 8.2 MB)

### `00_lectura_rapida/` (5 archivos)
Documentos de entrada al proyecto — léelos primero si retomas el trabajo después de una pausa.
| Archivo | Descripción |
|---|---|
| `PROYECTO_TESIS_ESTADO.md` | Estado consolidado del proyecto |
| `HISTORIAL_PASOS_TESIS.md` | Bitácora cronológica de 9 etapas |
| `GUIA_DEL_STACK.md` | Setup Python + DuckDB + JupyterLab |
| `README_repo_actualizado.md` | README maestro del repositorio |
| `SKILL_tesis-gemses-mimic.md` | Plantilla de skill para futuras sesiones |

### `01_plan_de_tesis/` (1 archivo)
| Archivo | Descripción |
|---|---|
| `Plan_Tesis_Cap_I_Carlos_Perez.docx` | Capítulo I (planteamiento + justificación) |

### `02_revision_literatura/` (4 archivos)
Trabajo de revisión sistemática (12 papers). Listo para entregar como Resúmenes el **DOM 24/05**.
| Archivo | Descripción |
|---|---|
| `Resumen_12_Articulos_MIA303_FINAL.pdf` | **PDF final compilado (36 pp)** |
| `Resumen_12_Articulos_MIA303_FINAL.tex` | Fuente LaTeX (Overleaf-ready) |
| `Resumen_12_Articulos_MIA303_v3_Citas_y_Formulas.docx` | Versión Word con citas «…» |
| `Strings_Busqueda_y_Guia_PhysioNet.docx` | Strings de búsqueda y guía operativa |

### `03_metodologia_critica/` (2 archivos)
| Archivo | Descripción |
|---|---|
| `Workflow_Lit_Review_Adversarial_Preregistro.docx` | Lit-review + Devils-advocate + Preregistro |
| `DOCUMENTACION_MAPEO_ICD10.md` | Metodología del mapeo ICD-10 → Anexo 02 GEMSES |

### `04_pipeline_codigo/` (7 archivos + 4 datos intermedios)
Todo el código Python del pipeline NLP sobre MIMIC-IV.
| Archivo | Descripción |
|---|---|
| `tesis_pipeline.py` | **Script único de replicación (445 líneas)** |
| `tesis_exploracion_inicial.ipynb` | Notebook de exploración Jupyter |
| `mapeo_eventos_gemses_v2.py` | Módulo de clasificación ICD-10 → GEMSES |
| `analisis_eventos_adversos.py` | Análisis de detecciones de eventos |
| `analisis_estancia_flujo.py` | Análisis de estancia hospitalaria |
| `pipeline_clasificacion_texto.py` | Clasificador de texto base |
| `eventos_adversos_icd10_v2.csv` | Mapeo ICD-10 ↔ 51 eventos Anexo 02 (149 códigos) |
| `datos_intermedios/0.parquet` | Datasets intermedios del pipeline |
| `datos_intermedios/codes.parquet` | Códigos ICD-10 procesados |
| `datos_intermedios/subject_splits.parquet` | Splits paciente/cohorte |
| `datos_intermedios/dataset.json` | Metadata del dataset |

### `05_validacion_experta/` (2 archivos + 4 datos + 2 figuras)
**El resultado más importante de la tesis al 21/05/2026.**
| Archivo | Descripción |
|---|---|
| `REPORTE_VALIDACION_70_EVENTOS.md` | **Reporte académico definitivo n=70 (precisión 65.7 %, IC95 54-76 %)** |
| `REPORTE_VALIDACION_FASE2.md` | Reporte detallado de Fase 2 (n=50) |
| `datos_crudos/fase2_validacion_experta_20notas.csv` | Datos crudos Fase 1 (n=20, 45 % precisión) |
| `datos_crudos/fase2_validacion_experta_50notas.csv` | Datos crudos Fase 2 (n=50, 74 % precisión) |
| `datos_crudos/validacion_70_consolidada.csv` | CSV combinado de las 2 fases |
| `datos_crudos/metricas_validacion_70.csv` | Resumen numérico de métricas |
| `figuras/grafico_validacion_70.png` | **Figura 4 paneles (lista para LaTeX)** |
| `figuras/grafico_fase2_validacion.png` | Figura 4 paneles solo Fase 2 |

### `06_presentaciones_y_showcase/` (2 archivos actuales + 3 versiones anteriores)
| Archivo | Descripción |
|---|---|
| `Showcase_Tesis_GEMSES_MIMIC_v4.html` | **Showcase actual (será `index.html` en GitHub Pages)** |
| `Sustentacion_MIA303_GEMSES_MIMIC.pptx` | PPT de sustentación 12 slides |
| `showcase_versiones_anteriores/v1, v2, v3` | Versiones anteriores (referencia histórica) |

### `07_bitacoras/` (1 archivo)
| Archivo | Descripción |
|---|---|
| `Informe_Sesion_14_Mayo_2026.docx` | Bitácora formal sesión 14 mayo (con carátula UNI) |

### `08_administracion_curso/` (1 archivo)
| Archivo | Descripción |
|---|---|
| `CRONOGRAMA_OFICIAL_MIA303.md` | **Fechas oficiales Mg Tejada + criterios de evaluación** |

### `99_trabajo_externo_no_tesis/` (6 archivos)
Trabajos previos relacionados pero NO parte del entregable de tesis. Material de respaldo.
| Archivo | Descripción |
|---|---|
| `Clasificador_ERSP_EsSalud.html` | Clasificador ERSP EsSalud (proyecto previo) |
| `Informe_NLP_ML_ERSP_EsSalud.docx` | Informe ERSP EsSalud |
| `ERSP_con_prediccion.xlsx` | Dataset ERSP con predicciones |
| `Resumen_12_Articulos_MIA303.tex` | Versión preliminar del LaTeX (legacy) |
| `mapeo_eventos_gemses.py` | Versión 1 del módulo (legacy) |
| `eventos_adversos_icd10.csv` | Versión 1 del CSV (legacy) |

### `_scripts_sincronizacion/` (2 archivos)
| Archivo | Descripción |
|---|---|
| `SINCRONIZAR_TESIS_v2.bat` | Versión anterior del script |
| `SINCRONIZAR_TESIS_v3.bat` | **Script DEFINITIVO (usa nueva estructura)** |

---

## 🔄 FLUJO DE TRABAJO

```
OneDrive (esta carpeta)         →    C:\MIMIC\tesis            →    GitHub
─────────────────────────────        ──────────────────             ───────────────
Fuente única de verdad               Repo local Git                 Repo remoto público
Donde editas archivos                Solo recibe copias             Donde se publica
                                                                    Showcase a GitHub Pages
```

**Regla de oro:** SIEMPRE editar archivos en OneDrive (esta carpeta). NUNCA editar directamente en `C:\MIMIC\tesis` (se sobreescribe en la próxima sincronización).

**Para sincronizar:** doble clic en `_scripts_sincronizacion/SINCRONIZAR_TESIS_v3.bat` → abrir GitHub Desktop → commit → push.

---

## 📊 INDICADORES DEL PROYECTO AL 21/05/2026

| Indicador | Valor |
|---|---|
| Notas MIMIC-IV epicrisis (total) | 331 793 |
| Pacientes únicos | 145 914 |
| Notas validadas manualmente | 70 (de 60 únicas) |
| Eventos GEMSES distintos detectados | 34 / 51 del Anexo 02 |
| **Precisión global del pipeline** | **65.7 %** (IC 95 % Wilson: 54.0–75.8 %) |
| Mejora Fase 1 → Fase 2 | +29 pp (p = 0.021) |
| Categorías mejores (≥ 75 %) | Infección, Procedimiento |
| Categorías a rediseñar (< 50 %) | Cuidado del paciente, Medicación |

---

## 📆 PRÓXIMAS FECHAS (desde 21/05/2026)

| Fecha | Hito | Acción |
|---|---|---|
| **DOM 24/05** | Resúmenes (mín. 9) | ✅ Ya enviados a maria.tejada.b@uni.edu.pe el 14/05 |
| **DOM 31/05** | Trabajo Parcial (Cap 1 + 2) | 🔥 Migrar a template Overleaf `jbhvhxvqdgyd#8e17ae` |
| MAR 16/06 | Presentación Parcial #6 | Preparar slides 25 min |
| DOM 12/07 | Trabajo Final (Cap 1-4) | Integrar Fase 3, 4, 5 del pipeline |
| MAR 14/07 | Presentación Final #1 (¡abres bloque!) | Preparar slides 25 min |
