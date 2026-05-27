const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, BorderStyle, PageNumber, Header, Footer,
  LevelFormat, NumberFormat, Tab, TabStopType, TabStopPosition,
  UnderlineType
} = require('C:/Users/infor/AppData/Roaming/npm/node_modules/docx');
const fs = require('fs');

// ─── Helpers ────────────────────────────────────────────────────────────────

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 180 },
    children: [new TextRun({ text, bold: true, size: 28, font: 'Times New Roman' })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
    children: [new TextRun({ text, bold: true, size: 26, font: 'Times New Roman' })]
  });
}

function body(text, { justify = true, spacingBefore = 0, spacingAfter = 200 } = {}) {
  return new Paragraph({
    alignment: justify ? AlignmentType.JUSTIFIED : AlignmentType.LEFT,
    spacing: { before: spacingBefore, after: spacingAfter, line: 360 }, // 1.5 line spacing
    indent: { firstLine: 720 },
    children: [new TextRun({ text, size: 24, font: 'Times New Roman' })]
  });
}

function bodyNI(text, { spacingAfter = 200 } = {}) {
  // No indent
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 0, after: spacingAfter, line: 360 },
    children: [new TextRun({ text, size: 24, font: 'Times New Roman' })]
  });
}

function bullet(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 0, after: 120, line: 360 },
    indent: { left: 720, hanging: 360 },
    numbering: { reference: 'bullets', level: 0 },
    children: [new TextRun({ text, size: 24, font: 'Times New Roman' })]
  });
}

function numbered(text, level = 0) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 0, after: 120, line: 360 },
    indent: { left: 720, hanging: 360 },
    numbering: { reference: 'numbered', level },
    children: [new TextRun({ text, size: 24, font: 'Times New Roman' })]
  });
}

function spacer() {
  return new Paragraph({ spacing: { before: 0, after: 120 }, children: [] });
}

function centeredBold(text, size = 28) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 160 },
    children: [new TextRun({ text, bold: true, size, font: 'Times New Roman' })]
  });
}

function centered(text, size = 24) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [new TextRun({ text, size, font: 'Times New Roman' })]
  });
}

// ─── Document ───────────────────────────────────────────────────────────────

