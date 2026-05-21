# ============================================================
#  PIPELINE NLP + ML CLÁSICO — CLASIFICACIÓN DE TEXTO
#  Autor: Carlos Pérez Pérez | Maestría IA – UNI | 2026
#  Adapta las variables de configuración (sección CONFIG)
#  y ejecuta: python3 pipeline_clasificacion_texto.py
# ============================================================

# ── INSTALACIÓN (ejecutar una vez antes si es necesario) ────
# pip install pandas openpyxl scikit-learn lightgbm matplotlib seaborn

import pandas as pd
import numpy as np
import re
import warnings
import os
import json
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, cohen_kappa_score,
    classification_report, confusion_matrix
)
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')   # cambiar a 'TkAgg' o quitar esta línea para ver las figuras en pantalla
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
#  ██████  CONFIG — MODIFICA AQUÍ SEGÚN TU BASE DE DATOS
# ============================================================

ARCHIVO_EXCEL   = 'Base ERSP Eventos adveersso sodificados.xlsx'   # ruta al Excel (.xlsx o .csv)
COLUMNA_TEXTO   = 'DESCRIPCION OCURRENCIA'   # columna de texto libre (predictor)
COLUMNA_CLASE   = 'EVENTO CLASIFICADO'        # columna objetivo (lo que quieres predecir)
MIN_MUESTRAS    = 20       # clases con menos registros que este número serán descartadas
TEST_SIZE       = 0.20     # proporción del conjunto de prueba (0.20 = 20%)
RANDOM_STATE    = 42       # semilla para reproducibilidad
TFIDF_FEATURES  = 15000    # número máximo de características TF-IDF
TFIDF_NGRAMS    = (1, 2)   # rango de n-gramas (1,2) = unigramas + bigramas
CARPETA_SALIDA  = 'resultados_pipeline'  # carpeta donde se guardarán los resultados

# ============================================================

os.makedirs(CARPETA_SALIDA, exist_ok=True)
print("=" * 60)
print("  PIPELINE NLP + ML | CLASIFICACIÓN DE TEXTO")
print("=" * 60)

# ── 1. CARGA DE DATOS ────────────────────────────────────────
print(f"\n[1] Cargando: {ARCHIVO_EXCEL}")

if ARCHIVO_EXCEL.endswith('.csv'):
    df = pd.read_csv(ARCHIVO_EXCEL, encoding='utf-8-sig')
else:
    df = pd.read_excel(ARCHIVO_EXCEL)

print(f"    Registros totales : {len(df)}")
print(f"    Columnas          : {df.columns.tolist()}")

df = df[[COLUMNA_TEXTO, COLUMNA_CLASE]].dropna()
print(f"    Registros válidos : {len(df)}")

# ── 2. LIMPIEZA Y NORMALIZACIÓN ──────────────────────────────
print("\n[2] Normalizando etiquetas y limpiando texto...")

df[COLUMNA_CLASE] = (df[COLUMNA_CLASE]
                     .str.upper()
                     .str.strip()
                     .str.replace(r'\s+', ' ', regex=True))

conteo_original = df[COLUMNA_CLASE].value_counts()
clases_validas  = conteo_original[conteo_original >= MIN_MUESTRAS].index
df = df[df[COLUMNA_CLASE].isin(clases_validas)].copy()

print(f"    Clases únicas (total original) : {len(conteo_original)}")
print(f"    Clases tras filtro (>={MIN_MUESTRAS} registros): {len(clases_validas)}")
print(f"    Registros tras filtro          : {len(df)}")

def limpiar_texto(texto):
    """
    Preprocesamiento básico para texto clínico en español.
    Adapta esta función según las particularidades de tu corpus.
    """
    texto = str(texto).upper()
    texto = re.sub(r'[¶\n\r\t]+', ' ', texto)            # saltos de línea
    texto = re.sub(r'[^\w\sáéíóúñüÁÉÍÓÚÑÜ]', ' ', texto) # signos de puntuación
    texto = re.sub(r'\d+', ' NUM ', texto)                 # números → token NUM
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

df['texto_limpio'] = df[COLUMNA_TEXTO].apply(limpiar_texto)

# ── 3. CODIFICACIÓN DE ETIQUETAS ─────────────────────────────
le = LabelEncoder()
df['label'] = le.fit_transform(df[COLUMNA_CLASE])
clases_nombres = le.classes_

# ── 4. DIVISIÓN TRAIN / TEST ─────────────────────────────────
print(f"\n[3] Dividiendo dataset: {int((1-TEST_SIZE)*100)}% train / {int(TEST_SIZE*100)}% test...")
X = df['texto_limpio'].values
y = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
print(f"    Entrenamiento : {len(X_train)} registros")
print(f"    Prueba        : {len(X_test)} registros")

