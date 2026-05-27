"""
Tier C — Detección de eventos adversos del Anexo 02 GEMSES usando
VARIABLES ESTRUCTURADAS de MIMIC-IV.

Estos eventos no son detectables por NLP (Tier B) ni por ICD-10 directo
(Tier A): requieren combinar tablas estructuradas (admissions, transfers,
labevents, procedures_icd, services, icustays) con lógica temporal o
agregada.

Total de eventos cubiertos: 11
  - 1009  Fallecimiento (hospital)
  - 1009b Mortalidad UCI
  - 1007  Estancia prolongada (LOS > P75 dentro del DRG)
  - 1002  Disponibilidad/idoneidad de camas/servicios (proxy AGAINST ADVICE)
  - 10010 Retraso o espera del paciente (gap ED → admisión > 6h)
  - 10011 Retraso interconsulta (sin nota de consult en 24h)
  - 10018 Retraso exámenes (lag order→result > 4h en labs)
  - 8016  Múltiples punciones — proxy por count de procedimientos
  - 8033  Múltiples punciones (variante por procedures_icd 4C4*)
  - 1011  Readmisión precoz (< 30 días, mismo subject_id)
  -  803  Dehiscencia (proxy por readmisión < 30d con T81)

Uso:
    import duckdb
    from tier_c_variables_estructuradas import detectar_todos_tier_c
    conn = duckdb.connect('mimic.db')
    df = detectar_todos_tier_c(conn)

Cada función devuelve un DataFrame con columnas:
    hadm_id, id_evento, evento, tier, valor_calculado, detectado

Autor: Pipeline tesis MIA-303 (GEMSES × MIMIC-IV)
"""

from __future__ import annotations

import logging
from typing import Optional, List

import duckdb
import pandas as pd

# ────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Esquema MIMIC-IV típico cuando se carga en DuckDB:
#   mimiciv_hosp.admissions, mimiciv_hosp.transfers, mimiciv_hosp.labevents,
#   mimiciv_hosp.procedures_icd, mimiciv_hosp.services, mimiciv_hosp.drgcodes
#   mimiciv_icu.icustays
# Si el schema difiere en tu DuckDB, edita SCHEMA_HOSP / SCHEMA_ICU.
SCHEMA_HOSP = "mimiciv_hosp"
SCHEMA_ICU = "mimiciv_icu"


def _filter_hadm(query: str, hadm_ids: Optional[List[int]]) -> str:
    """Inyecta cláusula WHERE hadm_id IN (...) si se pasa lista."""
    if not hadm_ids:
        return query
    ids_str = ",".join(str(int(h)) for h in hadm_ids)
    if "WHERE" in query.upper():
        return query + f" AND hadm_id IN ({ids_str})"
    return query + f" WHERE hadm_id IN ({ids_str})"


def _resultado_vacio() -> pd.DataFrame:
    return pd.DataFrame(columns=["hadm_id", "id_evento", "evento", "tier", "valor_calculado", "detectado"])


