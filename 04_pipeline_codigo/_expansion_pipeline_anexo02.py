"""
Script de expansión del pipeline de detección de eventos adversos Anexo 02 GEMSES.

Genera:
  1) CSV ampliado: eventos_adversos_icd10_v2.csv (Tier A) — añade columna `tier`
  2) JSON ampliado: mapeo_anexo2_ingles.json (Tier B)

Mantiene los registros existentes (no duplica). Solo añade.

Autor: Pipeline tesis MIA-303 (GEMSES × MIMIC-IV)
"""

import csv
import json
import os
from collections import OrderedDict

# ────────────────────────────────────────────────────────────────────
# RUTAS
# ────────────────────────────────────────────────────────────────────
CSV_PATH = r"C:\MIMIC\tesis\04_pipeline_codigo\eventos_adversos_icd10_v2.csv"
JSON_PATH = r"C:\MIMIC\tesis\notebooks\mapeo_anexo2_ingles.json"

CSV_BACKUP = CSV_PATH.replace(".csv", "_backup_pre_expansion.csv")
JSON_BACKUP = JSON_PATH.replace(".json", "_backup_pre_expansion.json")


# ────────────────────────────────────────────────────────────────────
# TIER A (ICD-10) — Nuevos eventos a añadir
# ────────────────────────────────────────────────────────────────────
# Estructura: (id_naturaleza, id_evento_anexo02, evento_anexo02, codigo_icd10,
#              descripcion_es, descripcion_en, categoria_anexo02_essalud,
#              naturaleza_oms, grupo_gemses, severidad_base, fuente_normativa)
#
# Nota sobre ICD-10-CM: MIMIC-IV usa la variante estadounidense ICD-10-CM
# (no la OMS pura). Se usan códigos estándar reconocidos en ambos sistemas;
# cuando aplica, se anota "CIE-10-CM" en fuente_normativa.