const doc = new Document({
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: '•',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: 'numbered',
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: '%1.',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: 'Times New Roman', size: 24 } }
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: 'Times New Roman', color: '000000' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 }
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Times New Roman', color: '000000' },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 }
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, italics: true, font: 'Times New Roman', color: '000000' },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 2268, right: 1701, bottom: 2268, left: 2268 } // ~2.5cm left, 1.5cm right
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '2E4057', space: 1 } },
          children: [
            new TextRun({ text: 'MIA-303 – Trabajo de Investigación I  |  Carlos Pérez Pérez', size: 18, font: 'Times New Roman', color: '555555' })
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 1 } },
          children: [
            new TextRun({ text: 'Página ', size: 18, font: 'Times New Roman', color: '555555' }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: 'Times New Roman', color: '555555' }),
            new TextRun({ text: ' de ', size: 18, font: 'Times New Roman', color: '555555' }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: 'Times New Roman', color: '555555' })
          ]
        })]
      })
    },
    children: [

      // ── PORTADA ─────────────────────────────────────────────────────────
      centeredBold('UNIVERSIDAD NACIONAL DE INGENIERÍA', 26),
      centeredBold('FACULTAD DE INGENIERÍA INDUSTRIAL Y DE SISTEMAS', 24),
      centeredBold('UNIDAD DE POSGRADO — MAESTRÍA EN INTELIGENCIA ARTIFICIAL', 24),
      spacer(),
      centeredBold('PROYECTO DE INVESTIGACIÓN', 28),
      spacer(),
      centeredBold(
        '«DETECCIÓN AUTOMATIZADA Y PRIORIZACIÓN DE EVENTOS ADVERSOS EN NOTAS CLÍNICAS ' +
        'MEDIANTE UN FLUJO DE PROCESAMIENTO (PIPELINE) DE NLP Y APRENDIZAJE AUTOMÁTICO — ' +
        'APLICACIÓN DE LA MATRIZ DE PRIORIZACIÓN DEL MODELO GEMSES SOBRE MIMIC-IV»',
        24
      ),
      spacer(),
      centered('TRABAJO PARCIAL — CAPÍTULOS I Y II', 24),
      spacer(),
      centered('Elaborado por:', 24),
      centeredBold('Carlos Pérez Pérez', 24),
      spacer(),
      centered('Curso: MIA-303 — Proyectos de Investigación I', 24),
      centered('Docente: Mg. María Tejada Begazo', 24),
      spacer(),
      centered('Lima — Perú, 2026', 24),

      // ── PAGE BREAK ───────────────────────────────────────────────────────
      new Paragraph({ pageBreakBefore: true, children: [] }),

      // ════════════════════════════════════════════════════════════════════
      // CAPÍTULO I
      // ════════════════════════════════════════════════════════════════════
      centeredBold('CAPÍTULO I: PLANTEAMIENTO DEL PROBLEMA Y JUSTIFICACIÓN', 28),
      spacer(),

      // ── 1.1 Planteamiento del Problema ─────────────────────────────────
      heading2('1.1 Planteamiento del Problema'),

      body(
        'La seguridad del paciente constituye uno de los principales retos de los sistemas de salud ' +
        'contemporáneos. Según la Organización Mundial de la Salud (OMS, 2019), los eventos adversos ' +
        'derivados de la atención sanitaria figuran entre las diez principales causas de muerte y ' +
        'discapacidad en el mundo, generando además costos sustanciales para los sistemas asistenciales. ' +
        'En el contexto peruano, EsSalud aprobó en 2021 la Directiva GG-ESSALUD «Registro, Notificación ' +
        'y Gestión de los Eventos Relacionados con la Seguridad del Paciente (ERSP)», la cual incorpora ' +
        'explícitamente la Matriz de Priorización del Modelo de Gestión Moderna de los Servicios de Salud ' +
        '(GEMSES) como herramienta normativa para clasificar el nivel de riesgo y de gestión de los eventos.'
      ),

      body(
        'Sin embargo, el proceso de identificación y priorización depende todavía del registro voluntario ' +
        'de los profesionales de la salud y del análisis manual de las descripciones libres consignadas en ' +
        'las notas clínicas. Esta dependencia genera tres obstáculos persistentes: (i) la subnotificación ' +
        'voluntaria, asociada al temor de repercusiones laborales; (ii) la dependencia de descripciones en ' +
        'lenguaje natural que dificultan su codificación, agregación y análisis sistemático; y (iii) la ' +
        'falta de mecanismos automatizados que prioricen los eventos de mayor riesgo para escalarlos al ' +
        'nivel de gestión adecuado en tiempo oportuno.'
      ),

      body(
        'En el caso específico de EsSalud, la Directiva GG-ESSALUD-2021 establece un flujo formal de ' +
        'Registro → Notificación → Validación → Codificación → Priorización → Mitigación → Análisis de ' +
        'Causa Raíz → Plan de Acción. Aunque la directiva normaliza la Matriz de Priorización GEMSES como ' +
        'instrumento oficial, su aplicación efectiva requiere que personal de la Oficina de Gestión de la ' +
        'Calidad y Humanización procese manualmente cada notificación, lo que constituye un cuello de botella ' +
        'estructural que hace el proceso lento, costoso y vulnerable a la heterogeneidad en la interpretación.'
      ),

      body(
        'La presente investigación propone aprovechar los avances recientes en procesamiento de lenguaje ' +
        'natural (NLP) y aprendizaje automático para automatizar la detección de los 51 eventos adversos ' +
        'del Anexo 02 GEMSES en notas clínicas no estructuradas, y la posterior aplicación de la Matriz de ' +
        'Priorización. Dada la imposibilidad operativa de acceder a registros institucionales de historias ' +
        'clínicas electrónicas en el contexto peruano, el estudio se desarrollará sobre el dataset abierto ' +
        'MIMIC-IV (Medical Information Mart for Intensive Care, versión IV), reconocido internacionalmente ' +
        'como referencia en investigación de inteligencia artificial aplicada a la salud.'
      ),

      // ── 1.2 Formulación del Problema ───────────────────────────────────
      heading2('1.2 Formulación del Problema'),

      body(
        'La gestión de eventos adversos en los servicios de salud presenta brechas críticas en la ' +
        'detección oportuna, la codificación consistente y la priorización basada en evidencia. Los ' +
        'modelos manuales dependen del criterio subjetivo del profesional, generan subnotificación ' +
        'sistemática y no escalan frente al volumen de notas clínicas generadas en hospitales de tercer ' +
        'nivel. Existe, por tanto, una oportunidad de investigación claramente delimitada: desarrollar ' +
        'un pipeline automatizado que procese texto clínico libre y produzca una priorización reproducible ' +
        'y trazable.'
      ),

      body('En consecuencia, el problema central se formula mediante la siguiente pregunta de investigación:'),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 160, after: 160, line: 360 },
        indent: { left: 720, right: 720 },
        children: [
          new TextRun({
            text: '¿En qué medida un pipeline integrado de procesamiento de lenguaje natural y aprendizaje ' +
              'automático supervisado, aplicado sobre notas clínicas no estructuradas del dataset MIMIC-IV, ' +
              'permite detectar eventos adversos y aplicar la Matriz de Priorización del Modelo GEMSES con ' +
              'una concordancia significativamente mayor a la clasificación manual experta tradicional?',
            size: 24, font: 'Times New Roman', italics: true
          })
        ]
      }),

      // ── 1.3 Justificación ──────────────────────────────────────────────
      heading2('1.3 Justificación'),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 0, after: 200, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: 'La presente investigación se justifica desde cuatro dimensiones complementarias:',
            size: 24, font: 'Times New Roman'
          })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: '1.3.1 Justificación Teórica', bold: true, italics: true, size: 24, font: 'Times New Roman' })]
      }),

      body(
        'El campo de la detección automática de eventos adversos en texto clínico ha avanzado ' +
        'sustancialmente en los últimos años, con trabajos basados en sistemas de supervisión débil ' +
        '(Ratner et al., 2017), modelos de transformers biométricos (Lee et al., 2020; Alsentzer ' +
        'et al., 2019) y técnicas de negación clínica como NegEx (Chapman et al., 2001). Sin embargo, ' +
        'ningún trabajo previo ha articulado estos enfoques con la Matriz de Priorización del Modelo ' +
        'GEMSES ni con la taxonomía de 51 eventos del Anexo 02 de la Directiva GG-ESSALUD-2021. Esta ' +
        'investigación cierra esa brecha teórica, aportando un marco de operacionalización que vincula ' +
        'las dimensiones de Tiempo, Calidad, Costos y Satisfacción del Modelo GEMSES con variables ' +
        'proxy derivables de datos clínicos estructurados y no estructurados.'
      ),

      body(
        'Adicionalmente, el estudio contribuye al debate metodológico sobre la transferibilidad de ' +
        'modelos de NLP entrenados en inglés clínico hacia sistemas sanitarios de habla hispana, ' +
        'problema de creciente relevancia en la literatura de informática biomédica internacional.'
      ),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: '1.3.2 Justificación Práctica', bold: true, italics: true, size: 24, font: 'Times New Roman' })]
      }),

      body(
        'Desde una perspectiva práctica, el sistema propuesto responde a una necesidad institucional ' +
        'concreta: el cuello de botella operativo que genera el procesamiento manual de notificaciones ' +
        'de eventos adversos en EsSalud. El pipeline automatizado permitiría procesar el volumen ' +
        'completo de notas clínicas de alta (331,793 notas en MIMIC-IV; equivalente a decenas de miles ' +
        'en EsSalud) sin incremento proporcional de recursos humanos especializados, reduciendo el ' +
        'tiempo entre la ocurrencia del evento y su priorización para la gestión correctiva.'
      ),

      body(
        'El modelo validado sobre MIMIC-IV generará un protocolo de implementación documentado y ' +
        'replicable, que podrá ser adaptado por la Oficina de Gestión de la Calidad y Humanización ' +
        'de EsSalud —o cualquier institución que opere bajo estándares GEMSES— cuando se habilite el ' +
        'acceso a datos clínicos institucionales para investigación. El impacto práctico esperado incluye: ' +
        'reducción de la subnotificación, mayor consistencia en la codificación, y escalamiento de la ' +
        'capacidad de vigilancia de la seguridad del paciente.'
      ),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: '1.3.3 Justificación Metodológica', bold: true, italics: true, size: 24, font: 'Times New Roman' })]
      }),

      body(
        'El uso de MIMIC-IV como corpus de validación garantiza la reproducibilidad del estudio: ' +
        'es un dataset de acceso controlado pero abierto (PhysioNet credentialing), con 145,914 ' +
        'pacientes únicos, en formato estándar internacional, y ampliamente utilizado como benchmark ' +
        'en investigación de NLP clínico. La elección de este dataset —en lugar de datos institucionales ' +
        'peruanos no accesibles— no es una limitación sino una decisión metodológica deliberada que ' +
        'garantiza la trazabilidad, la posibilidad de revisión por pares y la comparabilidad con el ' +
        'estado del arte internacional.'
      ),

      body(
        'El diseño del pipeline combina supervisión débil para etiquetado a escala, detección de ' +
        'negación con NegEx, mapeo a 149 códigos ICD-10, y comparación de múltiples clasificadores ' +
        '(TF-IDF + regresión logística, LinearSVC, modelos basados en transformers). La validación ' +
        'mediante panel experto (n = 70 notas) con métricas de concordancia (kappa de Cohen) ' +
        'proporciona evidencia estadística rigurosa sobre la capacidad del sistema, con un IC95% ' +
        'Wilson calculado correctamente para muestras pequeñas.'
      ),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: '1.3.4 Justificación Social', bold: true, italics: true, size: 24, font: 'Times New Roman' })]
      }),

      body(
        'La OMS estima que en países de ingresos medios y bajos, la carga de eventos adversos ' +
        'evitables equivale a 134 millones de episodios anuales con 2.6 millones de muertes asociadas ' +
        '(OMS, 2019). Perú, como país de ingreso medio-alto con un sistema de seguridad social en ' +
        'expansión, enfrenta este problema de manera aguda: la red asistencial de EsSalud atiende a ' +
        'más de 13 millones de asegurados con capacidad limitada de vigilancia activa de seguridad.'
      ),

      body(
        'Un sistema automatizado de detección y priorización contribuye directamente a la protección ' +
        'de pacientes vulnerables, a la rendición de cuentas institucional y al aprendizaje ' +
        'organizacional. La generación de alertas tempranas sobre eventos de nivel Rojo (alta ' +
        'prioridad GEMSES) permitiría activar protocolos de mitigación antes de que el daño escale, ' +
        'con un impacto social concreto y medible en términos de morbimortalidad prevenible.'
      ),

      // ── PAGE BREAK ───────────────────────────────────────────────────────
      new Paragraph({ pageBreakBefore: true, children: [] }),

      // ════════════════════════════════════════════════════════════════════
      // CAPÍTULO II
      // ════════════════════════════════════════════════════════════════════
      centeredBold('CAPÍTULO II: OBJETIVOS', 28),
      spacer(),

      // ── 2.1 Objetivo General ───────────────────────────────────────────
      heading2('2.1 Objetivo General'),

      body(
        'Diseñar, implementar y validar un sistema basado en procesamiento de lenguaje natural y ' +
        'aprendizaje automático que detecte eventos adversos a partir de notas clínicas no estructuradas ' +
        'del dataset MIMIC-IV y los priorice automáticamente aplicando la Matriz de Priorización del ' +
        'Modelo GEMSES, con miras a su transferencia metodológica a sistemas sanitarios de habla hispana ' +
        'y, en particular, a la red asistencial de EsSalud.'
      ),

      // ── 2.2 Objetivos Específicos ──────────────────────────────────────
      heading2('2.2 Objetivos Específicos'),

      body('Para alcanzar el objetivo general se plantean los siguientes objetivos específicos:', { spacingAfter: 120 }),

      numbered(
        'OE1 — Construir un corpus etiquetado de eventos adversos a partir de notas clínicas no ' +
        'estructuradas de MIMIC-IV, utilizando como marco de etiquetado la taxonomía de los 51 ' +
        'eventos del Anexo 02 de la Directiva GG-ESSALUD-2021, mapeados a 149 códigos ICD-10.'
      ),

      numbered(
        'OE2 — Implementar y comparar al menos tres modelos de procesamiento de lenguaje natural para ' +
        'la detección y clasificación de eventos adversos en texto libre, incluyendo modelos basados ' +
        'en transformers biomédicos (BioBERT, ClinicalBERT) y un modelo base clásico de referencia ' +
        '(TF-IDF + regresión logística).'
      ),

      numbered(
        'OE3 — Operacionalizar las cuatro dimensiones de la Matriz de Priorización del Modelo GEMSES ' +
        '(Tiempo, Calidad, Costos, Satisfacción) mediante variables proxy derivables del dataset ' +
        'MIMIC-IV, justificando teóricamente cada equivalencia de medida.'
      ),

      numbered(
        'OE4 — Comparar el cálculo automatizado del Nivel de Riesgo y Nivel de Gestión generado por ' +
        'el pipeline frente a la clasificación manual de un panel experto sobre una muestra ' +
        'estratificada (n = 70 notas), mediante métricas estándar: kappa de Cohen, sensibilidad, ' +
        'especificidad, F1 ponderado y área bajo la curva ROC (AUC-ROC).'
      ),

      numbered(
        'OE5 — Documentar el método de transferencia del pipeline a sistemas sanitarios de habla ' +
        'hispana, identificando los retos lingüísticos, taxonómicos y de localización que deberán ' +
        'abordarse para su implementación en EsSalud u otras instituciones equivalentes.'
      ),

      spacer(),
      spacer(),

      // ── Coherencia: nota final de articulación ──────────────────────────
      heading2('2.3 Articulación entre Problema, Justificación y Objetivos'),

      bodyNI(
        'Los objetivos específicos OE1 y OE2 responden directamente al obstáculo de la dependencia ' +
        'del análisis manual (problema), mediante la construcción de corpus etiquetado y la ' +
        'comparación de modelos (metodología). OE3 operacionaliza el instrumento GEMSES, que es el ' +
        'núcleo normativo del contexto institucional descrito en la justificación práctica. OE4 ' +
        'provee la evidencia empírica de validez que sustenta la justificación metodológica, ' +
        'asegurando rigor estadístico. OE5 conecta el resultado de laboratorio con el impacto social ' +
        'y práctico identificado en la justificación, cerrando el ciclo de investigación aplicada.'
      ),

      bodyNI(
        'Esta articulación garantiza la coherencia global del proyecto: el problema plantea una ' +
        'necesidad, la justificación la fundamenta desde cuatro dimensiones, y los objetivos definen ' +
        'los pasos concretos —verificables y medibles— para responder a la pregunta de investigación.'
      ),

    ]
  }]
});

// ─── Export ─────────────────────────────────────────────────────────────────
Packer.toBuffer(doc).then(buffer => {
  const outPath = 'C:\\MIMIC\\tesis\\01_plan_de_tesis\\Trabajo_Parcial_Cap1_Cap2_CarlosPerez.docx';
  fs.writeFileSync(outPath, buffer);
  console.log('OK: ' + outPath);
}).catch(err => { console.error(err); process.exit(1); });
