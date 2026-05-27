"""
Tier D — Auditoría de COMPLETITUD del Registro Clínico Electrónico (EHR).

Implementa los 23 eventos de "Historia Clínica" (HC) del Anexo 02 GEMSES
que se auditan por AUSENCIA o INCOMPLETITUD de campos/notas en MIMIC-IV.

Cada función devuelve un DataFrame:
    hadm_id, id_evento, evento, tier, valor_calculado, detectado

`detectado = True` significa que la información ESTÁ AUSENTE (es decir, el
evento adverso de completitud está presente). Es lo opuesto a Tier C: aquí
"detectado" = "no se registró".

Tabla de eventos Tier D auditables en MIMIC-IV:
    503   Examenes auxiliares no corresponden al paciente
    504   No constan resultados de examenes auxiliares
    505   No cuenta con consentimiento informado
    506   No cuenta con reporte quirurgico
    507   No se registra el examen fisico completo
    508   No se registra el nombre del paciente (siempre presente — control)
    509   No se registra el Plan de Trabajo (discharge plan)
    5010  No se registra el tratamiento
    5011  No se registra evento adverso (meta — saltado)
    5012  No se registra fecha y hora de atencion
    5014  No se registra fecha y hora del alta
    5015  No se registra filiacion completa
    5016  No se registra la enfermedad actual (HPI)
    5017  No se registra la evolucion diaria SOAP
    5018  No se registran indicaciones al alta
    5019  No se registran las interconsultas
    5020  No se registran los antecedentes (PMH)
    5021  No se registran los diagnosticos
    5023  Historia clinica incompleta (agregado)
    7026  Falta de prescripcion (medicacion ausente)
    9016  Pruebas pretransfusionales ausentes
    2014  Brazalete de identificación (auditoría)
    2020  Datos erroneos identificacion

NOTAS:
- MIMIC-IV separa `mimiciv_hosp.*` (estructurado) y `mimiciv_note.*` (texto).
- Algunos eventos requieren la tabla `mimiciv_note.discharge` (discharge summaries).
- Otros se auditan sobre campos estructurados (admissions, prescriptions, etc.).

Autor: Pipeline tesis MIA-303 (GEMSES × MIMIC-IV)
"""

from __future__ import annotations

import logging
from typing import Optional, List

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SCHEMA_HOSP = "mimiciv_hosp"
SCHEMA_NOTE = "mimiciv_note"

# Secciones típicas en discharge summaries de MIMIC-IV (usadas como anclas)
# para auditoría textual.
SECCIONES_HPI = ["history of present illness", "hpi:"]
SECCIONES_PMH = ["past medical history", "pmh:"]
SECCIONES_PHYS = ["physical exam", "physical examination", "exam:"]
SECCIONES_PLAN = ["discharge plan", "plan:", "assessment and plan"]
SECCIONES_DX = ["discharge diagnosis", "discharge diagnoses", "primary diagnosis"]
SECCIONES_INST = ["discharge instructions", "instructions:"]
SECCIONES_TX = ["discharge medications", "medications on discharge"]
SECCIONES_OR = ["operative report", "operation:", "procedure:"]
SECCIONES_CONSENT = ["informed consent", "consent obtained", "consent was obtained"]
SECCIONES_CONSULT = ["consult note", "consultation note", "consult was called"]
SECCIONES_SOAP = ["progress note", "subjective:", "soap"]


def _filter_hadm(query: str, hadm_ids: Optional[List[int]]) -> str:
    if not hadm_ids:
        return query
    ids_str = ",".join(str(int(h)) for h in hadm_ids)
    if "WHERE" in query.upper():
        return query + f" AND hadm_id IN ({ids_str})"
    return query + f" WHERE hadm_id IN ({ids_str})"


def _resultado_vacio() -> pd.DataFrame:
    return pd.DataFrame(columns=["hadm_id", "id_evento", "evento", "tier", "valor_calculado", "detectado"])


