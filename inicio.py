import pandas as pd

bpc = pd.read_csv("bpc_teste.csv")

print(bpc.head())

unidade = pd.read_csv("unidade_territorial.csv")

print(unidade.head())
print(unidade.columns)

mesoregiaos = unidade['mesorregiao'].unique().tolist()
print(mesoregiaos)