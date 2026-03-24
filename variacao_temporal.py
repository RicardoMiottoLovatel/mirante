import pandas as pd

df = pd.read_csv("bpc_teste.csv")

col = "Pessoas com Deficiência (PCD) beneficiárias do BPC"

# Ajustar tipos
df[col] = pd.to_numeric(df[col], errors="coerce")
df["Referência"] = pd.to_datetime(df["Referência"], errors="coerce")

# Ordenar
df = df.sort_values(["Código", "Referência"])

# Variação absoluta
df["variacao"] = df.groupby("Código")[col].diff()

# Variação percentual
df["variacao_percentual"] = df.groupby("Código")[col].pct_change() * 100