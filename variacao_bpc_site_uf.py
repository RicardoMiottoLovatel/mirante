import streamlit as st
import pandas as pd

# =============================================
# CONFIGURAÇÕES INICIAIS
# =============================================
st.set_page_config(page_title="Mirante VISDATA", layout="wide")

# Dicionário de meses em português (siglas)
MESES_PT_BR = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

def formatar_mes_ano(serie_dt):
    if pd.isna(serie_dt):
        return ""
    mes = serie_dt.month
    ano = serie_dt.year
    return f"{MESES_PT_BR.get(mes, '???')}/{ano}"

def fmt_br(num, decimais=0):
    if pd.isna(num):
        return ""
    s = f"{num:,.{decimais}f}"
    return s.replace(".", "X").replace(",", ".").replace("X", ",")

# =============================================
# CARREGAMENTO E PROCESSAMENTO 
# =============================================
df = pd.read_csv('bpc_teste.csv')   
# pop = pd.read_csv('POP_IBGE.csv')
unidade = pd.read_csv('unidade_mirante_porte_pop.csv')


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
    df_var['Referencia'].dt.month.map(MESES_PT_BR) + '/' +
    df_var['Referencia'].dt.year.astype(str)
)

df_var['Referencia_ant_fmt'] = (
    df_var['Referencia_ant'].dt.month.map(MESES_PT_BR) + '/' +
    df_var['Referencia_ant'].dt.year.astype(str)
)

df_var['PCD_fmt']       = df_var['PCD'].apply(lambda x: fmt_br(x, 0))
df_var['Idosos_fmt']    = df_var['Idosos'].apply(lambda x: fmt_br(x, 0))
df_var['PCD_var_fmt']   = df_var['PCD_var'].apply(lambda x: fmt_br(x, 0))
df_var['Idosos_var_fmt'] = df_var['Idosos_var'].apply(lambda x: fmt_br(x, 0))

# =============================================
# INTERFACE
# =============================================
#st.subtitle("Mirante VISDATA")
st.title("Mirante VISDATA")
st.markdown("BPC por Município - As 20 maiores variações absolutas (aumentos ou quedas)")

# Filtro por UF
ufs_disponiveis = sorted(df_var['UF'].dropna().unique().tolist())

# Multiselect para escolher UFs (padrão: todas selecionadas)
ufs_selecionadas = st.multiselect(
    "Filtrar por UF(s):",
    options=ufs_disponiveis,
    default=ufs_disponiveis,  # começa com todas selecionadas
    help="Selecione uma ou mais Unidades da Federação para filtrar as tabelas abaixo."
)

# Aplicar filtro nas tabelas
if ufs_selecionadas:
    df_filtrado = df_var[df_var['UF'].isin(ufs_selecionadas)].copy()
else:
    df_filtrado = df_var.copy()

# Recalcular top 20 com o filtro aplicado
df_filtrado['PCD_var_abs']    = df_filtrado['PCD_var'].abs()
df_filtrado['Idosos_var_abs'] = df_filtrado['Idosos_var'].abs()

top_pcd_filtrado = df_filtrado.nlargest(20, 'PCD_var_abs')[
    ['Codigo', 'Municipio', 'UF', 'Referencia_ant_fmt', 'Referencia_fmt',
     'PCD_fmt', 'PCD_var_fmt']
].rename(columns={
    'Referencia_ant_fmt': 'Mês Anterior',
    'Referencia_fmt':     'Mês Atual',
    'PCD_fmt':            'PCD Atual',
    'PCD_var_fmt':        'Variação PCD'
})

top_idosos_filtrado = df_filtrado.nlargest(20, 'Idosos_var_abs')[
    ['Codigo', 'Municipio', 'UF', 'Referencia_ant_fmt', 'Referencia_fmt',
     'Idosos_fmt', 'Idosos_var_fmt']
].rename(columns={
    'Referencia_ant_fmt': 'Mês Anterior',
    'Referencia_fmt':     'Mês Atual',
    'Idosos_fmt':         'Idosos Atual',
    'Idosos_var_fmt':     'Variação Idosos'
})

# Abas
tab1, tab2 = st.tabs(["📈 Variações em PCD", "👴 Variações em Idosos"])

with tab1:
    st.subheader("20 maiores variações absolutas – PCD")
    if top_pcd_filtrado.empty:
        st.warning("⚠️ Nenhum município atende aos filtros selecionados.")
    else:
        st.dataframe(
            top_pcd_filtrado,
 #           width='stretch',
            hide_index=True
        )

with tab2:
    st.subheader("20 maiores variações absolutas – Idosos")

    if top_idosos_filtrado.empty:
        st.warning("⚠️ Nenhum município atende aos filtros selecionados.")
    else:
        st.dataframe(
            top_idosos_filtrado,
 #           width='stretch',
            hide_index=True
        )

# Rodapé
st.markdown("---")
st.caption("Desenvolvido pelo DGI/SAGICAD • Dados originais : VISDATA")