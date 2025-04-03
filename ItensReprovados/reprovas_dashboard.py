from ItensReprovados.gerador_dados import carregar_dados
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px



def carregar_states():
    if not 'df_inspecoes' in st.session_state:
        st.session_state['df_inspecoes'] = None
    if not 'df_reprovas' in st.session_state:
        st.session_state['df_reprovas'] = None
    if not 'download' in st.session_state:
        st.session_state['download'] = None
    if not 'inspetor_atual' in st.session_state: 
        st.session_state['inspetor_atual'] = None

def imprimir_relatorio():
    ...


carregar_states()

@st.fragment
def analisar_empresa():
     # Totais Inspeçoes Empresa.
    empresa_total = df_inspecoes.shape[0]
    empresa_aprovadas = df_inspecoes[df_inspecoes['SituacaoInspecao'] == 'Aprovado'].shape[0]
    empresa_reprovadas = df_inspecoes[df_inspecoes['SituacaoInspecao'] == 'Reprovado'].shape[0] 
    i_aprovadas_empresa = round((empresa_aprovadas / empresa_total) * 100, 2)
    i_reprovadas_empresa = round((empresa_reprovadas / empresa_total) * 100, 2)

    with st.container(border=True):
        st.subheader('Overview:')
        st.write(f'Periodo analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f'Total de inspeções: {empresa_total}')

        with col2:
            st.write(f'Inspecoes aprovadas: {empresa_aprovadas}')
            st.write(f'Percentual de inspeções aprovadas: {i_aprovadas_empresa}%')

        with col3:
            st.write(f'Inspecoes reprovadas: {empresa_reprovadas}')
            st.write(f'Percentual de inspeções reprovadas: {i_reprovadas_empresa}%')

    col1, col2 = st.columns(2)
    with col1:
        # Gráfico - Total Inspeções Empresa
        with st.container(border=True):
            st.subheader('Total Inspeções Empresa')
            df_aprovados_x_reprovados_empresa = pd.DataFrame({'Situacao': ['Aprovado', 'Reprovado'], 'Quantidade': [empresa_aprovadas, empresa_reprovadas]})
            fig1 = px.pie(df_aprovados_x_reprovados_empresa, values='Quantidade', names='Situacao', color_discrete_sequence=['green', 'red'])
            st.plotly_chart(fig1, use_container_width=True)

        # Gráfico - Inspeções x Inspetor
        with st.container(border=True):
            st.subheader('Inspecoes x Inspetor')
            inspetores = df_inspecoes['NomeInspetor'].unique().tolist()
            inspetores.sort()
            qtd_inspetor = {}
            for inspetor in inspetores:
                qtd = df_inspecoes[df_inspecoes['NomeInspetor'] == inspetor].shape[0]
                qtd_inspetor[inspetor] = qtd

            df_qtd_inspetores = pd.DataFrame(qtd_inspetor.items(), columns=['Inspetor', 'Quantidade'])
            df_qtd_inspetores['Quantidade'] = df_qtd_inspetores['Quantidade'].astype(int)
            fig2 = px.bar(df_qtd_inspetores, x='Inspetor', y='Quantidade', color_discrete_sequence=['blue'])
            st.plotly_chart(fig2, use_container_width=True)
        
    with col2:
        # Gráfico - Grupos grupos mais reprovados
        with st.container(border=True):
            st.subheader('Grupos de Elementos mais Reprovados') 
            qtd_grupos = df_reprovas['GrupoDescricao'].nunique()
            valor_slider = st.slider('Filtrar Grupos', 1, qtd_grupos, value=5, step=2)
            df_itens_mais_reprovados_empresa = df_reprovas['GrupoDescricao'].value_counts().head(valor_slider).reset_index()
            df_itens_mais_reprovados_empresa.columns = ['Grupo', 'Quantidade']
            fig2 = px.bar(df_itens_mais_reprovados_empresa, x='Grupo', y='Quantidade', color_discrete_sequence=['red'])
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico - Elementos mais reprovados
        with st.container(border=True):
            st.subheader('Elementos Mais Reprovados')
            qtd_elementos = df_reprovas['ElementoDescricao'].nunique()
            valor_slider = st.slider('Filtrar Elementos', 1, qtd_elementos, value=10, step=5)
            df_elementos_mais_reprovados_empresa = df_reprovas['ElementoDescricao'].value_counts().head(valor_slider).reset_index()
            df_elementos_mais_reprovados_empresa.columns = ['Elemento', 'Quantidade']
            fig3 = px.bar(df_elementos_mais_reprovados_empresa, x='Elemento', y='Quantidade', color_discrete_sequence=['red'])
            st.plotly_chart(fig3, use_container_width=True)

    # Elementos mais reprovados e suas quantidades.
    with st.container(border=True):
        st.subheader('Itens Mais Reprovados: Quantidades')
        col1, col2 = st.columns([2,10])
        with col1:
            numero_elementos_unicos = df_reprovas['ElementoDescricao'].nunique()
            qtd_elementos_unicos = st.slider('Itens a Exibir:', 5, numero_elementos_unicos, 5)

        with col2:
            df_elementos_mais_reprovados_empresa = df_reprovas[['ElementoDescricao', 'GrupoDescricao']].value_counts().head(qtd_elementos_unicos).reset_index()
            df_elementos_mais_reprovados_empresa.columns = ['Elemento', 'Grupo', 'Quantidade']
            st.dataframe(df_elementos_mais_reprovados_empresa, hide_index=True, use_container_width=True)

@st.fragment
def analisar_inspetores():
    def selecionar_inspetor(inspetores:list):
        inspetor_atual = st.selectbox('Inspetor Analisado:', inspetores)
        st.session_state['inspetor_atual'] = inspetor_atual
        return inspetor_atual
    
    # Estatisticas por Inspetor   
    with st.container(border=True):
        inspetores = df_inspecoes['NomeInspetor'].unique().tolist()
        inspetores.sort()
        inspetor_atual = selecionar_inspetor(inspetores)
        df_inspetor = df_inspecoes[df_inspecoes['NomeInspetor'] == inspetor_atual]

        inspetor_total_aprovadas = df_inspetor[df_inspetor['SituacaoInspecao'] == 'Aprovado'].shape[0]
        inspetor_total_reprovadas = df_inspetor[df_inspetor['SituacaoInspecao'] == 'Reprovado'].shape[0]
        inspetor_total = inspetor_total_aprovadas + inspetor_total_reprovadas
        i_aprovadas_inspetor = round((inspetor_total_aprovadas / inspetor_total) * 100, 2)
        i_reprovadas_inspetor = round((inspetor_total_reprovadas / inspetor_total) * 100, 2)

        st.subheader('Overview:')
        st.write(f'Periodo analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}')

        # Gráfico - Comparaçao entre total de inspeçoes do inspetor e o total da empresa.

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f'Total de inspeções: {inspetor_total}')
        with col2:
            st.write(f'Inspecoes aprovadas: {inspetor_total_aprovadas}')
            st.write(f'Percentual de inspeções aprovadas: {i_aprovadas_inspetor}%')
        with col3:
            st.write(f'Inspecoes reprovadas: {inspetor_total_reprovadas}')
            st.write(f'Percentual de inspeções reprovadas: {i_reprovadas_inspetor}%')

        # Gráficos Inspetor
        col1, col2 = st.columns(2)
        with col1:
            # Gráfico - Porcentagem de inspeções aprovadas e reprovadas.
            df_aprovados_x_reprovados_inspetor = pd.DataFrame({'Situacao': ['Aprovado', 'Reprovado'], 'Quantidade': [inspetor_total_aprovadas, inspetor_total_reprovadas]})
            fig1 = px.pie(df_aprovados_x_reprovados_inspetor, values='Quantidade', names='Situacao', title='Total Inspeções Inspetor', color_discrete_sequence=['green', 'red'])
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Gráfico - Itens mais reprovados.
            qtd_grupos = df_reprovas[df_reprovas['NomeInspetor'] == inspetor_atual]['GrupoDescricao'].nunique()
            valor_slider = st.slider('Filtrar Grupos', 5, qtd_grupos, 5, 1)
            df_grupos_mais_reprovados_inspetor = df_reprovas[df_reprovas['NomeInspetor'] == inspetor_atual]['GrupoDescricao'].value_counts().head(valor_slider).reset_index()
            df_grupos_mais_reprovados_inspetor.columns = ['Grupo', 'Quantidade']
            fig2 = px.bar(df_grupos_mais_reprovados_inspetor, x='Grupo', y='Quantidade', title='Itens Mais Reprovados', color_discrete_sequence=['red'])
            st.plotly_chart(fig2, use_container_width=True)

        # Elementos mais reprovados e seus respectivos quantidades.
       
        st.subheader('Itens Mais Reprovados:')
        col1, col2 = st.columns([2, 10])
        with col1:  
            numero_elementos_unicos = df_reprovas[df_reprovas['NomeInspetor'] == inspetor_atual]['ElementoDescricao'].nunique()
            qtd_elementos_unicos = st.slider('Itens a Exibir:', 5, numero_elementos_unicos, 5)
        with col2:
            df_elementos_mais_reprovados_inspetor = df_reprovas[df_reprovas['NomeInspetor'] == inspetor_atual][['ElementoDescricao', 'GrupoDescricao']].value_counts().head(qtd_elementos_unicos).reset_index()
            df_elementos_mais_reprovados_inspetor.columns = ['Elemento', 'Grupo', 'Quantidade']
            st.dataframe(df_elementos_mais_reprovados_inspetor, use_container_width=True)
        


