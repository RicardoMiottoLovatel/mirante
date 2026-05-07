import streamlit as st
import pandas as pd
import locale

# Configurar locale para formato brasileiro
# locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

########################################################################
# Funções
#############################################

def format_br(valor):
    return f"{valor:,.0f}".replace(",", ".")

def milhar_br(valor):
    return f"{valor:,}".replace(",", ".")

def formato_br(numero, casas: int = 0) -> str:
    """Formata número no padrão brasileiro (1.234.567,89)"""
    if pd.isna(numero) or numero is None:
        return ""
    try:
        return f"{float(numero):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(numero)

#########################################################################

st.set_page_config(layout="wide")

st.set_page_config(page_title="Filtro de Municípios IBGE", layout="wide")


st.markdown("""
<h1 style='text-align: center; margin-bottom: 0;'>
📊 Mirante Visdata
</h1>

<p style='text-align: center; color: gray; margin-top: 0;'>
Análise de indicadores municipais
</p>
""", unsafe_allow_html=True)

# Upload do arquivo
# uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])
 
df = pd.read_csv("unidade_mirante_porte_pop.csv",
                 thousands=".",
                 decimal=","
                )


# if uploaded_file is not None:
#df = pd.read_csv(uploaded_file,
#                  thousands=".",
#                  decimal=",")
    
# Garantir que as colunas existem
colunas_esperadas = [
    "codigo_ibge", "IBGE7", "codigo_ibge_uf", "nome_municipio", "regiao",
    "mesorregiao", "sigla_uf", "uf_municipio", "nome_uf",
    "Porte_pop_2022", "Porte_pop_2022_label", "pop_censo_2022"
]

for col in colunas_esperadas:
    if col not in df.columns:
        st.warning(f"Coluna esperada não encontrada: **{col}**")

#st.success(f"Arquivo carregado com sucesso! {len(df):,} municípios encontrados.")

# ==================== FILTROS NO SIDEBAR ====================
st.sidebar.header("🔎 Seleção")

# 1. Região
regioes = sorted(df["regiao"].dropna().unique())
regiao_selecionada = st.sidebar.multiselect(
    "Região",
    options=regioes,
    default=[]
)

# 2. Estado (UF)
ufs = sorted(df["sigla_uf"].dropna().unique())
uf_selecionada = st.sidebar.multiselect(
    "Estado (Sigla UF)",
    options=ufs,
    default=[]
)

# 3. Nome do Estado (opcional)
estados = sorted(df["nome_uf"].dropna().unique())
estado_selecionado = st.sidebar.multiselect(
    "Nome do Estado",
    options=estados,
    default=[]
)

# 4. Porte da população
portes = sorted(df["Porte_pop_2022_label"].dropna().unique())
porte_selecionado = st.sidebar.multiselect(
    "Porte Populacional (2022)",
    options=portes,
    default=[]
)

# 5. Faixa de população (slider)

pop_min = int(df["pop_censo_2022"].min())
pop_max = int(df["pop_censo_2022"].max())
faixa_pop = st.sidebar.slider(
    "Faixa de População (Censo 2022)",
    min_value=pop_min,
    max_value=pop_max,
    value=(pop_min, pop_max)
)

# 6. Busca por nome do município (texto)
busca_municipio = st.sidebar.text_input("Buscar por nome do município (parcial)")

# ==================== APLICANDO OS FILTROS ====================
df_filtrado = df.copy()
 
if regiao_selecionada:
    df_filtrado = df_filtrado[df_filtrado["regiao"].isin(regiao_selecionada)]

if uf_selecionada:
    df_filtrado = df_filtrado[df_filtrado["sigla_uf"].isin(uf_selecionada)]

if estado_selecionado:
    df_filtrado = df_filtrado[df_filtrado["nome_uf"].isin(estado_selecionado)]

if porte_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Porte_pop_2022_label"].isin(porte_selecionado)]

# Filtro de população
df_filtrado = df_filtrado[
    (df_filtrado["pop_censo_2022"] >= faixa_pop[0]) &
    (df_filtrado["pop_censo_2022"] <= faixa_pop[1])
]

# Busca textual no nome do município
if busca_municipio:
    df_filtrado = df_filtrado[
        df_filtrado["nome_municipio"].str.contains(busca_municipio, case=False, na=False)
    ]

