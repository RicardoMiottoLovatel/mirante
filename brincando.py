import pandas as pd
import streamlit as st

unidade = pd.read_csv("unidade_mirante_porte_pop.csv", dtype={'pop_censo_2022': 'Int64'})
st.set_page_config(page_title="Brincando com Streamlit", layout="wide")
st.title("🎉 Brincando com Streamlit e Pandas")
st.write("Aqui estamos testando a leitura de um arquivo CSV e exibindo seu conteúdo.")

# Exibir o DataFrame
st.dataframe(unidade)

pop_min = int(unidade["pop_censo_2022"].min())
pop_max = int(unidade["pop_censo_2022"].max())

st.write(f"População máxima: {pop_max:,.0f}".replace(",", "."))
st.write(f"População mínima: {pop_min:,.0f}".replace(",", "."))