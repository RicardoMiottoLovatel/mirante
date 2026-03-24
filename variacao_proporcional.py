import pandas as pd

# =========================
# 1. Ler arquivos
# =========================
df_bpc = pd.read_csv("bpc_teste.csv", sep=",", encoding="utf-8")
df_pop = pd.read_csv("POP_IBGE.csv", sep=",", encoding="utf-8")

# =========================
# 2. Tratar datas (mm/aaaa)
# =========================
df_bpc["Referência"] = pd.to_datetime(
    df_bpc["Referência"],
    format="%m/%Y",
    errors="coerce"
)

# =========================
# 3. Padronizar chaves
# =========================

# Garantir que Código seja string
df_bpc["Código"] = df_bpc["Código"].astype(str).str.zfill(6)

# IBGE7 sem último dígito
df_pop["IBGE6"] = df_pop["IBGE7"].astype(str).str[:-1]

# Padronizar também como string
df_pop["IBGE6"] = df_pop["IBGE6"].str.zfill(6)

# =========================
# 4. Merge (junção)
# =========================
df_merge = df_bpc.merge(
    df_pop,
    left_on="Código",
    right_on="IBGE6",
    how="left"
)

# =========================
# 5. Converter colunas numéricas
# =========================
cols_numericas = [
    "Pessoas com Deficiência (PCD) beneficiárias do BPC",
    "Idosos beneficiários do BPC",
    "pop_censo_2022"
]

for col in cols_numericas:
    df_merge[col] = pd.to_numeric(df_merge[col], errors="coerce")

# =========================
# 6. Criar indicadores
# =========================

df_merge["pcd_por_habitante"] = (
    df_merge["Pessoas com Deficiência (PCD) beneficiárias do BPC"] /
    df_merge["pop_censo_2022"]
)

df_merge["idosos_por_habitante"] = (
    df_merge["Idosos beneficiários do BPC"] /
    df_merge["pop_censo_2022"]
)

# Opcional: por 1.000 habitantes (mais comum em auditoria)
df_merge["pcd_por_1000"] = df_merge["pcd_por_habitante"] * 1000
df_merge["idosos_por_1000"] = df_merge["idosos_por_habitante"] * 1000

# =========================
# 7. Resultado final
# =========================
df_final = df_merge[[
    "Código",
    "Unidade Territorial",
    "UF_x",
    "Referência",
    "pop_censo_2022",
    "pcd_por_1000",
    "idosos_por_1000"
]]

# Salvar se quiser
df_final.to_csv("resultado_bpc_pop.csv", index=False)

print(df_final.head())

# =========================
# Garantir que não há valores nulos
# =========================
df_rank = df_final.dropna(subset=["pcd_por_1000", "idosos_por_1000"])

# =========================
# 1. MAIORES valores
# =========================

top20_pcd = df_rank.sort_values("pcd_por_1000", ascending=False).head(20)
top20_idosos = df_rank.sort_values("idosos_por_1000", ascending=False).head(20)

# =========================
# 2. MENORES valores
# =========================

bottom20_pcd = df_rank.sort_values("pcd_por_1000", ascending=True).head(20)
bottom20_idosos = df_rank.sort_values("idosos_por_1000", ascending=True).head(20)

# =========================
# 3. Exibir
# =========================

print("\n=== TOP 20 PCD por 1000 habitantes ===")
print(top20_pcd[["Código", "Unidade Territorial", "pcd_por_1000"]])

print("\n=== TOP 20 Idosos por 1000 habitantes ===")
print(top20_idosos[["Código", "Unidade Territorial", "idosos_por_1000"]])

print("\n=== BOTTOM 20 PCD por 1000 habitantes ===")
print(bottom20_pcd[["Código", "Unidade Territorial", "pcd_por_1000"]])

print("\n=== BOTTOM 20 Idosos por 1000 habitantes ===")
print(bottom20_idosos[["Código", "Unidade Territorial", "idosos_por_1000"]])

# =========================
# 4. Salvar em arquivos (opcional)
# =========================

top20_pcd.to_csv("top20_pcd.csv", index=False)
top20_idosos.to_csv("top20_idosos.csv", index=False)
bottom20_pcd.to_csv("bottom20_pcd.csv", index=False)
bottom20_idosos.to_csv("bottom20_idosos.csv", index=False)