# ==================== RESULTADOS ====================
# st.subheader(f"Resultados")
# st.markdown("<h3 style='text-align: center;'>📊 Resultados</h3>", unsafe_allow_html=True)

st.markdown("""
<style>

/* Centraliza todo o conteúdo do metric */
[data-testid="stMetric"] {
    text-align: center;
    align-items: center;
    justify-content: center;
}

/* Centraliza label */
[data-testid="stMetricLabel"] {
    width: 100%;
    justify-content: center;
    display: flex;
}

/* Centraliza valor */
[data-testid="stMetricValue"] {
    width: 100%;
    justify-content: center;
    display: flex;
}

/* Centraliza delta */
[data-testid="stMetricDelta"] {
    width: 100%;
    justify-content: center;
    display: flex;
}

</style>
""", unsafe_allow_html=True)


# Métricas rápidas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Municípios selecionados",
        value=formato_br(len(df_filtrado))
    )
with col2:
    st.metric(
        label="População total",
        value=formato_br(
            df_filtrado["pop_censo_2022"]
            .fillna(0)
            .sum()
        )
    )

with col3:
    st.metric(
        label="Unidades Federativas",
        value=formato_br(
            df_filtrado["sigla_uf"]
            .dropna()
            .nunique()
        )
    )

    
# ++++++++++++++++++ CONVERTER A COLUNA DE POPULAÇÃO PARA FORMATO BRASILEIRO ++++++++++++++++++++
# Formata a coluna com ponto como separador de milhar (formato brasileiro)

df_filtrado["pop_censo_2022_fmt"] = df_filtrado["pop_censo_2022"].apply(lambda x: formato_br(x, 0))

styled_df = df_filtrado.style.set_properties(
    subset=["pop_censo_2022_fmt"],
    **{'text-align': 'right'}
)

# ==================== CSS para alinhamento à direita ====================
st.markdown("""
    <style>
        /* Alinha à direita a coluna "População 2022" - versão mais robusta */
        div[data-testid="stDataFrame"] table th[data-field="População 2022"],
        div[data-testid="stDataFrame"] table td[data-field="População 2022"] {
            text-align: righ;
        }

        /* Força em todas as células da coluna (caso use classes diferentes) */
        div[data-testid="stDataFrame"] table td:nth-child(10),
        div[data-testid="stDataFrame"] table th:nth-child(10) {
            text-align: right;
        }

        /* Centraliza todos os cabeçalhos (opcional, mas fica mais bonito) */
        div[data-testid="stDataFrame"] table th {
            text-align: center;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Exibir dataframe (com configuração de colunas) 
st.dataframe(
    df_filtrado,
    width="stretch",
    hide_index=True,
    column_config={
        "codigo_ibge": st.column_config.TextColumn("Código IBGE"),
        "IBGE7": None,
        "codigo_ibge_uf": st.column_config.TextColumn("Código UF"),  
        "nome_municipio": st.column_config.TextColumn("Município"),
        "regiao": st.column_config.TextColumn("Região"),
        "mesorregiao": st.column_config.TextColumn("Mesorregião"),
        "sigla_uf": st.column_config.TextColumn("Sigla UF"),    
        "uf_municipio": st.column_config.TextColumn("UF-Município"),
        "nome_uf": st.column_config.TextColumn("Nome do Estado"),
        "Porte_pop_2022_label": st.column_config.TextColumn("Porte"),
       
        "pop_censo_2022_fmt": st.column_config.NumberColumn(
            "População 2022", 
            help="População segundo o Censo 2022"
        ),

        "pop_censo_2022": None,  # Esconde a coluna original de população
        "Porte_pop_2022": None,
    }
)

# Botão para download do resultado filtrado
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar CSV selecionados",
    data=csv,
    file_name="municipios_selecionados.csv",
    mime="text/csv"
)
#

#else:
    #st.info("👆 Faça upload do arquivo CSV para começar.")
    #st.markdown("""
    #**Colunas esperadas no CSV:**
   # `codigo_ibge, IBGE7, codigo_ibge_uf, nome_municipio, regiao, mesorregiao, sigla_uf, uf_municipio, nome_uf, Porte_pop_2022, Porte_pop_2022_label, pop_censo_2022`
   # """)