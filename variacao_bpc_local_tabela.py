MESES_PT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}


import pandas as pd

# 1. Carregar os dados (ajuste o caminho/nome do arquivo)
df = pd.read_csv('bpc_teste.csv')   

# 2. Renomear colunas para facilitar
df = df.rename(columns={
    'Código': 'Codigo',
    'Unidade Territorial': 'Municipio',
    'UF': 'UF',
    'Referência': 'Referencia',
    'Pessoas com Deficiência (PCD) beneficiárias do BPC': 'PCD',
    'Idosos beneficiários do BPC': 'Idosos'
})

# 3. Converter tipos
df['Referencia'] = pd.to_datetime(df['Referencia'], format='%m/%Y', errors='coerce')
df['PCD']    = pd.to_numeric(df['PCD'].astype(str).str.replace(',', '.'), errors='coerce')
df['Idosos'] = pd.to_numeric(df['Idosos'].astype(str).str.replace(',', '.'), errors='coerce')

df = df.dropna(subset=['Referencia', 'PCD', 'Idosos'])

# 4. Ordenar por município e data (obrigatório)
df = df.sort_values(['Codigo', 'Referencia'])

# 5. Função para formatar números no estilo brasileiro
def fmt_br(num, decimais=0):
    if pd.isna(num):
        return ""
    return f"{num:,.{decimais}f}".replace(".", "X").replace(",", ".").replace("X", ",")

# 6. Calcular variações e capturar mês anterior
df['PCD_var']     = df.groupby('Codigo')['PCD'].diff()
df['Idosos_var']  = df.groupby('Codigo')['Idosos'].diff()
df['Referencia_ant'] = df.groupby('Codigo')['Referencia'].shift(1)

# Remover a primeira linha de cada grupo (sem variação anterior)
df_var = df.dropna(subset=['PCD_var', 'Idosos_var', 'Referencia_ant']).copy()

# 7. Formatar as colunas desejadas
df_var['Referencia_fmt'] = (
    df_var['Referencia'].dt.month.map(MESES_PT) + '/' +
    df_var['Referencia'].dt.year.astype(str)
)

df_var['Referencia_ant_fmt'] = (
    df_var['Referencia_ant'].dt.month.map(MESES_PT) + '/' +
    df_var['Referencia_ant'].dt.year.astype(str)
)

df_var['PCD_fmt']       = df_var['PCD'].apply(lambda x: fmt_br(x, 0))
df_var['Idosos_fmt']    = df_var['Idosos'].apply(lambda x: fmt_br(x, 0))
df_var['PCD_var_fmt']   = df_var['PCD_var'].apply(lambda x: fmt_br(x, 0))
df_var['Idosos_var_fmt'] = df_var['Idosos_var'].apply(lambda x: fmt_br(x, 0))

#-------------------------------
# Top 20 maiores variações absolutas PCD
# -------------------------------

top_pcd = (
    df_var
    .assign(PCD_var_abs = lambda x: x['PCD_var'].abs())
    .sort_values('PCD_var_abs', ascending=False)
    .head(20)
    [[ 'Codigo', 'Municipio', 'UF', 'Referencia_ant_fmt', 'Referencia_fmt', 'PCD_fmt', 'PCD_var_fmt' ]]
    .rename(columns={
        'Referencia_ant_fmt': 'Mês Anterior',
        'Referencia_fmt':     'Mês Atual',
        'PCD_fmt':            'PCD Atual',
        'PCD_var_fmt':        'Variação PCD'
    })
)
# -------------------------------
# Top 20 maiores variações absolutas Idosos
# -------------------------------
top_idosos = (
    df_var
    .assign(Idosos_var_abs = lambda x: x['Idosos_var'].abs())
    .sort_values('Idosos_var_abs', ascending=False)
    .head(20)
    [[ 'Codigo', 'Municipio', 'UF', 'Referencia_ant_fmt', 'Referencia_fmt', 'Idosos_fmt', 'Idosos_var_fmt' ]]
    .rename(columns={
        'Referencia_ant_fmt': 'Mês Anterior',
        'Referencia_fmt':     'Mês Atual',
        'Idosos_fmt':         'Idosos Atual',
        'Idosos_var_fmt':     'Variação Idosos'
    })
)
# 10. Exibir resultados
print("\n=== 20 maiores variações absolutas em PCD (beneficiários BPC) ===")
print(top_pcd.to_string(index=False))

print("\n=== 20 maiores variações absolutas em Idosos (beneficiários BPC) ===")
print(top_idosos.to_string(index=False))

# 11. Salvar em Excel (opcional, mas recomendado)
with pd.ExcelWriter("top_20_maiores_variacoes_formatado.xlsx") as writer:
    top_pcd.to_excel(writer, sheet_name="Top 20 - PCD", index=False)
    top_idosos.to_excel(writer, sheet_name="Top 20 - Idosos", index=False)

print("\nResultados salvos em: top_20_maiores_variacoes_formatado.xlsx")