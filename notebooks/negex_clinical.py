# -*- coding: utf-8 -*-
"""
NegEx clinico para ingles, en Python puro.

Implementacion del algoritmo NegEx (Chapman, Bridewell, Hanbury, Cooper & Buchanan,
"A Simple Algorithm for Identifying Negated Findings and Diseases in Discharge
Summaries", Journal of Biomedical Informatics 2001).

Para cada termino detectado en un texto clinico, determina si esta:
  - AFIRMADO    (presente y confirmado)
  - NEGADO      (negacion explicita: "no", "denies", "without"...)
  - HIPOTETICO  (mencionado como posibilidad: "if", "should", "could"...)
  - HISTORICO   (antecedente del paciente: "history of", "previous", "prior"...)
  - FAMILIAR    (antecedente familiar: "father", "mother", "family history of"...)
  - PROFILAXIS  (mencion de profilaxis/prevencion, no evento real)

El analisis se hace sobre la oracion que contiene el termino, con una ventana
de hasta 6 tokens antes/despues del trigger.

Esta implementacion es la version castellana adaptada a la tesis GEMSES-MIMIC.
Citable en el Capitulo III como: "NegEx (Chapman et al., 2001), implementacion
adaptada en Python".
"""
import re

# ---- Triggers (en ingles clinico) ----
# fuente: Chapman et al. 2001 + extensiones tipicas usadas en medspaCy/negspacy
NEGATION_PRE = [
    "no", "not", "no evidence of", "no signs of", "no sign of", "no history of",
    "denies", "denied", "without", "absence of", "absent", "negative for",
    "ruled out", "rule out", "r/o", "free of", "no findings of", "no symptoms of",
    "no complaints of", "no indication of", "no suggestion of", "no concern for",
    "unremarkable for", "neither", "doubt", "doubtful",
]
NEGATION_POST = [
    "was not", "were not", "is not", "are not", "has not", "have not",
    "is ruled out", "are ruled out", "was ruled out", "were ruled out",
    "is negative", "are negative", "was negative", "were negative",
    "has been ruled out", "have been ruled out",
]

HYPOTHETICAL = [
    "if", "should", "could", "would", "may", "might", "possible",
    "possibly", "potentially", "potential", "suspected", "suspect",
    "concern for", "concerning for", "rule out", "questionable",
    "presumed", "probable", "probably", "likely", "unlikely",
    "in case of", "in case",
]

HISTORICAL = [
    "history of", "hx of", "h/o", "previous", "previously", "prior",
    "past medical history", "past surgical history", "pmh", "psh",
    "status post", "s/p", "remote", "longstanding", "long-standing",
    "chronic", "recurrent",
]

FAMILY = [
    "father", "mother", "brother", "sister", "son", "daughter",
    "grandfather", "grandmother", "uncle", "aunt", "cousin",
    "family history of", "family history", "fh of", "fhx",
    "father's", "mother's",
]

PROPHYLAXIS = [
    "prophylaxis", "prophylactic", "prevention of", "to prevent",
    "preventive", "preventative", "vaccination", "vaccinated against",
]

ADMISSION_REASON = [  # señalan que el evento es el motivo de ingreso
    "presents with", "presenting with", "presented with", "admitted for",
    "admitted with", "chief complaint", "reason for admission",
    "presents to the ed with", "presenting complaint",
]

PSEUDO = [  # frases que parecen negacion pero no lo son (NegEx las excluye)
    "no increase", "no further", "no change", "no other", "no significant change",
    "not certain if", "not certain whether", "not necessarily",
    "gram negative", "gram-negative",
]

# Triggers amplios a nivel de oracion: si aparecen EN CUALQUIER PARTE de la oracion,
# todo el contenido se considera hipotetico
SENTENCE_WIDE_HYPOTHETICAL = [
    "unlikely", "improbable", "doubtful", "ruled out", "was ruled out",
    "were ruled out", "have been ruled out", "has been ruled out",
]

# Patrones que indican que el termino es parte de un nombre de test de laboratorio
# o de un reporte donde el resultado aparece despues
LAB_REPORT_MARKERS = [
    "test", "culture", "toxin", "antigen", "report", "final report",
    "specimen", "assay", "screen", "panel",
]

# Marcador semantico: cuando el termino describe una propiedad del donante,
# no del paciente
DONOR_CONTEXT = ["donor with", "donor had", "donor's", "from donor"]

