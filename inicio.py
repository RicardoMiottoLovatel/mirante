import pandas as pd

bpc = pd.read_csv("bpc_teste.csv")

print(bpc.head())

unidade = r"C:\Users\ricar\OneDrive\Área de Trabalho\Python\arquivos_auxiliares\unidade_territorial.csv"



unidade = pd.read_csv(unidade)

print(unidade.head())
print(unidade.columns)

mesoregiaos = unidade['mesorregiao'].unique().tolist()
print(mesoregiaos)

