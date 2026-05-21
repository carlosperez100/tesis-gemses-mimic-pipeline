"""
Identificación y Estadística de Eventos Adversos
Dataset: K-MIMIC-MEDS (SYN-ICU)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

df = pd.read_parquet('0.parquet')

print("=" * 70)
print("  IDENTIFICACIÓN DE EVENTOS ADVERSOS - SYN-ICU")
print("=" * 70)

# Mapeo de códigos a nombres legibles
CODE_MAP = {
    'CHARTEVENT//001C_1003_24480//%': 'SpO2',
    'CHARTEVENT//001C_1012_24795//mmHg': 'SBP',
    'CHARTEVENT//001C_1013_25640//mmHg': 'DBP',
    'CHARTEVENT//001C_1014_27095//mmHg': 'MAP_NI',
    'CHARTEVENT//001C_1015_24795//mmHg': 'ASBP',
    'CHARTEVENT//001C_1016_25640//mmHg': 'ADBP',
    'CHARTEVENT//001C_1017_27095//mmHg': 'MAP_A',
    'CHARTEVENT//001C_1021_25105///min': 'HR',
    'CHARTEVENT//001C_1023_27310///min': 'RR',
    'CHARTEVENT//001C_1026_26520//Cel': 'Temp',
    'CHARTEVENT//001C_1187_20765': 'GCS_Eye',
    'CHARTEVENT//001C_1187_20770': 'GCS_Motor',
    'CHARTEVENT//001C_1187_20775': 'GCS_Verbal',
    'CHARTEVENT//001C_1894_20720//%': 'FiO2',
    'CHARTEVENT//001C_1567_21330//cmH2O': 'PEEP',
}

# ============================================================
# 1. EVENTOS ADVERSOS POR SIGNOS VITALES
# ============================================================
print("\n" + "=" * 70)
print("  1. EVENTOS ADVERSOS - SIGNOS VITALES FUERA DE RANGO")
print("=" * 70)

# Umbrales clínicos (referencia: guías de cuidados críticos)
UMBRALES = {
    'SpO2':      {'code': 'CHARTEVENT//001C_1003_24480//%',      'bajo': 90,   'alto': None,  'desc': 'Hipoxemia (SpO2 < 90%)'},
    'SBP_hipo':  {'code': 'CHARTEVENT//001C_1012_24795//mmHg',   'bajo': 90,   'alto': None,  'desc': 'Hipotensión sistólica (SBP < 90 mmHg)'},
    'SBP_hiper': {'code': 'CHARTEVENT//001C_1012_24795//mmHg',   'bajo': None, 'alto': 180,   'desc': 'Crisis hipertensiva (SBP > 180 mmHg)'},
    'HR_bradi':  {'code': 'CHARTEVENT//001C_1021_25105///min',    'bajo': 50,   'alto': None,  'desc': 'Bradicardia (HR < 50 lpm)'},
    'HR_taqui':  {'code': 'CHARTEVENT//001C_1021_25105///min',    'bajo': None, 'alto': 120,   'desc': 'Taquicardia (HR > 120 lpm)'},
    'RR_bajo':   {'code': 'CHARTEVENT//001C_1023_27310///min',    'bajo': 8,    'alto': None,  'desc': 'Bradipnea (RR < 8 rpm)'},
    'RR_alto':   {'code': 'CHARTEVENT//001C_1023_27310///min',    'bajo': None, 'alto': 30,    'desc': 'Taquipnea (RR > 30 rpm)'},
    'Temp_hipo': {'code': 'CHARTEVENT//001C_1026_26520//Cel',     'bajo': 36.0, 'alto': None,  'desc': 'Hipotermia (T < 36°C)'},
    'Temp_hiper':{'code': 'CHARTEVENT//001C_1026_26520//Cel',     'bajo': None, 'alto': 38.3,  'desc': 'Fiebre (T > 38.3°C)'},
    'MAP_bajo':  {'code': 'CHARTEVENT//001C_1014_27095//mmHg',    'bajo': 65,   'alto': None,  'desc': 'MAP baja (< 65 mmHg) - shock'},
}

resultados_vitales = []
total_pac = df['subject_id'].nunique()

for nombre, cfg in UMBRALES.items():
    subset = df[df['code'] == cfg['code']].dropna(subset=['numeric_value'])
    if len(subset) == 0:
        continue
    if cfg['bajo'] is not None:
        eventos = subset[subset['numeric_value'] < cfg['bajo']]
    else:
        eventos = subset[subset['numeric_value'] > cfg['alto']]
    
    n_eventos = len(eventos)
    n_pac = eventos['subject_id'].nunique()
    resultados_vitales.append({
        'Evento': cfg['desc'],
        'N_episodios': n_eventos,
        'N_pacientes': n_pac,
        'Pct_pacientes': round(n_pac / total_pac * 100, 1),
        'Valor_medio': round(eventos['numeric_value'].mean(), 1) if n_eventos > 0 else None,
        'Valor_min': round(eventos['numeric_value'].min(), 1) if n_eventos > 0 else None,
        'Valor_max': round(eventos['numeric_value'].max(), 1) if n_eventos > 0 else None,
    })

df_vitales = pd.DataFrame(resultados_vitales).sort_values('N_pacientes', ascending=False)
print(f"\nTotal pacientes en dataset: {total_pac}")
print(f"\n{'Evento Adverso':<40s} {'Episodios':>9s} {'Pac.':>5s} {'%Pac':>6s} {'Media':>7s} {'Min':>7s} {'Max':>7s}")
print("-" * 85)
for _, r in df_vitales.iterrows():
    print(f"{r['Evento']:<40s} {r['N_episodios']:>9d} {r['N_pacientes']:>5d} {r['Pct_pacientes']:>5.1f}% {r['Valor_medio']:>7.1f} {r['Valor_min']:>7.1f} {r['Valor_max']:>7.1f}")

# ============================================================
# 2. EVENTOS ADVERSOS - LABORATORIO
# ============================================================
print("\n" + "=" * 70)
print("  2. EVENTOS ADVERSOS - LABORATORIO CRÍTICO")
print("=" * 70)

LAB_UMBRALES = {
    'Lactato':     {'code': 'LAB//001L3077//mmol/L',  'bajo': None, 'alto': 2.0,   'desc': 'Hiperlactatemia (> 2 mmol/L)'},
    'Creatinina':  {'code': 'LAB//001L3006//mg/dL',   'bajo': None, 'alto': 2.0,   'desc': 'Falla renal (Creat > 2 mg/dL)'},
    'K_hiper':     {'code': 'LAB//001L3044//mmol/L',  'bajo': None, 'alto': 5.5,   'desc': 'Hiperkalemia (K > 5.5 mmol/L)'},
    'K_hipo':      {'code': 'LAB//001L3044//mmol/L',  'bajo': 3.0,  'alto': None,  'desc': 'Hipokalemia (K < 3.0 mmol/L)'},
    'Na_hiper':    {'code': 'LAB//001L3043//mmol/L',  'bajo': None, 'alto': 150,   'desc': 'Hipernatremia (Na > 150 mmol/L)'},
    'Na_hipo':     {'code': 'LAB//001L3043//mmol/L',  'bajo': 130,  'alto': None,  'desc': 'Hiponatremia (Na < 130 mmol/L)'},
    'Hb_baja':     {'code': 'LAB//001L2003//g/dL',    'bajo': 7.0,  'alto': None,  'desc': 'Anemia severa (Hb < 7 g/dL)'},
    'Plaquetas':   {'code': 'LAB//001L2009//x10e3/uL','bajo': 50,   'alto': None,  'desc': 'Trombocitopenia (Plaq < 50k)'},
    'INR_alto':    {'code': 'LAB//001L22031//INR',     'bajo': None, 'alto': 2.0,   'desc': 'Coagulopatía (INR > 2.0)'},
    'BUN':         {'code': 'LAB//001L3005//mg/dL',    'bajo': None, 'alto': 40,    'desc': 'Azoemia (BUN > 40 mg/dL)'},
    'Bilirrubina': {'code': 'LAB//001L3011//mg/dL',    'bajo': None, 'alto': 2.0,   'desc': 'Hiperbilirrubinemia (> 2 mg/dL)'},
    'ALT':         {'code': 'LAB//001L3014//IU/L',     'bajo': None, 'alto': 200,   'desc': 'Daño hepático (ALT > 200 IU/L)'},
    'pH_bajo':     {'code': 'LAB//001L30821',          'bajo': 7.30, 'alto': None,  'desc': 'Acidosis (pH < 7.30)'},
    'pH_alto':     {'code': 'LAB//001L30821',          'bajo': None, 'alto': 7.50,  'desc': 'Alcalosis (pH > 7.50)'},
    'pCO2_alto':   {'code': 'LAB//001L30823//mmHg',    'bajo': None, 'alto': 50,    'desc': 'Hipercapnia (pCO2 > 50 mmHg)'},
    'pO2_bajo':    {'code': 'LAB//001L30822//mmHg',    'bajo': 60,   'alto': None,  'desc': 'Hipoxemia arterial (pO2 < 60)'},
    'Glucosa':     {'code': 'LAB//001L3041//mg/dL',    'bajo': None, 'alto': 200,   'desc': 'Hiperglicemia (Glu > 200 mg/dL)'},
    'Gluc_baja':   {'code': 'LAB//001L3041//mg/dL',    'bajo': 70,   'alto': None,  'desc': 'Hipoglicemia (Glu < 70 mg/dL)'},
    'CRP':         {'code': 'LAB//001L3092//mg/dL',    'bajo': None, 'alto': 10,    'desc': 'Inflamación severa (CRP > 10)'},
    'WBC_alto':    {'code': 'LAB//001L2001//x10e3/uL', 'bajo': None, 'alto': 12,    'desc': 'Leucocitosis (WBC > 12k)'},
    'WBC_bajo':    {'code': 'LAB//001L2001//x10e3/uL', 'bajo': 4,    'alto': None,  'desc': 'Leucopenia (WBC < 4k)'},
}

resultados_lab = []
for nombre, cfg in LAB_UMBRALES.items():
    subset = df[df['code'] == cfg['code']].dropna(subset=['numeric_value'])
    if len(subset) == 0:
        continue
    if cfg['bajo'] is not None:
        eventos = subset[subset['numeric_value'] < cfg['bajo']]
    else:
        eventos = subset[subset['numeric_value'] > cfg['alto']]
    
    n_eventos = len(eventos)
    n_pac = eventos['subject_id'].nunique()
    if n_eventos > 0:
        resultados_lab.append({
            'Evento': cfg['desc'],
            'N_episodios': n_eventos,
            'N_pacientes': n_pac,
            'Pct_pacientes': round(n_pac / total_pac * 100, 1),
            'Valor_medio': round(eventos['numeric_value'].mean(), 1),
            'Total_mediciones': len(subset),
            'Tasa_anormal': round(n_eventos / len(subset) * 100, 1),
        })

df_lab = pd.DataFrame(resultados_lab).sort_values('N_pacientes', ascending=False)
print(f"\n{'Evento Adverso':<40s} {'Epis.':>6s} {'Pac.':>5s} {'%Pac':>6s} {'Media':>7s} {'Medic.':>7s} {'%Anorm':>7s}")
print("-" * 85)
for _, r in df_lab.iterrows():
    print(f"{r['Evento']:<40s} {r['N_episodios']:>6d} {r['N_pacientes']:>5d} {r['Pct_pacientes']:>5.1f}% {r['Valor_medio']:>7.1f} {r['Total_mediciones']:>7d} {r['Tasa_anormal']:>6.1f}%")

# ============================================================
# 3. GCS - DETERIORO NEUROLÓGICO
# ============================================================
print("\n" + "=" * 70)
print("  3. DETERIORO NEUROLÓGICO (Glasgow Coma Scale)")
print("=" * 70)

gcs_e = df[df['code'] == 'CHARTEVENT//001C_1187_20765'].dropna(subset=['numeric_value'])
gcs_m = df[df['code'] == 'CHARTEVENT//001C_1187_20770'].dropna(subset=['numeric_value'])
gcs_v = df[df['code'] == 'CHARTEVENT//001C_1187_20775'].dropna(subset=['numeric_value'])

# Calcular GCS total por paciente y tiempo
gcs_all = pd.concat([gcs_e, gcs_m, gcs_v])
gcs_pivot = gcs_all.pivot_table(index=['subject_id', 'time'], columns='code', values='numeric_value', aggfunc='first').reset_index()

if len(gcs_pivot.columns) > 2:
    cols = [c for c in gcs_pivot.columns if 'CHARTEVENT' in str(c)]
    gcs_pivot['GCS_total'] = gcs_pivot[cols].sum(axis=1)
    
    gcs_severo = gcs_pivot[gcs_pivot['GCS_total'] <= 8]
    gcs_moderado = gcs_pivot[(gcs_pivot['GCS_total'] > 8) & (gcs_pivot['GCS_total'] <= 12)]
    gcs_leve = gcs_pivot[gcs_pivot['GCS_total'] > 12]
    
    print(f"\nMediciones totales de GCS: {len(gcs_pivot)}")
    print(f"\n--- Clasificación por severidad ---")
    print(f"  GCS Severo (≤ 8):    {len(gcs_severo):>5d} mediciones, {gcs_severo['subject_id'].nunique():>3d} pacientes ({gcs_severo['subject_id'].nunique()/total_pac*100:.1f}%)")
    print(f"  GCS Moderado (9-12): {len(gcs_moderado):>5d} mediciones, {gcs_moderado['subject_id'].nunique():>3d} pacientes ({gcs_moderado['subject_id'].nunique()/total_pac*100:.1f}%)")
    print(f"  GCS Leve (13-15):    {len(gcs_leve):>5d} mediciones, {gcs_leve['subject_id'].nunique():>3d} pacientes ({gcs_leve['subject_id'].nunique()/total_pac*100:.1f}%)")
    
    print(f"\n--- GCS Total - Estadísticas ---")
    stats = gcs_pivot['GCS_total'].describe()
    print(f"  Media: {stats['mean']:.1f} | Mediana: {stats['50%']:.1f} | Min: {stats['min']:.0f} | Max: {stats['max']:.0f}")

# ============================================================
# 4. MORTALIDAD Y FACTORES ASOCIADOS
# ============================================================
print("\n" + "=" * 70)
print("  4. MORTALIDAD Y FACTORES ASOCIADOS")
print("=" * 70)

muertos = set(df[df['code'] == 'MEDS_DEATH']['subject_id'].unique())
vivos = set(df['subject_id'].unique()) - muertos

print(f"\nFallecidos: {len(muertos)} ({len(muertos)/total_pac*100:.1f}%) | Sobrevivientes: {len(vivos)} ({len(vivos)/total_pac*100:.1f}%)")

# Comparar signos vitales entre vivos y muertos
print(f"\n--- Comparación signos vitales: Fallecidos vs Sobrevivientes ---")
VITALES_COMP = {
    'SpO2 (%)':     'CHARTEVENT//001C_1003_24480//%',
    'SBP (mmHg)':   'CHARTEVENT//001C_1012_24795//mmHg',
    'HR (lpm)':     'CHARTEVENT//001C_1021_25105///min',
    'RR (rpm)':     'CHARTEVENT//001C_1023_27310///min',
    'Temp (°C)':    'CHARTEVENT//001C_1026_26520//Cel',
    'MAP (mmHg)':   'CHARTEVENT//001C_1014_27095//mmHg',
}

print(f"\n{'Variable':<16s} {'Fallecidos':>12s} {'Sobreviv.':>12s} {'Diferencia':>12s}")
print("-" * 55)
for nombre, code in VITALES_COMP.items():
    subset = df[df['code'] == code].dropna(subset=['numeric_value'])
    media_m = subset[subset['subject_id'].isin(muertos)]['numeric_value'].mean()
    media_v = subset[subset['subject_id'].isin(vivos)]['numeric_value'].mean()
    if not np.isnan(media_m) and not np.isnan(media_v):
        diff = media_m - media_v
        print(f"{nombre:<16s} {media_m:>12.1f} {media_v:>12.1f} {diff:>+12.1f}")

# Comparar laboratorio
print(f"\n--- Comparación laboratorio: Fallecidos vs Sobrevivientes ---")
LAB_COMP = {
    'Creatinina':   'LAB//001L3006//mg/dL',
    'BUN':          'LAB//001L3005//mg/dL',
    'Lactato':      'LAB//001L3077//mmol/L',
    'WBC':          'LAB//001L2001//x10e3/uL',
    'Hemoglobina':  'LAB//001L2003//g/dL',
    'Plaquetas':    'LAB//001L2009//x10e3/uL',
    'INR':          'LAB//001L22031//INR',
    'Potasio':      'LAB//001L3044//mmol/L',
    'Sodio':        'LAB//001L3043//mmol/L',
    'Bilirrubina':  'LAB//001L3011//mg/dL',
    'ALT':          'LAB//001L3014//IU/L',
}
print(f"\n{'Variable':<16s} {'Fallecidos':>12s} {'Sobreviv.':>12s} {'Diferencia':>12s}")
print("-" * 55)
for nombre, code in LAB_COMP.items():
    subset = df[df['code'] == code].dropna(subset=['numeric_value'])
    media_m = subset[subset['subject_id'].isin(muertos)]['numeric_value'].mean()
    media_v = subset[subset['subject_id'].isin(vivos)]['numeric_value'].mean()
    if not np.isnan(media_m) and not np.isnan(media_v):
        diff = media_m - media_v
        print(f"{nombre:<16s} {media_m:>12.1f} {media_v:>12.1f} {diff:>+12.1f}")

# ============================================================
# 5. SCORES DE SEVERIDAD ESTIMADOS
# ============================================================
print("\n" + "=" * 70)
print("  5. SCORE DE EVENTOS ADVERSOS POR PACIENTE")
print("=" * 70)

# Contar cuántos tipos de eventos adversos tiene cada paciente
ALL_THRESHOLDS = {**UMBRALES, **LAB_UMBRALES}
paciente_scores = {pid: {'n_tipos': 0, 'n_total': 0, 'tipos': []} for pid in df['subject_id'].unique()}

for nombre, cfg in ALL_THRESHOLDS.items():
    subset = df[df['code'] == cfg['code']].dropna(subset=['numeric_value'])
    if len(subset) == 0:
        continue
    if cfg['bajo'] is not None:
        eventos = subset[subset['numeric_value'] < cfg['bajo']]
    else:
        eventos = subset[subset['numeric_value'] > cfg['alto']]
    
    for pid in eventos['subject_id'].unique():
        n = len(eventos[eventos['subject_id'] == pid])
        paciente_scores[pid]['n_tipos'] += 1
        paciente_scores[pid]['n_total'] += n
        paciente_scores[pid]['tipos'].append(cfg['desc'].split('(')[0].strip())

df_scores = pd.DataFrame([
    {'subject_id': pid, 'n_tipos_EA': v['n_tipos'], 'n_total_EA': v['n_total'],
     'fallecido': pid in muertos}
    for pid, v in paciente_scores.items()
]).sort_values('n_tipos_EA', ascending=False)

print(f"\n--- Distribución de tipos de EA por paciente ---")
bins = [0, 1, 3, 5, 10, 15, 50]
labels = ['0', '1-2', '3-4', '5-9', '10-14', '15+']
df_scores['rango_EA'] = pd.cut(df_scores['n_tipos_EA'], bins=bins, labels=labels, right=False)
dist = df_scores.groupby('rango_EA', observed=True).agg(
    N=('subject_id', 'count'),
    Fallecidos=('fallecido', 'sum')
).reset_index()
for _, r in dist.iterrows():
    mort = r['Fallecidos'] / r['N'] * 100 if r['N'] > 0 else 0
    bar = '█' * int(r['N'] / 2)
    print(f"  {r['rango_EA']:>6s} tipos: {int(r['N']):>4d} pac. | {int(r['Fallecidos']):>2d} fallecidos ({mort:5.1f}%) {bar}")

# Top 10 pacientes con más EA
print(f"\n--- Top 10 pacientes con más tipos de EA ---")
print(f"{'Paciente':<22s} {'Tipos':>6s} {'Total':>6s} {'Falleció':>9s}")
print("-" * 48)
for _, r in df_scores.head(10).iterrows():
    estado = "SÍ ⚠️" if r['fallecido'] else "No"
    print(f"{str(r['subject_id']):<22s} {r['n_tipos_EA']:>6d} {r['n_total_EA']:>6d} {estado:>9s}")

# Correlación EA vs mortalidad
print(f"\n--- EA promedio: Fallecidos vs Sobrevivientes ---")
m_ea = df_scores[df_scores['fallecido']]['n_tipos_EA'].mean()
v_ea = df_scores[~df_scores['fallecido']]['n_tipos_EA'].mean()
m_tot = df_scores[df_scores['fallecido']]['n_total_EA'].mean()
v_tot = df_scores[~df_scores['fallecido']]['n_total_EA'].mean()
print(f"  Fallecidos:     {m_ea:.1f} tipos promedio, {m_tot:.1f} episodios totales")
print(f"  Sobrevivientes: {v_ea:.1f} tipos promedio, {v_tot:.1f} episodios totales")

# ============================================================
# 6. RESUMEN EJECUTIVO
# ============================================================
print("\n" + "=" * 70)
print("  6. RESUMEN EJECUTIVO DE EVENTOS ADVERSOS")
print("=" * 70)

total_ea_vitales = df_vitales['N_episodios'].sum()
total_ea_lab = df_lab['N_episodios'].sum()
pac_con_ea = df_scores[df_scores['n_tipos_EA'] > 0]['subject_id'].nunique()

print(f"""
  ┌─────────────────────────────────────────────────┐
  │           RESUMEN EVENTOS ADVERSOS              │
  ├─────────────────────────────────────────────────┤
  │ Pacientes totales:           {total_pac:>5d}              │
  │ Pacientes con ≥1 EA:         {pac_con_ea:>5d} ({pac_con_ea/total_pac*100:.1f}%)       │
  │ Episodios EA vitales:        {total_ea_vitales:>5d}              │
  │ Episodios EA laboratorio:    {total_ea_lab:>5d}              │
  │ Total episodios EA:          {total_ea_vitales + total_ea_lab:>5d}              │
  │ Mortalidad global:             {len(muertos):>3d} ({len(muertos)/total_pac*100:.1f}%)       │
  └─────────────────────────────────────────────────┘
""")

# Top 5 EA más frecuentes
all_ea = pd.concat([df_vitales, df_lab]).sort_values('N_pacientes', ascending=False)
print("  Top 5 eventos adversos más frecuentes:")
for i, (_, r) in enumerate(all_ea.head(5).iterrows(), 1):
    print(f"    {i}. {r['Evento']} — {r['N_pacientes']} pac. ({r['Pct_pacientes']}%)")

print("\n" + "=" * 70)
print("  FIN DEL ANÁLISIS DE EVENTOS ADVERSOS")
print("=" * 70)