# Secciones tipicas en discharge summaries de MIMIC. Cuando el termino aparece
# dentro de estas secciones, su contexto cambia.
SECTION_HEADERS = {
    "HISTORICO": [
        "past medical history", "past surgical history", "pmh:", "psh:",
        "medical history:", "surgical history:", "social history:",
        "prior to admission",
    ],
    "FAMILIAR": ["family history:", "family hx:", "fh:"],
    "MOTIVO_INGRESO": [
        "chief complaint:", "cc:", "history of present illness:", "hpi:",
        "reason for admission:", "presenting complaint:", "presents with",
    ],
}


def _tokenize(text):
    """Tokenizacion simple: palabras y signos, conserva offsets."""
    return list(re.finditer(r"\b[\w'-]+\b", text))


def _split_sentences(text):
    """Divide en oraciones por puntuacion fuerte. Devuelve [(ini, fin, texto)]."""
    sents = []
    start = 0
    for m in re.finditer(r"[.!?]\s+|\n\s*\n", text):
        sents.append((start, m.start(), text[start:m.start()]))
        start = m.end()
    if start < len(text):
        sents.append((start, len(text), text[start:]))
    return sents


def _find_trigger(sentence_lower, triggers, pseudo=PSEUDO):
    """Busca triggers en la oracion. Devuelve lista de (inicio, fin, trigger)."""
    hits = []
    for trig in sorted(triggers, key=len, reverse=True):
        for m in re.finditer(r"(?<!\w)" + re.escape(trig) + r"(?!\w)", sentence_lower):
            # excluir pseudo-negaciones
            context = sentence_lower[max(0, m.start()-2):m.end()+15]
            if any(p in context for p in pseudo if p.startswith(trig.split()[0])):
                continue
            hits.append((m.start(), m.end(), trig))
    return hits


def _find_section(text, term_start, lookback=2000):
    """Busca el ultimo header de seccion antes del termino, dentro de lookback chars."""
    pre = text[max(0, term_start - lookback):term_start].lower()
    last_section = None
    last_pos = -1
    for clase, headers in SECTION_HEADERS.items():
        for h in headers:
            pos = pre.rfind(h)
            if pos > last_pos:
                last_pos = pos
                last_section = clase
    return last_section


def _next_sentences(text, after_pos, n=2):
    """Devuelve hasta n oraciones siguientes a after_pos."""
    rest = text[after_pos:]
    sents = _split_sentences(rest)
    return [s[2] for s in sents[:n]]


