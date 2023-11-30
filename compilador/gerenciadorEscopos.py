class Pilha:
    def __init__(self):
        # Método de inicialização. Cria um dicionário vazio para armazenar os blocos.
        self.items = {}

    def empilha(self, identificador_bloco, lexema, tipo, valor):
        # Adiciona um novo lexema ao bloco identificado por 'identificador_bloco'.
        # Se o bloco ainda não existir, cria um novo bloco.
        if identificador_bloco not in self.items:
            self.items[identificador_bloco] = {}
        self.items[identificador_bloco][lexema] = {
            'lexema': lexema,
            'tipo': tipo,
            'valor': valor
        }

    def desempilha(self, identificador_bloco):
        # Remove e retorna o bloco identificado por 'identificador_bloco'.
        return self.items.pop(identificador_bloco, None)

    def __str__(self, identificador_bloco=None, lexema=None):
        # Se 'identificador_bloco' e 'lexema' são fornecidos, retorna o valor associado ao lexema no bloco.
        if identificador_bloco is not None:
            if lexema is not None:
                # Obtém as informações do bloco identificado por 'identificador_bloco'.
                bloco = self.items.get(identificador_bloco, {})
                
                # Verifica se o lexema está presente no bloco atual.
                if lexema in bloco:
                    return str(bloco[lexema]['valor'])
                else:
                    # Se o lexema não está no bloco atual, procura nos blocos anteriores.
                    for bloco_id in reversed(list(self.items.keys())):
                        if bloco_id == identificador_bloco:
                            continue  # Pular o bloco atual
                        bloco_anterior = self.items.get(bloco_id, {})
                        if lexema in bloco_anterior:
                            return str(bloco_anterior[lexema]['valor'])

                    # Caso não encontre em nenhum bloco, retorna uma mensagem de erro.
                    return f"Lexema {lexema} não declarado."
            else:
                # Se 'lexema' não é fornecido, retorna o bloco identificado por 'identificador_bloco'.
                return str({identificador_bloco: self.items.get(identificador_bloco, {})})
        else:
            # Se nem 'identificador_bloco' nem 'lexema' são fornecidos, retorna a pilha completa.
            return str(self.items)

