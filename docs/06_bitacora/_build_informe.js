const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, LevelFormat, TableOfContents, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, PageBreak, Header, Footer } = require("docx");

// ---------- helpers ----------
const FONT = "Arial";
const MONO = "Consolas";

// monospace code/diagram block
function mono(text) {
  return text.split("\n").map(line =>
    new Paragraph({
      shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
      spacing: { before: 0, after: 0 },
      children: [new TextRun({ text: line || " ", font: MONO, size: 16 })],
    })
  );
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    ...opts,
    children: [new TextRun({ text, font: FONT, size: 22, ...(opts.run || {}) })],
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}
function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: FONT })] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: FONT })] }); }
function spacer() { return new Paragraph({ children: [new TextRun({ text: " ", font: FONT, size: 12 })] }); }

// table builder
const BRD = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const BORDERS = { top: BRD, bottom: BRD, left: BRD, right: BRD, insideHorizontal: BRD, insideVertical: BRD };
function cell(text, width, opts = {}) {
  return new TableCell({
    borders: BORDERS,
    width: { size: width, type: WidthType.DXA },
    shading: opts.head ? { fill: "1F3864", type: ShadingType.CLEAR }
           : opts.alt ? { fill: "EEF1F6", type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: "center",
    children: (Array.isArray(text) ? text : [text]).map(t =>
      new Paragraph({
        spacing: { after: 0 },
        children: [new TextRun({ text: t, font: FONT, size: 20,
          bold: !!opts.head, color: opts.head ? "FFFFFF" : "000000" })],
      })
    ),
  });
}
function table(widths, rows) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) =>
      new TableRow({
        children: r.map((c, ci) =>
          cell(c, widths[ci], { head: ri === 0, alt: ri > 0 && ri % 2 === 0 })
        ),
      })
    ),
  });
}

const CW = 9360; // content width US Letter, 1" margins

// ================= CONTENT =================
const children = [];

