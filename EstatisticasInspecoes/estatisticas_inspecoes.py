""""
Este módulo recebe e trata as inspeções vindos do banco dados retornando dois dicionários com as estatísticas por escopo e por tipos de veiculos.
"""

from bancosdedados.sqlserver.relatorio_completo_sivwin import RelatoriosSivWin
import pandas as pd
from collections import defaultdict
from datetime import datetime
import streamlit as st

def gerar_dataframe(data_inicio, data_fim):
    # Gerar dataframe principal.
    r = RelatoriosSivWin()
    df = r.gerar_relatorio(data_inicio=data_inicio, data_fim=data_fim,  tipo_relatorio='todas_inspecoes_periodo')

    # Tratando dados dataframe principal.
    df['NumeroCSV'] = df['NumeroCSV'].replace(['', ' '], None)  # Substitui strings vazias e espaços por NaN
    df.dropna(subset=['NumeroCSV', 'SituacaoInspecao', 'NumeroEscopo'], inplace=True) # Remove inspeções que nao sejam aprovadas ou reprovadas ou que não contenham um numero de escopo.
    df.drop_duplicates(subset=['OS'], keep='first', inplace=True) # Remove linhas duplicadas, mantendo apenas a primeira ocorrência.

    return df, data_inicio
    
def gerar_dataframe_inmetro(df, data_inicio):
    # Gerar o dataframe com os laudos inmetro.
    df_inmetro = df[df['TipoInspecao'] == 'Laudo CSV']
    df_inmetro.dropna(subset=['SituacaoInspecao'], inplace=True) # Remove inspeções que nao sejam aprovadas ou reprovadas.
    # df_inmetro[['NumeroEscopo', 'NomeEscopo']] = df_inmetro['Escopo'].str.split(' - ', expand=True) # Divide a coluna Escopo em duas colunas.
    df_inmetro = df_inmetro[df_inmetro['NumeroEscopo'] != ''] # Remove linhas cujo numero escopo seja vazio.
    df_inmetro['NumeroEscopo'] = df_inmetro['NumeroEscopo'].astype(int)
    df_inmetro = df_inmetro[['OS', 'DataAberturaOS', 'TipoInspecao', 'TipoLaudo', 'NumeroEscopo', 'NomeEscopo', 'SituacaoInspecao', 'TipoVeiculo']] # Filtrar dataframe apenas com as colunas necessárias.

    inicio = datetime.strptime(data_inicio, '%Y-%m-%d') # Converte a data de inicio para o objeto datetime.
    df_inmetro = df_inmetro[df_inmetro['DataAberturaOS'] >= data_inicio]  # Remove eventuais linhas com data menor que a data de inicio.

    return df_inmetro

# Função para classificar os escopos
def classificar_escopo(escopo):
    if escopo == 1073:
        return 'SINISTRO'
    elif escopo in [1079, 1007]:
        return 'GNV'
    else:
        return 'MODIFICADO'
    
def processar_dados(df_inmetro):
    # Inicializa o dict onde serão agrupados os dados.
    inspecoes_escopo = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0, 0])))

    # Iterando sobre o DataFrame
    for _, linha in df_inmetro.iterrows():
        data_abertura_os = linha['DataAberturaOS']
        ano = data_abertura_os.year
        mes = data_abertura_os.month
        tipo_laudo = classificar_escopo(linha['NumeroEscopo'])
        situacao = linha['SituacaoInspecao']

        if not inspecoes_escopo[ano][mes][tipo_laudo]: # Inicializar os valores de Aprovado, Reprovado e Total, se necessário
            inspecoes_escopo[ano][mes][tipo_laudo] = [0, 0, 0]  # Aprovados, Reprovados, Totais

        # Incrementar as contagens de acordo com a Situação
        if situacao == 'Aprovado':
            inspecoes_escopo[ano][mes][tipo_laudo][0] += 1  # Incrementar Aprovados
        elif situacao == 'Reprovado':
            inspecoes_escopo[ano][mes][tipo_laudo][1] += 1  # Incrementar Reprovados

        # Atualizar o Total (Aprovados + Reprovados)
        inspecoes_escopo[ano][mes][tipo_laudo][2] = (
            inspecoes_escopo[ano][mes][tipo_laudo][0] + inspecoes_escopo[ano][mes][tipo_laudo][1]
        )

    # Convertendo defaultdict para um dict comum para melhor legibilidade
    inspecoes_escopo = {ano: {mes: dict(laudos) for mes, laudos in meses.items()} for ano, meses in inspecoes_escopo.items()}
    inspecoes_tipo_veiculo = df_inmetro['TipoVeiculo'].astype(str) + ' ' + df_inmetro['TipoLaudo'].astype(str)
    inspecoes_tipo_veiculo = inspecoes_tipo_veiculo.value_counts().to_dict()

    return inspecoes_escopo, inspecoes_tipo_veiculo

@st.cache_data
def carregar_dados(data_inicio, data_fim):
    df, data_inicio = gerar_dataframe(data_inicio, data_fim)
    df_inmetro = gerar_dataframe_inmetro(df, data_inicio)
    inspecoes_escopo, inspecoes_tipo_veiculo = processar_dados(df_inmetro)

    return df_inmetro, inspecoes_escopo, inspecoes_tipo_veiculo

if __name__ == "__main__":
    inicio = '2024-03-01'
    fim = '2025-02-28'

    inspecoes_escopo, inspecoes_tipo_veiculo = carregar_dados(inicio, fim)
    
    dados_escopo = {}
    dados_tipo_veiculo = {}

    total_sinistro = 0 
    total_gnv = 0
    total_modificado = 0
    total_geral = 0

    if not dados_escopo and not dados_tipo_veiculo:
        print('Vazio Dict')

    for k, v in inspecoes_escopo.items():
        for k2, v2 in v.items():
            periodo = str(k2) + '/' + str(k)
            dados_escopo[periodo] = [v2['SINISTRO'][0], v2['SINISTRO'][1], v2['SINISTRO'][2], v2['GNV'][0], v2['GNV'][1], v2['GNV'][2], v2['MODIFICADO'][0], v2['MODIFICADO'][1], v2['MODIFICADO'][2]]

            total_sinistro += v2['SINISTRO'][2]
            total_gnv += v2['GNV'][2]
            total_modificado += v2['MODIFICADO'][2]
            total_geral += v2['SINISTRO'][2] + v2['GNV'][2] + v2['MODIFICADO'][2]   

    for k, v in inspecoes_tipo_veiculo.items():
        dados_tipo_veiculo[k] = v 

    print(dados_escopo)
    # if dados_escopo and dados_tipo_veiculo:
    #     print('Dicionários preenchidos')
    #     for k, v in dados_escopo.items():
    #         print(total_sinistro, total_gnv, total_modificado, total_geral)

    #     for k, v in dados_tipo_veiculo.items():
    #         print(k, v)