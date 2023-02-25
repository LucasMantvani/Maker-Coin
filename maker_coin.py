
''' Maker coin by João Lucas Mantovani Baiôco'''

# aba de importação
import os, hashlib, time, getpass, datetime

import pandas as pd 

#inicio das classes 

class Block_chain:

    def __init__(self, block_chain_path:str):

        self.block_chain      = pd.read_csv(block_chain_path)
        self.block_chain_path = block_chain_path
        self.time             = time.time()

        return None

    def encriptar(self, emissario:str, remetente:str, valor:float):

        hash_str = ''

        prova_trabalho = -1

        while hash_str[:2] != '00':

            prova_trabalho += 1
            mensagem = '{}, {}, {}, {}, {}, {}'.format(emissario, remetente, valor, self.time, prova_trabalho, self.block_chain.iloc[-1]['hash'])

            hash_str = hashlib.sha256(mensagem.encode()).hexdigest()

        l =  [emissario, remetente, valor, self.time, prova_trabalho, hash_str]
        
        return l

    def prova_block_chain(self):

        for i in range(1, len(self.block_chain)-1):

            j = self.block_chain.iloc[i]

            mensagem = '{}, {}, {}, {}, {}, {}'.format(j['emissario'], j['remetente'], j['valor'], j['time'], j['prova_trabalho'], self.block_chain.iloc[i-2]['hash'])
            hash_str = hashlib.sha256(mensagem.encode()).hexdigest()

            if hash_str != j['hash']:
                return False 

            else:
                pass

        return True

    def prova_valor_carteira(self, valoracao:object, emisario:str, valor:float):

        valoracao.ataualizar()
        
        valoracao = valoracao.valoracao_carteira() 

        if valoracao['public_key'][emisario] >= valor:

            return True
        
        else:
            return False

    def transacao(self, livro:object, emissario:str, senha:str,  remetente:str, valor:float):

        if self.prova_block_chain:
            if self.prova_valor_carteira:
                if livro.verificar_credenciais(emissario, senha): 
                    if livro.verificar_remetente(remetente):

                        transacao_aprovada = self.encriptar(emissario, remetente, valor)

                        self.block_chain.loc[len(self.block_chain)] = transacao_aprovada
                        os.remove(self.block_chain_path)
                        self.block_chain.to_csv(self.block_chain_path, index=False)
                    
                    else:
                        print('Erro 05: O remetente é inexistente.')
                else:
                    print('Erro 04: suas credenciais estão erradas tente novamente.')
            else:
                print('Erro 02: sua carteira não tem valor o suficiente para efetuar essa transação.')
        else: 
            print('Erro 01: essa block chain foi adulterada, um novo nodo será procurado.')

        return None

class Valoracao(Block_chain):

    def __init__(self, block_chain_path:str, vlr_path:str):
        super().__init__(block_chain_path)

        self.valoracao_carteira      = pd.read_csv(vlr_path)
        self.valoracao_carteira_path = vlr_path

        return None

    def extrato(self, public_key:str):

        a = {'carteira': [0], 'valor': [0], 'data': [0], 'total': [0]}
        df = pd.DataFrame(a)

        for i in range(1, len(self.block_chain)):#deve ou não deve ter o -1?

            j = self.block_chain.iloc[i]

            if j['emissario'] == public_key:

                df.loc[len(df)] = [j['remetente'], -j['valor'], datetime.datetime.fromtimestamp(j['time']), df.iloc[-1]['total'] - j['valor']]

            elif  j['remetente'] == public_key:

                df.loc[len(df)] = [j['remetente'], j['valor'], datetime.datetime.fromtimestamp(j['time']), df.iloc[-1]['total'] + j['valor']]

            else:
                pass

        return df.loc[::-1]

    def ataualizar(self):

        l = []

        a = lambda x: l.append(x)

        map(a, self.block_chain['emissario'])
        map(a, self.block_chain['remetente'])

        l = list(set(l))

        self.valoracao_carteira['public_key'] = l
        
        l = []

        for i in self.valoracao_carteira['public_key']:

            entrada  = sum(self.block_chain[self.block_chain['remetente'] == i]['valor'])
            retirada = sum(self.block_chain[self.block_chain['emissario'] == i]['valor'])

            l.append(entrada - retirada)
        
        self.valoracao_carteira['value'] = l

        os.remove(self.valoracao_carteira_path)
        self.valoracao_carteira.to_csv(self.valoracao_carteira_path, index=False)

        return None