// ---- Portada ----
children.push(
  new Paragraph({ spacing: { before: 2600, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "INFORME DE AVANCE", font: FONT, size: 56, bold: true, color: "1F3864" })] }),
  new Paragraph({ spacing: { before: 120, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Pipeline de detección y priorización de eventos adversos", font: FONT, size: 30, color: "2E2E2E" })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Modelo GEMSES sobre el dataset MIMIC-IV", font: FONT, size: 30, color: "2E2E2E" })] }),
  new Paragraph({ spacing: { before: 900, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Tesis de Maestría en Inteligencia Artificial — UNI", font: FONT, size: 24 })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Curso MIA 303 — Proyectos de Investigación I", font: FONT, size: 24 })] }),
  new Paragraph({ spacing: { before: 600, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Autor: Carlos Pérez Pérez", font: FONT, size: 24, bold: true })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Fecha: 14 de mayo de 2026", font: FONT, size: 24 })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Sesión de trabajo: instalación de datos, corrección del Anexo 2 y construcción del puente de detección", font: FONT, size: 20, italics: true, color: "595959" })] }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- TOC ----
children.push(
  h1("Contenido"),
  new TableOfContents("Tabla de Contenido", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 1. Resumen ejecutivo ----
children.push(
  h1("1. Resumen ejecutivo"),
  p("En esta sesión de trabajo el proyecto de tesis pasó de tener los datos “sin abrir” a tener el primer cálculo de la Matriz de Priorización GEMSES ejecutándose sobre datos clínicos reales. Se completaron cuatro etapas:"),
  bullet("Etapa 1 — Instalación y verificación del dataset MIMIC-IV v3.1 (10.3 GB, 31 archivos)."),
  bullet("Etapa 2 — Corrección de la base de datos del Anexo 2 de la Directiva de Eventos Adversos de EsSalud, a partir de la fuente oficial."),
  bullet("Etapa 3 — Construcción del puente automático entre las notas clínicas de MIMIC (en inglés) y el Anexo 2 (en español)."),
  bullet("Etapa 4 — Preparación de un set de 20 detecciones para validación por juicio experto."),
  spacer(),
  p("El resultado es un flujo reproducible que detecta eventos adversos en epicrisis, los codifica según el Anexo 2 y aplica la fórmula GEMSES para clasificar cada evento por Nivel de Riesgo (Verde / Amarillo / Rojo) y Nivel de Gestión.", { run: { } }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 2. Estado inicial ----
children.push(
  h1("2. Estado inicial del proyecto"),
  p("Al iniciar la sesión, los datos descargados de PhysioNet estaban comprimidos y la base de datos del modelo GEMSES estaba vacía. El siguiente esquema muestra la transformación de la estructura de carpetas:"),
  ...mono(
`ANTES                                  DESPUES
-----                                  -------
C:\\MIMIC\\                               C:\\MIMIC\\
  +- note\\                                +- mimiciv\\        <- NUEVO, datos listos
      +- mimic-iv-3.1.zip (cerrado)        |   +- hosp\\  (22 archivos)
      +- note\\  (ya extraido)              |   +- icu\\   (9 archivos)
                                           +- note\\note\\  (4 archivos)
                                           +- tesis\\   (repositorio de la tesis)`),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 3. Etapa 1 ----
children.push(
  h1("3. Etapa 1 — Instalación y verificación de MIMIC-IV"),
  p("Se realizó la instalación del dataset principal y se verificó que ningún archivo se hubiera dañado en la descarga."),
  table([520, 4400, 4440], [
    ["Paso", "Acción", "Resultado"],
    ["1.1", "Revisión del contenido descargado en C:\\MIMIC", "2 archivos ZIP + notas ya extraídas"],
    ["1.2", "Descompresión de mimic-iv-3.1.zip (10.3 GB)", "31 archivos: 22 de hosp/ + 9 de icu/"],
    ["1.3", "Renombrado de la carpeta a 'mimiciv'", "Coincide con la ruta esperada por el notebook"],
    ["1.4", "Verificación de integridad con huellas SHA-256", "33 de 33 archivos íntegros"],
    ["1.5", "Ejecución del notebook de exploración inicial", "Sin errores; 11 vistas de datos conectadas"],
  ]),
  spacer(),
  h2("Hallazgo principal de la exploración"),
  p("El corpus contiene 331,793 epicrisis (discharge summaries) de 145,914 pacientes. La longitud media de una epicrisis es de ~10,500 caracteres. Solo el 0.14 % de las notas caben enteras en los 512 tokens de los modelos BioBERT / ClinicalBERT; el 99.86 % requiere segmentación. Este dato justifica técnicamente la estrategia de segmentación de texto en el Capítulo III."),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 4. Etapa 2 ----
children.push(
  h1("4. Etapa 2 — Corrección de la base de datos del Anexo 2"),
  p("Esta fue la etapa más delicada. Se detectaron cinco problemas de integridad de datos y se resolvieron usando la fuente oficial."),
  h2("4.1 Problemas encontrados"),
  table([400, 5560, 3400], [
    ["#", "Problema", "Gravedad"],
    ["1", "El PDF de la Directiva estaba 100 % corrupto (8 MB de bytes vacíos)", "Alta"],
    ["2", "Existían dos versiones contradictorias del “Anexo 2”", "Alta"],
    ["3", "El CSV procesado tenía la codificación rota (acentos dañados)", "Media"],
    ["4", "La naturaleza “Infección asociada a la atención” estaba partida en 5 variantes", "Media"],
    ["5", "El Impacto no cuadraba con la fórmula GEMSES en 33 eventos", "Media"],
  ]),
  spacer(),
  h2("4.2 Acciones realizadas"),
  table([520, 4400, 4440], [
    ["Paso", "Acción", "Resultado"],
    ["2.1", "Carlos entregó la fuente oficial (Directiva ERSP - Anexo 2.xlsx)", "Fuente de verdad confirmada"],
    ["2.2", "Verificación de la fórmula del Impacto", "Pesos 0.40 / 0.20 / 0.15 / 0.20 (Insatisfacción pesa 0.20, no 0.25)"],
    ["2.3", "Regeneración del CSV desde el Excel oficial", "231 eventos, 12 naturalezas, UTF-8 correcto"],
    ["2.4", "Normalización de la naturaleza “Infección”", "De 5 variantes de texto a 1 sola"],
    ["2.5", "Adición de columnas de trazabilidad", "impacto, impacto_formula, verificacion (OK / REVISAR)"],
    ["2.6", "Carga de la tabla en gemses.db", "Antes la base estaba vacía"],
    ["2.7", "Archivado de la versión no oficial", "Movida a processed/_descartado/, no borrada"],
    ["2.8", "Respaldo del CSV anterior incorrecto", "Guardado con sufijo .bak"],
  ]),
  spacer(),
  h2("4.3 Observación sobre los 33 eventos a revisar"),
  p("33 de los 231 eventos tienen un valor de Impacto que no cuadra con la fórmula GEMSES estándar. Se identificó una pista: en los eventos administrativos donde Estancia y Complicación valen 0, el valor oficial cuadra si el Sobrecosto pesara 0.35. Es probable que la directiva use una ponderación distinta para los procesos de soporte. Queda pendiente confirmarlo con el texto de la directiva. Estos eventos quedaron marcados como REVISAR en la columna de verificación."),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 5. Etapa 3 ----
children.push(
  h1("5. Etapa 3 — Construcción del puente MIMIC ↔ Anexo 2"),
  p("El reto central: las notas de MIMIC están en inglés y el Anexo 2 en español; no se pueden cruzar directamente por texto. La solución fue un diccionario de mapeo que traduce cada evento del Anexo 2 a sus patrones en inglés clínico."),
  table([520, 4400, 4440], [
    ["Paso", "Acción", "Resultado"],
    ["3.1", "Creación del diccionario de mapeo (mapeo_anexo2_ingles.json)", "51 eventos → 186 patrones en inglés, con nivel de confianza"],
    ["3.2", "Construcción del notebook fase2_deteccion_anexo2.ipynb", "Conecta MIMIC + gemses.db y aplica la Matriz GEMSES"],
    ["3.3", "Ejecución del notebook de extremo a extremo", "Sin errores"],
  ]),
  spacer(),
  h2("5.1 Resultado de la primera corrida (muestra de 2,000 epicrisis)"),
  bullet("1,358 notas (67.9 %) con al menos un evento detectado."),
  bullet("2,500 detecciones, 35 tipos de evento distintos."),
  bullet("Matriz GEMSES calculada completa: Índice de Frecuencia, Impacto, Riesgo, Índice de Impacto y Nivel de Gestión."),
  spacer(),
  p("Limitación documentada: el 67.9 % está inflado porque la detección por palabras clave aún no maneja la negación (“no pneumonia” se cuenta como positivo). Es justamente lo que debe resolver la fase con BioBERT / ClinicalBERT."),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 6. Etapa 4 ----
children.push(
  h1("6. Etapa 4 — Validación experta"),
  p("Para medir la precisión inicial del método se preparó un set de 20 detecciones para revisión por juicio experto."),
  table([520, 4400, 4440], [
    ["Paso", "Acción", "Resultado"],
    ["4.1", "Selección de 20 detecciones estratificadas", "Mezcla de confianza alta, media y baja"],
    ["4.2", "Extracción del fragmento de texto (±350 caracteres)", "Del campo discharge.text"],
    ["4.3", "Traducción de los 20 fragmentos al castellano", "Columna fragmento_es"],
    ["4.4", "Generación del CSV de validación y su guía", "Listo para llenado por el experto"],
  ]),
  spacer(),
  p("El experto debe responder, por cada detección: (1) si el evento se menciona realmente, (2) si está afirmado o negado, y (3) si ocurrió durante esa hospitalización. Con ello emite un dictamen de Verdadero Positivo o Falso Positivo. La precisión inicial se calcula como VP / (VP + FP)."),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 7. Esquemas del proyecto ----
children.push(
  h1("7. Esquemas del proyecto"),
  h2("7.1 Proceso de instalación de datos (5 pasos)"),
  ...mono(
`[1] ABRIR LA CAJA      Descomprimir mimic-iv-3.1.zip (10.3 GB) -> 31 archivos
        |
[2] ORDENAR            Renombrar carpeta a 'mimiciv'
        |
[3] VERIFICAR          Comparar huellas SHA-256 -> 33/33 integros
        |
[4] CONECTAR           Ejecutar notebook -> 11 vistas de datos
        |
[5] RADIOGRAFIA        Conteo y medicion del corpus`),
  spacer(),
  h2("7.2 Las dos llaves que conectan todo"),
  ...mono(
`subject_id  ->  el PACIENTE          (como el DNI del paciente)
hadm_id     ->  la HOSPITALIZACION   (como el numero de cuenta del internamiento)

Con estas dos llaves se cruza cualquier tabla con cualquier otra.`),
  spacer(),
  h2("7.3 El puente español ↔ inglés"),
  ...mono(
`Anexo 2 (ES)                Patrones (EN)              Nota MIMIC (EN)
------------                -------------              ---------------
202 "Caida de paciente"  -> "fell","found on floor" -> "...patient fell in
601 "Infeccion torrente  -> "bacteremia","CLABSI"       the bathroom..."
     sanguineo"

Cada patron tiene un nivel de confianza: alta / media / baja.`),
  spacer(),
  h2("7.4 Flujo de cálculo de la Matriz de Priorización GEMSES"),
  ...mono(
`PASO A  Indice de Frecuencia    B = A / (suma de a)
PASO B  Impacto                 G = c*0.40 + d*0.20 + e*0.15 + f*0.20
                                (c=Tiempo d=Calidad e=Costos f=Satisfaccion)
PASO C  Riesgo                  H = B * G
PASO D  Indice de Impacto       I = H / (suma de H)
PASO E  Nivel de Gestion        J = I * 100
        Clasificacion por percentiles:
           P25 -> VERDE     -> gestiona el Servicio
           P50 -> AMARILLO  -> gestiona el Departamento
           P75 -> ROJO      -> gestiona el Director`),
  spacer(),
  h2("7.5 Arquitectura del flujo de datos"),
  ...mono(
`  FUENTE 1: MIMIC                      FUENTE 2: Anexo 2
  discharge.text  ----.                231 eventos valorados
  (331,793 notas)     |                por panel experto
                      |                      |
   BioBERT / reglas detectan                 |
   el evento adverso                         |
                      |                      |
                      v                      v
              se codifica (id_evento)  ->  Matriz GEMSES
                                            |
                                            v
                                   Verde / Amarillo / Rojo`),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 8. Estructura de archivos ----
children.push(
  h1("8. Estructura de archivos del proyecto"),
  h2("8.1 Archivos producidos en C:\\BASE DATOS"),
  table([4200, 5160], [
    ["Archivo", "Descripción"],
    ["processed/anexo2_eventos_adversos.csv", "Anexo 2 corregido desde la fuente oficial (reemplazado)"],
    ["processed/anexo2_eventos_adversos.csv.bak_...", "Respaldo del CSV anterior incorrecto"],
    ["processed/_descartado/", "Versión no oficial archivada, con su archivo LEEME"],
    ["db/gemses.db", "Tabla anexo2_eventos_adversos creada (antes vacía)"],
  ]),
  spacer(),
  h2("8.2 Archivos producidos en C:\\MIMIC\\tesis"),
  table([4200, 5160], [
    ["Archivo", "Descripción"],
    ["notebooks/fase2_deteccion_anexo2.ipynb", "Notebook del puente MIMIC ↔ Anexo 2"],
    ["notebooks/mapeo_anexo2_ingles.json", "Diccionario de mapeo español ↔ inglés"],
    ["fase2_detecciones_weak_supervision.csv", "Corpus pre-etiquetado (2,500 filas)"],
    ["fase2_matriz_gemses_muestra.csv", "Matriz GEMSES de la muestra (35 eventos)"],
    ["fase2_validacion_experta_20notas.csv", "Set de 20 detecciones para validación"],
    ["fase2_validacion_experta_GUIA.txt", "Guía de criterios para el experto"],
    ["docs/06_bitacora/Informe_Avance_GEMSES_MIMIC_2026-05-14.docx", "Este informe"],
  ]),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 9. Roadmap ----
children.push(
  h1("9. Roadmap y estado del proyecto"),
  ...mono(
`[OK ] Acceso PhysioNet + DUA firmado
[OK ] Datos descargados
[OK ] Datos instalados, verificados y conectados
[OK ] Anexo 2 corregido desde la directiva oficial
[OK ] Puente MIMIC <-> Anexo 2 construido y funcionando
[>> ] Validacion experta de 20 notas  (EN CURSO - Carlos)
[   ] Notebook BioBERT / ClinicalBERT  (siguiente)
[   ] Fase 1: corpus etiquetado de 5,000 notas
[   ] Fase 3: modelo multimodal (texto + tabular)
[   ] Fase 4: aplicacion de la Matriz GEMSES
[   ] Fase 5: validacion con panel experto
[   ] Fase 6: transferencia al castellano`),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---- 10. Pendientes ----
children.push(
  h1("10. Puntos pendientes y decisiones"),
  bullet("Validación experta: Carlos está llenando el CSV de 20 notas; al terminar se calcula la precisión inicial y se arma el análisis de errores para el Capítulo III."),
  bullet("Los 33 eventos marcados REVISAR: confirmar con el texto de la directiva si los procesos de soporte usan una ponderación distinta de Sobrecosto."),
  bullet("Power BI: si existía un tablero conectado al CSV no oficial archivado, debe reapuntarse al CSV corregido."),
  bullet("El PDF corrupto de la Directiva debe reemplazarse por una copia que abra correctamente, como respaldo de la fuente normativa."),
  spacer(),
  p("Fin del informe.", { run: { italics: true, color: "595959" } }),
);

// ================= DOCUMENT =================
const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: FONT, color: "1F3864" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 25, bold: true, font: FONT, color: "2E5496" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 460, hanging: 280 } } } }] },
    ],
  },
  features: { updateFields: true },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1F3864", space: 2 } },
        children: [new TextRun({ text: "Informe de Avance — Tesis GEMSES-MIMIC — Carlos Pérez Pérez", font: FONT, size: 16, color: "595959" })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Página ", font: FONT, size: 16, color: "595959" }),
                   new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "595959" }),
                   new TextRun({ text: " de ", font: FONT, size: 16, color: "595959" }),
                   new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: "595959" })],
      })] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(String.raw`C:\MIMIC\tesis\docs\06_bitacora\Informe_Avance_GEMSES_MIMIC_2026-05-14.docx`, buf);
  console.log("Documento escrito.");
});
