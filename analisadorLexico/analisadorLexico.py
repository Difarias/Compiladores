from tabulate import tabulate #biblioteca para parte visual das tabelas
import re #regex, apenas para uso de letras com til

tokens = {
    'numero': [],
    'moedas': [],
    'cadeia': [],
    'identificador': [],
    'operadores': [],
    'comentario': [],
    'parenteses_aberto': [],
    'parenteses_fechado': [],
    'virgula': [],
    'palavras_reservadas': [],
}

regex_letra_com_til = re.compile(r'[A-Za-zÀ-ÿ]~?[A-Za-zÀ-ÿ]*')

caracteresMinusculos = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
          'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
          'u', 'v', 'w', 'x', 'y', 'z', '_']

caracteresMaiusculos = [['A', 'B', 'C', 'D', 'E', 'F'], ['G', 'H', 'I', 'J',
          'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
          'U', 'V', 'W', 'X', 'Y', 'Z']]

numeros = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

palavras_reservadas = ['programa', 'fim_programa', 'se', 'senao',
                       'entao', 'imprima', 'leia', 'enquanto']

erros = {}

def ler_arquivo(nome_arquivo):
    """
    Tenta abrir um arquivo com o nome especificado no modo de leitura ('r').

    Args:
        nome_arquivo (str): O nome do arquivo a ser aberto.

    Returns:
        bool: True se o arquivo foi aberto com sucesso, False se o arquivo não foi encontrado.
    """

    global arquivo

    try:
        arquivo = open(nome_arquivo, 'r')
        return True
    except FileNotFoundError:
        return False
    
def inicializar_contadores():

    """
    Inicializa variáveis globais para controle do analisador léxico.

    Esta função reconfigura as variáveis globais 'arquivo', 'estados', 'linha',
    'coluna', 'char', 'conteudo' e 'tem_erro' para seus valores iniciais, 
    preparando-as para uma nova análise léxica.

    Args:
        Nenhum.

    Returns:
        Nenhum.
    """

    global arquivo, estados, linha, coluna, char, conteudo, tem_erro

    estados = 0
    linha = 1
    coluna = -1
    char = ''
    conteudo = ''
    tem_erro = False
        
def gera_erro(tipo_erro, linha_erro = -1, coluna_erro = -1):
    
    """
    Gera um erro léxico e configura a flag de erro global.

    Esta função é usada para gerar erros léxicos durante o processamento do analisador léxico.
    Ela permite especificar o tipo de erro, a linha e a coluna onde o erro ocorreu.

    Args:
        tipo_erro   (str): O tipo de erro léxico ocorrido.
        linha_erro  (int): O número da linha onde o erro ocorreu. Padrão é -1.
        coluna_erro (int): O número da coluna onde o erro ocorreu. Padrão é -1.

    Returns:
        int: retorna 0 para continuar a verificação do restante do arquivo, fazendo a análise.
    """
    
    global tem_erro

    if linha_erro > -1 and coluna_erro > -1:
        alerta_erro = (f"Erro léxico na linha {linha_erro} coluna {coluna_erro}: {tipo_erro}")
        erros[linha_erro] = {'coluna':coluna_erro, 'alerta':alerta_erro}
        tem_erro = True
        return 0
    else:
        print('Não foi possível identificar a ocorrência do erro!')
        tem_erro = True
        return 0

def verifica_caminho(arquivo):
    
    """
    Verifica o caminho no analisador léxico no caso do primeiro caractere ser uma letra no intervalo [A-F],
    pois, baseado na regra definida, palavras começadas com essas letras, podem ser moedas ou números.

    Esta função lê um caractere do arquivo, atualiza a coluna e toma decisões com base no caractere lido.

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.

    Returns:
        tuple: Uma tupla contendo o novo estado (int), e o caractere lido(char).
    """

    global estados, coluna

    if estados == 50:
        char = arquivo.read(1)
        coluna += 1
        
        if char == '$':
            return 4, char
        elif char in numeros or char in caracteresMaiusculos[0] or char == '.':
            return 40, char

