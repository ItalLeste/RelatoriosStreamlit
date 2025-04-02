import streamlit as st

st.set_page_config(layout="wide", page_title="Relatórios Ital Leste", page_icon=":Book:")

# Páginas de relatórios
reprovas_x_inspetor = st.Page('ReprovaPorInspetor/reprovas_dashboard.py', title='Reprovas por Inspetor')
qtd_inspecoes = st.Page('EstatisticasInspecoes\quantidades_dashboard.py', title='Estatísticas de Inspecoes')


paginas = st.navigation([reprovas_x_inspetor, qtd_inspecoes])
paginas.run()