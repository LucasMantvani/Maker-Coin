#aba de importações
import pandas as pd
import os 

# variaveis globais 

# classes

class VerificacaoCarteira:

    def __init__(self, file_path_block_chain, file_path_values, file_path_extrato):

        self.block_chain =  pd.read_csv(file_path_block_chain)
        self.file_path_extrato = file_path_extrato
        self.file_path_values = file_path_values
    
    def verificacao_valoracao(self):

        tamanho = len(self.block_chain)
        lista_transacoes = []
        extrato = {} #preoculpação como o código vai saber se é um dictionary or an set ?

        for i in range(tamanho):

            a = list(self.block_chain.iloc[i])

            if a[0] in extrato:
                pass
                
            else: 
                extrato[a[0]] = []

            if a[1] in extrato:
                pass

            else:
                extrato[a[1]] = []

            lista_transacoes.append((a[0], -a[2], a[1], a[2]))

        extrato_data = pd.DataFrame(extrato)
        colunas = list(extrato_data.columns)

        for i in lista_transacoes:

            a = []

            for j in colunas:

                if i[0] == j:

                    a.append(i[1])

                elif i[2] == j:

                    a.append(i[3])

                else: 
                    
                    a.append(0)

            extrato_data.loc[len(extrato_data)] = a

        return extrato_data

    def manutencao_simples(self):

        #precisa ser decidido o formato do data_set que armazena as transações no caso o nodo

        return None
        
