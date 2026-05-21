"""
=============================================================================
  MÓDULO DE MAPEO ICD-10 → ANEXO 02 EsSalud (GEMSES) — v2
=============================================================================

Versión 2: agrega soporte para ID Naturaleza e ID Evento Anexo 02 oficial.

ESTRUCTURA DE IDs (Anexo 02 Directiva GG-ESSALUD-2021)
------------------------------------------------------
ID Naturaleza:
    10 = COMPORTAMIENTO            (no aplica a ICD-10 estándar)
    20 = CUIDADO DEL PACIENTE
    30 = PROCEDIMIENTO
    40 = INFECCIÓN NOSOCOMIAL
    50 = MEDICACIÓN
    60 = DISPOSITIVO MÉDICO / EQUIPO / BIEN
    70 = HISTORIA CLÍNICA          (no aplica a ICD-10)

ID Evento Anexo 02: número entero. Los primeros 2 dígitos coinciden con
ID Naturaleza. Ej: 202 = "Caída de paciente", 401 = "ITU nosocomial",
502 = "Transfusión incompatible".

USO BÁSICO
----------
    from mapeo_eventos_gemses import cargar_mapeo_icd10, clasificar_codigo

    mapeo = cargar_mapeo_icd10("eventos_adversos_icd10_v2.csv")

    info = clasificar_codigo("W19", mapeo)
    # info["id_evento_anexo02"] = "202"
    # info["evento_anexo02"]    = "Caida de paciente"
=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Optional


ESCALA_SEVERIDAD = {
    "Muy alto": 9, "Alto": 6, "Medio": 3, "Bajo": 1, "Nulo": 0,
}

NATURALEZAS_ANEXO02 = {
    10: "COMPORTAMIENTO",
    20: "CUIDADO DEL PACIENTE",
    30: "PROCEDIMIENTO",
    40: "INFECCION NOSOCOMIAL",
    50: "MEDICACION",
    60: "DISPOSITIVO MEDICO / EQUIPO / BIEN",
    70: "HISTORIA CLINICA",
}


def cargar_mapeo_icd10(ruta_csv: str = "eventos_adversos_icd10_v2.csv") -> pd.DataFrame:
    """Carga el CSV de mapeo ICD-10 → Anexo 02 EsSalud."""
    df = pd.read_csv(ruta_csv, dtype=str)
    df.columns = df.columns.str.strip()
    df["codigo_icd10"] = df["codigo_icd10"].str.strip().str.upper()
    df["id_naturaleza"] = df["id_naturaleza"].astype(int)
    df["id_evento_anexo02"] = df["id_evento_anexo02"].astype(str)
    df = df.set_index("codigo_icd10", drop=False)
    return df


def clasificar_codigo(codigo: str, mapeo: pd.DataFrame) -> Optional[dict]:
    """Devuelve info de un código ICD-10 o None si no está en el mapeo."""
    codigo = codigo.strip().upper()
    if codigo in mapeo.index:
        return mapeo.loc[codigo].to_dict()
    if "." in codigo:
        codigo_base = codigo.split(".")[0]
        if codigo_base in mapeo.index:
            return mapeo.loc[codigo_base].to_dict()
    return None


def clasificar_por_id_evento(evento_id, mapeo: pd.DataFrame) -> pd.DataFrame:
    """Devuelve todos los códigos ICD-10 asociados a un ID Evento Anexo 02."""
    evento_id_str = str(evento_id)
    return mapeo[mapeo["id_evento_anexo02"] == evento_id_str].copy()


def score_calidad_gemses(codigos: list, mapeo: pd.DataFrame,
                          estrategia: str = "max") -> int:
    """Calcula el score d (Calidad) de la fórmula GEMSES."""
    if not codigos:
        return 0
    severidades = []
    for cod in codigos:
        info = clasificar_codigo(cod, mapeo)
        if info is not None:
            sev_label = info.get("severidad_base", "Nulo")
            severidades.append(ESCALA_SEVERIDAD.get(sev_label, 0))
    if not severidades:
        return 0
    if estrategia == "max":
        return max(severidades)
    elif estrategia == "promedio":
        return int(round(sum(severidades) / len(severidades)))
    elif estrategia == "suma_normalizada":
        return min(sum(severidades), 9)
    raise ValueError(f"Estrategia desconocida: {estrategia}")


def estadisticas_por_naturaleza(mapeo: pd.DataFrame) -> pd.DataFrame:
    """Distribución de códigos por ID Naturaleza."""
    grupos = mapeo.groupby("id_naturaleza").agg(
        n_codigos_icd10=("codigo_icd10", "count"),
        n_eventos_distintos=("id_evento_anexo02", "nunique"),
    ).reset_index()
    grupos["naturaleza_nombre"] = grupos["id_naturaleza"].map(NATURALEZAS_ANEXO02)
    return grupos[["id_naturaleza", "naturaleza_nombre",
                   "n_codigos_icd10", "n_eventos_distintos"]]


def resumir_cohorte(df_diagnosticos, mapeo, col_codigo="icd_code", col_hadm="hadm_id"):
    """Procesa tabla diagnoses_icd y devuelve scores Calidad por hadm_id."""
    resultados = []
    for hadm, grupo in df_diagnosticos.groupby(col_hadm):
        codigos = grupo[col_codigo].tolist()
        score = score_calidad_gemses(codigos, mapeo, estrategia="max")
        eventos = set()
        naturalezas = set()
        for c in codigos:
            info = clasificar_codigo(c, mapeo)
            if info:
                eventos.add(f"{info['id_evento_anexo02']}-{info['evento_anexo02']}")
                naturalezas.add(NATURALEZAS_ANEXO02.get(int(info['id_naturaleza']), "?"))
        resultados.append({
            "hadm_id": hadm,
            "score_calidad_d": score,
            "n_eventos_detectados": len(eventos),
            "eventos_anexo02": ", ".join(sorted(eventos)) if eventos else "ninguno",
            "naturalezas": ", ".join(sorted(naturalezas)) if naturalezas else "ninguna",
        })
    return pd.DataFrame(resultados)


# =============================================================================
# DEMO
# =============================================================================
if __name__ == "__main__":
    ruta = Path(__file__).parent / "eventos_adversos_icd10_v2.csv"
    mapeo = cargar_mapeo_icd10(str(ruta))

    print("=" * 70)
    print(" DEMO v2 - Mapeo ICD-10 con IDs oficiales del Anexo 02 EsSalud")
    print("=" * 70)
    print()
    print("ESTADISTICAS POR NATURALEZA:")
    print(estadisticas_por_naturaleza(mapeo).to_string(index=False))
    print()

    # Ejemplo 1
    print("=" * 70)
    print(" Ejemplo 1 - Clasificacion del codigo W19")
    print("=" * 70)
    info = clasificar_codigo("W19", mapeo)
    nat_id = int(info["id_naturaleza"])
    nat_nombre = NATURALEZAS_ANEXO02.get(nat_id)
    sev = info["severidad_base"]
    sev_num = ESCALA_SEVERIDAD[sev]
    print()
    print(f"   id_naturaleza      : {nat_id} ({nat_nombre})")
    print(f"   id_evento_anexo02  : {info['id_evento_anexo02']}")
    print(f"   evento_anexo02     : {info['evento_anexo02']}")
    print(f"   severidad_base     : {sev} (score={sev_num})")
    print()

    # Ejemplo 2
    print("=" * 70)
    print(" Ejemplo 2 - Codigos ICD-10 que indican 'Caida de paciente' (202)")
    print("=" * 70)
    caidas = clasificar_por_id_evento(202, mapeo)
    print()
    print(f"   {len(caidas)} codigos ICD-10 mapean al evento Anexo 02 = 202:")
    for _, fila in caidas.iterrows():
        cod = fila["codigo_icd10"]
        desc = fila["descripcion_es"][:55]
        print(f"   {cod:<8s} - {desc}")
    print()

    # Ejemplo 3
    print("=" * 70)
    print(" Ejemplo 3 - Score Calidad de una hospitalizacion ejemplo")
    print("=" * 70)
    codigos = ["T81.0", "N39.0", "L89.2", "W19"]
    score = score_calidad_gemses(codigos, mapeo)
    print()
    print(f"   Codigos del paciente: {codigos}")
    print(f"   Score Calidad (d)   = {score} (escala 0-9, peso GEMSES = 0.20)")
    print(f"   Contribucion a G    = {score} * 0.20 = {score * 0.20:.2f}")