def processar_cadeia(arquivo, palavra_aux):

    """
    Processa uma cadeia de caracteres no analisador léxico.

    Esta função é responsável por processar uma cadeia de caracteres delimitada por aspas duplas no analisador léxico.
    Ela lê caracteres do arquivo, atualiza as variáveis de linha e coluna, e armazena o conteúdo da cadeia.

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual e servir para inserir no lexema lido.

    Returns:
        Nenhum valor de retorno explícito.
    """
    
    global estados, linha, coluna, conteudo

    linha_inicio = linha
    coluna_inicio = coluna

    if estados == 1:
        char = arquivo.read(1)
        coluna += 1
        le_cadeia = True

        while le_cadeia:
            conteudo += char

            if char == '\n':
                linha +=1
                coluna = -1    
            palavra_aux += char

            if char == '"':
                estados = 2
                le_cadeia = False
                break
            elif char == '\n' or char == '' or char == '': 
                char = arquivo.read(1)
                while char != '\n' and char != '': #Lê cadeias que não foram fechadas na mesma linha que começou
                    palavra_aux += char              
                    char = arquivo.read(1)
                    conteudo += char
                    
                    if char == '\n':
                        palavra_aux += char
                        coluna_inicio = 0
                        linha += 1

                estados = 29
                if estados == 29:
                    estados = gera_erro("cadeia não fechada",linha_inicio+1,coluna_inicio)
                    le_cadeia = False
                    break
            else:
                coluna += 1 #incrementa a coluna sempre que for lendo caracteres

            char = arquivo.read(1)
            
        if estados == 2:
            tokens['cadeia'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
            estados = 0

def processar_moedas(arquivo, palavra_aux):

    """
    Processa moedas no analisador léxico.

    Esta função é responsável por processar moedas no analisador léxico, seguindo uma série de estados (baseado no autômato)
    e regras (definidas no projeto).
    Ela lê caracteres do arquivo, atualiza as variáveis de linha e coluna, e constrói a moeda.

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual.

    Returns:
        Nenhum valor de retorno explícito.
    """

    global estados, linha, coluna, conteudo

    linha_inicio  = linha
    coluna_inicio = coluna

    if estados == 3:
        char = arquivo.read(1)
        conteudo += char
        palavra_aux += char
        coluna += 1

        if char == '$':
            estados = 4
        else:
            #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
            while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.': 
                        char = arquivo.read(1)
                        conteudo += char
                        coluna += 1

                        if char == '\n':
                            linha += 1
                            coluna = -1

                        palavra_aux += char

            estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)
            
    if estados == 4:
        char = arquivo.read(1)
        palavra_aux += char
        conteudo += char
        coluna += 1

        if char in numeros:
            estados = 5
        else:
            #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
            while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.': 
                    char = arquivo.read(1)
                    conteudo += char
                    coluna += 1

                    if char == '\n':
                        linha += 1
                        coluna = -1

                    palavra_aux += char

            estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)
            
    if estados == 5:  #o estado 5 está fora da identação pois é usado na rotina do [a...z] tbm
        char = arquivo.read(1)
        palavra_aux += char
        conteudo += char
        coluna += 1

        while char in numeros:
            char = arquivo.read(1)
            conteudo += char
            palavra_aux += char
            coluna += 1

            if char == '.':
                estados = 6
            elif char == '\n' or char == '' or char == ' ':
                conteudo += char
    
                if char == '\n':
                    linha += 1
                    coluna = -1

                estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)
                break
            
        if estados == 6:
            char = arquivo.read(1)
            conteudo += char
            palavra_aux += char
            coluna += 1

            if char in numeros: 
                estados = 7
            else:
                #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
                while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.': 
                    char = arquivo.read(1)
                    conteudo += char
                    coluna += 1

                    if char == '\n':
                        linha += 1
                        coluna = -1

                    palavra_aux += char
                
                estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)              
                
        if estados == 7:
            char = arquivo.read(1)
            palavra_aux += char
            conteudo += char
            coluna += 1

            if char in numeros:
                char = arquivo.read(1)
                palavra_aux += char
                coluna += 1

                if char not in numeros: #para nao aceitar moedas com mais de 2 casas decimais
                    conteudo += char

                    if char == '\n':
                        linha += 1
                        coluna = -1
                
                    estados = 8
                else:
                    #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
                    while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.': 
                        char = arquivo.read(1)
                        conteudo += char
                        coluna += 1

                        if char == '\n':
                            linha += 1
                            coluna = -1

                        palavra_aux += char
                    
                    estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)
            else:
                #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
                while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.': 
                    char = arquivo.read(1)
                    conteudo += char
                    coluna += 1

                    if char == '\n':
                        linha += 1
                        coluna = -1
                        
                    palavra_aux += char
                
                estados = gera_erro("moeda mal formatada",linha_inicio,coluna_inicio)
                
        if estados == 8:
            tokens['moedas'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})    
            estados = 0
            
