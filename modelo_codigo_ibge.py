import pandas as pd

df = pd.read_csv("bpc_teste.csv")

col = "Pessoas com Deficiência (PCD) beneficiárias do BPC"

# Ajustar tipos
df[col] = pd.to_numeric(df[col], errors="coerce")
df["Referência"] = pd.to_datetime(df["Referência"], format="%m/%Y", errors="coerce")

# Ordenar para garantir cálculo correto da variação temporal
df = df.sort_values(["Código", "Referência"])

# Calcular variação entre referências para cada Código
df["variacao"] = df.groupby("Código")[col].diff()

# Calcular estatísticas por Código
resultado = (
    df.groupby("Código")["variacao"]
    .agg(
        variacao_media="mean",
        variacao_max="max",
        variacao_min="min"
    )
    .reset_index()
)

print(resultado)