# ────────────────────────────────────────────────────────────────────
# 1009 — Fallecimiento (hospital_expire_flag)
# ────────────────────────────────────────────────────────────────────
def detectar_fallecimiento(conn: duckdb.DuckDBPyConnection,
                           hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 1009: fallecimiento intrahospitalario.

    Lógica: admissions.hospital_expire_flag = 1.
    """
    q = f"""
        SELECT
            hadm_id,
            1009 AS id_evento,
            'Fallecimiento' AS evento,
            'C' AS tier,
            hospital_expire_flag::VARCHAR AS valor_calculado,
            (hospital_expire_flag = 1)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[1009 Fallecimiento] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 1009b — Mortalidad UCI
# ────────────────────────────────────────────────────────────────────
def detectar_mortalidad_uci(conn: duckdb.DuckDBPyConnection,
                            hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 1009b: fallecimiento durante estancia en UCI.

    Lógica: admissions.hospital_expire_flag = 1 AND existe icustays para el hadm_id
            con outtime >= deathtime (paciente murió estando en UCI).
    """
    q = f"""
        WITH icu AS (
            SELECT hadm_id, MIN(intime) AS intime_min, MAX(outtime) AS outtime_max
            FROM {SCHEMA_ICU}.icustays
            GROUP BY hadm_id
        )
        SELECT
            a.hadm_id,
            10090 AS id_evento,
            'Mortalidad UCI' AS evento,
            'C' AS tier,
            CONCAT('expire=', a.hospital_expire_flag, ' icu_in=', i.intime_min) AS valor_calculado,
            (a.hospital_expire_flag = 1 AND i.hadm_id IS NOT NULL
             AND a.deathtime BETWEEN i.intime_min AND i.outtime_max)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN icu i USING (hadm_id)
        WHERE a.hospital_expire_flag = 1
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[1009b Mortalidad UCI] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 1007 — Estancia prolongada (LOS > P75 del mismo DRG)
# ────────────────────────────────────────────────────────────────────
def detectar_estancia_prolongada(conn: duckdb.DuckDBPyConnection,
                                 hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 1007: LOS > percentil 75 dentro del mismo DRG.

    Lógica:
      1. Calcular LOS = (dischtime - admittime) en días.
      2. Joinar con drgcodes para obtener DRG.
      3. Marcar como evento si LOS > P75 del DRG.
    Si no hay DRG, se usa el P75 global como fallback.
    """
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"WHERE a.hadm_id IN ({ids_str})"

    q = f"""
        WITH los AS (
            SELECT
                a.hadm_id,
                a.subject_id,
                DATE_DIFF('day', a.admittime, a.dischtime) AS los_days,
                d.drg_code
            FROM {SCHEMA_HOSP}.admissions a
            LEFT JOIN (
                SELECT hadm_id, MIN(drg_code) AS drg_code
                FROM {SCHEMA_HOSP}.drgcodes
                GROUP BY hadm_id
            ) d USING (hadm_id)
            {where_clause}
        ),
        p75_drg AS (
            SELECT drg_code,
                   QUANTILE_CONT(los_days, 0.75) AS p75
            FROM los
            WHERE drg_code IS NOT NULL
            GROUP BY drg_code
        ),
        p75_global AS (
            SELECT QUANTILE_CONT(los_days, 0.75) AS p75 FROM los
        )
        SELECT
            l.hadm_id,
            1007 AS id_evento,
            'Estancia prolongada' AS evento,
            'C' AS tier,
            CONCAT('LOS=', l.los_days, 'd P75=', COALESCE(p.p75, g.p75)) AS valor_calculado,
            (l.los_days > COALESCE(p.p75, g.p75))::BOOLEAN AS detectado
        FROM los l
        LEFT JOIN p75_drg p ON l.drg_code = p.drg_code
        CROSS JOIN p75_global g
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[1007 Estancia prolongada] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 1002 — Disponibilidad/idoneidad de camas (proxy)
# ────────────────────────────────────────────────────────────────────
def detectar_falta_camas(conn: duckdb.DuckDBPyConnection,
                         hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 1002: proxy = AGAINST ADVICE en discharge_location.

    Una alta contra opinión médica sugiere insatisfacción que puede correlacionarse
    con saturación de servicios. Es un proxy débil (Confianza: baja).
    """
    q = f"""
        SELECT
            hadm_id,
            1002 AS id_evento,
            'Disponibilidad/idoneidad camas (proxy)' AS evento,
            'C' AS tier,
            discharge_location AS valor_calculado,
            (UPPER(discharge_location) LIKE '%AGAINST ADVICE%')::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[1002 Falta camas] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 10010 — Retraso/espera del paciente (ED → admisión > 6h)
# ────────────────────────────────────────────────────────────────────
def detectar_retraso_espera(conn: duckdb.DuckDBPyConnection,
                            hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 10010: tiempo desde edregtime hasta admittime > 6 horas.

    Solo aplica a admisiones que pasaron por ED (edregtime NOT NULL).
    """
    q = f"""
        SELECT
            hadm_id,
            10010 AS id_evento,
            'Retraso o espera del paciente' AS evento,
            'C' AS tier,
            CONCAT('gap_h=', ROUND(DATE_DIFF('minute', edregtime, admittime) / 60.0, 1)) AS valor_calculado,
            (edregtime IS NOT NULL
             AND DATE_DIFF('minute', edregtime, admittime) > 360)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions
        WHERE edregtime IS NOT NULL
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[10010 Retraso espera] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 10011 — Retraso interconsulta (sin nota de consult en 24h)
# ────────────────────────────────────────────────────────────────────
def detectar_retraso_interconsulta(conn: duckdb.DuckDBPyConnection,
                                   hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 10011: hadm_id con transferencias a >=2 servicios (sugiere interconsulta)
    pero sin nota tipo 'Consult' / 'Consultation' en las primeras 24h post-admisión.

    Requiere mimiciv_note.noteevents (puede no existir en todas las builds).
    Si la tabla no está disponible, devuelve resultado vacío con warning.
    """
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a.hadm_id IN ({ids_str})"

    q = f"""
        WITH servicios AS (
            SELECT hadm_id, COUNT(DISTINCT curr_service) AS n_servicios
            FROM {SCHEMA_HOSP}.services
            GROUP BY hadm_id
        ),
        notas_consult AS (
            SELECT n.hadm_id, COUNT(*) AS n_consult_24h
            FROM mimiciv_note.discharge n
            JOIN {SCHEMA_HOSP}.admissions a USING (hadm_id)
            WHERE LOWER(n.text) LIKE '%consult%'
              AND n.charttime <= a.admittime + INTERVAL 24 HOUR
            GROUP BY n.hadm_id
        )
        SELECT
            a.hadm_id,
            10011 AS id_evento,
            'Retraso interconsulta' AS evento,
            'C' AS tier,
            CONCAT('n_serv=', COALESCE(s.n_servicios, 0),
                   ' consult24h=', COALESCE(c.n_consult_24h, 0)) AS valor_calculado,
            (COALESCE(s.n_servicios, 1) >= 2 AND COALESCE(c.n_consult_24h, 0) = 0)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a
        LEFT JOIN servicios s USING (hadm_id)
        LEFT JOIN notas_consult c USING (hadm_id)
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.warning(f"[10011 Retraso interconsulta] no se pudo computar (probablemente "
                       f"falta mimiciv_note.discharge): {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 10018 — Retraso exámenes (lag order→result > 4h)
# ────────────────────────────────────────────────────────────────────
def detectar_retraso_examenes(conn: duckdb.DuckDBPyConnection,
                              hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 10018: en labevents, mediana de (storetime - charttime) > 4h por hadm_id.

    En MIMIC-IV:
      charttime = momento de toma de muestra
      storetime = momento en que se ingresó el resultado
    """
    q = f"""
        WITH lags AS (
            SELECT
                hadm_id,
                MEDIAN(DATE_DIFF('minute', charttime, storetime)) AS mediana_lag_min
            FROM {SCHEMA_HOSP}.labevents
            WHERE charttime IS NOT NULL AND storetime IS NOT NULL
              AND hadm_id IS NOT NULL
            GROUP BY hadm_id
        )
        SELECT
            hadm_id,
            10018 AS id_evento,
            'Retraso examenes auxiliares' AS evento,
            'C' AS tier,
            CONCAT('mediana_min=', ROUND(mediana_lag_min, 0)) AS valor_calculado,
            (mediana_lag_min > 240)::BOOLEAN AS detectado
        FROM lags
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[10018 Retraso examenes] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 8016 / 8033 — Múltiples punciones
# ────────────────────────────────────────────────────────────────────
def detectar_multiples_punciones(conn: duckdb.DuckDBPyConnection,
                                 hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 8016/8033: hadm con >3 procedimientos cuyo icd_code empieza con códigos
    de punción venosa/arterial.

    Códigos ICD-10-PCS relevantes:
      - 3E0* / 4A04* : drenaje/insertion vascular
      - 0JH* / 02H* / 05H* / 06H* : insertion de dispositivos venosos/arteriales

    Como aproximación, contamos procedimientos cuyos primeros caracteres
    coinciden con punciones repetidas en el mismo hadm_id.
    """
    q = f"""
        WITH puncts AS (
            SELECT hadm_id, COUNT(*) AS n_puncts
            FROM {SCHEMA_HOSP}.procedures_icd
            WHERE icd_version = 10
              AND (
                  icd_code LIKE '02H%'  -- insertion en corazón/grandes vasos
                  OR icd_code LIKE '05H%'  -- insertion venas
                  OR icd_code LIKE '06H%'  -- insertion venas
                  OR icd_code LIKE '03H%'  -- insertion arterias
                  OR icd_code LIKE '04H%'  -- insertion arterias
                  OR icd_code LIKE '3E0%'  -- introduction
                  OR icd_code LIKE '4A04%' -- monitoring vascular
              )
            GROUP BY hadm_id
        )
        SELECT
            hadm_id,
            8033 AS id_evento,
            'Multiples punciones' AS evento,
            'C' AS tier,
            CONCAT('n_puncts=', n_puncts) AS valor_calculado,
            (n_puncts > 3)::BOOLEAN AS detectado
        FROM puncts
    """
    q = _filter_hadm(q, hadm_ids)
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[8033 Multiples punciones] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 1011 — Readmisión precoz (< 30 días, mismo subject_id)
# ────────────────────────────────────────────────────────────────────
def detectar_readmision_30d(conn: duckdb.DuckDBPyConnection,
                            hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 1011 (readmisión precoz): readmisión dentro de 30 días.

    Lógica: para cada hadm, ¿existe otra hadm del mismo subject_id cuyo
    admittime esté entre dischtime y dischtime + 30 días?

    Marcamos como detectado el hadm "índice" (el primero, no la readmisión).
    """
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a1.hadm_id IN ({ids_str})"

    q = f"""
        SELECT
            a1.hadm_id,
            1011 AS id_evento,
            'Readmision precoz <30d' AS evento,
            'C' AS tier,
            CONCAT('next_hadm_in_d=',
                   COALESCE(DATE_DIFF('day', a1.dischtime, MIN(a2.admittime)), 999)) AS valor_calculado,
            (MIN(a2.admittime) IS NOT NULL)::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a1
        LEFT JOIN {SCHEMA_HOSP}.admissions a2
          ON a1.subject_id = a2.subject_id
          AND a2.admittime > a1.dischtime
          AND a2.admittime <= a1.dischtime + INTERVAL 30 DAY
          AND a2.hadm_id != a1.hadm_id
        WHERE 1=1 {where_clause}
        GROUP BY a1.hadm_id, a1.dischtime
    """
    try:
        df = conn.execute(q).fetchdf()
        return df[df["detectado"]].reset_index(drop=True)
    except Exception as e:
        logger.error(f"[1011 Readmision 30d] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# 803 — Dehiscencia (proxy por readmisión < 30d con T81)
# ────────────────────────────────────────────────────────────────────
def detectar_dehiscencia_proxy(conn: duckdb.DuckDBPyConnection,
                               hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Evento 803 (proxy estructurado): el hadm índice es seguido por
    readmisión <30d con diagnóstico T81* (complicaciones de procedimiento).

    Esto complementa al Tier A (que detecta T81.3 directo) y al Tier B (NLP)
    capturando casos donde la dehiscencia se diagnostica solo en la readmisión.
    """
    where_clause = ""
    if hadm_ids:
        ids_str = ",".join(str(int(h)) for h in hadm_ids)
        where_clause = f"AND a1.hadm_id IN ({ids_str})"

    q = f"""
        WITH readm_t81 AS (
            SELECT DISTINCT a2.subject_id, a2.admittime
            FROM {SCHEMA_HOSP}.admissions a2
            JOIN {SCHEMA_HOSP}.diagnoses_icd d
              ON a2.hadm_id = d.hadm_id
            WHERE d.icd_version = 10
              AND d.icd_code LIKE 'T81%'
        )
        SELECT
            a1.hadm_id,
            8030 AS id_evento,
            'Dehiscencia (proxy readmision T81)' AS evento,
            'C' AS tier,
            'readmision_T81<30d' AS valor_calculado,
            TRUE::BOOLEAN AS detectado
        FROM {SCHEMA_HOSP}.admissions a1
        JOIN readm_t81 r
          ON a1.subject_id = r.subject_id
          AND r.admittime > a1.dischtime
          AND r.admittime <= a1.dischtime + INTERVAL 30 DAY
        WHERE 1=1 {where_clause}
    """
    try:
        df = conn.execute(q).fetchdf()
        return df
    except Exception as e:
        logger.error(f"[803 Dehiscencia proxy] {e}")
        return _resultado_vacio()


# ────────────────────────────────────────────────────────────────────
# ORQUESTADOR
# ────────────────────────────────────────────────────────────────────
DETECTORES_TIER_C = [
    ("1009 Fallecimiento", detectar_fallecimiento),
    ("1009b Mortalidad UCI", detectar_mortalidad_uci),
    ("1007 Estancia prolongada", detectar_estancia_prolongada),
    ("1002 Falta camas (proxy)", detectar_falta_camas),
    ("10010 Retraso/espera", detectar_retraso_espera),
    ("10011 Retraso interconsulta", detectar_retraso_interconsulta),
    ("10018 Retraso examenes", detectar_retraso_examenes),
    ("8033 Multiples punciones", detectar_multiples_punciones),
    ("1011 Readmision precoz", detectar_readmision_30d),
    ("803 Dehiscencia (proxy)", detectar_dehiscencia_proxy),
]


def detectar_todos_tier_c(conn: duckdb.DuckDBPyConnection,
                          hadm_ids: Optional[List[int]] = None) -> pd.DataFrame:
    """Ejecuta TODOS los detectores Tier C y devuelve un DataFrame unificado.

    Cada detector aporta filas hadm_id × id_evento. Un mismo hadm puede tener
    múltiples eventos Tier C.
    """
    frames = []
    for nombre, detector in DETECTORES_TIER_C:
        logger.info(f"Ejecutando: {nombre}")
        try:
            df = detector(conn, hadm_ids)
            logger.info(f"  → {len(df)} detecciones")
            if not df.empty:
                frames.append(df)
        except Exception as e:
            logger.error(f"  ✗ Fallo en {nombre}: {e}")

    if not frames:
        return _resultado_vacio()
    out = pd.concat(frames, ignore_index=True)
    return out


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detector Tier C — Anexo 02 GEMSES")
    parser.add_argument("--db", default=r"C:\MIMIC\tesis\mimic.db",
                        help="Ruta a la base DuckDB de MIMIC-IV")
    parser.add_argument("--out", default=r"C:\MIMIC\tesis\tier_c_detecciones.csv",
                        help="Ruta CSV de salida")
    parser.add_argument("--hadm-ids", default=None,
                        help="Lista CSV de hadm_ids para filtrar (opcional)")
    args = parser.parse_args()

    hadm_ids = None
    if args.hadm_ids:
        hadm_ids = [int(x) for x in args.hadm_ids.split(",")]

    conn = duckdb.connect(args.db, read_only=True)
    df = detectar_todos_tier_c(conn, hadm_ids)
    df.to_csv(args.out, index=False)
    print(f"OK — {len(df)} detecciones Tier C exportadas a {args.out}")
