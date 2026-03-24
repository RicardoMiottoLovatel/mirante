import pandas as pd

df = pd.read_csv("bpc_teste.csv")

col = "Pessoas com Deficiência (PCD) beneficiárias do BPC"

# Converter tipos
df[col] = pd.to_numeric(df[col], errors="coerce")
df["Referência"] = pd.to_datetime(df["Referência"], format = "%m%y", errors="coerce")

# Ordenar para calcular a variação temporal
df = df.sort_values(["Código", "Referência"])

# Calcular variação entre referências
df["variacao"] = df.groupby("Código")[col].diff()

print(df.head)

# Estatísticas
variacao_media = df["variacao"].mean()
variacao_max = df["variacao"].max()
variacao_min = df["variacao"].min()

print("Variação média:", variacao_media)
print("Variação máxima:", variacao_max)
print("Variação mínima:", variacao_min)