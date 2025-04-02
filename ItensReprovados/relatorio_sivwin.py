from bancosdedados.sqlserver.conexao_sql import BancoDeDadosSivWin
from credenciais.banco_de_dados import SIVWIN
from datetime import datetime
import pandas as pd

class RelatoriosSivWin(BancoDeDadosSivWin):
    """
    Esta clase é responsável por gerar o relatorio completo de inspeções cadastradas através do sistema SivWin. 
    A saída padrão dos métodos que compoem o corpo desta classe é uma dataframe contendo as seguintes colunas:
    ['OS', 'RI', 'DataAberturaOS', 'DataAberturaInspecao', 'TipoCSV', 'NUMERO CSV',
       'CodigoEscopo', 'NomeEscopo', 'DataConclusaoInspecao',        
       'DataVencimentoDocumento', 'NF', 'VALOR BRUTO', 'VALOR LIQUIDO',
       'Forma de Pagamento', 'PortariaInmetro', 'SituaçaoInspecao',
       'Placa', 'Chassi', 'EspecieVeiculo', 'TipoVeiculo', 'MarcaModelo',
       'anofabricacao', 'AnoModelo', 'Carrocaria', 'NumeroSelo',
       'CPF do Inspetor', 'Nome do Inspetor', 'CPF do Engenheiro',
       'Nome do Engenheiro', 'NOME RAZAO SOCIAL INDICAÇÃO', 'Proprietario',
       'UFProprietario', 'MunicipioProprietario', 'BairroProprietario',
       'CEPProprietario', 'LogradouroProprietario', 'NumeroProprietario',
       'ComplementoProprietario', 'TelefoneDDDProprietario',
       'TelefoneProprietario', 'CelularDDDProprietario', 'CelularProprietario',
       'EmailProprietario', 'Contratante', 'UFContratante',
       'MunicipioContratante', 'BairroContratante', 'CEPContratante',
       'LogradouroContratante', 'NumeroContratante', 'ComplementoContratante',
       'TelefoneDDDContratante', 'TelefoneContratante',
       'CelularDDDContratante', 'CelularContratante', 'EmailContratante',
       'Condutor', 'UFCondutor', 'MunicipioCondutor', 'BairroCondutor',
       'CEPCondutor', 'LogradouroCondutor', 'NumeroCondutor',
       'ComplementoCondutor', 'TelefoneDDDCondutor', 'TelefoneCondutor',
       'CelularDDDCondutor', 'CelularCondutor', 'EmailCondutor']
    """
    def __init__(self):
        super().__init__(server = SIVWIN['host'], database = SIVWIN['database'], user = SIVWIN['user'], password = SIVWIN['password'])
        self.engine = self.conectar()

    def gerar_dataframe(self, query):
        """
        Gera o dataframe com base nos dados retornados da consulta.
        Requer uma conexão ativa com o banco de dados.
        """
        df = pd.read_sql(query, self.engine)

        # Tratando dados
        df['DataAberturaOS'] = df['DataAberturaOS'].str.strip()  # Remove espaços vazios
        df['DataAberturaOS'] = pd.to_datetime(df['DataAberturaOS'], format='%d/%m/%Y') # Converte para datetime a coluna DataAberturaOS

        # colunas = ['CelularProprietario', 'CelularContratante', 'CelularCondutor']
        # for i in colunas:
        #     if drop_na:
        #         df = df.dropna(subset=i) # Remover linhas em que o telefone esteja vazio.

        #     df[i] = df[i].str.replace('-', '') # Remover traços e espaços do número de telefone.

        #     if drop_telefone:
        #         df = df[df[i].str.len() >= 8] # Remover linhas que os numeros de telefones contenham menos de 8 dígitos.

        return df

    def script_padrao(self):
        """
        Este método, é base da consulta para gerar o relatório no banco de dados. A partir dele é implementado os filtros de modo a refinar os dados consultados.
        """
        consulta = f"""
            select
            Servicos.ServicoNumero AS 'OS',
            TabelaCertificado.Numero AS 'RI',
            convert(char,servicos.AberturaDataHora,103) as 'DataAberturaOS',
            dbo.Inspecoes.AberturaDataHora AS 'DataAberturaInspecao',
            case
            when dbo.Servicos.TipoServico='SR' then 'Laudo CSV'
            when dbo.Servicos.TipoServico='LD' then 'Laudo CSV Legado'
            when dbo.Servicos.TipoServico='LG' then 'Laudo Geral'
            when dbo.Servicos.TipoServico='LS' then 'Laudo SISLIT'
                end as 'TipoInspecao',
            case
                when dbo.Servicos.TipoServico='SR' then dbo.Servicos.TipoCsvSerproNome
                when dbo.Servicos.TipoServico='LG' then dbo.servicos.TipoLaudoNome
                when dbo.Servicos.TipoServico='LS' then dbo.servicos.ProjetoSisLitIdentificacao
                end as 'TipoLaudo',
            Convert(varchar (20), dbo.Inspecoes.NumeroCsvSerpro) as 'NumeroCSV',
            dbo.SivWin_TabelaEscoposSerpro.Codigo AS 'NumeroEscopo',
            dbo.SivWin_TabelaEscoposSerpro.Nome AS NomeEscopo,
            inspecoes.InspecaoEmissaoDataHora AS 'DataConclusaoInspecao',
            inspecoes.InspecaoVencimentoData AS 'DataVencimentoDocumento',
            NotasFiscais.Numero as 'NF',

            Servicos.ValorBrutoServico AS 'ValorBruto',
            Servicos.ValorServico AS 'ValorLiquido',
            Financeiro_DocumentosTipos.Nome AS 'FormaPagamento',
            dbo.inspecoes.CsvPdfArquivoNome,
            dbo.inspecoes.SisLitNomeArquivoLaudo,

            dbo.TabelaPortarias.Portaria AS PortariaInmetro,
            Case 
            When dbo.Inspecoes.SituacaoVeiculo = 1 Then 'Aprovado'
            When dbo.Inspecoes.SituacaoVeiculo = 2 Then 'Reprovado'
            End AS 'SituacaoInspecao',
        
            servicos.placa AS Placa,
            servicos.chassi as Chassi,
            SivWin_CaracteristicasSerpro.EspecieVeiculo,
            SivWin_CaracteristicasSerpro.TipoVeiculo,
            SivWin_CaracteristicasSerpro.MarcaModelo,
            SivWin_CaracteristicasSerpro.anofabricacao,
            SivWin_CaracteristicasSerpro.AnoModelo,
            SivWin_CaracteristicasSerpro.Carrocaria,           
            dbo.Gnv.SeloNumero AS NumeroSelo,
            
            dbo.Processos.ConfirmadoCpf AS 'CPFInspetor',
            dbo.Processos.ConfirmadoNome AS 'NomeInspetor',
            dbo.Inspecoes.ConfirmadoCpf AS 'CPFEngenheiro',
            dbo.inspecoes.ConfirmadoNome AS 'NomeEngenheiro',

            Principal_Indicacoes.Nome_RazaoSocial as 'NOME RAZAO SOCIAL INDICAÇÃO',

            Principal_Contatos_1.Nome_RazaoSocial AS Proprietario,
            Principal_Contatos_1.UF AS UFProprietario, 
            Principal_Contatos_1.Municipio AS MunicipioProprietario, 
            Principal_Contatos_1.Bairro AS BairroProprietario, 
            Principal_Contatos_1.CEP AS CEPProprietario, 
            Principal_Contatos_1.Logradouro AS LogradouroProprietario,
            Principal_Contatos_1.Numero AS NumeroProprietario, 
            Principal_Contatos_1.Complemento AS ComplementoProprietario, 
            Principal_Contatos_1.Telefone1DDD AS TelefoneDDDProprietario, 
            Principal_Contatos_1.Telefone1 AS TelefoneProprietario,
            Principal_Contatos_1.Telefone2DDD AS CelularDDDProprietario, 
            Principal_Contatos_1.Telefone2 AS CelularProprietario, 
            Principal_Contatos_1.Email AS EmailProprietario, 
            
            Principal_Contatos.Nome_RazaoSocial AS Contratante,
            Principal_Contatos.UF AS UFContratante, 
            Principal_Contatos.Municipio AS MunicipioContratante, 
            Principal_Contatos.Bairro AS BairroContratante, 
            Principal_Contatos.CEP AS CEPContratante, 
            Principal_Contatos.Logradouro AS LogradouroContratante,
            Principal_Contatos.Numero AS NumeroContratante, 
            Principal_Contatos.Complemento AS ComplementoContratante, 
            Principal_Contatos.Telefone1DDD AS TelefoneDDDContratante, 
            Principal_Contatos.Telefone1 AS TelefoneContratante,
            Principal_Contatos.Telefone2DDD AS CelularDDDContratante, 
            Principal_Contatos.Telefone2 AS CelularContratante, 
            Principal_Contatos.Email AS EmailContratante,
            
            Principal_Contatos_2.Nome_RazaoSocial AS Condutor,
            Principal_Contatos_2.UF AS UFCondutor, 
            Principal_Contatos_2.Municipio AS MunicipioCondutor, 
            Principal_Contatos_2.Bairro AS BairroCondutor, 
            Principal_Contatos_2.CEP AS CEPCondutor, 
            Principal_Contatos_2.Logradouro AS LogradouroCondutor,
            Principal_Contatos_2.Numero as NumeroCondutor, 
            Principal_Contatos_2.Complemento AS ComplementoCondutor, 
            Principal_Contatos_2.Telefone1DDD AS TelefoneDDDCondutor, 
            Principal_Contatos_2.Telefone1 AS TelefoneCondutor,
            Principal_Contatos_2.Telefone2DDD AS CelularDDDCondutor, 
            Principal_Contatos_2.Telefone2 AS CelularCondutor, 
            Principal_Contatos_2.Email AS EmailCondutor
            
            from servicos
            left outer JOIN dbo.TabelaCertificado ON dbo.TabelaCertificado.ServicoId = dbo.Servicos.Id 
            INNER JOIN dbo.Inspecoes ON dbo.Servicos.Id = dbo.Inspecoes.ServicoId  
            LEFT OUTER JOIN dbo.SivWin_CaracteristicasSerpro ON dbo.Servicos.CaracteristicaAtualSerproId = dbo.SivWin_CaracteristicasSerpro.Id 
            LEFT OUTER JOIN dbo.Caracteristicas ON dbo.Servicos.CaracteristicaAtualId = dbo.Caracteristicas.Id 
            LEFT OUTER JOIN dbo.TabelaPortarias ON dbo.Servicos.PortariaId = dbo.TabelaPortarias.Id 
            INNER JOIN  dbo.Principal_Contatos AS Principal_Contatos_1 ON dbo.Servicos.proprietarioId = Principal_Contatos_1.Id
            LEFT OUTER JOIN Principal_Indicacoes ON Servicos.IndicacaoId = Principal_Indicacoes.Id
            LEFT OUTER JOIN dbo.Gnv ON dbo.Gnv.ServicoId = dbo.Servicos.Id
            LEFT OUTER JOIN NotasFiscais ON Servicos.NotaFiscalId = NotasFiscais.Id
            LEFT OUTER JOIN Financeiro_Lancamentos ON Servicos.ServicoNumero = Financeiro_Lancamentos.NumeroPedido AND Financeiro_Lancamentos.SistemaRemoto = 'SIVWIN' 
            LEFT OUTER JOIN Financeiro_DocumentosTipos ON Financeiro_DocumentosTipos.Id = Financeiro_Lancamentos.DocumentoTipo
            LEFT OUTER JOIN dbo.Processos ON dbo.Processos.Id = dbo.Inspecoes.ProcessoId
            INNER JOIN  dbo.Principal_Contatos AS Principal_Contatos_2 ON dbo.Servicos.CondutorId = Principal_Contatos_2.Id
            INNER JOIN dbo.Principal_Contatos ON dbo.Principal_Contatos.Id =dbo.Servicos.ClienteId
            LEFT OUTER JOIN dbo.SivWin_ProcedimentosEscopoServicoSerpro ON dbo.Servicos.Id = dbo.SivWin_ProcedimentosEscopoServicoSerpro.ServicoId
            LEFT OUTER JOIN dbo.SivWin_ProcedimentosEscoposSerpro ON dbo.SivWin_ProcedimentosEscopoServicoSerpro.ProcedimentoEscopoId = dbo.SivWin_ProcedimentosEscoposSerpro.Id
            LEFT OUTER JOIN dbo.SivWin_TabelaEscoposSerpro ON dbo.SivWin_ProcedimentosEscoposSerpro.EscopoDenatranId = dbo.SivWin_TabelaEscoposSerpro.Id
        """
        return consulta
        
    def filtro_relatorio(self, data_inicio, data_fim, tipo_relatorio:str):
        """Retorna uma string com o filtro de data para a consulta SQL."""

        filtro = { 
            'todas_inspecoes_periodo': f"""WHERE Inspecoes.InspecaoEmissaoDataHora BETWEEN '{data_inicio}T00:00:00' AND '{data_fim}T23:59:59'""",

            'inmetro_aprovadas': f"""WHERE Inspecoes.InspecaoEmissaoDataHora BETWEEN '{data_inicio}T00:00:00' AND '{data_fim}T23:59:59'
                                    AND inspecoes.status=1
                                    AND TabelaCertificado.Numero IS NOT NULL 
                                    AND dbo.Servicos.TipoServico='SR'""",

            'inspecoes_a_vencer': f"""WHERE Inspecoes.SituacaoVeiculo = 2
                                    AND Inspecoes.InspecaoEmissaoDataHora BETWEEN '{data_inicio}T00:00:00' AND '{data_fim}T23:59:59'
                                    AND TabelaCertificado.Numero IS NULL
                                    AND NOT EXISTS (
                                        SELECT 1
                                        FROM Inspecoes i2
                                        INNER JOIN Servicos s2 ON i2.ServicoId = s2.Id
                                        WHERE s2.Placa = Servicos.Placa
                                        AND i2.InspecaoEmissaoDataHora > Inspecoes.InspecaoEmissaoDataHora
                                        AND i2.InspecaoEmissaoDataHora <= Inspecoes.InspecaoVencimentoData
                                    )
                                    ORDER BY Servicos.ServicoNumero ASC;""",

            'os_em_aberto': f"""WHERE Inspecoes.InspecaoEmissaoDataHora BETWEEN '{data_inicio}T00:00:00' AND '{data_fim}T23:59:59'
                            AND Servicos.Status = 0 
                            AND Inspecoes.Status = 0
                            AND TabelaCertificado.Numero IS NULL
                            AND NOT EXISTS ( 
                                SELECT 1 
                                FROM dbo.Inspecoes AS InspecaoPosterior
                                WHERE InspecaoPosterior.ServicoId = Inspecoes.ServicoId
                                AND InspecaoPosterior.AberturaDataHora > Inspecoes.AberturaDataHora)"""
                }

        return filtro[tipo_relatorio]

    def gerar_relatorio(self, data_inicio, data_fim, tipo_relatorio:str):
        """
        Gera o relatório para inspeções finalizadas no período especificado.

        Tipos de relatorios: {
        
        todas_inspecoes_periodo, inmetro_aprovadas, inspecoes_a_vencer, os_em_aberto
        
        }
        """
        query = (self.script_padrao() + self.filtro_relatorio(data_inicio, data_fim, tipo_relatorio)) # Montar a consulta
        relatorio = self.gerar_dataframe(query) # Gerar o DataFrame a partir da consulta

        return relatorio
    
    def consulta_personalizada(self, query):
        """ Gera o relatório com base na consulta SQL fornecida."""
        df = pd.read_sql(query, self.engine) 
        
        return df