# ── 5. VECTORIZACIÓN TF-IDF ──────────────────────────────────
print(f"\n[4] Vectorizando con TF-IDF (max_features={TFIDF_FEATURES}, ngrams={TFIDF_NGRAMS})...")
tfidf = TfidfVectorizer(
    ngram_range=TFIDF_NGRAMS,
    max_features=TFIDF_FEATURES,
    sublinear_tf=True,
    min_df=2
)
X_train_tf = tfidf.fit_transform(X_train)
X_test_tf  = tfidf.transform(X_test)
print(f"    Features generados: {X_train_tf.shape[1]}")

# ── 6. ENTRENAMIENTO Y EVALUACIÓN ────────────────────────────
print("\n[5] Entrenando modelos...")

modelos = {
    'Regresión Logística': LogisticRegression(
        max_iter=1000, C=5, class_weight='balanced', random_state=RANDOM_STATE),
    'SVM Lineal': LinearSVC(
        max_iter=2000, C=1, class_weight='balanced', random_state=RANDOM_STATE),
    'Random Forest': RandomForestClassifier(
        n_estimators=100, max_depth=25, class_weight='balanced',
        random_state=RANDOM_STATE, n_jobs=-1),
    'LightGBM': lgb.LGBMClassifier(
        n_estimators=150, max_depth=7, learning_rate=0.1,
        num_leaves=63, class_weight='balanced',
        random_state=RANDOM_STATE, n_jobs=-1, verbose=-1),
}

resultados = {}
y_preds    = {}

for nombre, modelo in modelos.items():
    print(f"\n  → {nombre}...", end=' ')
    modelo.fit(X_train_tf, y_train)
    y_pred = modelo.predict(X_test_tf)
    y_preds[nombre] = y_pred

    resultados[nombre] = {
        'accuracy'    : round(accuracy_score(y_test, y_pred), 4),
        'f1_weighted' : round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'f1_macro'    : round(f1_score(y_test, y_pred, average='macro',    zero_division=0), 4),
        'kappa'       : round(cohen_kappa_score(y_test, y_pred), 4),
    }
    m = resultados[nombre]
    print(f"Acc={m['accuracy']}  F1_w={m['f1_weighted']}  F1_m={m['f1_macro']}  κ={m['kappa']}")

# Mejor modelo por F1 ponderado
mejor_nombre = max(resultados, key=lambda n: resultados[n]['f1_weighted'])
print(f"\n  ★ Mejor modelo: {mejor_nombre} (F1 ponderado = {resultados[mejor_nombre]['f1_weighted']})")

# ── 7. GUARDAR RESULTADOS EN JSON ────────────────────────────
resumen = {
    'configuracion': {
        'archivo': ARCHIVO_EXCEL,
        'columna_texto': COLUMNA_TEXTO,
        'columna_clase': COLUMNA_CLASE,
        'n_total': int(len(df)),
        'n_train': int(len(X_train)),
        'n_test' : int(len(X_test)),
        'n_clases': int(len(clases_nombres)),
        'tfidf_features': int(X_train_tf.shape[1]),
    },
    'metricas': resultados,
    'mejor_modelo': mejor_nombre,
}
json_path = os.path.join(CARPETA_SALIDA, 'metricas.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)
print(f"\n[6] Métricas guardadas en: {json_path}")

# ── 8. GRÁFICOS ──────────────────────────────────────────────
print("\n[7] Generando gráficos...")
colores = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
nombres = list(resultados.keys())

# Figura 1 – Comparación de métricas
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle(f'Comparación de Modelos ML\n{COLUMNA_CLASE} | n={len(df)} | {len(clases_nombres)} clases',
             fontsize=12, fontweight='bold')
metricas = ['accuracy', 'f1_weighted', 'f1_macro']
titulos  = ['Accuracy', 'F1 Ponderado', 'F1 Macro']
for ax, met, tit in zip(axes, metricas, titulos):
    vals = [resultados[n][met] for n in nombres]
    bars = ax.bar(range(len(nombres)), vals, color=colores, edgecolor='white', width=0.6)
    ax.set_title(tit, fontsize=11, fontweight='bold')
    ax.set_xticks(range(len(nombres)))
    ax.set_xticklabels([n.replace(' ', '\n') for n in nombres], fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Score')
    ax.grid(axis='y', alpha=0.3)
    ax.spines[['top', 'right']].set_visible(False)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_SALIDA, 'fig1_comparacion_metricas.png'), dpi=150, bbox_inches='tight')
plt.close()

# Figura 2 – Kappa de Cohen
fig, ax = plt.subplots(figsize=(9, 5))
kappas = [resultados[n]['kappa'] for n in nombres]
bars = ax.bar(nombres, kappas, color=colores, edgecolor='white', width=0.5)
ax.axhline(0.6, color='red',   linestyle='--', lw=1.8, label='Umbral sustancial (κ=0.60)')
ax.axhline(0.8, color='green', linestyle='--', lw=1.8, label='Acuerdo fuerte (κ=0.80)')
ax.set_title('Kappa de Cohen por Modelo', fontsize=12, fontweight='bold')
ax.set_ylabel('Kappa de Cohen (κ)')
ax.set_ylim(0, 1.0)
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
for bar, val in zip(bars, kappas):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_SALIDA, 'fig2_kappa_cohen.png'), dpi=150, bbox_inches='tight')
plt.close()

