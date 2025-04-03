import streamlit as st
import pandas as pd
from EstatisticasInspecoes.estatisticas_inspecoes import carregar_dados
import plotly.express as px
from datetime import datetime, timedelta

def carregar_states():
    if not 'df_inmetro' in st.session_state:    
        st.session_state['df_inmetro'] = None
    if not 'df_inspecoes_escopo' in st.session_state:  
        st.session_state['df_inspecoes_escopo'] = None
    if not 'df_inspecoes_tipo_veiculo' in st.session_state:
        st.session_state['df_inspecoes_tipo_veiculo'] = None
    if not 'download' in st.session_state:
        st.session_state['download'] = None

def imprimir_relatorio():
    ...

carregar_states()

def criar_grafico_escopo(df_dict, titulo):
    df = pd.DataFrame.from_dict(df_dict, orient='index', columns=['Aprovado', 'Reprovado', 'Total'])
    df.index.name = 'Período'
    df = df.reset_index()
    df['Período'] = pd.to_datetime(df['Período'], format='%m/%Y')
    df = df.sort_values('Período')
    df['Período'] = df['Período'].dt.strftime('%m/%Y')
    
    fig = px.line(df, x='Período', y=['Aprovado', 'Reprovado', 'Total'],
                  markers=True, labels={'value': 'Quantidade', 'variable': 'Situação'},
                  color_discrete_sequence=['green', 'red', 'blue'])
    
    with st.container(border=True):
        st.write(titulo)
        st.plotly_chart(fig, use_container_width=True)

def criar_grafico_pizza(df, titulo):
    aprovados = df[df['SituacaoInspecao'] == 'Aprovado'].shape[0]
    reprovados = df[df['SituacaoInspecao'] == 'Reprovado'].shape[0]
    total = aprovados + reprovados

    labels = ['Aprovado', 'Reprovado']
    values = [aprovados, reprovados]

    fig = px.pie(df, values=values, names=labels, title=titulo,
                  color_discrete_sequence=['green', 'red'], labels={'value': 'Quantidade', 'variable': 'Situação'})

    with st.container(border=True):
        st.write(titulo)
        st.plotly_chart(fig, use_container_width=True)


@st.fragment
def analisar_escopo():
    with st.container(border=True):
        st.subheader('Overview:')
        st.write(f'Periodo analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}')

        df = st.session_state['df_inmetro']
        df_inspecoes_escopo = st.session_state['df_inspecoes_escopo']
        df_tipos = {'SINISTRO': {}, 'GNV': {}, 'MODIFICADO': {}}

        # Organizar dados dataframe inseções escopo.
        for k, v in df_inspecoes_escopo.items():
            for k2, v2 in v.items():
                periodo = f'{k2}/{k}'
                for tipo in df_tipos:
                    df_tipos[tipo][periodo] = v2[tipo]

    # st.dataframe(df)

    # Gráficos
    # Total Inspeções Periodo
    with st.container(border=True):
        st.subheader('Total Inspeções Periodo')
        col1, col2 = st.columns(2)
        with col1:
            # Total Inspeções Resultado.
            aprovados = df[df['SituacaoInspecao'] == 'Aprovado'].shape[0]
            reprovados = df[df['SituacaoInspecao'] == 'Reprovado'].shape[0]
            labels = ['Aprovado', 'Reprovado']
            values = [aprovados, reprovados]
            fig = px.pie(df, values=values, names=labels, color_discrete_sequence=['green', 'red'], labels={'value': 'Quantidade', 'variable': 'Situação'})
    
            st.write('Total Inspeções: Resultado')
            st.plotly_chart(fig, use_container_width=True)
    
        with col2:
            # Total Inspeções Escopo.
            sinistro = df[df['TipoLaudo'] == 'SINISTRADO'].shape[0]
            gnv = df[df['TipoLaudo'] == 'GNV - PERIÓDICA'].shape[0]
            modificado = df[df['TipoLaudo'] == 'NORMAL'].shape[0]
            labels = ['Sinistro', 'GNV', 'Modificado']
            values = [sinistro, gnv, modificado]
            fig = px.pie(df, values=values, names=labels, color_discrete_sequence=['green', 'red', 'blue'], labels={'value': 'Quantidade', 'variable': 'Situação'})
    
            st.write('Total Inspeções: Escopo')
            st.plotly_chart(fig, use_container_width=True)

    criar_grafico_escopo(df_tipos['SINISTRO'], 'Total Inspeções: Sinistro')
    criar_grafico_escopo(df_tipos['GNV'], 'Total Inspeções: GNV')
    criar_grafico_escopo(df_tipos['MODIFICADO'], 'Total Inspeções: Modificados')

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
            st.session_state['df_inmetro'],st.session_state['df_inspecoes_escopo'], st.session_state['df_inspecoes_tipo_veiculo'], = carregar_dados(data_inicio, data_fim) # Armazena os dataframes na sessão.
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