def _ausencia_seccion_en_discharge(conn, secciones: List[str],
                                   id_evento: int, evento: str,
                                   hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Helper: marca como detectado los hadm cuya discharge summary NO contiene
    ninguna de las secciones dadas (case-insensitive)."""
    cond = " OR ".join([f"LOWER(text) LIKE '%{s}%'" for s in secciones])

    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH disc AS (
            SELECT hadm_id,
                   MAX(CASE WHEN ({cond}) THEN 1 ELSE 0 END) AS tiene_seccion,
                   MAX(LENGTH(text)) AS max_len
            FROM {SCHEMA_NOTE}.discharge
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            {id_evento} AS id_evento,
            '{evento}' AS evento,
            'D' AS tier,
            CONCAT('tiene_seccion=', COALESCE(d.tiene_seccion, 0)) AS valor_calculado,
            (COALESCE(d.tiene_seccion, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN disc d USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[{id_evento} {evento}] fallo (probablemente falta mimiciv_note.discharge): {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 503 — Examenes auxiliares no corresponden al paciente
# ────────────────────────────────────────────────────────────────────
def auditar_labs_paciente_incorrecto(conn, hadm_ids=None) -> pd.DataFrame:
    """503: cruce de subject_id en labevents vs admissions.

    En MIMIC-IV los labevents llevan subject_id+hadm_id. Detectamos
    inconsistencias: labevents.subject_id ≠ admissions.subject_id para el mismo hadm.
    """
    q = f"""
        WITH inconsist AS (
            SELECT l.hadm_id, COUNT(*) AS n_mismatch
            FROM {SCHEMA_HOSP}.labevents l
            JOIN {SCHEMA_HOSP}.admissions a USING (hadm_id)
            WHERE l.subject_id IS NOT NULL
              AND l.subject_id != a.subject_id
            GROUP BY l.hadm_id
        )
        SELECT
            hadm_id,
            503 AS id_evento,
            'Examenes auxiliares no corresponden al paciente' AS evento,
            'D' AS tier,
            CONCAT('n_mismatch=', n_mismatch) AS valor_calculado,
            (n_mismatch > 0)::BOOLEAN AS detectado
        FROM inconsist
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[503] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 504 — No constan resultados de examenes auxiliares
# ────────────────────────────────────────────────────────────────────
def auditar_labs_vacios(conn, hadm_ids=None) -> pd.DataFrame:
    """504: hadm sin filas en labevents (cero resultados de laboratorio)."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH counts AS (
            SELECT hadm_id, COUNT(*) AS n_labs
            FROM {SCHEMA_HOSP}.labevents
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            504 AS id_evento,
            'No constan resultados de examenes auxiliares' AS evento,
            'D' AS tier,
            CONCAT('n_labs=', COALESCE(c.n_labs, 0)) AS valor_calculado,
            (COALESCE(c.n_labs, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN counts c USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[504] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 505 — No cuenta con consentimiento informado
# ────────────────────────────────────────────────────────────────────
def auditar_consentimiento(conn, hadm_ids=None) -> pd.DataFrame:
    """505: hadm con procedures_icd pero sin mención de consentimiento en discharge."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    cond_consent = " OR ".join([f"LOWER(text) LIKE '%{s}%'" for s in SECCIONES_CONSENT])
    q = f"""
        WITH proc_hadms AS (
            SELECT DISTINCT hadm_id
            FROM {SCHEMA_HOSP}.procedures_icd
        ),
        consent_hadms AS (
            SELECT hadm_id,
                   MAX(CASE WHEN ({cond_consent}) THEN 1 ELSE 0 END) AS tiene
            FROM {SCHEMA_NOTE}.discharge
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            505 AS id_evento,
            'No cuenta con consentimiento informado' AS evento,
            'D' AS tier,
            CONCAT('tiene_consent=', COALESCE(c.tiene, 0)) AS valor_calculado,
            (p.hadm_id IS NOT NULL AND COALESCE(c.tiene, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN proc_hadms p USING (hadm_id)
        LEFT JOIN consent_hadms c USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[505 Consentimiento] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 506 — No cuenta con reporte quirúrgico
# ────────────────────────────────────────────────────────────────────
def auditar_reporte_quirurgico(conn, hadm_ids=None) -> pd.DataFrame:
    """506: hadm con procedimiento quirúrgico pero sin sección operatoria en notas."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    cond_or = " OR ".join([f"LOWER(text) LIKE '%{s}%'" for s in SECCIONES_OR])
    q = f"""
        WITH surg_hadms AS (
            -- procedures_icd con códigos quirúrgicos (ICD-10-PCS empieza por 0)
            SELECT DISTINCT hadm_id
            FROM {SCHEMA_HOSP}.procedures_icd
            WHERE icd_version = 10 AND icd_code LIKE '0%'
        ),
        or_notes AS (
            SELECT hadm_id,
                   MAX(CASE WHEN ({cond_or}) THEN 1 ELSE 0 END) AS tiene
            FROM {SCHEMA_NOTE}.discharge
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            506 AS id_evento,
            'No cuenta con reporte quirurgico' AS evento,
            'D' AS tier,
            CONCAT('tiene_OR_note=', COALESCE(o.tiene, 0)) AS valor_calculado,
            (s.hadm_id IS NOT NULL AND COALESCE(o.tiene, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN surg_hadms s USING (hadm_id)
        LEFT JOIN or_notes o USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[506] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 507 — No se registra el examen fisico
# ────────────────────────────────────────────────────────────────────
def auditar_examen_fisico(conn, hadm_ids=None) -> pd.DataFrame:
    return _ausencia_seccion_en_discharge(conn, SECCIONES_PHYS, 507,
                                          "No se registra el examen fisico", hadm_ids)


# ────────────────────────────────────────────────────────────────────
# 508 — No se registra el nombre del paciente (CONTROL)
# ────────────────────────────────────────────────────────────────────
def auditar_nombre_paciente(conn, hadm_ids=None) -> pd.DataFrame:
    """508: subject_id es siempre obligatorio en MIMIC-IV. Este detector funciona
    como CONTROL/sanity check: debe devolver vacío.
    """
    q = f"""
        SELECT
            hadm_id,
            508 AS id_evento,
            'No se registra el nombre del paciente' AS evento,
            'D' AS tier,
            'subject_id_null' AS valor_calculado,
            (subject_id IS NULL)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[508] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 509 — No se registra el Plan de Trabajo (discharge plan)
# ────────────────────────────────────────────────────────────────────
def auditar_plan_trabajo(conn, hadm_ids=None) -> pd.DataFrame:
    return _ausencia_seccion_en_discharge(conn, SECCIONES_PLAN, 509,
                                          "No se registra el Plan de Trabajo", hadm_ids)


# ────────────────────────────────────────────────────────────────────
# 5010 — No se registra el tratamiento (prescriptions)
# ────────────────────────────────────────────────────────────────────
def auditar_tratamiento(conn, hadm_ids=None) -> pd.DataFrame:
    """5010: hadm sin filas en prescriptions."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH rx AS (
            SELECT hadm_id, COUNT(*) AS n
            FROM {SCHEMA_HOSP}.prescriptions
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            5010 AS id_evento,
            'No se registra el tratamiento' AS evento,
            'D' AS tier,
            CONCAT('n_rx=', COALESCE(rx.n, 0)) AS valor_calculado,
            (COALESCE(rx.n, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN rx USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[5010] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5012 — No se registra fecha y hora de atencion (admittime)
# ────────────────────────────────────────────────────────────────────
def auditar_admittime(conn, hadm_ids=None) -> pd.DataFrame:
    q = f"""
        SELECT
            hadm_id,
            5012 AS id_evento,
            'No se registra fecha y hora de atencion' AS evento,
            'D' AS tier,
            'admittime_null' AS valor_calculado,
            (admittime IS NULL)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[5012] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5014 — No se registra fecha y hora del alta (dischtime)
# ────────────────────────────────────────────────────────────────────
def auditar_dischtime(conn, hadm_ids=None) -> pd.DataFrame:
    q = f"""
        SELECT
            hadm_id,
            5014 AS id_evento,
            'No se registra fecha y hora del alta' AS evento,
            'D' AS tier,
            'dischtime_null' AS valor_calculado,
            (dischtime IS NULL)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[5014] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5015 — No se registra filiacion completa
# ────────────────────────────────────────────────────────────────────
def auditar_filiacion(conn, hadm_ids=None) -> pd.DataFrame:
    """5015: campos demográficos críticos ausentes (gender, anchor_age en patients)."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        SELECT
            a.hadm_id,
            5015 AS id_evento,
            'No se registra filiacion completa' AS evento,
            'D' AS tier,
            CONCAT('gender_null=', (p.gender IS NULL),
                   ' age_null=', (p.anchor_age IS NULL),
                   ' race_null=', (a.race IS NULL OR a.race IN ('UNKNOWN', 'OTHER'))) AS valor_calculado,
            (p.gender IS NULL OR p.anchor_age IS NULL
             OR a.race IS NULL OR a.race = 'UNKNOWN')::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN {SCHEMA_HOSP}.patients p USING (subject_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[5015] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5016 — No se registra HPI
# ────────────────────────────────────────────────────────────────────
def auditar_hpi(conn, hadm_ids=None) -> pd.DataFrame:
    return _ausencia_seccion_en_discharge(conn, SECCIONES_HPI, 5016,
                                          "No se registra la enfermedad actual (HPI)", hadm_ids)


# ────────────────────────────────────────────────────────────────────
# 5017 — No se registra la evolucion diaria SOAP
# ────────────────────────────────────────────────────────────────────
def auditar_progress_notes(conn, hadm_ids=None) -> pd.DataFrame:
    """5017: hadm con LOS >= 2 días pero sin progress notes."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    # En MIMIC-IV las progress notes están en mimiciv_note.radiology o discharge.
    # Aquí usamos un proxy: discharge summary debería al menos referenciar progress.
    cond = " OR ".join([f"LOWER(text) LIKE '%{s}%'" for s in SECCIONES_SOAP])
    q = f"""
        WITH disc AS (
            SELECT hadm_id,
                   MAX(CASE WHEN ({cond}) THEN 1 ELSE 0 END) AS tiene
            FROM {SCHEMA_NOTE}.discharge
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            5017 AS id_evento,
            'No se registra la evolucion diaria SOAP' AS evento,
            'D' AS tier,
            CONCAT('LOS=', DATE_DIFF('day', a.admittime, a.dischtime),
                   ' tiene_soap=', COALESCE(d.tiene, 0)) AS valor_calculado,
            (DATE_DIFF('day', a.admittime, a.dischtime) >= 2
             AND COALESCE(d.tiene, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN disc d USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[5017] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5018 — No se registran indicaciones al alta
# ────────────────────────────────────────────────────────────────────
def auditar_indicaciones_alta(conn, hadm_ids=None) -> pd.DataFrame:
    return _ausencia_seccion_en_discharge(conn, SECCIONES_INST, 5018,
                                          "No se registran indicaciones al alta", hadm_ids)


# ────────────────────────────────────────────────────────────────────
# 5019 — No se registran las interconsultas
# ────────────────────────────────────────────────────────────────────
def auditar_interconsultas(conn, hadm_ids=None) -> pd.DataFrame:
    """5019: hadm con >=2 servicios pero sin nota de consult."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    cond = " OR ".join([f"LOWER(text) LIKE '%{s}%'" for s in SECCIONES_CONSULT])
    q = f"""
        WITH srv AS (
            SELECT hadm_id, COUNT(DISTINCT curr_service) AS n
            FROM {SCHEMA_HOSP}.services
            GROUP BY hadm_id
        ),
        cn AS (
            SELECT hadm_id, MAX(CASE WHEN ({cond}) THEN 1 ELSE 0 END) AS tiene
            FROM {SCHEMA_NOTE}.discharge
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            5019 AS id_evento,
            'No se registran las interconsultas' AS evento,
            'D' AS tier,
            CONCAT('n_srv=', COALESCE(srv.n, 1), ' tiene_consult=', COALESCE(cn.tiene, 0)) AS valor_calculado,
            (COALESCE(srv.n, 1) >= 2 AND COALESCE(cn.tiene, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN srv USING (hadm_id)
        LEFT JOIN cn USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[5019] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5020 — No se registran los antecedentes (PMH)
# ────────────────────────────────────────────────────────────────────
def auditar_pmh(conn, hadm_ids=None) -> pd.DataFrame:
    return _ausencia_seccion_en_discharge(conn, SECCIONES_PMH, 5020,
                                          "No se registran los antecedentes (PMH)", hadm_ids)


# ────────────────────────────────────────────────────────────────────
# 5021 — No se registran los diagnosticos
# ────────────────────────────────────────────────────────────────────
def auditar_diagnosticos(conn, hadm_ids=None) -> pd.DataFrame:
    """5021: hadm sin filas en diagnoses_icd."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH dx AS (
            SELECT hadm_id, COUNT(*) AS n
            FROM {SCHEMA_HOSP}.diagnoses_icd
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            5021 AS id_evento,
            'No se registran los diagnosticos' AS evento,
            'D' AS tier,
            CONCAT('n_dx=', COALESCE(dx.n, 0)) AS valor_calculado,
            (COALESCE(dx.n, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN dx USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[5021] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 5023 — Historia clinica incompleta (agregado)
# ────────────────────────────────────────────────────────────────────
def auditar_hc_incompleta(conn, hadm_ids=None) -> pd.DataFrame:
    """5023: agregado — el hadm acumula >=3 deficiencias de los detectores anteriores.
    Esta función se llama AL FINAL, sobre el DataFrame consolidado.
    Aquí devolvemos vacío; la agregación se hace en detectar_todos_tier_d().
    """
    return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 7026 — Falta de prescripcion (alias de 5010 más estricto)
# ────────────────────────────────────────────────────────────────────
def auditar_falta_prescripcion(conn, hadm_ids=None) -> pd.DataFrame:
    """7026: hadm que sobrevivió al alta (no expirado) y sin prescripciones."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH rx AS (
            SELECT hadm_id, COUNT(*) AS n
            FROM {SCHEMA_HOSP}.prescriptions
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            7026 AS id_evento,
            'Falta de prescripcion' AS evento,
            'D' AS tier,
            CONCAT('n_rx=', COALESCE(rx.n, 0)) AS valor_calculado,
            (a.hospital_expire_flag = 0 AND COALESCE(rx.n, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN rx USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[7026] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 9016 — Pruebas pretransfusionales ausentes
# ────────────────────────────────────────────────────────────────────
def auditar_pruebas_pretransfusionales(conn, hadm_ids=None) -> pd.DataFrame:
    """9016: hadm con transfusión (procedure 30233N1 o similar) pero sin lab
    de typing/crossmatch (itemid de TYPE & SCREEN en d_labitems)."""
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH transf AS (
            SELECT DISTINCT hadm_id
            FROM {SCHEMA_HOSP}.procedures_icd
            WHERE icd_version = 10
              AND icd_code LIKE '3023%'  -- transfusion codes ICD-10-PCS
        ),
        types AS (
            SELECT DISTINCT l.hadm_id
            FROM {SCHEMA_HOSP}.labevents l
            JOIN {SCHEMA_HOSP}.d_labitems d USING (itemid)
            WHERE LOWER(d.label) LIKE '%type%screen%'
               OR LOWER(d.label) LIKE '%crossmatch%'
               OR LOWER(d.label) LIKE '%blood group%'
        )
        SELECT
            a.hadm_id,
            9016 AS id_evento,
            'Pruebas pretransfusionales ausentes' AS evento,
            'D' AS tier,
            CONCAT('transf=', (t.hadm_id IS NOT NULL),
                   ' type_screen=', (ts.hadm_id IS NOT NULL)) AS valor_calculado,
            (t.hadm_id IS NOT NULL AND ts.hadm_id IS NULL)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN transf t USING (hadm_id)
        LEFT JOIN types ts USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[9016] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# ORQUESTADOR
# ────────────────────────────────────────────────────────────────────
DETECTORES_TIER_D = [
    ("503 Labs paciente erroneo", auditar_labs_paciente_incorrecto),
    ("504 Labs vacios", auditar_labs_vacios),
    ("505 Consentimiento", auditar_consentimiento),
    ("506 Reporte quirurgico", auditar_reporte_quirurgico),
    ("507 Examen fisico", auditar_examen_fisico),
    ("508 Nombre paciente (control)", auditar_nombre_paciente),
    ("509 Plan de trabajo", auditar_plan_trabajo),
    ("5010 Tratamiento", auditar_tratamiento),
    ("5012 Admittime", auditar_admittime),
    ("5014 Dischtime", auditar_dischtime),
    ("5015 Filiacion", auditar_filiacion),
    ("5016 HPI", auditar_hpi),
    ("5017 Progress notes", auditar_progress_notes),
    ("5018 Indicaciones alta", auditar_indicaciones_alta),
    ("5019 Interconsultas", auditar_interconsultas),
    ("5020 PMH", auditar_pmh),
    ("5021 Diagnosticos", auditar_diagnosticos),
    ("7026 Falta prescripcion", auditar_falta_prescripcion),
    ("9016 Pretransfusionales", auditar_pruebas_pretransfusionales),
]


def detectar_todos_tier_d(conn: duckdb.DuckDBPyConnection,
                          hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Ejecuta TODOS los auditores Tier D y agrega 5023 (HC incompleta agregada)."""
    frames = []
    for nombre, detector in DETECTORES_TIER_D:
        logger.info(f"Auditando: {nombre}")
        try:
            df = detector(conn, hadm_ids)
            logger.info(f"  → {len(df)} hadms con deficiencia")
            if not df.empty:
                frames.append(df)
        except Exception as e:
            logger.error(f"  ✗ Fallo en {nombre}: {e}")

    if not frames:
        return _resultado_vacio()

    out = pd.concat(frames, ignore_index=True)

    # 5023 HC incompleta: hadms con >=3 deficiencias
    conteos = out.groupby("hadm_id").size().reset_index(name="n_def")
    hc_incompleta = conteos[conteos["n_def"] >= 3].copy()
    if not hc_incompleta.empty:
        hc_incompleta["id_evento"] = 5023
        hc_incompleta["evento"] = "Historia clinica incompleta"
        hc_incompleta["tier"] = "D"
        hc_incompleta["valor_calculado"] = "n_def=" + hc_incompleta["n_def"].astype(str)
        hc_incompleta["detectado"] = True
        hc_incompleta = hc_incompleta[["hadm_id", "id_evento", "evento", "tier", "valor_calculado", "detectado"]]
        out = pd.concat([out, hc_incompleta], ignore_index=True)

    return out


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auditor Tier D — Completitud EHR (Anexo 02 GEMSES)")
    parser.add_argument("--db", default=r"C:\MIMIC\tesis\mimic.db",
                        help="Ruta a la base DuckDB de MIMIC-IV")
    parser.add_argument("--out", default=r"C:\MIMIC\tesis\tier_d_completitud.csv",
                        help="Ruta CSV de salida")
    parser.add_argument("--hadm-ids", default=None,
                        help="Lista CSV de hadm_ids para filtrar (opcional)")
    args = parser.parse_args()

    hadm_ids = None
    if args.hadm_ids:
        hadm_ids = [int(x) for x in args.hadm_ids.split(",")]

    conn = duckdb.connect(args.db, read_only=True)
    df = detectar_todos_tier_d(conn, hadm_ids)
    df.to_csv(args.out, index=False)
    print(f"OK — {len(df)} deficiencias Tier D auditadas en {args.out}")
