'''Código By João Lucas Mantovani Baiôco & Bruno Carvalho Kruscinscki'''

import hashlib
import os
import pandas as pd 
from time import time

class BlockChain():

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = time()
        self.blockchain = pd.read_csv(file_path)
        self.hash_anterior = self.blockchain.iloc[-1]

    def encrypt(self, emisario, remetente, valor):

        hash_str = ''
        prova_trabalho = 0

        while hash_str[:2] != '00':

            mensagem = '{},{},{},{},{},{}'.format(emisario, remetente, valor, self.data, prova_trabalho, self.hash_anterior)

            hash_str = hashlib.sha256(mensagem.encode()).hexdigest()

            prova_trabalho += 1

        linha = [emisario, remetente, valor, self.data, prova_trabalho, hash_str]

        return linha

    def escrever(self, mensagem):

        #mensagem tem que estar no formato: [emisario, remetente, valor, self.data, self.hash_anterior]

        self.blockchain.loc[len(self.blockchain)] = mensagem


        os.remove(self.file_path)
        self.blockchain.to_csv(self.file_path, index=False)


def main():

    b = BlockChain("caminho do arquivo")

    b.escrever(b.encrypt('emisor', 'remetente', valor))

if __name__ == '__main__':
    main()
