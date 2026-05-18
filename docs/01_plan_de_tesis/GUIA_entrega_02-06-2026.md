# Guía para la entrega parcial del 02 de junio de 2026

**Curso:** MIA 303 — Proyectos de Investigación I
**Entregable:** Capítulo I (Introducción)
**Deadline:** martes 02/06/2026 — 19:00 hs
**Template oficial:** https://www.overleaf.com/read/jbhvhxvqdgyd#8e17ae
**Rúbrica:** 20 puntos (ver desglose abajo)

---

## Archivos disponibles en esta carpeta

| Archivo | Propósito |
|---|---|
| `Plan_Tesis_Cap_I_Carlos_Perez.docx` | Borrador original de abril (mantenido como respaldo) |
| **`Capitulo_I_v2_para_entrega_2026-06-02.docx`** | **Versión actualizada para revisar y editar en Word** |
| **`capitulo1_v2.tex`** | **Contenido en LaTeX listo para pegar en el template de Overleaf** |
| `GUIA_entrega_02-06-2026.md` | Este archivo |

---

## Cómo entregar (paso a paso)

### Paso 1 — Revisa el contenido en Word

Abre `Capitulo_I_v2_para_entrega_2026-06-02.docx` y léelo. Si necesitas ajustar texto, hazlo aquí primero. **No te preocupes por el formato visual** — el formato final lo da Overleaf.

### Paso 2 — Entra al template de Overleaf

1. Ve a https://www.overleaf.com/read/jbhvhxvqdgyd#8e17ae
2. En la esquina superior derecha, haz click en **"Menu"** → **"Copy Project"**.
   Esto crea una copia editable en tu cuenta. (Si no tienes cuenta, créala gratis con tu email UNI.)
3. Una vez copiado, ya puedes editar.

### Paso 3 — Pega el contenido del Capítulo I

1. En el panel izquierdo de Overleaf, busca el archivo del Capítulo I (puede llamarse `capitulo1.tex`, `cap1.tex`, `chapter1.tex` o estar dentro de `main.tex`).
2. Abre `capitulo1_v2.tex` (de esta carpeta) en un editor de texto.
3. Copia **todo el bloque** entre las líneas:

   ```
   % ========== COPIAR A PARTIR DE AQUI ==========
   ...contenido...
   % ========== HASTA AQUI COPIAR ==========
   ```

4. Pégalo dentro del archivo correspondiente del template.
5. **Importante:** si el template usa `\section{Introducción}` en vez de `\chapter{Introducción}`, comenta la línea del `\chapter` y descomenta la del `\section` (está indicado dentro del .tex).

### Paso 4 — Agrega las referencias bibliográficas

Al final del archivo `capitulo1_v2.tex` hay un bloque comentado con 9 entradas BibTeX. Cópialas al archivo `.bib` del template (suele llamarse `referencias.bib`, `bibliography.bib` o `biblio.bib`).

### Paso 5 — Compila en Overleaf

Click en **"Recompile"** en la barra superior. Si hay errores:

- Si falta algún paquete (`\citep`, `\citet`), revisa que el template tenga `\usepackage{natbib}` o `\usepackage{biblatex}`. Si usa biblatex, reemplaza `\citep{...}` por `\cite{...}`.
- Si faltan referencias, asegúrate de haber agregado el `.bib`.

### Paso 6 — Descarga el PDF y envíalo

Una vez compilado, descarga el PDF (Menu → Download → PDF) y envíalo al canal del curso antes del **02/06/2026 19:00**.

---

## Mapeo de tu contenido a la rúbrica (20 pts)

| Criterio | Pts | En qué sección del Capítulo está respondido |
|---|---:|---|
| **Formulación del Problema** | 4 | §1.1 — pregunta formulada en bloque destacado |
| **Hipótesis** | 3 | §1.2 — Hipótesis General + 4 Hipótesis Específicas (H₁–H₄) |
| **Objetivo General** | 4 | §1.3.1 — un único párrafo enfocado |
| **Objetivos Específicos** | 3 | §1.3.2 — 6 objetivos numerados, cada uno trazable a una hipótesis |
| **Justificación** | 3 | §1.4 — cuatro perspectivas (teórica, metodológica, práctica, social) |
| **Coherencia Global** | 3 | §1.6 — Estado de avance con métricas que conectan problema↔hipótesis↔objetivos↔resultados parciales |

---

## Fortalezas de esta versión (para anticipar comentarios del docente)

1. **El Estado de avance (§1.6) es tu carta fuerte** — pocos compañeros tendrán *resultados empíricos parciales* en el Capítulo I. La precisión 78%, el RR=1.49 y las 1,499 detecciones validadas dan una coherencia inmediata entre objetivos y viabilidad.

2. **Las hipótesis están redactadas como predicciones medibles** (con umbrales numéricos: 25 pp, 10 pp, RR > 1.3, ±10 %). Esto es la diferencia entre una hipótesis "buena" y una "excelente" según la mayoría de rúbricas académicas.

3. **El "principio rector"** (NLP detecta, GEMSES prioriza conforme a la directiva) **al inicio del Capítulo** comunica de inmediato la postura metodológica y desarma la pregunta crítica obvia: *"¿por qué no modificas el modelo?"*. Respuesta: porque se aplica la norma vigente sin alterarla.

4. **Los Objetivos Específicos están enumerados y cada uno es trazable** a una hipótesis o sub-resultado. Eso facilita la calificación del jurado/docente.

---

## Antes de enviar — checklist final

- [ ] El PDF compila sin errores en Overleaf.
- [ ] Todas las citas `\citep{...}` resuelven (no aparecen como `[?]` en el PDF).
- [ ] La portada tiene tu nombre, el curso y la fecha 02/06/2026.
- [ ] El número de páginas del Capítulo I está entre 6 y 12 (rango típico).
- [ ] Revisaste ortografía y acentos (Word lo hace bien; Overleaf no tanto).
- [ ] El docente te recibe en el canal/plataforma correcta (sigue las instrucciones del curso).

---

## Si algo falla en Overleaf

Pídeme ayuda inmediata. Los problemas típicos son:

1. **El template usa una clase de documento que no acepta `\chapter`** → cambia a `\section`.
2. **El template tiene un bibliography style raro** → cambia el comando `\bibliographystyle{...}`.
3. **Caracteres con acento se rompen** → asegúrate de tener `\usepackage[utf8]{inputenc}` y `\usepackage[T1]{fontenc}` en el preámbulo.

Si compartes screenshots del error de Overleaf, te los puedo diagnosticar uno por uno.
