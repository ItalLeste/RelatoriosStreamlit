import streamlit as st
import pandas as pd
from EstatisticasInspecoes.estatisticas_inspecoes import carregar_dados
import plotly.express as px
from datetime import datetime, timedelta

def carregar_states():
    if not 'df_inspecoes_escopo' in st.session_state:  
        st.session_state['df_inspecoes_escopo'] = None
    if not 'df_inspecoes_tipo_veiculo' in st.session_state:
        st.session_state['df_inspecoes_tipo_veiculo'] = None
    if not 'download' in st.session_state:
        st.session_state['download'] = None

def imprimir_relatorio():
    ...

carregar_states()

@st.fragment
def analisar_escopo():
    with st.container(border=True):
        st.subheader('Overview:')
        st.write(f'Periodo analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}')

        df_inspecoes_escopo = st.session_state['df_inspecoes_escopo']
        aprovado_sinistro = 0
        reprovado_sinistro = 0
        total_sinistro = 0

        aprovado_gnv = 0
        reprovado_gnv = 0
        total_gnv = 0

        aprovado_modificado = 0
        reprovado_modificado = 0
        total_modificado = 0

        df_sinistro = {}
        df_gnv = {}
        df_modificado = {}

        for k, v in df_inspecoes_escopo.items():
            for k2, v2 in v.items():
                periodo = str(k2) + '/' + str(k)

                aprovado_sinistro = v2['SINISTRO'][0]
                reprovado_sinistro = v2['SINISTRO'][1]
                total_sinistro = v2['SINISTRO'][2]

                aprovado_gnv = v2['GNV'][0]                
                reprovado_gnv = v2['GNV'][1]
                total_gnv = v2['GNV'][2]

                aprovado_modificado = v2['MODIFICADO'][0]                
                reprovado_modificado = v2['MODIFICADO'][1]
                total_modificado = v2['MODIFICADO'][2]

                df_sinistro[periodo] = [aprovado_sinistro, reprovado_sinistro, total_sinistro]
                df_gnv[periodo] = [aprovado_gnv, reprovado_gnv, total_gnv]  
                df_modificado[periodo] = [aprovado_modificado, reprovado_modificado, total_modificado]

        # Gráfico - Total Inspeções Escopo
        # Sinistro
        with st.container(border=True):
            st.write('Total Inspeções: Sinitro')

            # Transforma o dicionário em DataFrame
            df = pd.DataFrame.from_dict(df_sinistro, orient='index', columns=['Aprovado', 'Reprovado', 'Total'])
            df.index.name = 'Período'
            df = df.reset_index()

            # Ordena os períodos corretamente
            df['Período'] = pd.to_datetime(df['Período'], format='%m/%Y')
            df = df.sort_values('Período')
            df['Período'] = df['Período'].dt.strftime('%m/%Y')  # opcional: volta para string no eixo X

            # Cria o gráfico
            fig = px.line(df, x='Período', y=['Aprovado', 'Reprovado', 'Total'],
                        markers=True, labels={'value': 'Quantidade', 'variable': 'Situação'},
                        color_discrete_sequence=['green', 'red', 'blue'],)

            # Exibe no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        # GNV
        with st.container(border=True):
            st.write('Total Inspeções: GNV')

            # Transforma o dicionário em DataFrame
            df = pd.DataFrame.from_dict(df_gnv, orient='index', columns=['Aprovado', 'Reprovado', 'Total'])
            df.index.name = 'Período'
            df = df.reset_index()

            # Ordena os períodos corretamente
            df['Período'] = pd.to_datetime(df['Período'], format='%m/%Y')
            df = df.sort_values('Período')
            df['Período'] = df['Período'].dt.strftime('%m/%Y')  # opcional: volta para string no eixo X

            # Cria o gráfico
            fig = px.line(df, x='Período', y=['Aprovado', 'Reprovado', 'Total'],
                        markers=True, labels={'value': 'Quantidade', 'variable': 'Situação'},
                        color_discrete_sequence=['green', 'red', 'blue'],)

            # Exibe no Streamlit
            st.plotly_chart(fig, use_container_width=True)

        # Modificado    
        with st.container(border=True):
            st.write('Total Inspeções: Modificados')

            # Transforma o dicionário em DataFrame
            df = pd.DataFrame.from_dict(df_modificado, orient='index', columns=['Aprovado', 'Reprovado', 'Total'])
            df.index.name = 'Período'
            df = df.reset_index()

            # Ordena os períodos corretamente
            df['Período'] = pd.to_datetime(df['Período'], format='%m/%Y')
            df = df.sort_values('Período')
            df['Período'] = df['Período'].dt.strftime('%m/%Y')  # opcional: volta para string no eixo X

            # Cria o gráfico
            fig = px.line(df, x='Período', y=['Aprovado', 'Reprovado', 'Total'],
                        markers=True, labels={'value': 'Quantidade', 'variable': 'Situação'},
                        color_discrete_sequence=['green', 'red', 'blue'],)

            # Exibe no Streamlit
            st.plotly_chart(fig, use_container_width=True)

@st.fragment
def analisar_veiculo():
    with st.container(border=True):
        st.subheader('Overview:')
        st.write(f'Periodo analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}')


# --------- DASHBOARD -----------------
with st.container(border=True):
    st.title('Estatísticas de Inspeções')

    # Inputs de data
    col1, col2, _, _, _, _ = st.columns(6)
    with col1:
        data_inicio = st.date_input("Data de inicio", datetime.now() - timedelta(days=365), format='DD/MM/YYYY')
    with col2:
        data_fim = st.date_input("Data fim", datetime.now(), format='DD/MM/YYYY')

    btn_analise_escopo = None
    btn_analise_veiculo = None

    col1, col2, col3, col4, col5, col6 = st.columns(6, vertical_alignment="center")
    with col1:
        # Constultar banco e gerar dataframes.
        if st.button('Consultar'):
            data_inicio = data_inicio.strftime('%Y-%m-%d')
            data_fim = data_fim.strftime('%Y-%m-%d')
            st.session_state['df_inspecoes_escopo'], st.session_state['df_inspecoes_tipo_veiculo'], = carregar_dados(data_inicio, data_fim) # Armazena os dataframes na sessão.
            # st.session_state['download'] = st.session_state['df_inspecoes_escopo'].to_csv(index=False)

            
    # Preparação dos dados.
    if st.session_state['df_inspecoes_escopo'] is not None and st.session_state['df_inspecoes_tipo_veiculo'] is not None :
        df_escopo = st.session_state['df_inspecoes_escopo']
        df_veiculo = st.session_state['df_inspecoes_tipo_veiculo']
        
        # Botao Analisar dados empresa.
        with col3:
            btn_analise_escopo = st.button('Dados por Escopo')

        # Botao Analisar dados por Inspetor
        with col4:
            btn_analise_veiculo = st.button('Dados por Tipo de Veiculo')

        # Botão de download
        # with col6:
        #     data = st.session_state['download']
        #     st.download_button(label='Download Relatório', data=data, file_name='relatorio.csv', mime='text/csv')

    if btn_analise_escopo:
        analisar_escopo()
    if btn_analise_veiculo:
        analisar_veiculo()

# ----------- FIM DASHBOARD -----------

