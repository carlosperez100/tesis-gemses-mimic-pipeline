"""
Análisis de Estancia Hospitalaria y Flujo de Pacientes
Dataset: K-MIMIC-MEDS (SYN-ICU)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np

# Cargar datos
df = pd.read_parquet('0.parquet')

print("=" * 70)
print("  ANÁLISIS DE ESTANCIA Y FLUJO DE PACIENTES - SYN-ICU")
print("=" * 70)

# ============================================================
# 1. ESTANCIA HOSPITALARIA
# ============================================================
print("\n" + "=" * 70)
print("  1. ESTANCIA HOSPITALARIA")
print("=" * 70)

# Admisiones hospitalarias
hosp_adm = df[df['code'].str.startswith('HOSPITAL_ADMISSION')].copy()
hosp_dis = df[df['code'].str.startswith('HOSPITAL_DISCHARGE')].copy()

print(f"\nTotal eventos de admisión hospitalaria: {len(hosp_adm)}")
print(f"Total eventos de alta hospitalaria:     {len(hosp_dis)}")

# Calcular estancia por paciente (diferencia entre última alta y primera admisión)
estancias = []
for pid in df['subject_id'].unique():
    p_adm = hosp_adm[hosp_adm['subject_id'] == pid]['time'].dropna()
    p_dis = hosp_dis[hosp_dis['subject_id'] == pid]['time'].dropna()
    
    if len(p_adm) > 0 and len(p_dis) > 0:
        # Para cada admisión, buscar el alta más cercana posterior
        for adm_time in p_adm:
            altas_post = p_dis[p_dis > adm_time]
            if len(altas_post) > 0:
                alta_time = altas_post.min()
                dias = (alta_time - adm_time).total_seconds() / 86400
                estancias.append({
                    'subject_id': pid,
                    'fecha_ingreso': adm_time,
                    'fecha_alta': alta_time,
                    'dias_estancia': dias
                })

df_estancia = pd.DataFrame(estancias)

if len(df_estancia) > 0:
    print(f"\nEstancias hospitalarias calculadas: {len(df_estancia)}")
    print(f"\n--- Estadísticas de estancia (días) ---")
    stats = df_estancia['dias_estancia'].describe()
    print(f"  Media:    {stats['mean']:.1f} días")
    print(f"  Mediana:  {stats['50%']:.1f} días")
    print(f"  Mínimo:   {stats['min']:.1f} días")
    print(f"  Máximo:   {stats['max']:.1f} días")
    print(f"  Desv.Std: {stats['std']:.1f} días")
    print(f"  Q25:      {stats['25%']:.1f} días")
    print(f"  Q75:      {stats['75%']:.1f} días")
    
    # Distribución por rangos
    print(f"\n--- Distribución por rango de estancia ---")
    bins = [0, 1, 3, 7, 14, 30, 60, float('inf')]
    labels = ['<1 día', '1-3 días', '3-7 días', '7-14 días', '14-30 días', '30-60 días', '>60 días']
    df_estancia['rango'] = pd.cut(df_estancia['dias_estancia'], bins=bins, labels=labels, right=False)
    dist = df_estancia['rango'].value_counts().sort_index()
    for rango, count in dist.items():
        pct = count / len(df_estancia) * 100
        bar = '█' * int(pct / 2)
        print(f"  {rango:>12s}: {count:3d} ({pct:5.1f}%) {bar}")

# ============================================================
# 2. ESTANCIA EN UCI
# ============================================================
print("\n" + "=" * 70)
print("  2. ESTANCIA EN UCI")
print("=" * 70)

icu_adm = df[df['code'].str.startswith('ICU_ADMISSION')].copy()
icu_dis = df[df['code'].str.startswith('ICU_DISCHARGE')].copy()

print(f"\nTotal eventos de ingreso UCI: {len(icu_adm)}")
print(f"Total eventos de alta UCI:    {len(icu_dis)}")

# Tipos de UCI
print(f"\n--- Ingresos por tipo de UCI ---")
icu_tipos = icu_adm['code'].str.replace('ICU_ADMISSION//', '').value_counts()
for tipo, count in icu_tipos.items():
    pct = count / len(icu_adm) * 100
    bar = '█' * int(pct / 2)
    print(f"  {tipo:>8s}: {count:3d} ({pct:5.1f}%) {bar}")

# Estancia UCI por paciente
estancias_uci = []
for pid in df['subject_id'].unique():
    p_icu_adm = icu_adm[icu_adm['subject_id'] == pid].sort_values('time')
    p_icu_dis = icu_dis[icu_dis['subject_id'] == pid].sort_values('time')
    
    if len(p_icu_adm) > 0 and len(p_icu_dis) > 0:
        for _, adm_row in p_icu_adm.iterrows():
            adm_time = adm_row['time']
            tipo_uci = adm_row['code'].replace('ICU_ADMISSION//', '')
            altas_post = p_icu_dis[p_icu_dis['time'] > adm_time]
            if len(altas_post) > 0:
                alta_time = altas_post.iloc[0]['time']
                dias = (alta_time - adm_time).total_seconds() / 86400
                estancias_uci.append({
                    'subject_id': pid,
                    'tipo_uci': tipo_uci,
                    'fecha_ingreso_uci': adm_time,
                    'fecha_alta_uci': alta_time,
                    'dias_estancia_uci': dias
                })

df_estancia_uci = pd.DataFrame(estancias_uci)

if len(df_estancia_uci) > 0:
    print(f"\nEstancias UCI calculadas: {len(df_estancia_uci)}")
    stats_uci = df_estancia_uci['dias_estancia_uci'].describe()
    print(f"\n--- Estadísticas de estancia UCI (días) ---")
    print(f"  Media:    {stats_uci['mean']:.1f} días")
    print(f"  Mediana:  {stats_uci['50%']:.1f} días")
    print(f"  Mínimo:   {stats_uci['min']:.1f} días")
    print(f"  Máximo:   {stats_uci['max']:.1f} días")
    print(f"  Desv.Std: {stats_uci['std']:.1f} días")
    
    # Estancia UCI por tipo
    print(f"\n--- Estancia promedio por tipo de UCI (días) ---")
    por_tipo = df_estancia_uci.groupby('tipo_uci')['dias_estancia_uci'].agg(['mean', 'median', 'count'])
    por_tipo.columns = ['Media', 'Mediana', 'N']
    por_tipo = por_tipo.sort_values('N', ascending=False)
    for tipo, row in por_tipo.iterrows():
        print(f"  {tipo:>8s}: Media={row['Media']:6.1f}  Mediana={row['Mediana']:6.1f}  (n={int(row['N'])})")

# ============================================================
# 3. FLUJO DE PACIENTES
# ============================================================
print("\n" + "=" * 70)
print("  3. FLUJO DE PACIENTES")
print("=" * 70)

# Origen de admisión
print(f"\n--- Origen de admisión hospitalaria ---")
origen = hosp_adm['code'].str.replace('HOSPITAL_ADMISSION//', '').value_counts()
for tipo, count in origen.items():
    pct = count / len(hosp_adm) * 100
    bar = '█' * int(pct / 2)
    print(f"  {tipo:>25s}: {count:3d} ({pct:5.1f}%) {bar}")

# Destino al alta
print(f"\n--- Destino al alta hospitalaria ---")
destino = hosp_dis['code'].str.replace('HOSPITAL_DISCHARGE//', '').value_counts()
for tipo, count in destino.items():
    pct = count / len(hosp_dis) * 100
    bar = '█' * int(pct / 2)
    print(f"  {tipo:>20s}: {count:3d} ({pct:5.1f}%) {bar}")

# Mortalidad
muertes = df[df['code'] == 'MEDS_DEATH']
total_pacientes = df['subject_id'].nunique()
fallecidos = muertes['subject_id'].nunique()
print(f"\n--- Mortalidad ---")
print(f"  Total pacientes:  {total_pacientes}")
print(f"  Fallecidos:       {fallecidos} ({fallecidos/total_pacientes*100:.1f}%)")
print(f"  Sobrevivientes:   {total_pacientes - fallecidos} ({(total_pacientes-fallecidos)/total_pacientes*100:.1f}%)")

# Paso por urgencias
ed_reg = df[df['code'] == 'ED_REGISTRATION']
ed_out = df[df['code'] == 'ED_OUT']
print(f"\n--- Urgencias (ED) ---")
print(f"  Registros en urgencias:  {len(ed_reg)} (de {ed_reg['subject_id'].nunique()} pacientes)")
print(f"  Salidas de urgencias:    {len(ed_out)}")

# Flujo: Urgencias -> UCI
pacientes_ed = set(ed_reg['subject_id'].unique())
pacientes_uci = set(icu_adm['subject_id'].unique())
ed_a_uci = pacientes_ed & pacientes_uci
print(f"  Pacientes ED → UCI:      {len(ed_a_uci)} ({len(ed_a_uci)/len(pacientes_ed)*100:.1f}% de los de ED)" if pacientes_ed else "  Sin datos de ED")

# ============================================================
# 4. DEMOGRAFÍA
# ============================================================
print("\n" + "=" * 70)
print("  4. DEMOGRAFÍA DE PACIENTES")
print("=" * 70)

# Género
genero = df[df['code'].str.startswith('GENDER')].drop_duplicates('subject_id')
print(f"\n--- Distribución por sexo ---")
gen_dist = genero['code'].str.replace('GENDER//', '').value_counts()
for g, count in gen_dist.items():
    nombre = 'Masculino' if g == 'M' else 'Femenino'
    pct = count / len(genero) * 100
    bar = '█' * int(pct / 2)
    print(f"  {nombre:>10s}: {count:3d} ({pct:5.1f}%) {bar}")

# Estado civil
civil = df[df['code'].str.startswith('MARITAL_STATUS')].drop_duplicates('subject_id')
print(f"\n--- Estado civil ---")
civ_dist = civil['code'].str.replace('MARITAL_STATUS//', '').value_counts()
trad = {'married': 'Casado/a', 'single': 'Soltero/a', 'unclassifiable': 'No clasificado'}
for c, count in civ_dist.items():
    nombre = trad.get(c, c)
    pct = count / len(civil) * 100
    bar = '█' * int(pct / 2)
    print(f"  {nombre:>15s}: {count:3d} ({pct:5.1f}%) {bar}")

# Seguro médico
seguro = df[df['code'].str.startswith('INSURANCE')].drop_duplicates('subject_id')
print(f"\n--- Seguro médico ---")
seg_dist = seguro['code'].str.replace('INSURANCE//', '').value_counts()
for s, count in seg_dist.items():
    pct = count / len(seguro) * 100
    bar = '█' * int(pct / 2)
    print(f"  {s:>40s}: {count:3d} ({pct:5.1f}%) {bar}")

# ============================================================
# 5. RESUMEN DE FLUJO (DIAGRAMA TEXTUAL)
# ============================================================
print("\n" + "=" * 70)
print("  5. RESUMEN DEL FLUJO DE PACIENTES")
print("=" * 70)

n_total = total_pacientes
n_ed = len(pacientes_ed)
n_uci = len(pacientes_uci)
n_ed_uci = len(ed_a_uci)
n_died = fallecidos
n_home = len(hosp_dis[hosp_dis['code'] == 'HOSPITAL_DISCHARGE//Home']['subject_id'].unique())
n_other = len(hosp_dis[hosp_dis['code'] == 'HOSPITAL_DISCHARGE//Other hospital']['subject_id'].unique())

print(f"""
  ┌─────────────────────┐
  │  PACIENTES TOTALES  │
  │       {n_total:>4d}          │
  └─────────┬───────────┘
            │
     ┌──────┴──────┐
     │             │
  ┌──▼──┐    ┌────▼────────────────┐
  │ ED  │    │ Admisión directa    │
  │{n_ed:>4d} │    │    {n_total - n_ed:>4d}               │
  └──┬──┘    └────┬────────────────┘
     │            │
     └──────┬─────┘
            │
     ┌──────▼──────┐
     │    UCI      │
     │   {n_uci:>4d}      │
     └──────┬──────┘
            │
  ┌─────────┼──────────┐
  │         │          │
┌─▼──┐  ┌──▼──┐  ┌───▼────────┐
│Casa│  │Muere│  │Otro Hosp.  │
│{n_home:>4d}│  │ {n_died:>3d} │  │   {n_other:>4d}      │
└────┘  └─────┘  └────────────┘
""")

print("=" * 70)
print("  FIN DEL ANÁLISIS")
print("=" * 70)