def classify_mention(text, term_start, term_end, window_tokens=6):
    """
    Clasifica una mencion como AFIRMADO/NEGADO/HIPOTETICO/HISTORICO/
    FAMILIAR/PROFILAXIS/MOTIVO_INGRESO/SEMANTICO_DONANTE.

    Estrategia v0.2:
      1. Heuristicas semanticas (donor context).
      2. Seccion del documento (PMH, FH, HPI, etc.).
      3. NegEx clasico sobre la oracion + ventana de 6 tokens.
      4. Sentence-wide para hipoteticos ("unlikely", "ruled out").
      5. Lab report: si el termino esta cerca de "test/culture/toxin" y la
         siguiente oracion contiene "negative", se considera NEGADO.
    """
    # encontrar la oracion que contiene el termino
    sentence_text = None
    sent_offset = 0
    sent_end = 0
    for s_ini, s_fin, s_txt in _split_sentences(text):
        if s_ini <= term_start < s_fin:
            sentence_text = s_txt
            sent_offset = s_ini
            sent_end = s_fin
            break
    if sentence_text is None:
        return "AFIRMADO", None

    sent_lower = sentence_text.lower()
    text_lower = text.lower()
    t_ini = term_start - sent_offset
    t_fin = term_end - sent_offset

    # ---- 1. SEMANTICO_DONANTE: termino describe propiedad del donante ----
    pre_in_text = text_lower[max(0, term_start - 60):term_start]
    for dm in DONOR_CONTEXT:
        if dm in pre_in_text:
            return "SEMANTICO_DONANTE", dm
    # NOTA: la deteccion por secciones de documento (PMH/HPI/FH) fue probada
    # en v0.2 pero resulto demasiado agresiva en discharge summaries, donde el
    # HPI narra cronologicamente eventos que SI ocurrieron en la admision.
    # Se mantienen solo las heuristicas locales clasicas mas tres mejoras
    # quirurgicas: donante (arriba), lab report y sentence-wide hipotetico.

    # ---- ventana de tokens para reglas locales ----
    tokens = _tokenize(sent_lower)
    term_tok_idx = None
    for i, tk in enumerate(tokens):
        if tk.start() <= t_ini < tk.end() or (tk.start() >= t_ini and tk.start() < t_fin):
            term_tok_idx = i
            break
    if term_tok_idx is not None:
        win_ini = max(0, term_tok_idx - window_tokens)
        win_fin = min(len(tokens), term_tok_idx + window_tokens + 1)
        window_text = sent_lower[tokens[win_ini].start():tokens[win_fin - 1].end()]
    else:
        window_text = sent_lower

    # ---- 3. FAMILIAR local (override por trigger directo en ventana) ----
    if _find_trigger(window_text, FAMILY):
        return "FAMILIAR", _find_trigger(window_text, FAMILY)[0][2]

    # ---- 4. PROFILAXIS ----
    if _find_trigger(window_text, PROPHYLAXIS):
        return "PROFILAXIS", _find_trigger(window_text, PROPHYLAXIS)[0][2]

    # ---- 5. NEGACION clasica ----
    pre_window = sent_lower[:t_ini]
    pre_tokens = _tokenize(pre_window)
    if len(pre_tokens) >= 1:
        pre_text = pre_window[pre_tokens[max(0, len(pre_tokens) - window_tokens)].start():]
        if _find_trigger(pre_text, NEGATION_PRE):
            return "NEGADO", _find_trigger(pre_text, NEGATION_PRE)[0][2]
    post_window = sent_lower[t_fin:]
    post_tokens = _tokenize(post_window)
    if len(post_tokens) >= 1:
        post_text = post_window[:post_tokens[min(len(post_tokens) - 1, window_tokens)].end()]
        if _find_trigger(post_text, NEGATION_POST):
            return "NEGADO", _find_trigger(post_text, NEGATION_POST)[0][2]

    # ---- 6. LAB REPORT: termino en nombre de test, resultado en siguientes oraciones ----
    if any(m in window_text for m in LAB_REPORT_MARKERS):
        for s in _next_sentences(text_lower, sent_end, n=2):
            if re.search(r"\bnegative\b", s):
                return "NEGADO", "[lab report: negative en oracion siguiente]"

    # ---- 7. HIPOTETICO local ----
    if _find_trigger(window_text, HYPOTHETICAL):
        return "HIPOTETICO", _find_trigger(window_text, HYPOTHETICAL)[0][2]

    # ---- 8. HIPOTETICO sentence-wide (unlikely/improbable/doubtful en cualquier parte) ----
    for trig in SENTENCE_WIDE_HYPOTHETICAL:
        if re.search(r"(?<!\w)" + re.escape(trig) + r"(?!\w)", sent_lower):
            return "HIPOTETICO", trig

    # ---- 9. HISTORICO local ----
    if _find_trigger(window_text, HISTORICAL):
        return "HISTORICO", _find_trigger(window_text, HISTORICAL)[0][2]

    # ---- 10. MOTIVO DE INGRESO por trigger local antes del termino ----
    if _find_trigger(pre_window[-200:] if len(pre_window) > 200 else pre_window, ADMISSION_REASON):
        return "MOTIVO_INGRESO", _find_trigger(pre_window, ADMISSION_REASON)[0][2]

    return "AFIRMADO", None


# ---------- prueba rapida cuando se ejecuta como script ----------
if __name__ == "__main__":
    casos = [
        ("No pneumothorax was seen on the chest x-ray.", "pneumothorax"),
        ("Patient had a fall yesterday.", "fall"),
        ("Father died of peritonitis from gastric perforation.", "peritonitis"),
        ("Endocarditis prophylaxis is not recommended.", "endocarditis"),
        ("History of pneumonia treated 2 years ago.", "pneumonia"),
        ("Patient presents with acute hepatitis.", "hepatitis"),
        ("Possible drug interaction was considered but unlikely.", "drug interaction"),
        ("Patient developed bacteremia on day 5 of admission.", "bacteremia"),
    ]
    for texto, termino in casos:
        ini = texto.lower().find(termino.lower())
        fin = ini + len(termino)
        clase, trig = classify_mention(texto, ini, fin)
        print(f"  [{clase:15}] trig='{trig}' :: {texto}")
