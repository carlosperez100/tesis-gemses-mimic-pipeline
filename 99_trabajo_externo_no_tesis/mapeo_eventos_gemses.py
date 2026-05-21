"""
=============================================================================
  MÓDULO DE MAPEO ICD-10 → ANEXO 02 EsSalud (GEMSES)
=============================================================================

Convierte códigos ICD-10 detectados en notas clínicas (o en la tabla
diagnoses_icd de MIMIC-IV) a categorías de eventos adversos según la
taxonomía oficial de la Directiva GG-ESSALUD-2021 (Anexo 02).

Este módulo es el puente entre la dimensión "Calidad (d=0.20)" de la
fórmula GEMSES y los datos crudos de MIMIC-IV.

USO BÁSICO
----------
    from mapeo_eventos_gemses import (
        cargar_mapeo_icd10,
        clasificar_codigo,
        score_calidad_gemses,
    )

    mapeo = cargar_mapeo_icd10("eventos_adversos_icd10.csv")

    # Clasificar un código individual
    info = clasificar_codigo("T81.0", mapeo)
    # → {'categoria_anexo02': 'Procedimiento', 'severidad_base': 'Alto', ...}

    # Calcular el score de la dimensión Calidad para una hospitalización
    codigos_paciente = ["T81.0", "N39.0", "L89.2"]
    score_d = score_calidad_gemses(codigos_paciente, mapeo)
    # → 7 (alto, en la escala 0-9 del Anexo 03)

LIMITACIONES Y DISCLAIMERS
--------------------------
El CSV `eventos_adversos_icd10.csv` contiene una selección CURADA de ~150
códigos ICD-10 representativos de eventos adversos en hospitalización.
NO es la lista exhaustiva del CIE-10 OMS (que tiene 70 000+ códigos), ni
sustituye al CIE-10 PE oficial del MINSA Perú.

Para validación final contra norma peruana, cruzar con:
- CIE-10 PE oficial — http://www.minsa.gob.pe/portada/Especiales/2014/cie10/
- Lista de Hospital-Acquired Conditions (HACs) — CMS
- Lista de Patient Safety Indicators (PSIs) — AHRQ

ESCALA DE SEVERIDAD GEMSES (Anexo 03)
-------------------------------------
La Matriz de Priorización GEMSES usa escala 0-9 para cada dimensión:
    Muy alto = 9
    Alto     = 6
    Medio    = 3
    Bajo     = 1
    Nulo     = 0
=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Optional


# Escala de severidad GEMSES (Anexo 03 Directiva GG-ESSALUD-2021)
ESCALA_SEVERIDAD = {
    "Muy alto": 9,
    "Alto":     6,
    "Medio":    3,
    "Bajo":     1,
    "Nulo":     0,
}


# =============================================================================
# Carga del CSV
# =============================================================================

def cargar_mapeo_icd10(ruta_csv: str = "eventos_adversos_icd10.csv") -> pd.DataFrame:
    """
    Carga el CSV de mapeo ICD-10 → Anexo 02 EsSalud como DataFrame indexado
    por código ICD-10.

    Parameters
    ----------
    ruta_csv : str
        Path al CSV. Por defecto busca en el directorio actual.

    Returns
    -------
    pd.DataFrame con columnas:
        codigo_icd10, descripcion_es, descripcion_en,
        categoria_anexo02_essalud, naturaleza_oms, grupo_gemses,
        severidad_base, fuente_normativa
    """
    df = pd.read_csv(ruta_csv, dtype=str)
    df.columns = df.columns.str.strip()
    df["codigo_icd10"] = df["codigo_icd10"].str.strip().str.upper()
    df = df.set_index("codigo_icd10", drop=False)
    return df


# =============================================================================
# Clasificación individual
# =============================================================================

def clasificar_codigo(codigo: str, mapeo: pd.DataFrame) -> Optional[dict]:
    """
    Devuelve la información asociada a un código ICD-10 según el mapeo.

    Parameters
    ----------
    codigo : str
        Código ICD-10 (ej. "T81.0", "n39.0", "L89.2").
        Se normaliza a mayúsculas automáticamente.
    mapeo : pd.DataFrame
        DataFrame retornado por cargar_mapeo_icd10().

    Returns
    -------
    dict con la fila completa del mapeo, o None si el código no está.

    Ejemplo:
        >>> info = clasificar_codigo("T81.0", mapeo)
        >>> info["categoria_anexo02_essalud"]
        'Procedimiento'
        >>> info["severidad_base"]
        'Alto'
    """
    codigo = codigo.strip().upper()
    if codigo in mapeo.index:
        return mapeo.loc[codigo].to_dict()

    # Si no encuentra el código exacto, intenta el prefijo de 3 caracteres
    # (ej. "T81.05" → busca "T81")
    if "." in codigo:
        codigo_base = codigo.split(".")[0]
        if codigo_base in mapeo.index:
            return mapeo.loc[codigo_base].to_dict()

    return None


# =============================================================================
# Score de la dimensión Calidad (d) de GEMSES
# =============================================================================

def score_calidad_gemses(
    codigos: list,
    mapeo: pd.DataFrame,
    estrategia: str = "max",
) -> int:
    """
    Calcula el score de la dimensión Calidad (d, peso 0.20 en la fórmula G)
    de la Matriz GEMSES, dado un conjunto de códigos ICD-10 asignados a
    una hospitalización.

    Parameters
    ----------
    codigos : list[str]
        Lista de códigos ICD-10 de la hospitalización.
    mapeo : pd.DataFrame
        Mapeo cargado.
    estrategia : {"max", "promedio", "suma_normalizada"}
        Cómo combinar los scores cuando hay múltiples eventos:
        - "max": toma la severidad del evento más grave (recomendado)
        - "promedio": promedio aritmético de severidades
        - "suma_normalizada": suma capped a 9

    Returns
    -------
    int en escala 0-9 (escala GEMSES Anexo 03)
    """
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
    else:
        raise ValueError(f"Estrategia desconocida: {estrategia}")


# =============================================================================
# Resumen estadístico de una cohorte
# =============================================================================

def resumir_cohorte(
    df_diagnosticos: pd.DataFrame,
    mapeo: pd.DataFrame,
    col_codigo: str = "icd_code",
    col_hadm: str = "hadm_id",
) -> pd.DataFrame:
    """
    Toma un DataFrame con códigos ICD-10 de múltiples hospitalizaciones
    (típicamente la tabla `diagnoses_icd` de MIMIC-IV) y devuelve, por
    hospitalización, el score Calidad y las categorías Anexo 02 detectadas.

    Parameters
    ----------
    df_diagnosticos : pd.DataFrame
        DataFrame con columnas hadm_id y icd_code (al menos).
    mapeo : pd.DataFrame
        Mapeo cargado.
    col_codigo, col_hadm : str
        Nombres de las columnas relevantes.

    Returns
    -------
    pd.DataFrame con columnas:
        hadm_id, score_calidad_d, n_eventos, categorias_detectadas
    """
    resultados = []
    for hadm, grupo in df_diagnosticos.groupby(col_hadm):
        codigos = grupo[col_codigo].tolist()
        score = score_calidad_gemses(codigos, mapeo, estrategia="max")
        cats = set()
        for c in codigos:
            info = clasificar_codigo(c, mapeo)
            if info:
                cats.add(info["categoria_anexo02_essalud"])
        resultados.append({
            "hadm_id": hadm,
            "score_calidad_d": score,
            "n_eventos_detectados": len(cats),
            "categorias_anexo02": ", ".join(sorted(cats)) if cats else "ninguno",
        })
    return pd.DataFrame(resultados)


# =============================================================================
# Reporte rápido del mapeo cargado
# =============================================================================

def reporte_mapeo(mapeo: pd.DataFrame) -> None:
    """
    Imprime un resumen del CSV de mapeo cargado para verificación rápida.
    """
    print(f"Total de códigos ICD-10 mapeados: {len(mapeo)}")
    print("")
    print("Distribución por categoría Anexo 02 EsSalud:")
    for cat, n in mapeo["categoria_anexo02_essalud"].value_counts().items():
        print(f"   {cat:<30s} : {n:>4}")
    print("")
    print("Distribución por severidad base:")
    for sev, n in mapeo["severidad_base"].value_counts().items():
        score = ESCALA_SEVERIDAD.get(sev, "?")
        print(f"   {sev:<10s} (score={score}) : {n:>4}")


# =============================================================================
# Demo (corre si ejecutas este archivo directamente)
# =============================================================================

if __name__ == "__main__":
    # Carga el CSV (asume que está en la misma carpeta que este script)
    ruta = Path(__file__).parent / "eventos_adversos_icd10.csv"
    mapeo = cargar_mapeo_icd10(str(ruta))

    print("=" * 60)
    print(" DEMO — Mapeo ICD-10 → Anexo 02 EsSalud (GEMSES)")
    print("=" * 60)
    print()
    reporte_mapeo(mapeo)
    print()

    print("=" * 60)
    print(" Ejemplos de clasificación")
    print("=" * 60)
    ejemplos = ["T81.0", "N39.0", "L89.2", "W19", "T80.3", "A41.5", "ZZZ.99"]
    for cod in ejemplos:
        info = clasificar_codigo(cod, mapeo)
        if info:
            print(f"\n{cod}:")
            print(f"   Descripción : {info['descripcion_es'][:80]}...")
            print(f"   Categoría   : {info['categoria_anexo02_essalud']}")
            print(f"   Severidad   : {info['severidad_base']} "
                  f"(score={ESCALA_SEVERIDAD.get(info['severidad_base'], '?')})")
        else:
            print(f"\n{cod}: NO ENCONTRADO en el mapeo (código fuera del scope curado)")

    print()
    print("=" * 60)
    print(" Ejemplo — Score Calidad de una hospitalización")
    print("=" * 60)
    codigos_paciente = ["T81.0", "N39.0", "L89.2", "W19"]
    score = score_calidad_gemses(codigos_paciente, mapeo)
    print(f"\nCódigos del paciente: {codigos_paciente}")
    print(f"Score Calidad (d) = {score}  (escala 0-9, peso GEMSES = 0.20)")
    print(f"Contribución a G  = {score} * 0.20 = {score * 0.20:.2f}")
