
import pandas as pd

import scrappers.tjsp_esaj.funcs as funcs


### ------------------------------------------- Inputs -------------------------------------------
inp_path = "./Transporte Aereo - Metadata/"
out_path = "./Transporte Aereo - Pre Processado/"

metafile_1st = "metadata_1st.csv"
movifile_1st = "movidata_1st.csv"
metafile_2nd = "metadata_2nd.csv"
movifile_2nd = "movidata_2nd.csv"
metafile_mid = "metadata_mid.csv"


movi_files_rename = {"start_name": "mov_ini_name", "start_desc": "mov_ini_desc", "start_date": "mov_ini_date",
                     "finish_name": "mov_fim_name", "finish_desc": "mov_fim_desc", "finish_date": "mov_fim_date",
                     "sentence_name": "mov_stc_name", "sentence_desc": "mov_stc_desc", "sentence_date": "mov_stc_date"}

### ------------------------------------------- Loads data -------------------------------------------
# Loads 1st
meta_1st = pd.read_csv(f"{inp_path}{metafile_1st}", sep=";", index_col=False)
meta_1st.columns = meta_1st.columns.str.lower()

drop_1st = ["teve_arquivo", "caminho_arquivo", "controle", "last_mov", "incidente",
            "process_na_pag", "processo_principal", "apenso", "outros_links", "distribuicao"]
meta_1st = meta_1st.drop(drop_1st, axis=1).dropna(thresh=5, axis=0)
meta_1st = meta_1st[~meta_1st.index.duplicated(keep="first")]

movi_1st = pd.read_csv(f"{inp_path}{movifile_1st}", index_col=0)
movi_1st.columns = movi_1st.columns.str.lower()
movi_1st = movi_1st.rename(movi_files_rename, axis=1)
meta_1st = pd.merge(meta_1st, movi_1st, on="processo", how="left")

# Loads 2nd
meta_2nd = pd.read_csv(f"{inp_path}{metafile_2nd}", sep=";", index_col=False)
meta_2nd.columns = meta_2nd.columns.str.lower()

drop_2nd = ["last_mov", "apenso", 'incidente', "teve_arquivo", "caminho_arquivo", 'process_na_pag', 'outros_links']
meta_2nd = meta_2nd.drop(drop_2nd, axis=1).dropna(thresh=5, axis=0)
meta_2nd = meta_2nd[~meta_2nd.index.duplicated(keep="first")]

movi_2nd = pd.read_csv(f"{inp_path}{movifile_2nd}", index_col=0)
movi_2nd.columns = movi_2nd.columns.str.lower()
movi_2nd = movi_2nd.rename(movi_files_rename, axis=1)
meta_2nd = pd.merge(meta_2nd, movi_2nd, on="processo", how="left")

# Separates Mid
get_mid = meta_2nd.columns[meta_2nd.columns.str.contains("primeira")].to_list()
meta_mid = meta_2nd[["processo"] + get_mid].copy(deep=True)
meta_2nd = meta_2nd.drop(get_mid, axis=1)

print("Raw data")
print(meta_1st.sample(2).set_index("processo").T)
print()
print(meta_2nd.sample(2).set_index("processo").T)
print()
print(meta_mid.sample(2).set_index("processo").T)

### -------------------------------------- Parse / Clean columns -------------------------------------
# Parses 1st
str_cols = ["classe", "situacao", "assunto", "juiz", "foro", "area", "outros_assuntos", "partes_processo",
            "mov_ini_name", "mov_ini_desc", "mov_fim_name", "mov_fim_desc", "mov_stc_name", "mov_stc_desc"]
for str_col in str_cols:
    meta_1st[str_col] = meta_1st[str_col].fillna("").astype(str).str.lower()

meta_1st["vara"] = meta_1st["vara"].str.split(" ").str[0].str.extract(r'(\d+)')
meta_1st["valor_acao"] = meta_1st["valor_acao"].apply(funcs.convert_valor)

meta_1st["data_ini"] = pd.to_datetime(meta_1st["mov_ini_date"])
meta_1st["data_stc"] = pd.to_datetime(meta_1st["mov_stc_date"].replace("Not Found", pd.NaT))
meta_1st["data_fim"] = pd.to_datetime(meta_1st["last_mov_dt"], format="%d/%m/%Y", errors='coerce')
meta_1st["data_fim"] = pd.to_datetime(meta_1st["mov_fim_date"]).fillna(meta_1st["data_fim"])
meta_1st = meta_1st.drop(["mov_ini_date", "mov_stc_date", "mov_fim_date", "last_mov_dt"], axis=1)

meta_1st = pd.concat([meta_1st, meta_1st["partes_processo"].apply(funcs.convert_partes_proc_1st)], axis=1)
meta_1st = meta_1st.drop("partes_processo", axis=1)

# Parses 2nd
str_cols = ['classe', 'situacao', 'assunto', 'seção', 'orgão', 'relator', 'origem', 'area',
            'outros_assuntos', 'partes_processo', 'relator_1', 'relator_2', 'relator_3',
            'julgamento_data', 'julgament_situação', 'julgamento_decisão',
            "mov_ini_name", "mov_ini_desc", "mov_fim_name", "mov_fim_desc"]