NUEVOS_TIER_A = [
    # ─── COMPORTAMIENTO (10) ───────────────────────────────────────
    (10, 101, "Acoso", "Z65.5", "Exposicion a desastre, guerra u otras hostilidades", "Exposure to disaster war and other hostilities", "Comportamiento", "Comportamiento", "Calidad", "Medio", "CIE-10-CM"),
    (10, 102, "Agresion a objeto inanimado", "F68.1", "Produccion deliberada o simulacion de sintomas (proxy conductual)", "Intentional production or feigning of symptoms", "Comportamiento", "Comportamiento", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (10, 103, "Agresion fisica", "Y09", "Agresion por medios no especificados", "Assault by unspecified means", "Comportamiento", "Comportamiento", "Calidad", "Alto", "CIE-10-CM"),
    (10, 104, "Agresion sexual", "T74.2", "Abuso sexual confirmado", "Sexual abuse confirmed", "Comportamiento", "Comportamiento", "Calidad", "Muy alto", "CIE-10-CM"),
    (10, 105, "Agresion verbal", "F68.1", "Trastorno conductual con agresion verbal (proxy)", "Behavioral disorder with verbal aggression (proxy)", "Comportamiento", "Comportamiento", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (10, 106, "Amenaza de muerte", "Z65.4", "Victima de delito o terrorismo (proxy)", "Victim of crime or terrorism (proxy)", "Comportamiento", "Comportamiento", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (10, 107, "Arriesgado/imprudente", "F68.1", "Trastorno conductual con conducta imprudente (proxy)", "Behavioral disorder with reckless behavior (proxy)", "Comportamiento", "Comportamiento", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (10, 1010, "Discriminacion/prejuicio", "Z60.5", "Objeto de discriminacion y persecucion adversas", "Target of perceived adverse discrimination and persecution", "Comportamiento", "Comportamiento", "Calidad", "Bajo", "CIE-10-CM"),
    (10, 1011, "Incumplidor/obstructivo", "F68.1", "Trastorno conductual con incumplimiento (proxy)", "Behavioral disorder with non-adherence (proxy)", "Comportamiento", "Comportamiento", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (10, 1012, "Problema uso/abuso sustancias", "F19.9", "Trastorno mental por uso de multiples drogas no especificado", "Mental disorder due to multiple drug use unspecified", "Comportamiento", "Comportamiento", "Calidad", "Alto", "CIE-10-CM"),

    # ─── CUIDADO DEL PACIENTE (faltantes) ──────────────────────────
    (20, 203, "Desplazamiento dispositivos invasivos", "T85.69", "Otra complicacion mecanica de dispositivos protesicos internos", "Other mechanical complication of other specified internal prosthetic devices", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Medio", "CIE-10-CM"),
    (20, 204, "Eritema del panal", "L22", "Dermatitis del panal", "Diaper dermatitis", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Bajo", "CIE-10-CM"),
    (20, 208, "Lesion por esparadrapo", "L24.5", "Dermatitis de contacto irritativa por otros productos quimicos", "Irritant contact dermatitis due to other chemical products", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Bajo", "CIE-10-CM"),
    (20, 209, "Lesion ocular", "S05.9", "Lesion del ojo y orbita parte no especificada", "Injury of eye and orbit unspecified", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Medio", "CIE-10-CM"),
    (20, 2010, "Lesion por oximetro de pulso", "L29.9", "Prurito no especificado (proxy por irritacion cutanea)", "Pruritus unspecified (proxy for sensor skin irritation)", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (20, 2012, "Lesiones por prong nasal", "J95.9", "Trastorno respiratorio post-procedimiento no especificado (proxy)", "Postprocedural respiratory disorder unspecified (proxy)", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (20, 2014, "Paciente sin brazalete", "Z53.8", "Procedimiento no realizado por otras razones", "Procedure not carried out for other reasons", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (20, 2020, "Datos erroneos identificacion", "Z53.8", "Procedimiento no realizado por otras razones (proxy ID erronea)", "Procedure not carried out for other reasons (proxy wrong ID)", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (20, 207, "Incumplimiento bioseguridad", "Z77.9", "Otros problemas de salud relacionados con condiciones", "Other contact with and (suspected) exposures hazardous to health", "Cuidado del paciente", "Cuidado del paciente", "Calidad", "Medio", "CIE-10-CM (proxy)"),

    # ─── DIAGNOSTICO ────────────────────────────────────────────────
    (30, 301, "Error en diagnostico", "Y65.8", "Otras imprudencias y accidentes especificados en atencion medica", "Other specified misadventures during medical and surgical care", "Diagnostico", "Diagnostico", "Calidad", "Alto", "CIE-10-CM"),
    (30, 302, "Retraso en diagnostico", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy retraso dx)", "Other specified misadventures during medical care (proxy dx delay)", "Diagnostico", "Diagnostico", "Calidad", "Alto", "CIE-10-CM (proxy)"),

    # ─── DISPOSITIVO MEDICO (faltantes) ─────────────────────────────
    (60, 401, "Averia/mal funcionamiento dispositivo", "Y73", "Dispositivos medicos auxiliares asociados con incidentes adversos", "Gastroenterology and urology devices associated with adverse incidents", "Dispositivo medico", "Dispositivo", "Calidad", "Medio", "CIE-10-CM"),
    (60, 402, "Desplazamiento/conexion incorrecta dispositivo", "T85.628", "Desplazamiento de otros dispositivos internos especificados", "Displacement of other specified internal prosthetic devices", "Dispositivo medico", "Dispositivo", "Calidad", "Medio", "CIE-10-CM"),
    (60, 403, "Error del usuario (dispositivo)", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy error usuario)", "Other specified misadventures (proxy user device error)", "Dispositivo medico", "Dispositivo", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (60, 406, "Plaquetopenia por protesis intracardiaca", "D69.3", "Purpura trombocitopenica idiopatica (proxy plaquetopenia protesis)", "Idiopathic thrombocytopenic purpura (proxy prosthesis thrombocytopenia)", "Dispositivo medico", "Dispositivo", "Calidad", "Alto", "CIE-10-CM (proxy)"),

    # ─── INFECCION ASOCIADA (faltantes) ─────────────────────────────
    (40, 603, "Otras ITU", "N39.0", "Infeccion de vias urinarias sitio no especificado", "Urinary tract infection site not specified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 608, "Neumonia bacterias comunes", "J15.9", "Neumonia bacteriana no especificada", "Unspecified bacterial pneumonia", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 609, "Neumonia inmunocomprometidos", "B44.1", "Otras aspergilosis pulmonares (proxy pneumonia inmunocomprometidos)", "Other pulmonary aspergillosis (proxy immunocompromised pneumonia)", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Muy alto", "CIE-10-CM (proxy)"),
    (40, 6010, "Tracto respiratorio superior", "J06.9", "Infeccion aguda de las vias respiratorias superiores no especificada", "Acute upper respiratory infection unspecified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Bajo", "CIE-10-CM"),
    (40, 6011, "Bronquitis/traqueobronquitis", "J40", "Bronquitis no especificada como aguda o cronica", "Bronchitis not specified as acute or chronic", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6012, "Otras infecciones resp inferior", "J22", "Infeccion aguda no especificada de las vias respiratorias inferiores", "Unspecified acute lower respiratory infection", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6013, "Endometritis", "O86.1", "Otras infecciones genitales consecutivas al parto", "Other infection of genital tract following delivery", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6014, "Infeccion episiotomia", "O86.0", "Infeccion de herida obstetrica", "Infection of obstetric surgical wound", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6015, "Tapon vaginal", "N89.8", "Otros trastornos inflamatorios especificados de la vagina", "Other specified noninflammatory disorders of vagina", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (40, 6016, "Otras infecciones reproductivas", "N76.8", "Otras inflamaciones especificadas de la vagina y vulva", "Other specified inflammation of vagina and vulva", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6018, "Infeccion tracto GI", "K63.9", "Enfermedad del intestino no especificada", "Disease of intestine unspecified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6021, "Enteritis necrotizante", "K55.0", "Trastornos vasculares agudos del intestino", "Acute vascular disorders of intestine (NEC)", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Muy alto", "CIE-10-CM"),
    (40, 6024, "UPP infectada", "L89.95", "Ulcera por presion estadio no especificado infectada (proxy)", "Pressure ulcer of unspecified site stage unspecified (with infection proxy)", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6025, "Infeccion de quemadura", "T79.3", "Infeccion post-traumatica de una herida no clasificada en otra parte", "Posttraumatic wound infection NEC", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6026, "Absceso mama/mastitis", "O91.0", "Infeccion del pezon asociada con el parto", "Infection of nipple associated with pregnancy and the puerperium", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6027, "Onfalitis", "P38", "Onfalitis del recien nacido con o sin hemorragia leve", "Omphalitis of newborn with or without mild hemorrhage", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6028, "Pustulosis infante", "L08.0", "Piodermitis", "Pyoderma", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6031, "Articulacion/bursa", "M00.9", "Artritis piogena no especificada", "Pyogenic arthritis unspecified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6032, "Infeccion espacio discal", "M46.3", "Infeccion del disco intervertebral (piogena)", "Infection of intervertebral disc (pyogenic)", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6034, "Infeccion intracraneana", "G06.0", "Absceso y granuloma intracraneal", "Intracranial abscess and granuloma", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Muy alto", "CIE-10-CM"),
    (40, 6036, "Absceso medula espinal", "G06.1", "Absceso y granuloma intrarraquideo", "Intraspinal abscess and granuloma", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Muy alto", "CIE-10-CM"),
    (40, 6040, "Infeccion arterial/venosa", "I80.1", "Flebitis y tromboflebitis de la vena femoral", "Phlebitis and thrombophlebitis of femoral vein", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6043, "Otitis externa", "H60.3", "Otra otitis externa infecciosa", "Other infective otitis externa", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Bajo", "CIE-10-CM"),
    (40, 6044, "Otitis media", "H66.9", "Otitis media no especificada", "Otitis media unspecified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Bajo", "CIE-10-CM"),
    (40, 6045, "Otitis interna", "H83.0", "Laberintitis", "Labyrinthitis", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6046, "Mastoiditis", "H70.0", "Mastoiditis aguda", "Acute mastoiditis", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Alto", "CIE-10-CM"),
    (40, 6047, "Infeccion cavidad oral", "K12.2", "Celulitis y absceso de boca", "Cellulitis and abscess of mouth", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),
    (40, 6048, "Sinusitis", "J32.9", "Sinusitis cronica no especificada", "Chronic sinusitis unspecified", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Bajo", "CIE-10-CM"),
    (40, 6029, "Circuncision RN", "P96.8", "Otras afecciones especificadas originadas en periodo perinatal", "Other specified conditions originating in the perinatal period", "Infeccion nosocomial", "Infeccion nosocomial", "Calidad", "Medio", "CIE-10-CM"),

    # ─── MEDICACION (faltantes con ICD-10) ──────────────────────────
    (50, 701, "Cantidad erronea medicacion", "T50.905A", "Efecto adverso de otras drogas no especificadas, encuentro inicial", "Adverse effect of other and unspecified drugs initial encounter", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 703, "Contraindicacion medicacion", "T50.905A", "Efecto adverso de drogas no especificadas (proxy contraindicacion)", "Adverse effect of unspecified drugs (proxy contraindication)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 707, "Forma galenica erronea", "T50.905A", "Efecto adverso de drogas no especificadas (proxy forma galenica)", "Adverse effect of unspecified drugs (proxy wrong formulation)", "Medicacion", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (50, 708, "Hemorragia digestiva por medicacion", "K57.9", "Diverticulosis intestinal con hemorragia (proxy GI bleed por farmaco)", "Diverticulosis with hemorrhage (proxy drug-induced GI bleed)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 709, "Hemorragia por antiagregacion", "T45.525A", "Efecto adverso de drogas antitromboticas, encuentro inicial", "Adverse effect of antithrombotic drugs initial encounter", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 7012, "Interaccion farmacos", "T50.905A", "Efecto adverso de drogas no especificadas (proxy interaccion)", "Adverse effect of unspecified drugs (proxy drug interaction)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 7014, "Medicamento erroneo", "T50.905A", "Efecto adverso de drogas no especificadas (proxy medicamento erroneo)", "Adverse effect of unspecified drugs (proxy wrong drug)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 7016, "Omision medicamento", "T50.905A", "Efecto adverso por omision de droga", "Adverse effect from drug omission", "Medicacion", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (50, 7017, "Paciente erroneo medicacion", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy paciente erroneo)", "Other specified misadventures (proxy wrong patient med)", "Medicacion", "Medicacion", "Calidad", "Muy alto", "CIE-10-CM (proxy)"),
    (50, 7018, "Preparacion/dispensacion erronea", "T50.905A", "Efecto adverso de drogas no especificadas (proxy preparacion)", "Adverse effect of unspecified drugs (proxy preparation error)", "Medicacion", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (50, 7019, "Prescripcion erronea", "T50.905A", "Efecto adverso de drogas no especificadas (proxy prescripcion)", "Adverse effect of unspecified drugs (proxy prescribing error)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 7021, "Reaccion adversa medicacion", "T88.7", "Efecto adverso no especificado de droga o medicamento", "Unspecified adverse effect of drug or medicament", "Medicacion", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (50, 7023, "Necrosis por vasoconstrictor", "T63.094A", "Efecto toxico por contacto con otra toxina, encuentro inicial (proxy)", "Toxic effect by contact with venom (proxy vasoconstrictor necrosis)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (50, 7024, "Via erronea", "T50.905A", "Efecto adverso de drogas no especificadas (proxy via erronea)", "Adverse effect of unspecified drugs (proxy wrong route)", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (50, 7026, "Falta de prescripcion", "T50.905A", "Efecto adverso de drogas (proxy falta de prescripcion)", "Adverse effect (proxy missing prescription)", "Medicacion", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (50, 7031, "Diarrea por antimicrobianos", "A04.7", "Enterocolitis debida a Clostridium difficile", "Enterocolitis due to Clostridium difficile", "Medicacion", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),

    # ─── PROCEDIMIENTO (faltantes) ──────────────────────────────────
    (30, 801, "Adherencias tras cirugia", "K66.0", "Adherencias peritoneales (postprocedimiento)", "Peritoneal adhesions (postprocedural)", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 804, "Desplazamiento dispositivo intracardiaco", "T82.01XA", "Desplazamiento de protesis de valvula cardiaca, encuentro inicial", "Displacement of heart valve prosthesis initial encounter", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 806, "Extubacion fallida", "J95.89", "Otras complicaciones post-procedimiento del sistema respiratorio", "Other postprocedural complications of respiratory system", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 807, "Falla del procedimiento", "T81.89XA", "Otras complicaciones de procedimientos, encuentro inicial", "Other complications of procedures NEC initial encounter", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 808, "Hematoma por puncion", "T81.0XXA", "Hemorragia consecutiva a procedimiento, encuentro inicial", "Hemorrhage complicating a procedure initial encounter", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 809, "Hematoma post-cateterismo", "T81.0XXA", "Hemorragia consecutiva a procedimiento (proxy cateterismo)", "Hemorrhage complicating procedure (proxy post-cath)", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8010, "Hematoma intraoperatorio", "T81.0XXA", "Hemorragia consecutiva a procedimiento (proxy intraoperatorio)", "Hemorrhage complicating procedure (proxy intraoperative)", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8011, "Hematoma relacionado procedimiento", "T81.0XXA", "Hemorragia consecutiva a procedimiento (proxy general)", "Hemorrhage complicating procedure (proxy general)", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 8012, "Hematuria post-sondaje", "R31.9", "Hematuria no especificada", "Hematuria unspecified", "Procedimiento", "Procedimiento", "Calidad", "Bajo", "CIE-10-CM"),
    (30, 8013, "Intervencion ineficaz/incompleta", "T81.89XA", "Otras complicaciones de procedimientos (proxy intervencion incompleta)", "Other complications of procedures (proxy incomplete)", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8015, "Lesiones secundarias", "T81.89XA", "Otras complicaciones especificadas de procedimientos", "Other specified complications of procedures", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 8019, "Seroma", "T81.89XA", "Otras complicaciones de procedimientos (proxy seroma)", "Other complications of procedures (proxy seroma)", "Procedimiento", "Procedimiento", "Calidad", "Bajo", "CIE-10-CM"),
    (30, 8022, "Taponamiento cardiaco", "I31.9", "Enfermedad del pericardio no especificada", "Disease of pericardium unspecified", "Procedimiento", "Procedimiento", "Calidad", "Muy alto", "CIE-10-CM"),
    (30, 8024, "Guia retenida en vaso", "T82.818A", "Embolia por dispositivo cardiovascular, encuentro inicial", "Embolism due to cardiac and vascular prosthetic devices initial encounter", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8025, "Hemoglobinuria", "R82.3", "Hemoglobinuria", "Hemoglobinuria", "Procedimiento", "Procedimiento", "Calidad", "Medio", "CIE-10-CM"),
    (30, 8026, "Pseudoaneurisma", "I72.9", "Aneurisma de sitio no especificado", "Aneurysm of unspecified site", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8027, "Fistula arteriovenosa", "Q27.30", "Malformacion arteriovenosa de sitio no especificado", "Arteriovenous malformation site unspecified", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8028, "Derrame pericardico", "I31.3", "Derrame pericardico no inflamatorio", "Pericardial effusion noninflammatory", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8029, "Quilotorax", "J94.0", "Quilotorax", "Chylous effusion", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8030, "Dispositivo ubicacion incorrecta", "T82.898A", "Otras complicaciones de dispositivos cardiacos, encuentro inicial", "Other specified complication of cardiac and vascular prosthetic devices", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8031, "Lesion vascular", "T14.8", "Otras lesiones de region no especificada del cuerpo", "Other injury of unspecified body region", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),
    (30, 8033, "Multiples punciones", "T81.89XA", "Otras complicaciones de procedimientos (proxy multiples punciones)", "Other complications of procedures (proxy multiple sticks)", "Procedimiento", "Procedimiento", "Calidad", "Bajo", "CIE-10-CM"),
    (30, 8034, "Prolongacion CEC", "T81.89XA", "Otras complicaciones de procedimientos (proxy CPB prolongada)", "Other complications of procedures (proxy prolonged CPB)", "Procedimiento", "Procedimiento", "Calidad", "Alto", "CIE-10-CM"),

    # ─── SANGRE/HEMODERIVADOS (faltantes) ───────────────────────────
    (90, 902, "Cantidad erronea sangre", "T80.92XA", "Complicacion no especificada por transfusion, encuentro inicial", "Unspecified complication following transfusion initial encounter", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 905, "Contraindicacion sangre", "T80.92XA", "Complicacion por transfusion (proxy contraindicacion)", "Unspecified complication following transfusion (proxy contraindication)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 906, "Distribucion sangre", "T80.92XA", "Complicacion por transfusion (proxy error distribucion)", "Unspecified complication following transfusion (proxy distribution)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 908, "Hemoderivado erroneo", "T80.0XXA", "Embolia gaseosa por infusion/transfusion (proxy hemoderivado erroneo)", "Air embolism following infusion (proxy wrong blood product)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Muy alto", "CIE-10-CM (proxy)"),
    (90, 909, "Incompatibilidad grupo/factor", "T80.30XA", "Reaccion por incompatibilidad ABO no especificada, inicial", "ABO incompatibility reaction due to transfusion unspecified initial", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Muy alto", "CIE-10-CM"),
    (90, 9010, "Instrucciones dispensacion sangre", "T80.92XA", "Complicacion por transfusion (proxy instrucciones erroneas)", "Unspecified complication following transfusion (proxy wrong instructions)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (90, 9012, "Paciente erroneo sangre", "T80.92XA", "Complicacion por transfusion (proxy paciente erroneo)", "Unspecified complication following transfusion (proxy wrong patient)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Muy alto", "CIE-10-CM"),
    (90, 9013, "Preparacion/dispensacion sangre", "T80.92XA", "Complicacion por transfusion (proxy preparacion)", "Unspecified complication following transfusion (proxy preparation)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (90, 9014, "Prescripcion sangre", "T80.92XA", "Complicacion por transfusion (proxy orden erronea)", "Unspecified complication following transfusion (proxy wrong order)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Medio", "CIE-10-CM"),
    (90, 9016, "Pruebas pretransfusionales", "T80.92XA", "Complicacion por transfusion (proxy pruebas pretransfusionales)", "Unspecified complication following transfusion (proxy pretransfusion testing)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 9017, "Reaccion adversa sangre", "T80.92XA", "Complicacion por transfusion no especificada", "Unspecified complication following transfusion", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 907, "Dosis errónea sangre", "T80.92XA", "Complicacion por transfusion (proxy dosis erronea)", "Unspecified complication following transfusion (proxy wrong dose)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),
    (90, 901, "Administracion sangre", "T80.92XA", "Complicacion por transfusion (proxy error administracion)", "Unspecified complication following transfusion (proxy admin error)", "Sangre/Hemoderivados", "Medicacion", "Calidad", "Alto", "CIE-10-CM"),

    # ─── GESTION ORGANIZACION (detectables) ─────────────────────────
    (100, 1007, "Estancia prolongada", "Z75.1", "Persona en espera de admision en un establecimiento adecuado", "Person awaiting admission to adequate facility elsewhere", "Gestion Organizacion", "Sistema/Organizacion", "Eficiencia", "Bajo", "CIE-10-CM"),
    (100, 1009, "Fallecimiento", "R99", "Otras causas mal definidas y no especificadas de mortalidad", "Ill-defined and unknown cause of mortality", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Muy alto", "CIE-10-CM"),
    (100, 10010, "Retraso o espera del paciente", "Z75.3", "No disponibilidad y no accesibilidad a establecimientos asistenciales", "Unavailability and inaccessibility of health-care facilities", "Gestion Organizacion", "Sistema/Organizacion", "Eficiencia", "Medio", "CIE-10-CM"),
    (100, 10011, "Retraso interconsulta", "Z75.3", "No disponibilidad establecimientos (proxy retraso interconsulta)", "Unavailability of health-care facilities (proxy consult delay)", "Gestion Organizacion", "Sistema/Organizacion", "Eficiencia", "Medio", "CIE-10-CM"),
    (100, 10015, "Comunicacion inefectiva", "Z63.8", "Otros problemas especificados relacionados con grupo primario", "Other specified problems related to primary support group", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (100, 10016, "Error toma de muestra", "Y65.4", "Falla en la introduccion o extraccion de otra canula o instrumento", "Failure in dosage during other surgical and medical care", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (100, 10017, "Falla planificacion cateterismo", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy planificacion cat)", "Other specified misadventures (proxy cath planning)", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (100, 10018, "Retraso examenes", "Z75.3", "No disponibilidad establecimientos (proxy retraso examenes)", "Unavailability of health-care facilities (proxy lab delay)", "Gestion Organizacion", "Sistema/Organizacion", "Eficiencia", "Medio", "CIE-10-CM"),
    (100, 10020, "Prolongacion cirugia", "T81.89XA", "Otras complicaciones de procedimientos (proxy cirugia prolongada)", "Other complications of procedures (proxy prolonged surgery)", "Gestion Organizacion", "Sistema/Organizacion", "Eficiencia", "Medio", "CIE-10-CM"),
    (100, 10013, "Suspension procedimiento paciente invadido", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy suspension)", "Other specified misadventures (proxy procedure suspension)", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (100, 1008, "Falla planificacion cirugia", "Y65.8", "Otras imprudencias y accidentes en atencion (proxy planificacion cx)", "Other specified misadventures (proxy surgery planning)", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (100, 10014, "Robo de ninos", "Y09", "Agresion por medios no especificados (proxy robo de ninos)", "Assault by unspecified means (proxy infant abduction)", "Gestion Organizacion", "Sistema/Organizacion", "Calidad", "Muy alto", "CIE-10-CM (proxy)"),

    # ─── NUTRICION (detectables) ────────────────────────────────────
    (110, 1101, "Cantidad erronea nutricion", "T71.9", "Asfixia, causa no especificada (proxy nutricion erronea)", "Asphyxiation unspecified cause (proxy wrong nutrition amount)", "Nutricion", "Nutricion", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (110, 1103, "Consistencia erronea", "T71.9", "Asfixia, causa no especificada (proxy consistencia erronea)", "Asphyxiation unspecified cause (proxy wrong consistency)", "Nutricion", "Nutricion", "Calidad", "Alto", "CIE-10-CM (proxy)"),
    (110, 1104, "Dieta erronea", "T71.9", "Asfixia, causa no especificada (proxy dieta erronea)", "Asphyxiation unspecified cause (proxy wrong diet)", "Nutricion", "Nutricion", "Calidad", "Medio", "CIE-10-CM (proxy)"),
    (110, 1105, "Frecuencia erronea nutricion", "T71.9", "Asfixia, causa no especificada (proxy frecuencia erronea)", "Asphyxiation unspecified cause (proxy wrong frequency)", "Nutricion", "Nutricion", "Calidad", "Bajo", "CIE-10-CM (proxy)"),
    (110, 1106, "Paciente erroneo nutricion", "T71.9", "Asfixia, causa no especificada (proxy paciente erroneo)", "Asphyxiation unspecified cause (proxy wrong patient diet)", "Nutricion", "Nutricion", "Calidad", "Medio", "CIE-10-CM (proxy)"),
]


# ────────────────────────────────────────────────────────────────────
# TIER B (NLP en INGLÉS) — Nuevos eventos a añadir
# ────────────────────────────────────────────────────────────────────
# Patrones en lenguaje clinico anglosajon real (US-EHR style),
# pensados para discharge summaries de MIMIC-IV.

NUEVOS_TIER_B = [
    # ─── COMPORTAMIENTO ─────────────────────────────────────────────
    {"id_evento": 101, "evento": "Acoso", "naturaleza": "COMPORTAMIENTO", "confianza": "media",
     "patrones_en": ["harassment", "harassing behavior", "patient harassing staff", "harassing other patients", "inappropriate sexual comments", "verbal harassment"]},
    {"id_evento": 102, "evento": "Agresion a objeto inanimado", "naturaleza": "COMPORTAMIENTO", "confianza": "media",
     "patrones_en": ["threw object", "broke equipment", "punched the wall", "damaged property", "threw items", "destroyed personal property"]},
    {"id_evento": 103, "evento": "Agresion fisica", "naturaleza": "COMPORTAMIENTO", "confianza": "media",
     "patrones_en": ["physically aggressive", "assaulted staff", "struck the nurse", "punched staff member", "kicked staff", "physical altercation", "combative behavior", "required restraints for aggression"]},
    {"id_evento": 104, "evento": "Agresion sexual", "naturaleza": "COMPORTAMIENTO", "confianza": "alta",
     "patrones_en": ["sexual assault", "alleged sexual assault", "inappropriate touching", "victim of sexual abuse", "rape kit performed", "SANE exam"]},
    {"id_evento": 105, "evento": "Agresion verbal", "naturaleza": "COMPORTAMIENTO", "confianza": "baja",
     "patrones_en": ["verbally aggressive", "yelling at staff", "verbal outbursts", "shouting at the nurse", "cursing at providers", "verbally abusive"]},
    {"id_evento": 106, "evento": "Amenaza de muerte", "naturaleza": "COMPORTAMIENTO", "confianza": "media",
     "patrones_en": ["death threats", "threatened to kill", "homicidal ideation", "threatening staff", "threats of violence", "HI toward"]},
    {"id_evento": 107, "evento": "Arriesgado/imprudente", "naturaleza": "COMPORTAMIENTO", "confianza": "baja",
     "patrones_en": ["risk-taking behavior", "impulsive behavior", "reckless behavior", "high-risk behavior", "poor impulse control"]},
    {"id_evento": 109, "evento": "Desconsiderado/grosero/hostil", "naturaleza": "COMPORTAMIENTO", "confianza": "baja",
     "patrones_en": ["hostile behavior", "rude to staff", "inappropriate behavior", "disruptive behavior", "agitated and hostile"]},
    {"id_evento": 1011, "evento": "Incumplidor/obstructivo", "naturaleza": "COMPORTAMIENTO", "confianza": "media",
     "patrones_en": ["noncompliant", "non-compliant", "non-adherent", "uncooperative", "refused treatment", "refusing care", "refused medications", "obstructive behavior"]},
    {"id_evento": 1012, "evento": "Problema uso/abuso sustancias", "naturaleza": "COMPORTAMIENTO", "confianza": "alta",
     "patrones_en": ["substance abuse", "substance use disorder", "polysubstance use", "active drug use", "IV drug use", "IVDU", "history of substance abuse", "ongoing substance abuse"]},

    # ─── CUIDADO DEL PACIENTE ───────────────────────────────────────
    {"id_evento": 203, "evento": "Desplazamiento dispositivos invasivos", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "alta",
     "patrones_en": ["line dislodged", "catheter displaced", "PICC dislodged", "drain dislodged", "tube dislodged", "line came out", "catheter pulled out", "dislodgement of"]},
    {"id_evento": 204, "evento": "Eritema del panal", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "alta",
     "patrones_en": ["diaper rash", "diaper dermatitis", "perineal erythema", "perianal erythema", "diaper area irritation"]},
    {"id_evento": 208, "evento": "Lesion por esparadrapo", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "media",
     "patrones_en": ["tape injury", "skin tear from adhesive", "adhesive-related skin injury", "MARSI", "tape blister", "adhesive skin damage"]},
    {"id_evento": 209, "evento": "Lesion ocular", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "media",
     "patrones_en": ["corneal abrasion", "eye injury", "ocular injury", "corneal ulcer", "exposure keratopathy", "iatrogenic eye injury"]},
    {"id_evento": 2010, "evento": "Lesion por oximetro de pulso", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "media",
     "patrones_en": ["pulse ox burn", "pulse oximeter burn", "sensor injury", "finger blister from pulse ox", "skin injury from probe"]},
    {"id_evento": 2012, "evento": "Lesiones por prong nasal", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "media",
     "patrones_en": ["nasal prong injury", "nasal cannula pressure injury", "nares breakdown from cannula", "nasal septum injury from CPAP", "NC-related skin breakdown"]},
    {"id_evento": 2014, "evento": "Paciente sin brazalete", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "alta",
     "patrones_en": ["no ID band", "wristband missing", "patient without identification band", "ID bracelet missing", "no wristband on arrival"]},
    {"id_evento": 207, "evento": "Incumplimiento bioseguridad", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "baja",
     "patrones_en": ["breach of isolation", "isolation precautions not followed", "PPE breach", "isolation violation"]},
    {"id_evento": 2020, "evento": "Datos erroneos identificacion paciente", "naturaleza": "CUIDADO DEL PACIENTE", "confianza": "alta",
     "patrones_en": ["wrong patient identifier", "patient mislabeled", "ID error", "wrong patient labeled", "mislabeled specimen", "patient mix-up"]},

    # ─── DIAGNOSTICO ────────────────────────────────────────────────
    # 301 y 302 ya existen en JSON original; no se duplican.

    # ─── DISPOSITIVO MEDICO ─────────────────────────────────────────
    {"id_evento": 401, "evento": "Averia/mal funcionamiento dispositivo", "naturaleza": "DISPOSITIVO MEDICO", "confianza": "media",
     "patrones_en": ["device malfunction", "equipment failure", "machine not functioning", "device failure", "unable to use due to equipment", "device malfunctioned", "broken device"]},
    {"id_evento": 402, "evento": "Desplazamiento/conexion incorrecta dispositivo", "naturaleza": "DISPOSITIVO MEDICO", "confianza": "alta",
     "patrones_en": ["extravasation", "line displaced", "IV infiltrated", "infiltration of IV", "tubing disconnection", "circuit disconnection", "incorrect connection"]},
    {"id_evento": 403, "evento": "Error del usuario (dispositivo)", "naturaleza": "DISPOSITIVO MEDICO", "confianza": "baja",
     "patrones_en": ["user error", "improper use of device", "operator error", "device used incorrectly"]},
    {"id_evento": 406, "evento": "Plaquetopenia por protesis intracardiaca", "naturaleza": "DISPOSITIVO MEDICO", "confianza": "alta",
     "patrones_en": ["HIT", "heparin-induced thrombocytopenia", "thrombocytopenia after valve", "prosthetic valve thrombocytopenia", "mechanical valve thrombocytopenia"]},
    {"id_evento": 408, "evento": "Sucio/no esteril dispositivo", "naturaleza": "DISPOSITIVO MEDICO", "confianza": "media",
     "patrones_en": ["contaminated device", "nonsterile equipment", "sterility breach", "contamination of equipment"]},

    # ─── HISTORIA CLINICA (solo el evento 505 con NLP) ──────────────
    {"id_evento": 505, "evento": "No cuenta con consentimiento informado", "naturaleza": "HISTORIA CLINICA", "confianza": "media",
     "patrones_en": ["consent not obtained", "consent missing", "unable to obtain consent", "emergent procedure without consent", "verbal consent only"]},

    # ─── INFECCION ASOCIADA (faltantes) ─────────────────────────────
    {"id_evento": 603, "evento": "Otras ITU", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["cystitis", "pyelonephritis", "upper UTI", "complicated UTI", "ascending UTI", "urosepsis"]},
    {"id_evento": 608, "evento": "Neumonia bacterias comunes", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["bacterial pneumonia", "Strep pneumonia", "Staphylococcal pneumonia", "Klebsiella pneumonia", "Pseudomonas pneumonia", "gram-negative pneumonia"]},
    {"id_evento": 609, "evento": "Neumonia inmunocomprometidos", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["PCP", "Pneumocystis pneumonia", "PJP", "opportunistic pneumonia", "fungal pneumonia in immunocompromised", "CMV pneumonitis"]},
    {"id_evento": 6010, "evento": "Tracto respiratorio superior", "naturaleza": "INFECCION ASOCIADA", "confianza": "baja",
     "patrones_en": ["pharyngitis", "laryngitis", "URI", "upper respiratory infection", "rhinitis", "tonsillitis"]},
    {"id_evento": 6011, "evento": "Bronquitis/traqueobronquitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["bronchitis", "tracheobronchitis", "acute bronchitis", "purulent bronchitis"]},
    {"id_evento": 6012, "evento": "Otras infecciones resp inferior", "naturaleza": "INFECCION ASOCIADA", "confianza": "baja",
     "patrones_en": ["lower respiratory infection", "LRTI", "lower respiratory tract infection"]},
    {"id_evento": 6013, "evento": "Endometritis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["endometritis", "postpartum endometritis", "puerperal endometritis", "uterine infection postpartum"]},
    {"id_evento": 6014, "evento": "Infeccion episiotomia", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["episiotomy infection", "infected episiotomy", "perineal wound infection"]},
    {"id_evento": 6015, "evento": "Tapon vaginal", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["vaginal cuff infection", "vaginal cuff cellulitis", "post-hysterectomy cuff infection"]},
    {"id_evento": 6016, "evento": "Otras infecciones reproductivas", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["pelvic infection", "PID", "pelvic inflammatory disease", "tubo-ovarian abscess", "salpingitis"]},
    {"id_evento": 6018, "evento": "Infeccion tracto GI", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["GI infection", "infectious colitis", "bacterial colitis", "Salmonella enteritis", "Shigella infection"]},
    {"id_evento": 6021, "evento": "Enteritis necrotizante", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["necrotizing enterocolitis", "NEC", "neonatal NEC", "necrotizing colitis"]},
    {"id_evento": 6023, "evento": "Infeccion tejido blando", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["soft tissue infection", "cellulitis", "necrotizing fasciitis", "Fournier's gangrene", "abscess of soft tissue"]},
    {"id_evento": 6024, "evento": "UPP infectada", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["infected pressure ulcer", "infected decubitus ulcer", "pressure ulcer with cellulitis", "infected sacral ulcer"]},
    {"id_evento": 6025, "evento": "Infeccion de quemadura", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["burn wound infection", "infected burn", "burn cellulitis"]},
    {"id_evento": 6026, "evento": "Absceso mama/mastitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["mastitis", "breast abscess", "puerperal mastitis", "lactational mastitis"]},
    {"id_evento": 6027, "evento": "Onfalitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["omphalitis", "umbilical infection", "infected umbilical stump"]},
    {"id_evento": 6028, "evento": "Pustulosis infante", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["infant pustulosis", "neonatal pyoderma", "staphylococcal pustulosis"]},
    {"id_evento": 6029, "evento": "Circuncision RN infeccion", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["circumcision infection", "infected circumcision site", "post-circumcision cellulitis"]},
    {"id_evento": 6031, "evento": "Articulacion/bursa", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["septic arthritis", "septic joint", "bursitis infectious", "infected bursa", "pyogenic arthritis"]},
    {"id_evento": 6032, "evento": "Infeccion espacio discal", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["discitis", "disc space infection", "spondylodiscitis"]},
    {"id_evento": 6034, "evento": "Infeccion intracraneana", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["intracranial infection", "brain abscess", "subdural empyema", "epidural abscess intracranial"]},
    {"id_evento": 6036, "evento": "Absceso medula espinal", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["spinal abscess", "epidural abscess spine", "spinal epidural abscess", "intraspinal abscess"]},
    {"id_evento": 6038, "evento": "Miocarditis o pericarditis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["myocarditis", "pericarditis", "infectious pericarditis", "purulent pericarditis", "viral myocarditis"]},
    {"id_evento": 6039, "evento": "Mediastinitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["mediastinitis", "post-sternotomy mediastinitis", "deep sternal wound infection"]},
    {"id_evento": 6040, "evento": "Infeccion arterial/venosa", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["septic thrombophlebitis", "infected thrombus", "vascular graft infection", "infected AV fistula", "Lemierre's syndrome"]},
    {"id_evento": 6041, "evento": "Conjuntivitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["conjunctivitis", "bacterial conjunctivitis", "pink eye", "purulent conjunctivitis"]},
    {"id_evento": 6042, "evento": "Otras infecciones oculares", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["keratitis", "endophthalmitis", "infectious uveitis", "corneal infection", "orbital cellulitis"]},
    {"id_evento": 6043, "evento": "Otitis externa", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["otitis externa", "swimmer's ear", "external ear infection", "malignant otitis externa"]},
    {"id_evento": 6044, "evento": "Otitis media", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["otitis media", "acute otitis media", "AOM", "middle ear infection", "suppurative otitis media"]},
    {"id_evento": 6045, "evento": "Otitis interna", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["labyrinthitis", "inner ear infection", "vestibular neuritis"]},
    {"id_evento": 6046, "evento": "Mastoiditis", "naturaleza": "INFECCION ASOCIADA", "confianza": "alta",
     "patrones_en": ["mastoiditis", "acute mastoiditis"]},
    {"id_evento": 6047, "evento": "Infeccion cavidad oral", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["oral infection", "stomatitis", "Ludwig's angina", "oral cellulitis", "dental abscess"]},
    {"id_evento": 6048, "evento": "Sinusitis", "naturaleza": "INFECCION ASOCIADA", "confianza": "media",
     "patrones_en": ["sinusitis", "acute sinusitis", "bacterial sinusitis", "rhinosinusitis"]},

    # ─── MEDICACION (faltantes) ─────────────────────────────────────
    {"id_evento": 701, "evento": "Cantidad erronea medicacion", "naturaleza": "MEDICACION", "confianza": "media",
     "patrones_en": ["wrong amount", "wrong quantity", "incorrect amount dispensed", "dosing error in volume"]},
    {"id_evento": 703, "evento": "Contraindicacion medicacion", "naturaleza": "MEDICACION", "confianza": "media",
     "patrones_en": ["contraindicated medication", "given despite allergy", "given to patient with known allergy", "contraindication noted", "allergy reaction to medication"]},
    {"id_evento": 706, "evento": "Error de administracion", "naturaleza": "MEDICACION", "confianza": "media",
     "patrones_en": ["medication administration error", "administered in error", "given in error", "med error", "administration mistake"]},
    {"id_evento": 707, "evento": "Forma galenica erronea", "naturaleza": "MEDICACION", "confianza": "baja",
     "patrones_en": ["wrong formulation", "wrong form of medication", "tablet instead of liquid", "incorrect dosage form"]},
    {"id_evento": 7011, "evento": "Informacion/instrucciones dispensacion erroneas", "naturaleza": "MEDICACION", "confianza": "baja",
     "patrones_en": ["wrong instructions", "incorrect dispensing instructions", "patient misinstructed about medication"]},
    {"id_evento": 7016, "evento": "Omision medicamento o dosis", "naturaleza": "MEDICACION", "confianza": "media",
     "patrones_en": ["missed dose", "dose omitted", "medication held in error", "scheduled dose missed", "missed antibiotic dose"]},
    {"id_evento": 7018, "evento": "Preparacion/dispensacion erronea", "naturaleza": "MEDICACION", "confianza": "baja",
     "patrones_en": ["preparation error", "dispensing error", "compounding error", "wrong preparation"]},
    {"id_evento": 7023, "evento": "Necrosis por vasoconstrictor", "naturaleza": "MEDICACION", "confianza": "alta",
     "patrones_en": ["vasopressor extravasation", "vasopressor necrosis", "pressor extravasation", "norepinephrine extravasation", "phenylephrine extravasation with necrosis"]},
    {"id_evento": 7026, "evento": "Falta de prescripcion", "naturaleza": "MEDICACION", "confianza": "baja",
     "patrones_en": ["no prescription", "missing order", "medication not ordered", "no order for"]},

    # ─── PROCEDIMIENTO (faltantes) ──────────────────────────────────
    {"id_evento": 801, "evento": "Adherencias tras cirugia", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["postoperative adhesions", "adhesive small bowel obstruction", "lysis of adhesions", "intra-abdominal adhesions"]},
    {"id_evento": 804, "evento": "Desplazamiento dispositivo intracardiaco", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["lead displacement", "device migration", "pacemaker lead displacement", "ICD lead migration", "lead dislodgement"]},
    {"id_evento": 805, "evento": "Equimosis", "naturaleza": "PROCEDIMIENTO", "confianza": "baja",
     "patrones_en": ["ecchymosis", "bruising at site", "ecchymotic", "site ecchymosis"]},
    {"id_evento": 806, "evento": "Extubacion fallida", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["failed extubation", "reintubated", "required reintubation", "extubation failure", "extubation attempt failed"]},
    {"id_evento": 807, "evento": "Falla del procedimiento", "naturaleza": "PROCEDIMIENTO", "confianza": "media",
     "patrones_en": ["procedure failure", "unsuccessful procedure", "procedure aborted", "unable to complete procedure", "procedure failed"]},
    {"id_evento": 808, "evento": "Hematoma por puncion", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["puncture site hematoma", "access site hematoma", "hematoma at puncture site"]},
    {"id_evento": 809, "evento": "Hematoma post-cateterismo", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["groin hematoma", "femoral hematoma post-cath", "access site hematoma post-cath", "post-catheterization hematoma", "retroperitoneal hematoma post-cath"]},
    {"id_evento": 8010, "evento": "Hematoma intraoperatorio", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["intraoperative hematoma", "postoperative hematoma", "surgical site hematoma", "wound hematoma"]},
    {"id_evento": 8011, "evento": "Hematoma relacionado procedimiento", "naturaleza": "PROCEDIMIENTO", "confianza": "media",
     "patrones_en": ["procedural hematoma", "hematoma following procedure", "post-procedure hematoma"]},
    {"id_evento": 8012, "evento": "Hematuria post-sondaje", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["hematuria after foley", "catheter-induced hematuria", "hematuria post-catheter", "traumatic foley insertion with hematuria"]},
    {"id_evento": 8013, "evento": "Intervencion ineficaz/incompleta", "naturaleza": "PROCEDIMIENTO", "confianza": "media",
     "patrones_en": ["incomplete surgery", "residual lesion after surgery", "incomplete resection", "unsuccessful intervention"]},
    {"id_evento": 8015, "evento": "Lesiones secundarias procedimientos", "naturaleza": "PROCEDIMIENTO", "confianza": "media",
     "patrones_en": ["procedure-related injury", "injury secondary to procedure", "iatrogenic injury during"]},
    {"id_evento": 8019, "evento": "Seroma", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["seroma", "postoperative seroma", "wound seroma", "seroma drainage"]},
    {"id_evento": 8020, "evento": "Tratamiento medico ineficiente o ineficaz", "naturaleza": "PROCEDIMIENTO", "confianza": "baja",
     "patrones_en": ["treatment failure", "ineffective therapy", "failed medical management", "refractory to treatment"]},
    {"id_evento": 8022, "evento": "Taponamiento cardiaco", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["cardiac tamponade", "pericardial tamponade", "tamponade physiology", "required pericardiocentesis for tamponade"]},
    {"id_evento": 8024, "evento": "Guia retenida en vaso", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["retained guidewire", "guidewire left in vessel", "guidewire embolism", "missing guidewire"]},
    {"id_evento": 8025, "evento": "Hemoglobinuria", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["hemoglobinuria", "pigmenturia", "post-transfusion hemoglobinuria"]},
    {"id_evento": 8026, "evento": "Pseudoaneurisma", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["pseudoaneurysm", "femoral pseudoaneurysm", "access site pseudoaneurysm", "iatrogenic pseudoaneurysm"]},
    {"id_evento": 8027, "evento": "Fistula arteriovenosa", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["arteriovenous fistula", "AV fistula", "iatrogenic AV fistula", "post-procedure AV fistula"]},
    {"id_evento": 8028, "evento": "Derrame pericardico", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["pericardial effusion", "new pericardial effusion", "post-procedure pericardial effusion"]},
    {"id_evento": 8029, "evento": "Quilotorax", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["chylothorax", "chylous effusion", "thoracic duct injury"]},
    {"id_evento": 8030, "evento": "Dispositivo ubicacion incorrecta", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["malpositioned device", "malpositioned line", "line malposition", "catheter malposition", "wrongly placed line", "tube malpositioned"]},
    {"id_evento": 8031, "evento": "Lesion vascular", "naturaleza": "PROCEDIMIENTO", "confianza": "alta",
     "patrones_en": ["vascular injury", "vessel laceration", "arterial injury", "iatrogenic vascular injury", "venous injury during procedure"]},

    # ─── SANGRE/HEMODERIVADOS (faltantes) ───────────────────────────
    {"id_evento": 901, "evento": "Administracion sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "media",
     "patrones_en": ["transfusion error", "blood administration error", "transfusion administered in error"]},
    {"id_evento": 902, "evento": "Cantidad erronea sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "media",
     "patrones_en": ["wrong volume of blood", "incorrect blood volume", "transfusion volume error"]},
    {"id_evento": 905, "evento": "Contraindicacion sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "media",
     "patrones_en": ["transfusion contraindication", "contraindicated transfusion", "transfusion given despite refusal"]},
    {"id_evento": 907, "evento": "Dosis o frecuencia erronea sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "baja",
     "patrones_en": ["wrong transfusion dose", "incorrect units transfused", "extra units transfused"]},
    {"id_evento": 908, "evento": "Hemoderivado erroneo", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "alta",
     "patrones_en": ["wrong blood product", "wrong product transfused", "FFP instead of platelets", "wrong type transfused"]},
    {"id_evento": 9012, "evento": "Paciente erroneo sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "alta",
     "patrones_en": ["wrong patient transfusion", "blood given to wrong patient", "transfused wrong patient"]},
    {"id_evento": 9013, "evento": "Preparacion/dispensacion sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "baja",
     "patrones_en": ["preparation error blood", "blood bank preparation error"]},
    {"id_evento": 9014, "evento": "Prescripcion sangre", "naturaleza": "SANGRE/HEMODERIVADOS", "confianza": "baja",
     "patrones_en": ["transfusion order error", "wrong blood product ordered", "incorrect transfusion order"]},

    # ─── GESTION ORGANIZACION (detectables) ─────────────────────────
    {"id_evento": 1008, "evento": "Falla planificacion cirugia", "naturaleza": "GESTION ORGANIZACION", "confianza": "media",
     "patrones_en": ["surgery cancelled", "case cancelled", "surgery rescheduled", "case rescheduled", "OR cancelled", "operation postponed"]},
    {"id_evento": 1009, "evento": "Fallecimiento", "naturaleza": "GESTION ORGANIZACION", "confianza": "alta",
     "patrones_en": ["patient expired", "deceased", "patient died", "death pronounced", "expired in the ICU", "passed away"]},
    {"id_evento": 10013, "evento": "Suspension procedimiento paciente invadido", "naturaleza": "GESTION ORGANIZACION", "confianza": "alta",
     "patrones_en": ["case cancelled after induction", "procedure aborted after start", "case aborted intraoperatively", "procedure halted after access"]},
    {"id_evento": 10015, "evento": "Comunicacion inefectiva", "naturaleza": "GESTION ORGANIZACION", "confianza": "media",
     "patrones_en": ["communication failure", "miscommunication", "information not conveyed", "handoff failure", "poor handoff", "failure to communicate"]},
    {"id_evento": 10016, "evento": "Error toma de muestra", "naturaleza": "GESTION ORGANIZACION", "confianza": "alta",
     "patrones_en": ["hemolyzed sample", "contaminated specimen", "specimen rejected", "wrong tube collected", "improperly labeled specimen", "lab sample contaminated"]},
    {"id_evento": 10017, "evento": "Falla planificacion cateterismo", "naturaleza": "GESTION ORGANIZACION", "confianza": "media",
     "patrones_en": ["cath cancelled", "catheterization rescheduled", "cath lab cancelled case"]},

    # ─── NUTRICION (detectables) ────────────────────────────────────
    {"id_evento": 1101, "evento": "Cantidad erronea nutricion", "naturaleza": "NUTRICION", "confianza": "baja",
     "patrones_en": ["wrong diet amount", "incorrect feeding volume", "TPN volume error"]},
    {"id_evento": 1103, "evento": "Consistencia erronea", "naturaleza": "NUTRICION", "confianza": "media",
     "patrones_en": ["wrong diet consistency", "given regular diet instead of pureed", "thin liquids given to dysphagia patient", "diet not advanced as ordered"]},
    {"id_evento": 1104, "evento": "Dieta erronea", "naturaleza": "NUTRICION", "confianza": "media",
     "patrones_en": ["NPO violation", "wrong diet", "patient ate while NPO", "ate prior to procedure", "fed inappropriately"]},
    {"id_evento": 1105, "evento": "Frecuencia erronea nutricion", "naturaleza": "NUTRICION", "confianza": "baja",
     "patrones_en": ["wrong feeding frequency", "tube feeds at wrong rate", "missed feeding"]},
    {"id_evento": 1106, "evento": "Paciente erroneo nutricion", "naturaleza": "NUTRICION", "confianza": "media",
     "patrones_en": ["wrong patient diet", "diet tray to wrong patient"]},
]


# ────────────────────────────────────────────────────────────────────
# LECTURA Y BACKUP
# ────────────────────────────────────────────────────────────────────

def backup_file(src: str, dst: str):
    if os.path.exists(src) and not os.path.exists(dst):
        with open(src, "rb") as fi, open(dst, "wb") as fo:
            fo.write(fi.read())
        print(f"  Backup: {dst}")


def cargar_csv_existente(path: str):
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows, list(reader.fieldnames) if reader.fieldnames else []


def cargar_json_existente(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ────────────────────────────────────────────────────────────────────
# LÓGICA DE FUSIÓN
# ────────────────────────────────────────────────────────────────────

def fusionar_csv(existing_rows, new_tuples):
    """Añade columna 'tier'='A' a TODAS las filas (existentes + nuevas).

    Reglas:
      - No duplica: clave = (id_evento_anexo02, codigo_icd10).
      - Si una fila existente NO tiene 'tier', se le agrega 'A'.
    """
    # Construye claves existentes
    claves_existentes = set()
    for r in existing_rows:
        claves_existentes.add((str(r["id_evento_anexo02"]), str(r["codigo_icd10"])))
        if "tier" not in r or not r.get("tier"):
            r["tier"] = "A"

    # Filas nuevas (en formato dict)
    new_rows = []
    skipped = 0
    for t in new_tuples:
        clave = (str(t[1]), str(t[3]))
        if clave in claves_existentes:
            skipped += 1
            continue
        new_rows.append(OrderedDict([
            ("id_naturaleza", t[0]),
            ("id_evento_anexo02", t[1]),
            ("evento_anexo02", t[2]),
            ("codigo_icd10", t[3]),
            ("descripcion_es", t[4]),
            ("descripcion_en", t[5]),
            ("categoria_anexo02_essalud", t[6]),
            ("naturaleza_oms", t[7]),
            ("grupo_gemses", t[8]),
            ("severidad_base", t[9]),
            ("fuente_normativa", t[10]),
            ("tier", "A"),
        ]))
        claves_existentes.add(clave)

    all_rows = existing_rows + new_rows
    return all_rows, len(new_rows), skipped


def fusionar_json(existing_json, new_entries):
    """Añade entradas nuevas al JSON.

    Reglas:
      - No duplica: clave = id_evento.
      - Conserva metadata original; añade changelog.
    """
    existing_ids = {entry["id_evento"] for entry in existing_json["mapeo"]}
    added = 0
    skipped = 0
    for entry in new_entries:
        if entry["id_evento"] in existing_ids:
            skipped += 1
            continue
        existing_json["mapeo"].append(entry)
        existing_ids.add(entry["id_evento"])
        added += 1

    # Actualiza metadata
    existing_json["metadata"]["version"] = "0.3"
    existing_json["metadata"].setdefault("changelog", {})
    existing_json["metadata"]["changelog"]["0.3"] = (
        "Expansion masiva: anadidos patrones NLP en ingles clinico para los eventos "
        "Tier B faltantes del Anexo 02 GEMSES (comportamiento, cuidado del paciente, "
        "dispositivos, infeccion asociada, medicacion, procedimiento, sangre/hemoderivados, "
        "gestion organizacion, nutricion). Total objetivo: cobertura ~95 eventos NLP."
    )
    return existing_json, added, skipped


# ────────────────────────────────────────────────────────────────────
# ESCRITURA
# ────────────────────────────────────────────────────────────────────

def escribir_csv(path, rows):
    if not rows:
        return
    # Asegura orden de columnas (con tier al final)
    fieldnames = [
        "id_naturaleza", "id_evento_anexo02", "evento_anexo02", "codigo_icd10",
        "descripcion_es", "descripcion_en", "categoria_anexo02_essalud",
        "naturaleza_oms", "grupo_gemses", "severidad_base", "fuente_normativa", "tier"
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # Si la fila no tiene 'tier', se asume 'A'
            if "tier" not in r:
                r["tier"] = "A"
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def escribir_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("EXPANSION DEL PIPELINE DE DETECCION — ANEXO 02 GEMSES")
    print("=" * 72)

    # Backups
    print("\n[1/4] Backups...")
    backup_file(CSV_PATH, CSV_BACKUP)
    backup_file(JSON_PATH, JSON_BACKUP)

    # Tier A (CSV)
    print("\n[2/4] Expansion Tier A (ICD-10)...")
    existing_csv, _ = cargar_csv_existente(CSV_PATH)
    print(f"  Filas existentes: {len(existing_csv)}")
    print(f"  Nuevas filas candidatas: {len(NUEVOS_TIER_A)}")
    all_rows, added_csv, skipped_csv = fusionar_csv(existing_csv, NUEVOS_TIER_A)
    escribir_csv(CSV_PATH, all_rows)
    print(f"  Filas anadidas: {added_csv}")
    print(f"  Filas duplicadas omitidas: {skipped_csv}")
    print(f"  Total filas Tier A en CSV: {len(all_rows)}")

    # Tier B (JSON)
    print("\n[3/4] Expansion Tier B (NLP patterns)...")
    existing_json = cargar_json_existente(JSON_PATH)
    print(f"  Entradas existentes: {len(existing_json['mapeo'])}")
    print(f"  Nuevas entradas candidatas: {len(NUEVOS_TIER_B)}")
    updated_json, added_json, skipped_json = fusionar_json(existing_json, NUEVOS_TIER_B)
    escribir_json(JSON_PATH, updated_json)
    print(f"  Entradas anadidas: {added_json}")
    print(f"  Entradas duplicadas omitidas: {skipped_json}")
    print(f"  Total entradas Tier B en JSON: {len(updated_json['mapeo'])}")

    # Resumen
    print("\n[4/4] RESUMEN GLOBAL")
    print("-" * 72)
    eventos_unicos_a = len({r["id_evento_anexo02"] for r in all_rows})
    eventos_unicos_b = len({e["id_evento"] for e in updated_json["mapeo"]})
    print(f"  Eventos UNICOS con Tier A (ICD-10): {eventos_unicos_a}")
    print(f"  Eventos UNICOS con Tier B (NLP):    {eventos_unicos_b}")
    print(f"  Filas CSV totales:                  {len(all_rows)}")
    print(f"  Entradas JSON totales:              {len(updated_json['mapeo'])}")
    print("-" * 72)
    print("OK — Pipeline expandido.\n")


if __name__ == "__main__":
    main()