def processar_numeros(arquivo, char, palavra_aux):
    
    """
    Processa números no analisador léxico.

    Esta função é responsável por processar números no analisador léxico, seguindo uma série de estados e regras.
    Ela lê caracteres do arquivo, atualiza as variáveis de linha e coluna e constrói a palavra relacionada ao número.
    
    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        char (str): O caractere atual sendo processado. Foi-se necessário passar o primeiro caractere lido como parâmetro pois,
                    estava sendo perdido quando o número tinha uma letra no início e logo após um ponto. 
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual.

    Returns:
        Nenhum valor de retorno explícito.
    """

    global estados, linha, coluna, conteudo

    linha_inicio = linha
    coluna_inicio = coluna
    last_position = 0 #variável auxiliar que resolverá o problema do parênteses "colado" no arquivo.Ex: imprima(37.3e2), perdia o ')'. 
    last_char = None  #variável auxiliar para guardar os caracteres lidos

    if estados == 17:
        while char in numeros or char in caracteresMaiusculos[0]:
            char = arquivo.read(1)
            conteudo += char
            coluna += 1

            if char == '\n':
                linha += 1
            
            palavra_aux += char

            if char == '.':
                estados = 18
            elif char == 'e':
                estados = 19
            elif char == ' ' or char == '\n' or char == '' or char == ',':
                if char == '\n':
                    coluna = -1
                
                estados = 27
            elif char in numeros or char in caracteresMaiusculos[0]:
                pass 
            else:
                #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
                while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros: 
                        char = arquivo.read(1)
                        conteudo += char

                        if char == '\n':
                            linha += 1
                            coluna = -1
                            
                        palavra_aux += char

                estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)        
                break

        if estados == 18:
            char = arquivo.read(1)
            palavra_aux += char
            conteudo += char
            coluna += 1

            if char in caracteresMaiusculos[0] or char in numeros:
                estados = 21  # Aceitar letras na parte fracionária
            else:
                #irá varrer todo o conteudo e armazenará ele em uma varíavel para ser mostrada no erro
                while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros or char == '.' or char == '-': #para pegar a palavra inteira errada
                    char = arquivo.read(1)
                    conteudo += char

                    if char == '\n':
                        linha += 1
                        coluna = -1

                    palavra_aux += char
                
                estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)

            if estados == 21:
                while char in numeros or char in caracteresMaiusculos[0]:
                    char = arquivo.read(1)
                    palavra_aux += char
                    conteudo += char
                    coluna += 1

                    if char == 'e':
                        estados = 22
                    elif char == ' ' or char == '\n' or char == '':
                        if char == '\n':
                            coluna = -1

                        estados = 28
                    elif char in numeros or char in caracteresMaiusculos[0]:
                        pass
                    else:
                        estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)
                        break

                if estados == 22:
                    char = arquivo.read(1)
                    palavra_aux += char
                    conteudo += char
                    coluna += 1

                    if char == '-':
                        estados = 24
                    else:
                        pass
                    
                    while char in numeros or char in caracteresMaiusculos[0]:
                        
                        if char == '\n':
                            linha += 1
                            coluna = -1

                        if char !='(':
                            last_position = arquivo.tell() #armazena a posição atual do arquivo

                        char = arquivo.read(1)
                        last_char = char #ultimo caractere lido
                        palavra_aux += char
                        conteudo += char
                        coluna += 1

                        if char == ')':  
                            arquivo.seek(last_position) #aqui volta uma posição no arquivo baseado na ultima letra/número aceito 
                            char = last_char
                            conteudo = conteudo[:-1] #para não vir duplicado o último caractere
                            palavra_aux = palavra_aux[:-1]   
                            estados = 23

                    if estados == 24:
                        char = arquivo.read(1)
                        palavra_aux += char
                        conteudo += char
                        coluna += 1

                        if char in numeros or char in caracteresMaiusculos[0]:
                            estados = 25
                        else:
                            if char == '\n':
                                linha += 1
                                coluna = -1

                            estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)

                        if estados == 25:
                            while char in numeros or char in caracteresMaiusculos[0]:
                                char = arquivo.read(1)
                                conteudo += char
                                coluna += 1

                                if char == '\n':
                                    linha += 1
                                    coluna = -1

                                if char !='(':
                                    last_position = arquivo.tell() #armazena a posição atual do arquivo

                                char = arquivo.read(1)
                                last_char = char #ultimo caractere lido
                                palavra_aux += char
                                conteudo += char
                                coluna += 1

                                if char == ')':  
                                    arquivo.seek(last_position) #aqui volta uma posição no arquivo baseado na ultima letra/número aceito 
                                    char = last_char
                                    conteudo = conteudo[:-1] #para não vir duplicado o último caractere
                                    palavra_aux = palavra_aux[:-1]   
                                    estados = 48
      
                                if char == ' ' or char == '\n' or char == '':
                                    if char == '\n':
                                        linha += 1
                                        coluna = -1
                                    estados = 48

                            if estados == 51:
                                tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                                estados = 0
                        
                            if estados == 48:
                                    tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                                    estados = 0

                    if estados == 23:
                        tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                        estados = 0

            if estados == 28:
                if char == '\n':
                    linha += 1

                tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                estados = 0

        if estados == 19:
            char = arquivo.read(1)
            palavra_aux += char
            conteudo += char
            coluna += 1
            
            if char in numeros or char in caracteresMaiusculos[0]:
                while char in numeros or char in caracteresMaiusculos[0]:
                    char = arquivo.read(1)
                    palavra_aux += char
                    conteudo += char
                    coluna += 1

                    if char == ' ' or char == '\n' or char == '' or char == ',':
                        if char == '\n':
                            coluna = -1
                                   
                        estados = 20
                    elif char not in numeros and char not in caracteresMaiusculos[0]:
                        while char in caracteresMinusculos or any(char in sublista for sublista in caracteresMaiusculos) or char in numeros: 
                            char = arquivo.read(1)
                            palavra_aux += char
                            conteudo += char
                            coluna += 1

                        estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)
                        break 
            else:
                while char in caracteresMinusculos or char in caracteresMaiusculos[1] or char in numeros or char == '-':
                    char = arquivo.read(1)
                    palavra_aux += char
                    conteudo += char
                    coluna += 1

                estados = gera_erro("Número mal formatado",linha_inicio,coluna_inicio)
            
            
            if estados == 20:
                if char == '\n':
                    linha += 1
                    conteudo += char
                
                tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                estados = 0

        if estados == 27:
            tokens['numero'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
            estados = 0

def processar_identificador(arquivo, palavra_aux):
    
    """
    Processa identificadores no analisador léxico.

    Esta função é responsável por processar identificadores no analisador léxico, seguindo uma série de estados e regras.
    Ela começa com um '<' e passa a ler os próximos caracteres, em busca de achar o '>', para aceitar o token ou, caso não
    ache, gerar um erro. 
    
    Obs: Tem-se a chance de não ter mais nada ou ser um '=' e aceitar esses caracteres como operadores.

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual.

    Returns:
        Nenhum valor de retorno explícito.
    """
    
    global estados, linha, coluna, conteudo

    linha_inicio = linha
    coluna_inicio = coluna

    char = arquivo.read(1)
    conteudo += char
    palavra_aux += char
    coluna += 1

    if char == '=': #<=
        estados = 42
    elif char in caracteresMinusculos:
        estados = 10
    elif char == '\n' or char == ' ' or char == '':
        conteudo += char

        if char == '\n':
            linha += 1
            coluna = -1
    
        estados = 52 #<
    else:
        if char == '\n':
            linha += 1

        estados = 54

    if estados == 42: 
        char = arquivo.read(1)
        conteudo += char
        coluna += 1

        if char == '' or char == ' ':
            tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
            estados = 0
        else:
            palavra_aux += char
            estados = gera_erro('erro de operadores',linha_inicio, coluna_inicio)

    if estados == 10:
        while char in caracteresMinusculos or char in caracteresMaiusculos[0] or char in numeros:
            coluna += 1
            char = arquivo.read(1)
            conteudo += char
            palavra_aux += char

            if char == '>': #onde fecha o identificador
                coluna += 1
                estados = 11
            elif char == '\n' or char == '' or char == ' ':
                conteudo += char
                if char == '\n':
                    linha += 1
                    coluna = -1

                estados = gera_erro("identificador mal formatado",linha_inicio, coluna_inicio)
                break

    if estados == 54:
        while char in caracteresMinusculos or char in caracteresMaiusculos[0] or char in numeros:
            char = arquivo.read(1)
            palavra_aux += char
            conteudo += char
            coluna += 1

        estados = gera_erro('identificador mal formatado',linha_inicio, coluna_inicio)

    if estados == 11:
        tokens['identificador'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 52:
        tokens['operadores'].append({'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

def processar_comentario(arquivo, palavra_aux):

    """
    Processa comentários no analisador léxico.

    Esta função é responsável por processar comentários no analisador léxico. Ela lê caracteres do arquivo e identifica
    comentários em diferentes formatos, seguindo uma série de estados e regras. Os comentários podem ser no estilo Python 
    usando o # ou blocos de comentários ('''alguma coisa\n''').

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual.

    Returns:
        Nenhum valor de retorno explícito.
    """

    global estados, linha, coluna, conteudo
    
    linha_inicio = linha
    coluna_inicio = coluna
    ocorrencia_aspas = False #usado na forma de comentário em bloco

    if estados == 13:
        coluna += 1 
        while True:
            char = arquivo.read(1)
            conteudo += char
            palavra_aux += char

            if not char:
                break

            if char == '\n':  
                linha += 1
                coluna = -1
                estados = 15
                break

        if estados == 15:
            tokens['comentario'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
            estados = 0
    else:
        if estados == 14:
            char = arquivo.read(1)
            conteudo += char
            coluna += 1
            palavra_aux += char

            if char == "'":
                char = arquivo.read(1)
                conteudo += char
                coluna += 1
                palavra_aux += char

                if char == "'":
                    char = arquivo.read(1)
                    conteudo += char
                    coluna += 1

                    if char == '\n':
                        linha += 1
                        coluna = 0

                    palavra_aux += char
                   
                    while char != "'":
                        if char == '\n':
                            coluna = -1
                        elif not char:
                            palavra_aux = ''
                            break

                        char = arquivo.read(1)
                        conteudo += char
                        coluna += 1
                        palavra_aux += char

                    if char == "'":
                        linha += 1
                        ocorrencia_aspas = True
                    else:
                        while char and char != '\n':
                            if char == '\n':
                                linha += 1
                                coluna = 0
                            char = arquivo.read(1)
                            conteudo += char
                            coluna += 1
                            palavra_aux += char

                        estados = gera_erro("comentario não fechado",linha_inicio, coluna_inicio)
                else:
                    while char and char != '\n':
                            if char == '\n':
                                linha += 1
                                coluna = 0

                            char = arquivo.read(1)
                            conteudo += char
                            coluna += 1
                            palavra_aux += char

                    estados = gera_erro("comentario não fechado",linha_inicio, coluna_inicio)

                if ocorrencia_aspas == True:
                    char = arquivo.read(1)
                    conteudo += char
                    coluna += 1
                    palavra_aux += char

                    if char == "'":
                        char = arquivo.read(1)
                        conteudo += char
                        coluna += 1
                        palavra_aux += char

                        if char == "'":
                            estados = 16
                        else:
                            while char and char != '\n':
                                if char == '\n':
                                    linha += 1
                                    coluna = 0

                                char = arquivo.read(1)
                                conteudo += char
                                coluna += 1
                                palavra_aux += char

                            estados = gera_erro("comentario não fechado",linha_inicio, coluna_inicio)
                    else:
                        while char and char != '\n':
                            if char == '\n':
                                linha += 1
                                coluna = 0

                            char = arquivo.read(1)
                            conteudo += char
                            coluna += 1
                            palavra_aux += char

                        estados = gera_erro("comentario não fechado",linha_inicio, coluna_inicio)
                            

                    if estados == 16:
                        tokens['comentario'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                        linha -= 1
                        estados = 0
            else:
                while char and char != '\n':
                        char = arquivo.read(1)
                        conteudo += char
                        palavra_aux += char

                estados = gera_erro("comentario não fechado",linha_inicio, coluna_inicio)

def processar_operadores(arquivo, palavra_aux):
    
    """
    Processa operadores no analisador léxico.

    Esta função é responsável por processar operadores no analisador léxico, identificando diferentes operadores
    e seguindo regras específicas para cada um. Ela lê caracteres do arquivo e determina o tipo de operador, como
    atribuição, igualdade, aritmético, etc.

    Args:
        arquivo (file): O arquivo de entrada a ser analisado.
        palavra_aux (str): Uma variável auxiliar para construir a palavra atual.

    Returns:
        Nenhum valor de retorno explícito.
    """
    
    global estados, linha, coluna, conteudo

    linha_inicio = linha
    coluna_inicio = coluna

    if estados == 43:
        char = arquivo.read(1)
        palavra_aux += char
        conteudo += char
        coluna += 1

        if char == '=':
            estados = 44
        else:
            estados = gera_erro("erro de operadores",linha_inicio, coluna_inicio)
            
        if estados == 44:
            char = arquivo.read(1)
            conteudo += char
            coluna += 1

            if char == '' or char == ' ':
                tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                estados = 0
            else:
                palavra_aux += char
                estados = gera_erro("erro de operadores", linha_inicio, coluna_inicio)
    
    if estados == 37:  
        char = arquivo.read(1)
        conteudo += char
        palavra_aux += char
        coluna += 1

        if char == '=':
            estados = 38
        else:
            estados = gera_erro("erro de operadores",linha_inicio, coluna_inicio)

        if estados == 38:
            char = arquivo.read(1)
            conteudo += char
            coluna += 1
            if char == '' or char == ' ':
                tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                estados = 0
            else:
                palavra_aux += char
                estados = gera_erro("erro de operadores",linha_inicio, coluna_inicio)
    
    if estados == 36:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0
    
    if estados == 35:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0
    
    if estados == 30:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 31:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 32:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 33:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 34:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 39:
        coluna_inicio = coluna
        tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 40:
        coluna_inicio = coluna
        char = arquivo.read(1)
        conteudo += char
        coluna += 1

        if char == '\n':
            linha += 1
            coluna = -1

        palavra_aux += char
        if char == '=':
            estados = 41
        elif char == '\n' or char == ' ' or char == '':
            estados = 51
        else:
            estados = gera_erro("erro de operadores",linha_inicio, coluna_inicio)
            
        if estados == 41:
            char = arquivo.read(1)
            conteudo += char
            coluna += 1
            if char == '' or char == ' ':
                tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
                estados = 0
            else:
                palavra_aux += char
                estados = gera_erro("erro de operadores",linha_inicio, coluna_inicio)

        if estados == 51:
            tokens['operadores'].append({ 'palavra:':palavra_aux, 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
            estados = 0

def processar_delimitadores():

    """
    Processa delimitadores no analisador léxico.

    Esta função é responsável por processar delimitadores no analisador léxico, identificando diferentes delimitadores
    como parênteses abertos, parênteses fechados e vírgulas. Ela adiciona esses delimitadores à lista de tokens apropriada
    com informações sobre a linha e a coluna onde foram encontrados.

    Obs: Não há a necessidade de adicionar esses caracteres como lexema, uma vez que são únicos.

    Args:
        Nenhum argumento é necessário, pois os estados internos globais são usados para determinar os delimitadores.

    Returns:
        Nenhum valor de retorno explícito.
    """

    global estados, coluna

    linha_inicio = linha
    coluna_inicio = coluna

    if estados == 45:
        tokens['parenteses_aberto'].append({ 'palavra:':'', 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 46:
        tokens['parenteses_fechado'].append({ 'palavra:':'', 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

    if estados == 47:
        tokens['virgula'].append({ 'palavra:':'', 'Linha:':linha_inicio, 'Coluna:':coluna_inicio})
        estados = 0

def processar_palavrasReservadas(arquivo, char):
    
    """
    Processa palavras reservadas no analisador léxico.

    Esta função é responsável por identificar e processar palavras reservadas no analisador léxico. Ela verifica se uma
    sequência de caracteres forma uma palavra reservada, como "se", "enquanto", "fim_programa" ou outras palavras-chave,
    adicionando-as na lista de tokens correspondente.     

    Args:
        arquivo (file): O arquivo de entrada que está sendo analisado.
        char (str): O caractere atual lido do arquivo.

    Returns:
        Nenhum valor de retorno explícito, mas a função atualiza o estado global 'estados' conforme necessário.
    """
    
    global estados, linha, coluna, conteudo
    
    linha_inicio = linha
    coluna_inicio = coluna

    if estados == 49:
        palavra_aux = ''
        palavra_aux += char
        last_char = None

        char = arquivo.read(1)
        conteudo += char
        coluna += 1

        while (char in caracteresMinusculos or char in caracteresMaiusculos[0] or char in numeros or regex_letra_com_til.match(char)):
            palavra_aux += char
            last_char = char  # Armazena o último caractere lido
            char = arquivo.read(1)

            if char !='(':
                last_position = arquivo.tell()

            conteudo += char
            coluna += 1

            if char == '\n':
                linha += 1
                coluna = -1

            if palavra_aux in palavras_reservadas:
                if palavra_aux == "se" and not char.isalnum(): #isalnum() verifica se o próximo char é um número ou letra, retorna booleano
                    estados = 26
                    break
                elif not char.isalnum():
                    estados = 26

        if char == '(': #aqui volta uma posição no arquivo baseado na ultima letra da palavra reservada aceita
            arquivo.seek(last_position) 
            char = last_char
            conteudo = conteudo[:-1] # apaga do conteudo o caractere (, para n ficar duplicado 

        if estados == 26:
            tokens['palavras_reservadas'].append({ 'palavra:': palavra_aux, 'Linha:': linha_inicio, 'Coluna:': coluna_inicio})
            estados = 0
        else:
            estados = gera_erro(f"{palavra_aux} não é palavra reservada", linha_inicio, coluna_inicio)
      
def main():
    global estados, linha, coluna, conteudo, char

    inicializar_contadores()
    
    resposta_arquivo = ler_arquivo('ex3.cic')
    palavra_aux = ''
    
    if resposta_arquivo == True:
        while True:
            if estados == 0:
                palavra_aux = ''
                
                if char == '\n':
                    linha += 1
                    coluna = -1
                
                char = arquivo.read(1)
                conteudo += char
                
                palavra_aux += char

                if not char:
                    break 

                if char == '"': 
                    coluna += 1
                    estados = 1
                    processar_cadeia(arquivo, palavra_aux)
                elif char in caracteresMaiusculos[1]:  # moedas
                    coluna += 1
                    estados = 3
                    processar_moedas(arquivo, palavra_aux)
                elif char in caracteresMaiusculos[0]:
                    estados = 50
                    resposta, prox_char = verifica_caminho(arquivo)

                    if resposta == 4: #moedas
                        palavra_aux += prox_char
                        conteudo += prox_char
                        estados = 4
                        processar_moedas(arquivo, palavra_aux)
                    else:             #números
                        palavra_aux += prox_char
                        estados = 17
                        processar_numeros(arquivo, char, palavra_aux)
                elif char == '<':
                    coluna += 1
                    estados = 9
                    processar_identificador(arquivo, palavra_aux)
                elif char == '#':
                    coluna += 1
                    estados = 13
                    processar_comentario(arquivo, palavra_aux)
                elif char == "'":
                    coluna += 1
                    estados = 14
                    processar_comentario(arquivo, palavra_aux)
                elif char in numeros:
                    coluna += 1
                    estados = 17
                    processar_numeros(arquivo, char, palavra_aux)
                elif char == '+':
                    coluna += 1
                    estados = 30
                    processar_operadores(arquivo, palavra_aux)
                elif char == '-':
                    coluna += 1
                    estados = 31
                    processar_operadores(arquivo, palavra_aux)
                elif char == '*':
                    coluna += 1
                    estados = 32
                    processar_operadores(arquivo, palavra_aux)
                elif char == '~':
                    coluna += 1
                    estados = 33
                    processar_operadores(arquivo, palavra_aux)
                elif char == '/':
                    coluna += 1
                    estados = 34
                    processar_operadores(arquivo, palavra_aux)
                elif char == '&':
                    coluna += 1
                    estados = 35
                    processar_operadores(arquivo, palavra_aux)
                elif char == '|':
                    coluna += 1
                    estados = 36
                    processar_operadores(arquivo, palavra_aux)
                elif char == '!':
                    coluna += 1
                    estados = 37
                    processar_operadores(arquivo, palavra_aux)
                elif char == '=':
                    coluna += 1
                    estados = 39
                    processar_operadores(arquivo, palavra_aux)
                elif char == '>':
                    coluna += 1
                    estados = 40
                    processar_operadores(arquivo, palavra_aux)
                elif char == ':':
                    coluna += 1
                    estados = 43
                    processar_operadores(arquivo, palavra_aux)
                elif char == '(':
                    coluna += 1
                    estados = 45
                    processar_delimitadores()
                elif char == ')':
                    coluna += 1
                    estados = 46
                    processar_delimitadores()
                elif char == ',':
                    coluna += 1
                    estados = 47
                    processar_delimitadores()
                elif char in caracteresMinusculos:
                    coluna += 1
                    estados = 49
                    processar_palavrasReservadas(arquivo, char)
                elif char == '' or char == ' ':
                    coluna += 1

        arquivo.close()
        
        if tem_erro == False:

            dados_tabela = []

            #adiciona na lista todos os dados referente aos tokens lidos
            for tipo, itens in tokens.items():
                for item in itens:
                    linha = item['Linha:']
                    coluna = item['Coluna:']
                    palavra = item['palavra:']
                    dados_tabela.append([linha, coluna, tipo, palavra])
            
            #irá organizar esses dados em ordem de aparição baseado na primeira coluna da tabela e caso sejam iguais, usa a segunda para desempate
            dados_tabela.sort(key=lambda x: (x[0], x[1]), reverse=False)

            #usa a biblioteca tabulate apenas para organização, escolhendo-se o conteúdo, o estilo da tabela e seus cabeçalhos
            tabela_lexemas = tabulate(dados_tabela, headers=["Linha", "Coluna", "Tipo", "Lexema"], tablefmt="grid")

            #faz-se uma lista com o nome dos tokens e o tamanho de suas ocorrências na lista de tokens
            lista_de_quantidades = [
                ('Numeros', len(tokens['numero'])),
                ('Moedas', len(tokens['moedas'])),
                ('Cadeias', len(tokens['cadeia'])),
                ('Identificadores', len(tokens['identificador'])),
                ('Operadores', len(tokens['operadores'])),
                ('Comentarios', len(tokens['comentario'])),
                ('Parenteses_aberto', len(tokens['parenteses_aberto'])),
                ('Parenteses_fechado', len(tokens['parenteses_fechado'])),
                ('Virgulas', len(tokens['virgula'])),
                ('Palavras Reservadas', len(tokens['palavras_reservadas']))
            ]

            #calcula a soma das quantidades de tokens em todas as categorias da lista lista_de_quantidades.
            total_tokens = ["Total", sum(row[1] for row in lista_de_quantidades)]

            lista_de_quantidades.sort(key=lambda x: x[1], reverse=True) #ordem decrescente no código
            lista_de_quantidades.append(total_tokens)

            tabela_qntd = tabulate(lista_de_quantidades, headers=["Categoria", "Quantidade de Tokens"], tablefmt="grid")

            print(tabela_lexemas)
            print('\n')
            print(tabela_qntd)
        else:
            #divide o conteudo a cada quebra de linha
            linhas_arquivo = conteudo.split('\n')
            
            print('\nConteúdo Lido:\n')
            #Este é um loop que itera pelas linhas do arquivo, usando a função enumerate para obter tanto o índice (i) quanto o conteúdo da linha (linha_arquivo).
            for i , linha in enumerate(linhas_arquivo, start=1):
                print(f'[{i}] {linha}')

                #se o i for igual a linha salva na lista de erro, ele mostrará o erro nessa linha, logo abaixo dela
                if i in erros:
                    erro_info = erros[i]
                    coluna = erro_info['coluna']
                    mensagem = erro_info['alerta']

                    seta = '-' * (coluna + 4)  + '^'
                    print(seta)
                    print(mensagem)
    else:
        print("[ERRO]\nArquivo não se encontra no diretório atual")

if __name__ == "__main__":
    main()