class Livro:

    def __init__(self, livro_path:str):
        
        self.livro      = pd.read_csv(livro_path)
        self.livro_path = livro_path

        return None

    def verificar_credenciais(self, public_key:str, private_key:str):

        if self.verificar_livro():

            try:

                hash_str = hashlib.sha512(private_key.encode()).hexdigest()

                a = self.livro[self.livro['public_key'] == public_key]

                return a.iloc[0]['private_key_hash'] == hash_str
            
            except IndexError:

                print('Essa chave publica não existe')

                return False
        
        else:
            pass
    
    def verificar_remetente(self, remetente):

        if self.verificar_livro():

            return remetente in self.livro['public_key']
        
        else:
            pass

    def verificar_livro(self):

        for i in range(1, len(self.livro)-1):

            j = self.livro.iloc[i]

            mensagem = '{}, {}, {}, {}'.format(j['public_key'], j['private_key_hash'], j['prova_trabalho'], self.livro.iloc[i-1]['hash'])
            hash_str = hashlib.sha512(mensagem.encode()).hexdigest()
            
            if hash_str != j['hash']:
                print('Erro 05: o livro das senhas foi adulterado, um novo nodo será procurado.')
                return False

            else:
                pass

        return True

    def adicionar_carteira(self, b_c, v, public_key:str, private_key:str):

        if self.verificar_livro():

            private_key =  hashlib.sha512(private_key.encode()).hexdigest()
            hash_str = ''

            prova_trabalho = -1

            while hash_str[:3] != '000':
                

                prova_trabalho += 1 

                mensagem = '{}, {}, {}, {}'.format(public_key, private_key, prova_trabalho, self.livro.iloc[-1]['hash'])
                hash_str = hashlib.sha512(mensagem.encode()).hexdigest()

            l = [public_key, private_key, prova_trabalho, hash_str]

            self.livro.loc[len(self.livro)] = l
            os.remove(self.livro_path)
            self.livro.to_csv(self.livro_path, index=False)

            if len(self.livro) <= 10:

                transacao_aprovada = b_c.encriptar('0', public_key, 10)

                b_c.block_chain.loc[len(b_c.block_chain)] = transacao_aprovada
                os.remove(b_c.block_chain_path)
                b_c.block_chain.to_csv(b_c.block_chain_path, index=False)

                print("Voce é um dos 10 primeiro usuarios, parabens voce recebera 10 MKR's.")

            else:

                transacao_aprovada = b_c.encriptar('0', public_key, 0)

                b_c.block_chain.loc[len(b_c.block_chain)] = transacao_aprovada
                os.remove(b_c.block_chain_path)
                b_c.block_chain.to_csv(b_c.block_chain_path, index=False)

            v.ataualizar()

        else: 
            print('Erro 03: O Livro das senhas foi adulterado um novo nodo será procurado.')

        return None

class Dados:

    def __init__(self):
        pass

    def path_app_data(self):

        path = os.getcwd().split('\\')[:3]
        f = os.path.join(path[0], '\\', path[1], path[2], 'AppData', 'Local')

        return f
    
    def verificar_maquina(self):

        f = self.path_app_data()

        for i in os.listdir(f):

            if i == 'Maker Coin':
                
                return True
                
            else:
                pass
        
        return False

    def arquivos_temporarios(self, public_key:str, punicao:int):

        punicao = 5 * (3**punicao) + time.time()

        f = os.path.join(self.path_app_data(), 'Maker Coin', 'temp', public_key + '.temp')

        with open(f, mode='w', encoding='utf-8') as file:

            file.write(str(punicao))

        file.close()

        return None
    
    def ler_arquivos_temporarios(self, public_key):

        f = os.path.join(self.path_app_data(), 'Maker Coin', 'temp', public_key + '.temp')

        try: 
            with open(f, mode='r', encoding='utf-8') as file:

                if float(file.read()) <= time.time():

                    file.close()
                    os.remove(f)

                    return True
                
                else:

                    file.close()
                    return False

        except FileNotFoundError:
            return True

    def escrever_arquivos(self):

        block_chain = {'emissario': [0],'remetente': [0],'valor': [100],'time': [0],'prova_trabalho': [0],'hash': [0]}
        valoracao   = {'public_key': [],'value': []}
        livro       = {'public_key': [0],'private_key_hash': [0],'prova_trabalho': [0],'hash': [0]}

        block_chain = pd.DataFrame(block_chain)
        valoracao   = pd.DataFrame(valoracao)
        livro       = pd.DataFrame(livro)

        f = self.path_app_data()

        os.makedirs(os.path.join(f, 'Maker Coin', 'data storage'))
        os.makedirs(os.path.join(f, 'Maker Coin', 'temp'))
        os.makedirs(os.path.join(f, 'Maker Coin', 'init'))

        block_chain.to_csv(os.path.join(f, 'Maker Coin', 'data storage', 'block_chain.csv'), index=False)
        valoracao.to_csv(os.path.join(f, 'Maker Coin', 'data storage', 'valoracao.csv'), index=False)
        livro.to_csv(os.path.join(f, 'Maker Coin', 'data storage', 'livro.csv'), index=False)

        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'capa.txt')

        with open(dir_path, mode='r') as file_0:
            with open(os.path.join(f, 'Maker Coin', 'init', 'capa.txt'), mode='x') as file_1:

                a = file_0.readlines()
                file_1.writelines(a)

                file_1.close()
            file_0.close()

        os.remove(dir_path)

        return None
    
    def fazer_capa(self):
        
        f = self.path_app_data()

        with open(os.path.join(f, 'Maker Coin', 'init', 'capa.txt'), mode="r") as file:

            a = file.readlines() 

            b = lambda x: x.replace('\n', '')
            a = list(map(b, a))

            for i in a:
                print('\033[0;33;40m' + i)
                time.sleep(0.005)

            file.close()

        return None

