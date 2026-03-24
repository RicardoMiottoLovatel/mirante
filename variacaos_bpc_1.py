import pandas as pd

# ================================================
# 1. CARREGAR A PLANILHA
# ================================================
df = pd.read_csv('bpc_teste.csv')   

# ================================================
# 2. RENOMEAR COLUNAS (para facilitar o uso)
# ================================================
df = df.rename(columns={
    'Código': 'Codigo',
    'Unidade Territorial': 'Município',
    'UF': 'UF',
    'Referência': 'Referencia',
    'Pessoas com Deficiência (PCD) beneficiárias do BPC': 'PCD',
    'Idosos beneficiários do BPC': 'Idosos'
})
# ================================================
# 3. CONVERTER COLUNAS NUMÉRICAS 
# ================================================
df['Referencia'] = pd.to_datetime(df['Referencia'], format='%m/%Y', errors='coerce')
df['PCD']    = pd.to_numeric(df['PCD'].astype(str).str.replace(',', '.'), errors='coerce')
df['Idosos'] = pd.to_numeric(df['Idosos'].astype(str).str.replace(',', '.'), errors='coerce')

# Remover linhas com data inválida ou valores nulos nas colunas principais
df = df.dropna(subset=['Referencia', 'PCD', 'Idosos'])

# 3. Ordenar por município e data (essencial para calcular variação mês a mês)
df = df.sort_values(['Codigo', 'Referencia'])

# 4. Calcular variação mês a mês (dentro de cada município)
df['PCD_var']    = df.groupby('Codigo')['PCD'].diff()
df['Idosos_var'] = df.groupby('Codigo')['Idosos'].diff()

# Para PCD
top_pcd = df.nlargest(20, 'PCD_var', keep='all')[
    ['Codigo', 'Município', 'UF', 'Referencia', 'PCD', 'PCD_var']
].copy()
top_pcd = top_pcd.rename(columns={'PCD_var': 'Variacao_PCD'})

# Para Idosos
top_idosos = df.nlargest(20, 'Idosos_var', keep='all')[
    ['Codigo', 'Município', 'UF', 'Referencia', 'Idosos', 'Idosos_var']
].copy()
top_idosos = top_idosos.rename(columns={'Idosos_var': 'Variacao_Idosos'})

# Arredondar e formatar com vírgula (estilo brasileiro)
for col in ['Variacao_PCD', 'Variacao_Idosos']:
    if col in top_pcd.columns:
        top_pcd[col] = top_pcd[col].round(0).astype(int).map(lambda x: f"{x:,}".replace(",", "."))
    if col in top_idosos.columns:
        top_idosos[col] = top_idosos[col].round(0).astype(int).map(lambda x: f"{x:,}".replace(",", "."))

# 6. Mostrar resultados
print("\n=== 20 maiores variações (aumentos ou quedas) em PCD ===")
print(top_pcd.to_string(index=False))

print("\n=== 20 maiores variações (aumentos ou quedas) em Idosos ===")
print(top_idosos.to_string(index=False))

# Salvar em Excel
with pd.ExcelWriter("top_20_variacoes_mensais.xlsx") as writer:
    top_pcd.to_excel(writer, sheet_name="Top PCD", index=False)
    top_idosos.to_excel(writer, sheet_name="Top Idosos", index=False)

print("\nResultados salvos em 'top_20_variacoes_mensais.xlsx'")