# Figura 3 – Distribución de clases (Top 15)
fig, ax = plt.subplots(figsize=(12, 7))
top_n = min(15, len(clases_validas))
top_clases = conteo_original[clases_validas].head(top_n)
labels_short = [c[:50] + '…' if len(c) > 50 else c for c in top_clases.index]
bars = ax.barh(range(len(top_clases)), top_clases.values, color='#2196F3', alpha=0.85)
ax.set_yticks(range(len(top_clases)))
ax.set_yticklabels(labels_short, fontsize=8)
ax.invert_yaxis()
ax.set_xlabel('Número de registros')
ax.set_title(f'Top {top_n} clases más frecuentes – {COLUMNA_CLASE}', fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
for bar, val in zip(bars, top_clases.values):
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_SALIDA, 'fig3_distribucion_clases.png'), dpi=150, bbox_inches='tight')
plt.close()

# Figura 4 – Matriz de confusión del mejor modelo (Top 12 clases)
y_pred_mejor = y_preds[mejor_nombre]
n_top = min(12, len(clases_nombres))
top_idx = np.argsort(np.bincount(y_test))[-n_top:][::-1]
mask = np.isin(y_test, top_idx)
cm = confusion_matrix(y_test[mask], y_pred_mejor[mask], labels=top_idx)
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
labels_cm = [clases_nombres[i][:30] + '…' if len(clases_nombres[i]) > 30
             else clases_nombres[i] for i in top_idx]
fig, ax = plt.subplots(figsize=(13, 10))
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=labels_cm, yticklabels=labels_cm,
            ax=ax, linewidths=0.5, vmin=0, vmax=1)
ax.set_title(f'Matriz de Confusión Normalizada – {mejor_nombre} (Top {n_top} clases)',
             fontsize=12, fontweight='bold')
ax.set_xlabel('Predicción')
ax.set_ylabel('Real')
plt.xticks(rotation=45, ha='right', fontsize=7)
plt.yticks(rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_SALIDA, 'fig4_confusion_matrix.png'), dpi=150, bbox_inches='tight')
plt.close()

# Figura 5 – Precisión / Recall / F1 por clase (Top 15)
report = classification_report(y_test, y_pred_mejor, target_names=clases_nombres,
                                output_dict=True, zero_division=0)
rep_df = pd.DataFrame(report).T.iloc[:-3]
rep_df = rep_df[rep_df['support'] >= 5].sort_values('f1-score', ascending=False).head(15)
x = np.arange(len(rep_df))
w = 0.25
fig, ax = plt.subplots(figsize=(13, 6))
ax.bar(x - w, rep_df['precision'], w, label='Precisión', color='#2196F3', alpha=0.85)
ax.bar(x,     rep_df['recall'],    w, label='Recall',    color='#4CAF50', alpha=0.85)
ax.bar(x + w, rep_df['f1-score'],  w, label='F1-Score',  color='#FF9800', alpha=0.85)
ax.set_xticks(x)
sn = [n[:35] + '…' if len(n) > 35 else n for n in rep_df.index]
ax.set_xticklabels(sn, rotation=45, ha='right', fontsize=7)
ax.set_ylim(0, 1.15)
ax.set_title(f'Precisión / Recall / F1 por Clase – {mejor_nombre} (Top 15 por F1)',
             fontsize=11, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(CARPETA_SALIDA, 'fig5_por_clase.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f"    Gráficos guardados en: {CARPETA_SALIDA}/")

# ── 9. REPORTE FINAL EN CONSOLA ──────────────────────────────
print("\n" + "=" * 60)
print("  RESUMEN FINAL")
print("=" * 60)
print(f"  Dataset : {ARCHIVO_EXCEL}")
print(f"  Texto   : {COLUMNA_TEXTO}")
print(f"  Clase   : {COLUMNA_CLASE}")
print(f"  Registros usados : {len(df)}  |  Clases : {len(clases_nombres)}")
print(f"  Features TF-IDF  : {X_train_tf.shape[1]}")
print()
print(f"  {'Modelo':<25} {'Accuracy':>10} {'F1_w':>10} {'F1_m':>10} {'Kappa':>10}")
print(f"  {'-'*65}")
for n in nombres:
    m = resultados[n]
    tag = ' ★' if n == mejor_nombre else ''
    print(f"  {n:<25} {m['accuracy']:>10.4f} {m['f1_weighted']:>10.4f} {m['f1_macro']:>10.4f} {m['kappa']:>10.4f}{tag}")
print("=" * 60)
print(f"\n✅ Pipeline completado. Resultados en: ./{CARPETA_SALIDA}/")
