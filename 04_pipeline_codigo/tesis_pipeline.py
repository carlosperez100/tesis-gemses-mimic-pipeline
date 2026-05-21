"""
=============================================================================
  TESIS MIA 303 — PIPELINE ÚNICO DE REPLICACIÓN
  Detección automatizada y priorización de eventos adversos en notas clínicas
  mediante NLP y aplicación de la Matriz de Priorización del Modelo GEMSES
  sobre MIMIC-IV
=============================================================================

Autor:       Carlos Pérez Pérez (carlosperez100@gmail.com)
Curso:       MIA 303 - Maestría en Inteligencia Artificial, UNI
Docente:     Mg. Eng. Maria F. Tejada Begazo
Última act:  11 de mayo de 2026

PROPÓSITO
---------
Este es un script ÚNICO Y AUTOCONTENIDO que reproduce el pipeline base del
proyecto. Permite a cualquier persona con acceso a MIMIC-IV / MIMIC-IV-Note
ejecutar los mismos análisis exploratorios y construir el corpus inicial
para los experimentos de NLP.

Está diseñado para ser SIMPLE: una sola dependencia técnica obligatoria
(Python 3.10+), tres librerías estándar del ecosistema científico
(duckdb, pandas, pyarrow), y rutas configurables en la sección de constantes
al principio del archivo.

CÓMO USARLO
-----------
1. Instala las dependencias:
       pip install duckdb pandas pyarrow tqdm

2. Ajusta las rutas en la sección CONFIGURACIÓN (líneas 60-75) para que
   apunten a tus carpetas locales.

3. Ejecuta:
       python tesis_pipeline.py

   El script reportará por consola cada paso y guardará resultados en la
   carpeta de trabajo definida (por defecto, C:\\MIMIC\\tesis\\salidas\\).

REPLICACIÓN CON NUEVA INFORMACIÓN
---------------------------------
Para procesar OTRO corpus de notas clínicas (por ejemplo, MIMIC-IV-Note v3.0
en el futuro, o un corpus de notas en español de EsSalud), solo necesitas
cambiar la ruta PATH_NOTAS en la sección CONFIGURACIÓN. El resto del
pipeline corre idéntico siempre que el corpus tenga las columnas:
note_id, subject_id, hadm_id, note_type, charttime, text

REQUISITOS NORMATIVOS
---------------------
- Acceso credentialed a PhysioNet con DUA firmado para MIMIC-IV-Note v2.2
- Certificación CITI Program "Data or Specimens Only Research"
- NO redistribuir los datos generados — quedan bajo el mismo DUA

=============================================================================
"""

# =============================================================================
# IMPORTS — Solo librerías estándar y de uso masivo en data science
# =============================================================================
import os
import sys
import json
import gzip
from pathlib import Path
from datetime import datetime

# Dependencias externas (instaladas vía pip)
import duckdb
import pandas as pd

# =============================================================================
# CONFIGURACIÓN — Ajusta estas rutas a tu entorno local
# =============================================================================

# Rutas a los datos (modifica solo si tus datos están en otra carpeta)
PATH_NOTAS = Path(r"C:\MIMIC\note\note")        # Carpeta con discharge.csv.gz
PATH_MIMIC_MAIN = Path(r"C:\MIMIC\mimiciv")     # MIMIC-IV principal (hosp + icu)
PATH_SALIDAS = Path(r"C:\MIMIC\tesis\salidas")  # Donde se guardan resultados
PATH_DB = Path(r"C:\MIMIC\tesis\mimic.db")      # Base DuckDB de trabajo

# Parámetros del experimento
TAMANO_MUESTRA = 100              # Cuántas notas tomar para el sample inicial
SEMILLA_ALEATORIA = 42            # Para reproducibilidad de la muestra
NOTA_CARACTERES_PREVIEW = 800     # Caracteres a mostrar de la primera nota

# =============================================================================
# UTILIDADES — Funciones pequeñas reutilizables
# =============================================================================