def processar_programa(programa, pilha):
    bloco_atual = None
    lista_blocos = [] #será usada para desempilhar o bloco que for fechado.

    for linha in programa:
        tokens = linha.split()

        if not tokens:  
            #Verifica se tokens está vazio, para tratar as linhas em branco no arquivo
            continue

        if tokens[0] == "BLOCO":
            #como a linha é apenas bloco e o nome do bloco, a posição 1 será o bloco atual
            bloco_atual = tokens[1]
            lista_blocos.append(bloco_atual)
        elif tokens[0] == 'NUMERO' or tokens[0] == 'CADEIA':
            #caso a lista venha apenas com 3 elementos, podem ser, por exemplo:
            #[TIPO, lexema, valor] ou [TIPO lexema] 
            if len(tokens) == 2:
                lexema = tokens[1]
                if '=' in lexema:
                    #separa o lexema e o valor caso o '=' venha colado
                    lexema, valor = lexema.split('=')
                    tipo = tokens[0]

                    pilha.empilha(bloco_atual, lexema, tipo, valor)
                else:
                    #caso não venha nenhum valor associado à variável, atribui None por padrão.
                    tipo = tokens[0]
                    valor = None

                    pilha.empilha(bloco_atual, lexema, tipo, valor)
            else:
                if len(tokens) > 4: 
                    #casos em que há várias declarações de lexemas na mesma linha
                    #exemplo [TIPO a = 3, b = 4] ou [TIPO a, b, c]
                    tipo = tokens[0]
                    lexema_atual = None

                    for elemento in tokens:
                        elemento = elemento.replace(",", "")  # Remover vírgulas
                        
                        if elemento == '=':
                            #ignora o igual
                            continue
                        elif elemento.isalpha():
                            #verifica se é o elemento começa com letra
                            lexema_atual = elemento
                        elif elemento.isdigit(): 
                            #verifica se é dígito e quando encontrar, empilha
                            valor_atual = elemento
                            pilha.empilha(bloco_atual, lexema_atual, tipo, valor_atual)
                            lexema_atual = None
                        else:
                            #caso não entre na condição de cima, ele empilha sem valor, pois é apenas declaração de lexema.    
                            pilha.empilha(bloco_atual, elemento, tipo, None)

                    # Verificar se há um lexema sem valor no final
                    if lexema_atual is not None:
                        pilha.empilha(bloco_atual, lexema_atual, tipo, None)
                else:
                    #para casos em que o igual vem colado ao lexema nas várias declarações
                    tipo = tokens[0]
                    novos_tokens = []
                    
                    #variáveis auxiliares
                    iLexema_aux = 1
                    jValor_aux = 2
                    
                    for elemento in tokens:
                        novo_tokens = []
                        # Dividir elementos que contêm "=" colado
                        novo_tokens.extend(elemento.split('='))

                        # Remover elementos vazios após a divisão
                        novo_tokens = [elem for elem in novo_tokens if elem]
                        
                        if novo_tokens:
                            novos_tokens.extend(novo_tokens)
                            # Adicionar a atribuição à pilha
                            if len(novos_tokens) >= 3:
                                
                                lexema_index = iLexema_aux  # índice do lexema
                                valor_index = jValor_aux   # índice do valor
                                
                                # Verificar se o índice do lexema está dentro dos limites da lista
                                lexema = novos_tokens[lexema_index] if lexema_index < len(novos_tokens) else None
                                
                                # Verificar se o índice do valor está dentro dos limites da lista
                                valor = novos_tokens[valor_index].replace(",", "") if valor_index < len(novos_tokens) else None
                                
                                iLexema_aux += 2
                                jValor_aux += 2
                                
                                pilha.empilha(bloco_atual, lexema, tipo, valor)

        elif tokens[0] == 'PRINT':
            #quando identifica a palavra PRINT, pega o lexema e chama o método da "__str__" da pilha
            lexema = tokens[1]
            print(pilha.__str__(bloco_atual, lexema))

        elif tokens[0] == "FIM":
            #identifica qual bloco que está sendo fechado e armazena o nome dele
            bloco_atual = tokens[1]

            pilha.desempilha(bloco_atual)
            #desempilha o último elemento da lista_blocos, de forma a eliminar o nome do bloco fechado
            lista_blocos.pop()
            if len(lista_blocos) != 0:
                #bloco atual passa a ser o anterior, ou seja, o penúltimo aberto
                bloco_atual = lista_blocos[-1]

        else:
            '''
               condicional para casos onde há somente atribuições, sem declaração de tipo ou
               comandos de execução. Ex: [a=3, b="teste", "a = d"]
            '''
            resultado = []
            temp = []
            
            '''
            esse laço iterará sobre cada token recebido, separando-o em listas, para extrair
            o necessário: lexema e valor
            '''
            for elemento in tokens:
                if '=' in elemento:
                    temp.extend(elemento.split('=')) #ignora o '='
                elif elemento.startswith('“'): 
                    temp.append(elemento[1:])
                elif elemento.endswith('“'):
                    temp[-1] += ' ' + elemento[:-1]
                elif elemento.replace('.', '').isdigit():#verifica se o elemento é numero
                    temp.append(elemento)
                else:
                    temp.append(elemento)

            lista_reduzida = [elemento for elemento in temp if elemento != ''] #remove os elementos vazios da lista
            resultado = lista_reduzida
            
            # Se a lista resultante não estiver vazia
            if resultado:
                lexema = resultado[0]
                # Se o valor for uma variável existente na pilha
                if len(resultado) > 1 and resultado[1] in pilha.items.get(bloco_atual, {}):
                    # Verifica a existência do lexema tanto em resultado[0] quanto em resultado[1]
                    if resultado[0] in pilha.items.get(bloco_atual, {}) and resultado[1] in pilha.items.get(
                            bloco_atual, {}):
                        if pilha.items[bloco_atual][resultado[0]]['tipo'] == pilha.items[bloco_atual][resultado[1]]['tipo']:
                            # Obtemos o valor da variável existente e empilhamos
                            valor_existente = pilha.items[bloco_atual][resultado[1]]['valor']

                            pilha.empilha(bloco_atual, lexema, pilha.items[bloco_atual][resultado[1]]['tipo'],
                                          valor_existente)
                        else:
                            #não se pode atribuir valores quando as variáveis são de tipos diferentes
                            print(f"Erro. '{resultado[0]}' e '{resultado[1]}' são de tipos diferentes.")
                    else:
                        #caso tente atribuir valor sem declarar o tipo da variavel, infere.
                        lista_auxiliar = []
                        
                        #dividir em listas as atribuições
                        for elementos in tokens:
                            if elementos == '=':
                                continue
                            elif '=' in elementos:
                                elementos = elementos.split('=')
                                lista_auxiliar.extend(elementos)
                            else:
                                lista_auxiliar.append(elementos)

                        lexema_a_procurar = lista_auxiliar[1]
                        for bloco_id in reversed(list(pilha.items.keys())):
                            if lexema_a_procurar in pilha.items[bloco_id]:
                                valor_existente = pilha.items[bloco_id][lexema_a_procurar]['valor']
                                tipo_existente  = pilha.items[bloco_id][lexema_a_procurar]['tipo']
                                break  # interrompe o loop ao encontrar a primeira aparição

                        if valor_existente is not None:
                            pilha.empilha(bloco_atual, lista_auxiliar[0], tipo_existente, valor_existente)
                        else:
                            print(f"Erro. '{lexema_a_procurar}' não encontrado na pilha.")
                         
                else:
                    # Extrai o valor a partir do segundo elemento da lista resultado, unindo os elementos e removendo as aspas
                    valor = ' '.join(map(str, resultado[1:])).replace('“', '').replace('”', '')
                    #infere o tipo do valor extraído
                    tipo = determinar_tipo_lexema(valor)
                    
                    # Verifica se o lexema já existe no bloco atual da pilha
                    if bloco_atual in pilha.items and lexema in pilha.items[bloco_atual]:
                        
                        if pilha.items[bloco_atual][lexema]['tipo'] == tipo:
                             # Obtém o valor atual da variável existente
                            
                            valor_existente = pilha.items[bloco_atual][lexema]['valor']
                            
                            #Se o valor a ser atribuído é diferente do valor existente, atualiza o valor na pilha
                            if valor != valor_existente:
                                pilha.items[bloco_atual][lexema]['valor'] = valor
                        else:
                            print("Tipos não compatíveis.")
                    else:
                        # Caso o lexema não exista no bloco atual da pilha, empilha uma nova entrada
                        if '"' not in valor and '”' not in valor and tipo == 'CADEIA':
                            valor = "”" + valor + "”"
                        pilha.empilha(bloco_atual, lexema, tipo, valor)

def determinar_tipo_lexema(lexema):
    try:
        # Tenta converter o lexema para float
        if '.' in lexema:
            float_value = float(lexema)
            return 'NUMERO'
        else:
            # Se a conversão para float falhar, tenta converter para int
            int_value = int(lexema)
            return 'NUMERO'
    except ValueError:
        # Se ambas as conversões falharem, trata como uma cadeia de caracteres
        return 'CADEIA'

def main():
    # Inicializa uma lista para armazenar as linhas do programa
    programa_exemplo = []

    # Define o caminho do arquivo a ser lido
    caminho_arquivo = 'programa.txt'

    # Abre o arquivo e popula a lista programa_exemplo com as linhas do arquivo, removendo espaços em branco extras
    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            programa_exemplo.append(linha.strip())

    # Inicializa uma instância da classe Pilha
    pilha = Pilha()

    # Chama a função processar_programa para processar o programa usando a pilha
    processar_programa(programa_exemplo, pilha)

if __name__ == "__main__":
    main()