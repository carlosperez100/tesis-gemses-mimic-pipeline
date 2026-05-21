---
name: tesis-gemses-mimic
description: Activa el contexto completo del proyecto de tesis de Carlos Pérez Pérez sobre detección automatizada de eventos adversos en notas clínicas no estructuradas mediante NLP y aprendizaje automático, aplicando la Matriz de Priorización del Modelo GEMSES sobre MIMIC-IV. Activar cuando Carlos mencione tesis MIA 303, MIMIC-IV, GEMSES, eventos adversos, pipeline NLP, BioBERT, ClinicalBERT, ERSP de EsSalud, Directiva GG-ESSALUD-2021, priorización de riesgo clínico, o cuando retome el proyecto desde una sesión previa.
---

# Proyecto de Tesis — Carlos Pérez Pérez · MIA 303 UNI

## Identidad del proyecto

**Título:** Detección automatizada y priorización de eventos adversos desde notas clínicas no estructuradas mediante un flujo de procesamiento (pipeline) de NLP y aprendizaje automático — aplicación de la Matriz de Priorización del Modelo GEMSES sobre el dataset MIMIC-IV.

**Autor:** Carlos Pérez Pérez (carlosperez100@gmail.com)
**Curso:** MIA 303 — Proyectos de Investigación I (UNI)
**Docente:** Mg. Eng. Maria F. Tejada Begazo
**Periodo:** Mayo 2026 — Mayo 2027

## Activos confirmados

- **Email del autor:** carlosperez100@gmail.com
- **Repositorio:** https://github.com/carlosperez100/tesis-gemses-mimic-pipeline
- **Sitio oficial del Modelo GEMSES:** https://sites.google.com/view/gemses/inicio
- Carpeta local: C:\MIMIC\tesis
- MIMIC-IV v3.1 (DOI: 10.13026/kpb9-mt58) — usuario PhysioNet: carlosperez
- MIMIC-IV-Note v2.2 (DOI: 10.13026/1n74-ne17)
- CITI Program: ID 1912 (UNI) + ID 3641 (EsSalud, Record 54788726, vigente 28-Abr-2029)
- Stack: Python 3.13.5 + DuckDB 1.5.2 + JupyterLab 4.5.7 + Git 2.53

## Decisiones clave inmovibles

1. **DuckDB**, no PostgreSQL (sin servidor, lectura directa de CSVs comprimidos).
2. **MIMIC-IV es el dataset principal**, no hay acceso a HCE de EsSalud.
3. **Arquitectura multimodal** texto + tabular siguiendo Liu X. et al. 2024 (JMIR).
4. **Comillas latinas «...»** para citas de autores; texto plano para análisis del alumno.
5. **No hay aval institucional EsSalud** para la tesis (solo afiliación CITI). Conflicto de interés declarado explícitamente.

## Los 12 papers del marco teórico

**Tema 1 NLP:** [1] Modi & Feldman 2024, [2] Wang et al. 2024, [3] Mahendran et al. 2025, [4] Campillos-Llanos 2023 (MedLexSp).
**Tema 2 MIMIC-IV:** [5] Johnson et al. 2023, [6] van Aken et al. 2024, [7] Hu et al. 2024, [8] Liu X. et al. 2024.
**Tema 3 Priorización:** [9] Liu H.C. et al. 2023, [10] Kovačević et al. 2024, [11] Khan et al. 2025, [12] Ferrara et al. 2024.

## Fórmula GEMSES (Anexo 03 Directiva GG-ESSALUD-2021)

```
G = c·0.40 + d·0.20 + e·0.15 + f·0.25
```

Donde c=Tiempo, d=Calidad, e=Costos, f=Satisfacción. Derivadas: H=B·G (Riesgo), I=H÷Σh (Gestión), J=I×100 → percentiles P25/P50/P75 → Verde/Amarillo/Rojo.

## Operacionalización GEMSES → MIMIC-IV (aporte original)

| Dimensión | Peso | Variable proxy MIMIC-IV |
|---|---|---|
| Tiempo (c) | 0.40 | Length of Stay vs mediana DRG |
| Calidad (d) | 0.20 | ICD-9/10 complicaciones + NER eventos |
| Costos (e) | 0.15 | DRG weight + procedimientos invasivos |
| Satisfacción (f) | 0.25 | Readmisión 30d + AMA discharge |

## Estado de la sesión anterior

Última sesión: 10-11 mayo 2026. Cerrada con:
- 12 papers analizados y entregados (Word v3 + LaTeX en Overleaf).
- PPT 12 slides para sustentación generado y verificado visualmente.
- Entorno Python + DuckDB + JupyterLab instalado y funcional.
- Repositorio GitHub publicado con 7 documentos definitivos.
- Descarga de MIMIC-IV-Note en progreso (1.8 GB).

## Próximo paso al retomar

1. Confirmar descarga MIMIC-IV-Note completa y extraída en C:\MIMIC\note\.
2. Ejecutar tesis_exploracion_inicial.ipynb (DuckDB + 5 queries de descubrimiento).
3. Capturar Sección 4.1 (distribución de notas por tipo) y 4.2 (longitud).
4. Construir el segundo notebook (fase2_nlp_bioBERT.ipynb) calibrado a los datos reales.
5. Sustentación PPT pendiente para 12 o 19 de mayo 2026.

## Guía de respuesta para este perfil

- **Tono:** académico-profesional, no condescendiente. Carlos tiene background sólido en gestión de calidad sanitaria y prerequisitos de IA cumplidos.
- **Especifidad técnica:** mencionar nombres exactos de papers [N], paths exactos (C:\MIMIC\...), comandos exactos.
- **Reconocer su doble identidad:** alumno UNI + Asesor EsSalud + autor GEMSES. Cada una se invoca según el momento del proyecto.
- **Respetar el "un paso a la vez":** cuando esté en ejecución técnica (instalación, configuración, comandos), dar UN solo paso y esperar confirmación antes del siguiente.
- **Proteger el DUA:** nunca sugerir compartir datos de pacientes, subir a nubes públicas, o redistribuir MIMIC.
- **Idioma:** español académico, con anglicismos técnicos aceptados (pipeline, fine-tuning, embedding, NLP).