def log(mensaje: str, nivel: str = "INFO") -> None:
    """Imprime un mensaje con timestamp para seguimiento de ejecución."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{nivel:<5}] {mensaje}")


def verificar_archivo(ruta: Path, etiqueta: str) -> bool:
    """Comprueba que un archivo existe y muestra su tamaño en MB."""
    if ruta.exists():
        mb = ruta.stat().st_size / 1024 / 1024
        log(f"OK    {etiqueta:<40s} ({mb:>7.1f} MB)")
        return True
    else:
        log(f"FALTA {etiqueta:<40s} (no encontrado en {ruta})", "WARN")
        return False


def asegurar_carpeta(ruta: Path) -> None:
    """Crea la carpeta si no existe (sin error si ya existe)."""
    ruta.mkdir(parents=True, exist_ok=True)


# =============================================================================
# PASO 1 — VERIFICACIÓN DEL ENTORNO
# =============================================================================

def paso_1_verificar_entorno() -> dict:
    """
    Verifica que las librerías estén instaladas, los datos existan y la
    carpeta de salidas esté disponible. Retorna un diccionario con el
    estado de cada elemento.
    """
    log("=" * 70)
    log("PASO 1 — Verificación del entorno")
    log("=" * 70)

    estado = {
        "python": sys.version.split()[0],
        "duckdb": duckdb.__version__,
        "pandas": pd.__version__,
        "notas_disponible": False,
        "mimic_main_disponible": False,
    }

    log(f"Python      : {estado['python']}")
    log(f"DuckDB      : {estado['duckdb']}")
    log(f"Pandas      : {estado['pandas']}")
    log("")
    log("Archivos de datos:")
    estado["notas_disponible"] = verificar_archivo(
        PATH_NOTAS / "discharge.csv.gz", "discharge.csv.gz (MIMIC-IV-Note)"
    )
    estado["mimic_main_disponible"] = verificar_archivo(
        PATH_MIMIC_MAIN / "hosp" / "admissions.csv.gz",
        "admissions.csv.gz (MIMIC-IV principal)"
    )

    asegurar_carpeta(PATH_SALIDAS)
    log(f"Carpeta de salidas lista: {PATH_SALIDAS}")
    log("")

    return estado


# =============================================================================
# PASO 2 — CONEXIÓN A DUCKDB Y REGISTRO DE VISTAS
# =============================================================================

def paso_2_conectar_duckdb() -> duckdb.DuckDBPyConnection:
    """
    Crea (o reabre) la base DuckDB y registra los archivos .csv.gz como
    vistas. Las vistas son punteros a los archivos: NO copian los datos a
    memoria, lo que hace que la conexión sea casi instantánea.

    DuckDB lee los archivos comprimidos directamente sin descomprimir.
    """
    log("=" * 70)
    log("PASO 2 — Conexión DuckDB y registro de vistas")
    log("=" * 70)

    asegurar_carpeta(PATH_DB.parent)
    con = duckdb.connect(str(PATH_DB))
    log(f"Conectado a {PATH_DB}")

    # Registrar discharge.csv.gz como vista llamada 'discharge'
    archivo_notas = PATH_NOTAS / "discharge.csv.gz"
    if archivo_notas.exists():
        con.execute(f"""
            CREATE OR REPLACE VIEW discharge AS
            SELECT * FROM read_csv_auto('{archivo_notas.as_posix()}',
                                        compression='gzip')
        """)
        log("Vista 'discharge' creada (puntero al archivo .csv.gz)")

    # Si tienes MIMIC-IV principal descargado, registra esas tablas también
    for tabla in ["admissions", "patients", "diagnoses_icd"]:
        p = PATH_MIMIC_MAIN / "hosp" / f"{tabla}.csv.gz"
        if p.exists():
            con.execute(f"""
                CREATE OR REPLACE VIEW {tabla} AS
                SELECT * FROM read_csv_auto('{p.as_posix()}', compression='gzip')
            """)
            log(f"Vista '{tabla}' creada")

    log("")
    return con


# =============================================================================
# PASO 3 — EXPLORACIÓN INICIAL DEL CORPUS
# =============================================================================

def paso_3_explorar_corpus(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Ejecuta las queries de descubrimiento sobre el corpus de notas clínicas.
    Retorna un diccionario con las métricas y guarda un CSV resumen en
    PATH_SALIDAS.
    """
    log("=" * 70)
    log("PASO 3 — Exploración inicial del corpus")
    log("=" * 70)

    # Query 1 — total de notas
    total = con.execute("SELECT COUNT(*) FROM discharge").fetchone()[0]
    log(f"Total de epicrisis (discharge summaries): {total:,}")

    # Query 2 — distribución por tipo
    tipos = con.execute("""
        SELECT note_type,
               COUNT(*) AS n,
               COUNT(DISTINCT subject_id) AS pacientes,
               COUNT(DISTINCT hadm_id)    AS hospitalizaciones
        FROM discharge
        GROUP BY note_type
        ORDER BY n DESC
    """).df()
    log("Distribución por tipo de nota:")
    for _, fila in tipos.iterrows():
        log(f"   {fila['note_type']:<10s} | {fila['n']:>8,} notas | "
            f"{fila['pacientes']:>7,} pacientes | "
            f"{fila['hospitalizaciones']:>7,} hospitalizaciones")

    # Query 3 — estadísticas de longitud (útil para planear segmentación NLP)
    longitud = con.execute("""
        SELECT
            MIN(LENGTH(text))    AS min_chars,
            CAST(AVG(LENGTH(text)) AS INTEGER) AS avg_chars,
            CAST(MEDIAN(LENGTH(text)) AS INTEGER) AS median_chars,
            MAX(LENGTH(text))    AS max_chars
        FROM discharge
    """).fetchone()
    log(f"Longitud de las notas (caracteres):")
    log(f"   min={longitud[0]:>5}   avg={longitud[1]:>5}   "
        f"median={longitud[2]:>5}   max={longitud[3]:>5}")

    # Query 4 — distribución estimada de tokens
    # Heurística: 1 token ≈ 4 caracteres en texto clínico inglés.
    # BioBERT/ClinicalBERT tienen máximo 512 tokens, así que cualquier nota
    # con > 2048 caracteres necesita segmentación.
    rangos = con.execute("""
        SELECT
            CASE
                WHEN LENGTH(text) < 2048  THEN '1. < 512 tokens (cabe sin segmentar)'
                WHEN LENGTH(text) < 8192  THEN '2. 512-2048 tokens (segmentar 2-4 ventanas)'
                WHEN LENGTH(text) < 32768 THEN '3. 2048-8192 tokens (segmentar 4-16)'
                ELSE                           '4. > 8192 tokens (caso extremo)'
            END AS rango,
            COUNT(*) AS n
        FROM discharge
        GROUP BY rango
        ORDER BY rango
    """).df()
    log("Distribución estimada por rango de tokens (decisión de segmentación NLP):")
    for _, fila in rangos.iterrows():
        log(f"   {fila['rango']:<45s} : {fila['n']:>8,} notas")

    # Guardar resultados de exploración
    salida_resumen = PATH_SALIDAS / "01_resumen_exploracion.json"
    resumen = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "total_notas": int(total),
        "distribucion_tipos": tipos.to_dict("records"),
        "longitud": {
            "min": int(longitud[0]), "avg": int(longitud[1]),
            "median": int(longitud[2]), "max": int(longitud[3])
        },
        "distribucion_tokens": rangos.to_dict("records"),
    }
    with open(salida_resumen, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    log(f"Resumen guardado en {salida_resumen}")
    log("")

    return resumen


# =============================================================================
# PASO 4 — MUESTRA REPRODUCIBLE PARA DESARROLLO NLP
# =============================================================================

def paso_4_generar_muestra(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Genera una muestra reproducible de N notas (definido por TAMANO_MUESTRA)
    para usarla como corpus de desarrollo en la fase NLP.

    La muestra se guarda en CSV dentro de PATH_SALIDAS, pero ATENCIÓN:
    este CSV contiene datos credentialed bajo DUA y NO debe subirse a
    GitHub público ni redistribuirse.
    """
    log("=" * 70)
    log(f"PASO 4 — Generación de muestra reproducible (n={TAMANO_MUESTRA})")
    log("=" * 70)

    # Sample con semilla fija para que la muestra sea siempre la misma
    muestra = con.execute(f"""
        SELECT subject_id, hadm_id, note_type, charttime, text
        FROM discharge
        USING SAMPLE {TAMANO_MUESTRA} ROWS (reservoir, {SEMILLA_ALEATORIA})
    """).df()

    log(f"Muestra obtenida: {len(muestra)} notas")
    log(f"   Pacientes únicos:        {muestra['subject_id'].nunique()}")
    log(f"   Hospitalizaciones únicas: {muestra['hadm_id'].nunique()}")

    # Guardar muestra (gitignored)
    salida_muestra = PATH_SALIDAS / f"02_muestra_{TAMANO_MUESTRA}_notas.csv"
    muestra.to_csv(salida_muestra, index=False)
    log(f"Muestra guardada en {salida_muestra}")
    log("(IMPORTANTE: este archivo está bajo DUA, NO subirlo a GitHub público)")

    # Preview de la primera nota (para revisión cualitativa)
    log("")
    log(f"Preview de la primera nota ({NOTA_CARACTERES_PREVIEW} caracteres):")
    log("-" * 70)
    print(muestra.iloc[0]["text"][:NOTA_CARACTERES_PREVIEW])
    log("-" * 70)
    log("")

    return muestra


# =============================================================================
# PASO 5 — OPERACIONALIZACIÓN GEMSES (PLACEHOLDER PARA FASE 2)
# =============================================================================

def paso_5_estructura_gemses() -> dict:
    """
    Define la estructura conceptual del cálculo de la Matriz de Priorización
    GEMSES. Las funciones de mapeo concreto (variable proxy → score) se
    implementarán en la Fase 2 del roadmap.

    Fórmula del Impacto (Anexo 03 Directiva GG-ESSALUD-2021):
        G = c·0.40 + d·0.20 + e·0.15 + f·0.25

    Donde:
        c = Tiempo       (Length of Stay vs mediana DRG)
        d = Calidad      (ICD-9/10 complicaciones + NER eventos en notas)
        e = Costos       (DRG weight + procedimientos invasivos)
        f = Satisfacción (Readmisión 30d + AMA discharge)

    Derivadas:
        H = B · G                  (Nivel de Riesgo, B = índice frecuencia)
        I = H / sum(h)             (Índice de Gestión)
        J = I × 100                (Nivel de Gestión final)

    Mapeo a niveles de gestión por percentil:
        P25 (Verde, bajo)    → Servicios
        P50 (Amarillo, medio) → Departamentos
        P75 (Rojo, alto)     → Director del establecimiento
    """
    log("=" * 70)
    log("PASO 5 — Estructura conceptual GEMSES (placeholder Fase 2)")
    log("=" * 70)

    pesos_gemses = {
        "Tiempo (c)":       0.40,
        "Calidad (d)":      0.20,
        "Costos (e)":       0.15,
        "Satisfaccion (f)": 0.25,
    }
    suma = sum(pesos_gemses.values())
    log("Pesos de la Matriz de Priorización GEMSES (Anexo 03 Directiva):")
    for dim, peso in pesos_gemses.items():
        log(f"   {dim:<20s} = {peso:.2f}")
    log(f"   Suma de pesos        = {suma:.2f}  (debe ser 1.00)")
    assert abs(suma - 1.0) < 1e-9, "Los pesos GEMSES NO suman 1.0"

    log("")
    log("Variables proxy en MIMIC-IV (aporte original del autor):")
    proxies = [
        ("Tiempo (c)",      "Length of Stay (LOS) vs mediana del DRG"),
        ("Calidad (d)",     "ICD-9/10 complicaciones + NER eventos en notas"),
        ("Costos (e)",      "DRG weight + procedimientos invasivos adicionales"),
        ("Satisfaccion(f)", "Readmision no planificada 30d + AMA discharge"),
    ]
    for dim, descripcion in proxies:
        log(f"   {dim:<18s} -> {descripcion}")

    log("")
    log("Las funciones de scoring concreto (proxy → puntaje 0-9) se")
    log("implementarán en la Fase 2 del roadmap experimental, tras")
    log("descargar MIMIC-IV principal (módulos hosp + icu).")
    log("")

    return {
        "pesos": pesos_gemses,
        "proxies": dict(proxies),
        "formula_impacto": "G = c*0.40 + d*0.20 + e*0.15 + f*0.25",
        "umbrales_percentil": {"verde": "P25", "amarillo": "P50", "rojo": "P75"},
    }


# =============================================================================
# MAIN — Orquestación de la ejecución completa
# =============================================================================

def main():
    """
    Punto de entrada del script. Ejecuta los 5 pasos en orden y termina con
    un resumen del estado del proyecto.
    """
    log("=" * 70)
    log("INICIO DEL PIPELINE — TESIS GEMSES x MIMIC-IV")
    log(f"Carlos Pérez Pérez | MIA 303 UNI | {datetime.now():%Y-%m-%d %H:%M}")
    log("=" * 70)
    log("")

    # Paso 1 — Entorno
    estado = paso_1_verificar_entorno()
    if not estado["notas_disponible"]:
        log("ABORTANDO: no se encontró discharge.csv.gz", "ERROR")
        log(f"Verifica que la ruta {PATH_NOTAS} contenga los archivos extraidos del ZIP.", "ERROR")
        sys.exit(1)

    # Paso 2 — DuckDB
    con = paso_2_conectar_duckdb()

    # Paso 3 — Exploración
    paso_3_explorar_corpus(con)

    # Paso 4 — Muestra
    paso_4_generar_muestra(con)

    # Paso 5 — Estructura GEMSES (placeholder)
    paso_5_estructura_gemses()

    # Cierre
    con.close()
    log("=" * 70)
    log("PIPELINE COMPLETADO EXITOSAMENTE")
    log(f"Resultados en: {PATH_SALIDAS}")
    log("=" * 70)


if __name__ == "__main__":
    main()