if __name__ == '__main__':
    # Configura Pandas para exibir todas as colunas e linhas
    # pd.set_option('display.max_columns', None)  # Exibe todas as colunas
    # pd.set_option('display.max_rows', None)     # Exibe todas as linhas

    r = RelatoriosSivWin()
    inicio = '2024-03-01'
    fim = '2024-03-31'
    df = r.gerar_relatorio(inicio, fim, 'todas_inspecoes_periodo')
    df = df[df['TipoInspecao'] == 'Laudo CSV']
    df = df[['OS', 'RI', 'DataAberturaOS', 'NumeroCSV', 'TipoInspecao', 'TipoLaudo', 'NomeEscopo', 'PortariaInmetro', 'SituacaoInspecao', 'TipoVeiculo']]

    # Tratando dados
    df = df[df['DataAberturaOS'] >= pd.to_datetime(inicio)] # Remove enventuais linhas cuja a data de abertura seja menor que a data de inicio do periodo.
    df['NumeroCSV'] = df['NumeroCSV'].replace(['', ' '], None)  # Substitui strings vazias e espaços por NaN
    df.dropna(subset=['NumeroCSV', 'SituacaoInspecao'], inplace=True) # Remove inspeções que nao sejam aprovadas ou reprovadas.
    df.drop_duplicates(subset=['OS'], keep='first', inplace=True)
    
    df.sort_values('OS', ascending=True)

    print(df['TipoLaudo'].unique())

    total_gnv = df[df['PortariaInmetro'] == '147/2022']
    print(total_gnv.shape[0])

    
    total_sinistro = df[(df['PortariaInmetro'] == '149/2022') & (df['TipoLaudo'] == 'SINISTRADO')]
    total_sinistro.sort_values('OS', ascending=True, inplace=True)
    print(total_sinistro.shape[0])

    total_modificacao = df[(df['PortariaInmetro'] == '149/2022') & (df['TipoLaudo'] == 'NORMAL')]
    total_modificacao.sort_values('OS', ascending=True, inplace=True)
    print(total_modificacao.shape[0])
    



    # for _, l in total_sinistro.iterrows():
    #     print(l['OS'], l['TipoLaudo'], l['SituacaoInspecao'])

    # reprovados = (df['SituacaoInspecao'] == 'Reprovado').sum()
    # aprovados = (df['SituacaoInspecao'] == 'Aprovado').sum()

    # print(df.shape[0])
    # print(reprovados)
    # print(aprovados)
