from ReprovaPorInspetor.relatorio_sivwin import RelatoriosSivWin
import pandas as pd
import streamlit as st

def gerar_dataframe(data_inicio: str, data_fim: str):
    df = RelatoriosSivWin().gerar_relatorio(data_inicio=data_inicio, data_fim=data_fim, tipo_relatorio='todas_inspecoes_periodo')

    df = df[df['TipoInspecao'] == 'Laudo CSV']
    df['NumeroCSV'] = df['NumeroCSV'].replace(['', ' '], None)
    df = df.dropna(subset=['NomeInspetor', 'NomeEngenheiro', 'NumeroCSV', 'SituacaoInspecao'])
    df = df.drop_duplicates(subset=['OS', 'RI'], keep='first')

    df = df[['OS', 'RI', 'DataAberturaOS', 'NumeroCSV', 'SituacaoInspecao', 'NomeInspetor', 'NomeEngenheiro']]
    df = df.sort_values(by=['OS'])

    return df

def gerar_dataframe_reprovas(df: pd.DataFrame):
    df['DataAberturaOS'] = pd.to_datetime(df['DataAberturaOS'], format='%d/%m/%Y')
    df['NomeInspetor'] = df['NomeInspetor'].str.title()
    df['NomeEngenheiro'] = df['NomeEngenheiro'].str.title()
    
    df_reprovas = pd.DataFrame()
    
    for inspetor in df['NomeInspetor'].unique():
        oss_reprovadas = df[(df['SituacaoInspecao'] == 'Reprovado') & (df['NomeInspetor'] == inspetor)]['OS'].tolist()
        df_os_reprovadas = consultar_reprovas_os(oss_reprovadas) if oss_reprovadas else pd.DataFrame()
        
        if not df_os_reprovadas.empty:
            df_os_reprovadas['NomeInspetor'] = inspetor  # Adiciona coluna NomeInspetor
            df_reprovas = pd.concat([df_reprovas, df_os_reprovadas], ignore_index=True)
    
    df_reprovas = df_reprovas.dropna(subset=['NomeInspetor'])
    
    return df_reprovas

def consultar_reprovas_os(lista_os: list):
    l = ', '.join(str(os) for os in lista_os)
    query = f"""
        SELECT 
            d.*, 
            s.ServicoNumero AS OS
        FROM dbo.SivWin_Defeitos AS d
        JOIN dbo.Inspecoes AS i ON d.InspecaoId = i.Id
        JOIN dbo.Servicos AS s ON i.ServicoId = s.Id
        WHERE s.ServicoNumero IN ({l});
    """

    df = RelatoriosSivWin().consulta_personalizada(query)
    df = df[['GrupoCodigo', 'GrupoDescricao', 'ElementoCodigo', 'ElementoDescricao', 'DefeitoCodigo', 'DefeitoDescricao', 'DescricaoAdicional', 'OS']]
    return df

@st.cache_data
def carregar_dados(data_inicio: str, data_fim: str):
    df_inspecoes = gerar_dataframe(data_inicio, data_fim)
    df_reprovas = gerar_dataframe_reprovas(df_inspecoes)
    return df_inspecoes, df_reprovas


if __name__ == '__main__':
    data_inicio = '2024-03-01'
    data_fim = '2025-02-28'
    df_inspecoes = gerar_dataframe(data_inicio, data_fim)
    df_reprovas = gerar_dataframe_reprovas(df_inspecoes)
    
    print("Dataframe de inspeções:")
    print(df_inspecoes.head())
    
    print("\nItens de reprovação:")
    print(df_reprovas.columns)
    print(df_reprovas.shape[0])

    [print(gd) for gd in df_reprovas['GrupoDescricao'].unique()]
    