for str_col in str_cols:
    meta_2nd[str_col] = meta_2nd[str_col].fillna("").astype(str).str.lower()

meta_2nd = meta_2nd.rename({"julgament_situação": "mov_stc_name", "julgamento_decisão": "mov_stc_desc"}, axis=1)
meta_2nd["valor_acao"] = meta_2nd["valor_acao"].apply(funcs.convert_valor)

meta_2nd["data_ini"] = pd.to_datetime(meta_2nd["mov_ini_date"])
meta_2nd["data_stc"] = meta_2nd["julgamento_data"].fillna(meta_2nd["last_mov_dt"])
meta_2nd["data_stc"] = pd.to_datetime(meta_2nd["data_stc"], format="%d/%m/%Y", errors='coerce')
meta_2nd["data_fim"] = pd.to_datetime(meta_2nd["mov_fim_date"])
meta_2nd = meta_2nd.drop(["mov_ini_date", "julgamento_data", "mov_fim_date", "last_mov_dt"], axis=1)

meta_2nd["relator_1"] = meta_2nd["relator_1"].str.split(":").str[-1].fillna(meta_2nd["relator"])
meta_2nd["relator_2"] = meta_2nd["relator_2"].str.split(":").str[-1]
meta_2nd["relator_3"] = meta_2nd["relator_3"].str.split(":").str[-1]
meta_2nd = pd.concat([meta_2nd, meta_2nd["partes_processo"].apply(funcs.convert_partes_proc_2nd)], axis=1)
meta_2nd = meta_2nd.drop(["relator", "partes_processo", "outr", "adv_outr"], axis=1)

# Parses mid
str_cols = ['numero_primeira', 'foro_primeira', 'vara_primeira', 'juiz_primeira', 'obs_primeira']
for str_col in str_cols:
    meta_mid[str_col] = meta_mid[str_col].fillna("").astype(str).str.lower()

print("Parsed Data")
print(meta_1st.sample(2).set_index("processo").T)
print()
print(meta_2nd.sample(2).set_index("processo").T)
print()
print(meta_mid.sample(2).set_index("processo").T)

### -------------------------------------- Merge company names -------------------------------------
# Attempts to merge the same company names
preset_companies = ["azul", "vrg", "varig", "latan", "tam", "lan", "latam", "gol",
                    "avianca", "copa", "aeromexico",
                    "american", "united", "air canada",
                    "air europa", "tap", "air france", "lufthansa", "alitalia", "british airways", "iberia",
                    "air china", "emirates"]

# Look at all requerentes e requeridos to group have a list of names
all_parts = list(set(meta_1st["rqt"].to_list() + meta_1st["rqd"].to_list() + meta_2nd["apte"].to_list() + meta_2nd["apdo"].to_list()))
all_names, all_companies, all_people = [], [], []
for part in all_parts:
    sparts = part.split("', '")
    for name in sparts:
        name = name.strip("' ")
        if len(name) > 3:
            all_names.append(name)
            (all_companies if funcs.is_company_name(name, preset_companies) else all_people).append(name)

# Remove duplicated_names
all_names = list(set(all_names))
all_companies = list(set(all_companies))
all_people = list(set(all_people))

# Tries to group similar names under the same company
company_trad = pd.Series(funcs.group_similar(all_companies, preset=preset_companies,
                                                     strip_func=funcs.clean_company_name))

meta_1st["rqt_trad"] = meta_1st["rqt"].apply(lambda x: funcs.apply_name_convertion(x, company_trad))
meta_1st["rqd_trad"] = meta_1st["rqd"].apply(lambda x: funcs.apply_name_convertion(x, company_trad))

meta_2nd["apte_trad"] = meta_2nd["apte"].apply(lambda x: funcs.apply_name_convertion(x, company_trad))
meta_2nd["apdo_trad"] = meta_2nd["apdo"].apply(lambda x: funcs.apply_name_convertion(x, company_trad))

### -------------------------------------------- Export results ------------------------------------------
meta_1st.to_csv(f"./{out_path}/{metafile_1st}")
meta_mid.to_csv(f"./{out_path}/{metafile_mid}")
meta_2nd.to_csv(f"./{out_path}/{metafile_2nd}")

### -------------------------------------- Merge all data and Export -------------------------------------
meta_1st.columns = [f"1st_{i}" for i in meta_1st.columns]
meta_mid.columns = [f"mid_{i}" for i in meta_mid.columns]
meta_2nd.columns = [f"2nd_{i}" for i in meta_2nd.columns]
merged = pd.merge(meta_1st, meta_mid, left_on="1st_processo", right_on="mid_processo", how="outer")
merged = pd.merge(merged, meta_2nd, left_on="1st_processo", right_on="2nd_processo", how="outer")

for col, dtype in merged.dtypes.to_dict().items():
    if dtype is object:
        merged[col] = merged[col].fillna('')

merged.to_csv(f"./{out_path}/meta_all.csv")