# --------- DASHBOARD -----------------
with st.container(border=True):
    st.title('Análises de Itens Reprovados')

    # Inputs de data
    col1, col2, _, _, _, _ = st.columns(6)
    with col1:
        data_inicio = st.date_input("Data de inicio", datetime.now() - timedelta(days=365), format='DD/MM/YYYY')
    with col2:
        data_fim = st.date_input("Data fim", datetime.now(), format='DD/MM/YYYY')

    btn_analise_empresa = None
    btn_analise_inspetor = None
        
    col1, col2, col3, col4, col5, col6 = st.columns(6, vertical_alignment="center")
    with col1:
        # Constultar banco e gerar dataframes.
        if st.button('Consultar'):
            st.session_state['df_inspecoes'], st.session_state['df_reprovas'] = carregar_dados(data_inicio, data_fim) # Armazena os dataframes na sessão.
            st.session_state['download'] = st.session_state['df_reprovas'].to_csv(index=False)

            
    # Preparação dos dados.
    if st.session_state['df_inspecoes'] is not None and st.session_state['df_reprovas'] is not None :
        df_inspecoes = st.session_state['df_inspecoes']
        df_reprovas = st.session_state['df_reprovas']
        
        # Botao Analisar dados empresa.
        with col3:
            btn_analise_empresa = st.button('Dados Empresa')

        # Botao Analisar dados por Inspetor
        with col4:
            btn_analise_inspetor = st.button('Dados Inspetores')

        # Botão de download
        with col6:
            data = st.session_state['download']
            st.download_button(label='Download Relatório', data=data, file_name='relatorio.csv', mime='text/csv')


    if btn_analise_empresa:
        analisar_empresa()

    if btn_analise_inspetor:
        analisar_inspetores()

    # ----- Fim Dashboard -----------
   