def main():

    #operação padão, pré funcionamento da cripto.

    if Dados().verificar_maquina():
        pass

    else:
        Dados().escrever_arquivos()

    f = Dados().path_app_data()

    block_chain = Block_chain(os.path.join(f, 'Maker Coin', 'data storage', 'block_chain.csv'))
    valoracao   = Valoracao(block_chain_path=os.path.join(f, 'Maker Coin', 'data storage', 'block_chain.csv'), vlr_path=os.path.join(f, 'Maker Coin', 'data storage', 'valoracao.csv'))
    livro       = Livro(os.path.join(f, 'Maker Coin', 'data storage', 'livro.csv'))

    #operação padrão, cipto em funcionamento 

    while True:

        os.system('cls')
        Dados().fazer_capa()

        a = input('\033[0;37;40m' + 'Digite o numero da operação que deseja quer fazer: \n 1: Criar carteira. \n 2: Fazer uma transação. \n 3: Verificar seu saldo. \n Digite qualquer outro valor caso deseje sair.')

        if a == '1':

            b = input('\033[0;32;40m' + 'Voce deseja continuar (y/n)? ')

            if b == 'y':
                
                c, d = input('\033[0;37;40m' + 'digite sua chave publica: '), input('\033[0;37;40m' + 'confirme sua chave publica: ')

                while c != d:
                    
                    print('\033[0;31;40m' + 'As chaves sao diferentes tente novamente.')

                    c, d = input('\033[0;37;40m' + 'digite sua chave publica: '), input('\033[0;37;40m' + 'confirme sua chave publica: ')
                
                g, h = getpass.getpass('\033[0;37;40m' + 'digite sua chave privada: '), getpass.getpass('\033[0;37;40m' + 'confirme sua chave privada: ')

                while g != h:

                    print('\033[0;31;40m' + 'As chaves sao diferentes tente novamente.')

                    g, h = getpass.getpass('\033[0;37;40m' + 'digite sua chave privada: '), getpass.getpass('\033[0;37;40m' + 'confirme sua chave privada: ')
                
                livro.adicionar_carteira(block_chain, valoracao, c, g)
                i = input("Pressione enter para sair: ")

            else: 
                pass
        
        elif a == '2':

            b = input('\033[0;32;40m' + 'Voce deseja continuar (y/n)? ')

            if b == 'y':

                c = input('\033[0;37;40m' + 'Digite sua chave publica: ')
                d = getpass.getpass('\033[0;37;40m' + 'Digite sua chave pivada: ')
                p = 0

                

                while not(livro.verificar_credenciais(c, d) and Dados().ler_arquivos_temporarios(c)):

                    print('\033[0;31;40m' + 'Suas credenciais foram rejeitadas.')
                    b = input('\033[0;32;40m' + 'Voce deseja tentar essa operação novamente (y/n)? ')

                    if b == 'y':
                        
                        c = input('\033[0;37;40m' + 'Digite sua chave publica: ')
                        d = getpass.getpass('\033[0;37;40m' + 'Digite sua chave pivada: ')

                        p += 1

                        Dados().arquivos_temporarios(c, p)
                        print('\033[0;31;40m' + 'Suas transações foram bloqueadas por: {} segundos.'.format(5*3**p))
                        i = input('\033[0;37;40m' + "Pressione enter para sair: ")

                    else:
                        break
                
                if b == 'y':
                    e = input('\033[0;37;40m' + 'Digite a chave publica do remetente: ')
                    f = float(input('\033[0;37;40m' + 'Digite o valor da transação: '))

                    if f > 0:

                        block_chain.transacao(livro, c, d, e, f)
                        i = input("Pressione enter para sair: ")

                    else:
                        print('\033[0;31;40m' + 'Voce não pode transferir valores negativos ou nulos.')
                        i = input("Pressione enter para sair: ")
                
                else:
                    pass

            else: 
                pass

        elif a == '3':
            
            b = input('\033[0;32;40m' + 'Voce deseja continuar (y/n)? ')

            if b == 'y':

                c = input('\033[0;37;40m' + 'Digite sua chave publica: ')

                print(valoracao.extrato(c).head())
                i = input("Pressione enter para sair: ") 

            else:
                pass

        else:
            
            print('\033[0;37;40m' + 'Fim das operações :D')
            os.system('cls')
            break

    return 0

if __name__ == '__main__':
    main()

