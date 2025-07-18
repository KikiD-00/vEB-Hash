# vEB-Hash
Trabalho de estrutura de dados árvore Van Emde Boas com Hash table
<h1>Trabalho de Estrutura de dados</h1>

<h3>Contexto:</h3> 


Como pedido no enuncido o código implementa uma árvore Van Emde Boas, de 32 bits, com tabela de dispersão, fazendo as operações de: Predescessor; Sucessor; Inserção e Remoção, e também table doubling/halving. Para isso, foram usadas como base as anotações em sala de aula, o livro "Algoritmos: Teoria e Prática" e as anotações dos cursos "Advanced Data Structures" e "Design and Analysis of Algorithms" do MIT.


<h3>Van Emde Boas</h3> 


A Van Emde Boas é uma árvore que suporta operações de fila de prioridades como Remoção e Inserção, além de outras operações como sucessor e predescessor em, pior caso, O(lg lg n) (CORMEN et al., 2009). Uma de suas principais caractéristicas são suas chaves que recebem apenas valores inteiros, universo em potência de 2 e sua estrutura recursiva, com clusters e sumário  Para economizar espaço, uma boa alternativa é colocar uma tabela de dispersão no lugar do cluster. 


Dessa forma, o código inicia criando uma classe chamada vEB, que cotém todas as operações funções necessárias para o funcionamento de uma Van Emde Boas. A primeira função da classe inicializa a VEB, estabelecendo um universo de tamanho 32 bits e o valor mínimo e máximo, dentro da VEB. Essa função também garante que a capacidade da árvore é uma potência de 2 e que ela começará vazia. Como a Van Emde Boas é uma estrutura recursiva, é necessário criar um caso base. Logo se o universo for muito pequeno (<=2) não haverá a necessidade nem de clusters nem de resumo, se não, ela reduzirá o tamanho do universo pela raiz quadrada em cada nível de recursão, assim como explicado por Cormen et al. (2009), e os clusters passão a existir, e o resumo será usado para resumir quais clusters estão ocupados, porém nesse código o cluster é uma tabela de dispersão. Todavia, antes de fazer isso, o código também conta o número total de bits e os reduz pela metade para garantir que os clusters não sejam muito grandes.


```python
class vEB:
    def __init__(self, universe_size=2**32):
        self.universe_size = universe_size
        self.min = None
        self.max = None
        self.capacity = 1 << (universe_size.bit_length())
        self.size = 0
        if universe_size <= 2:
            self.summary = None
            self.cluster = None
        else:
            total_bits = universe_size.bit_length() - 1  
            half = total_bits // 2 

            self.lower_sqrt = 1 << half
            self.upper_sqrt = 1 << (total_bits - half)

            self.summary = None
            self.cluster = HashTable()

```


As quatro funções seguintes são escenciais para o funcionamento da estrutura da árvore, em geral. A primeira função conta quantos bits são necessários para representar o valor de x em binário. Por meio de um laço que se repete enquanto x for maior do que 0, os bits vão sendo contados e, a cada shift, o bit menos significativo é descatado até chegar em 0, então a função sai do laço e retorna bit lengh. Como explicado por Cormen et al. (2009), as funções high, low e index ajudaram a manter a recursividade da estrutura. Enquanto a função high retorna o número do grupo onde x está localizado, a função low retorna a posição do x dentro do grupo e a função index retorna o valor original de x, utilizando as funções anteriores.


```python

    def bit_length(self, x):
        length = 0
        while x > 0:
            x >>= 1
            length += 1
        return length
    
    def high(self, x):
        return x // self.lower_sqrt
    
    def low(self, x):
        return x % self.lower_sqrt
    
    def index(self, high, low):
        return (high * self.lower_sqrt) + low

```


As próximas duas funções são usadas para encontrar o valor mínimo e máximo da árvore


```python

    def minimum(self):
        return self.min

    def maximum(self):
        return self.max

```

Após isso usamos a função member para determinar se o valor x está presente na árvore. Por isso, primeiramente é preciso verificar se a árvore está vazia, se ela estiver, significa que nada está presente na árvore, então retorna False. Caso o contrário, verifica-se se o x é igual ao valor minímo ou máximo, se for, então x está presente na árvore e retornará true. De outro modo, passamos para o caso base que verifica se o universo só tem 2 elementos, se esse for o caso significa que o x realmente não está presente na árvore, retornando falso. Mas se x não for um caso base nem o mínimo e o máximo, é retornado o resultado da chamada recursiva. Porém, para que a função funcione sem erros é nescessário dividir a chamada recursiva em partes, verificado primeiro se o cluster está vazio, para apenas depois retornar. 


Em geral, no python, esse tipo de verificação "if alguma coisa is None" é necessária para que o código funcione da manira correta, por isso ela sempre aparece ao longo do código.


```python

    def member(self, x:int)-> bool:
        if self.min is None:
            return False
        if x == self.min or x == self.max:
            return True
        if self.universe_size == 2:
            return False
        high = self.high(x)
        low = self.low(x)
        child = self.cluster[high]
        if child is None:
            return False
        return child.member(low)

```


<h4>Sucessor</h4> 


A função seguinte implementa a operação de sucessor. O caso base, novamente, verifica se o universo só tem 2 elementos, sendo esse o caso, só existem duas possibilidades, x é 0 e seu sucessor é 1 ou x é 1 e seu sucessor não existe. Se não for o caso base, verifica-se se o x é menor que o menor elemento da árvore, se for, ele é o sucessor de x e a função retorna o elemento minínimo. Se não, já sabendo que o universo é maior que 2 e que x não é menor que valor minímo, faz-se a verificação se x é menor que o valor máximo de seu cluster, dessa forma é possível confirmar se o sucessor de x está dentro do mesmo cluster ou não. Se o sucessor estiver no mesmo cluster, ele retornará o sucessor de x, se não, isso quer dizer que x é o valor máximo no cluster, logo será necessário procurar o seu sucessor em outro cluster, retornando, por fim o sucessor de x.


```python

    def successor(self, x):
        if self.universe_size == 2:
            if x == 0 and self.max == 1:
                return 1
            else:
                return None
        elif self.min is not None and x < self.min:
            return self.min
        else:
            i = self.high(x)
            if self.cluster[i] is not None and self.low(x) < self.cluster[i].maximum():
                j = self.cluster[i].successor(self.low(x))
                return self.index(i, j)
            else:
                if self.summary is None:
                    return None
                succ_cluster = self.summary.successor(i)
                if succ_cluster is None:
                    return None
                j = self.cluster[succ_cluster].minimum()
                return self.index(succ_cluster, j)

```


<h4>Predecessor</h4> 


A função de predecessor é quase uma versão espelhada da função de sucessor, porém com um caso a mais. Assim como em sucessor,fazemos a verificação se o universo é de tamanho 2, sendo esse o caso, novamente nos deparamos com duas possibilidades: x = 1 e predescessor = 0, ou x = 0 e predecessor nil. Dessa vez, em vez de verificarmos se x < self.min, verificamos se x é maior que o maior elemento da árvore (self.max), se for, seu predecessor será o maior elemento e a função retornará self.max. Se não, a função verifica se x é maior que o valor mínimo de seu cluster, se esse for o caso, a função retorna seu predecessor. Caso o contrário, enquanto na outra função partia-se diretamente para a busca em outro cluster, nessa função é necessário checar se existem outros clusters, pois, caso não existam outros clusters, (considerando que o valor mínimo da VEB é armazenado separadamente) a função verificará se esse valor mínimo existe e se x é maior que ele. Se sim, ela retornará o valor mínimo da árvore. Se não, o predecessor não existe. Porém, se existirem outros clusters, a função, enfim, partirá para a busca em clusters anteriores, retornando o predecessor de x.


```python

    def predecessor(self, x):
        if self.universe_size == 2:
            if x == 1 and self.min == 0:
                return 0
            else:
                return None
        elif self.max is not None and x > self.max:
            return self.max
        else:
            i = self.high(x)
            if self.cluster[i] is not None:
                min_low = self.cluster[i].minimum()
                if min_low is not None and self.low(x) > min_low:
                    j = self.cluster[i].predecessor(self.low(x))
                    return self.index(i, j)
                
        if self.summary is None:
            if self.min is not None and x > self.min:
                return self.min
            else:
                return None
           
        predecessor_cluster = self.summary.predecessor(i)
        if predecessor_cluster is None:
            if self.min is not None and x > self.min:
                return self.min
            else:
                return None
        else:
            j = self.cluster[predecessor_cluster].maximum()
            return self.index(predecessor_cluster, j)

```


<h4>Inserção</h4> 

A próxima função realiza a operação de inserção. Para a inserção é importante ressaltar que essa função fará apenas uma chamada recursiva. Por isso, primeiramente verifica-se se a árvore está vazia, se sim, x passará a ser tanto o valor mínimo quanto o valor máximo da árvore, tendo em vista que x é o único valor na árvore. Caso não seja uma árvore vazia,verificamos se x é menor que o valor minímo da árvore, se sim, x troca de lucar com min (essa troca é feita para que x passe a ser o novo min sem que o min original seja perdido). Além disso, verificamos se x é maior que o valor máximo da árvore, se sim, atualizamos o valor máximo. Por fim, se o universo for <= 2, a função retorna pois não há clusters nem sumário. Se nenhum desses for o caso de x, levando em consideração que a árvore não está vazia e que x está em um cluster, (como o resumo só armazena clusters não) verificamos se o cluster de x está vazio, se estiver inserimos x, atualizando o resumo. Se não, faremos, enfirm a chamada recursiva inserindo x em seu cluster. 

```python

    def insert(self, x):
        if self.min is None:
            self.min = self.max = x
            return
        if x < self.min:
            x, self.min = self.min, x
        if x > self.max:
            self.max = x

        if self.universe_size <= 2:
            return 

        high = self.high(x)
        low = self.low(x)

        if self.cluster[high] is None:
            self.cluster[high] = vEB(self.lower_sqrt)

        if self.summary is None:
            self.summary = vEB(self.upper_sqrt)

        if self.cluster[high].min is None:
            self.summary.insert(high)

        self.cluster[high].insert(low)

```


<h4>Remoção</h4>

A função a seguir é realiza a operação de remoção da árvore VEB. Enquanto a inserção verifica primeiro se a árvore está vazia, a remoção, por sua vez, vai verificar primeiro se a árvore tem apenas 1 elemento. Se esse for o caso, como x é tanto min, quanto max (assim como na inserção), definimos min e max como nil, eliminando x. Partindo para o caso base, se existirem apenas 2 elementos, nos deparamos com duas possibilidades: se x for o valor mínimo (nesse caso, 0), removemos o x e o min passa a ser 1; se não, removemos x e o máximo e o mínimo passam a ser a mesma coisa. Então a função retorna o elemento que sobrou. Se não, tendo em mente que o universo possui mais de dois elementos, primeiramente, verificamos se x é o valor minímo. Se sim (como mínimo fica armazenado fora do resumo), buscaremos pelo primeiro cluster no resumo e pelo menor valor desse cluster para substituir o mínimo, que foi eliminado e atualizamos o valor minímo. Após isso, a remoção de x começa, de fato, independente de x ser o valor original passado para a árvore ou o novo mínimo. Então se o cluster não for vazio a função remove x do cluster. Se o cluster de x se tornar vazio após essa remoção, ela também remove o cluster do resumo. Caso o valor eliminado (x) tenha sido o valor máximo, se não existir sumário, restará apenas o valor minímo na estrutura, se não, a função procura pelo maior cluster do sumário e o maior valor dentro desse cluster para atualizar max. Se o cluster não ficou vazio após a remoção, mas o x era o valor máximo, a função atualiza o valor máximo.

```python

    def delete(self, x):
        if self.min == self.max:
            self.min = self.max = None
            return
        elif self.universe_size == 2:
            if x == 0:
                self.min = 1
            elif self.min == 0:
                self.max = self.min
            return
        else:
            high = self.high(x)
            low = self.low(x)
            if x == self.min:
                first_cluster = self.summary.minimum()
                x = self.index(first_cluster, self.cluster[first_cluster].minimum())
                self.min = x
            if self.cluster[high] is not None:
                self.cluster[high].delete(low)
            
                if self.cluster[high].minimum() is None:
                    self.summary.delete(high)
                    if x == self.max:
                        summary_max = self.summary.maximum()
                        if summary_max is None:
                            self.max = self.min
                        else:
                            self.max = self.index(summary_max, self.cluster[summary_max].maximum())
                elif x == self.max:
                    self.max = self.index(high, self.cluster[high].maximum())
                   
```

Dessa forma concluímos a estrutura Van Emde Boas e partimos para a segunda parte do código, que é a tabela de dispersão.

<h3>Tabela de dispersão</h3> 


A tabela hash ou tabela de dispersão é considerada uma tabela eficiente para implementar dicionários, pesquisando elementos em tempo médio O(1), se estiver sob condições razoáveis (Cormen et al., 2009). Para este trabalho, foi proposto que a tabela de dispersão, fique no lugar do vertor de clustes da VEB tradicional, como forma de economizar espaço. 

Dessa forma, começamos criando a classe HashTable, que será chamada na primeira função mostrada no trabalho. Nessa função, estabelecemos a capacidade inicial da tabela, criamos uma tabela vazia e inicializamos um contador do tamano da tabela que começa com 0 (mais adiante, isso ajudará com table halving/doubling). Por fim definimos o valor mínimo e máximo da tabela (essa definição é importante para as operações da VEB).


```python

class HashTable:
    def __init__(self, initial_capacity=2):
        self.capacity = initial_capacity
        self.table = [None] * self.capacity
        self.size = 0
        self.min = None
        self.max = None

```


Para este trabalho, optei por implementar a função hash de indereçamento aberto com sodagem linear. A escolha desse método se dá principalmente devido ao tratamento de colisões, pois, como explicado por Cormen et al.(2009), o endereçamento aberto possibilita uma maior quantidade de posições na tabela, devido à ausência de ponteiros, e consequêntimente diminui a possibilidade de colisões. Primeiro, começaremos implementando uma função de dispersão. Para valores inteiros começamos implementado o método da divisão h(k) = k mod m que retorna o módulo da divisão da chave pelo tamanho da tabela. Para strings procuramos aplicar a mesma função, porém como um string não é um número natural, primeiramente precisamos transformar a string em um número. Para isso, a função usa um laço que identifica o índice da letra na sting e e seu caractere correspondete, calculando a soma dos respectivos valores ASCII, para, enfim retornar módulo da divisão dessa soma pelo tamanho da tabela.


```python

    def _hash(self, key):
        if isinstance(key, int):
            return key % self.capacity
        elif isinstance(key, str):
            hash_value = 0
            for i, char in enumerate(key):
                hash_value += (i + 1) * ord(char)
            return hash_value % self.capacity
        else:
            raise TypeError("Tipo de chave não suportado")

```

A próxima função é utilizada para fazer a inclusão na tabela. Porém, antes de começar a inclusão faremos o table doubling. Para isso a função verifica se a tabela está cheia, se sim, ela dobra o tamando da tabela e recalcula o indíce da chave. Se a tabela não estiver cheia, ela apenas calcula o índice da chave. Então partiremos para o tratamento das colisões utilizando a função "h(k,i)=(h'(k) + i) mod m" para encontrar uma posição para nova chave. Para isso verificamos se o indíce dado pela função está vazio, se não estiver, inserimos a chave e atualizamos o contador do tamanho da tabela e retornamos, de outro modo (posição ocupada) partiremos para o próxima posição e assim por diante. 

```python

    def insert(self, key, value):
        if self.size >= self.capacity * 1:
            self._resize(self.capacity * 2)
            index = self._hash(key)
        else:
            index = self._hash(key)
        for i in range(self.capacity):
            new_index = (index + i) % self.capacity
            if self.table[new_index] is None or self.table[new_index][0] == key:
                self.table[new_index] = (key, value)
                self.size += 1
                return

```


Partindo para a função de remoção, começamos calculando o índice da chave e após isso utilizamos novamente a sondagem linear para tratamento de colisões. Porém, em vez de verificarmos se a posição está vazia, nessa sondagem, verificamos se a posição está ocupada. Se estiver, removemos a chave e atualizamos o contador, de outro modo, faremos a sondagem na próxima posição e assim por diante. Por fim, após a remoção, verificamos se a quantidade de posições ocupadas na tabela é menor ou igual a metade de sua capacidade e se sua capacidade atual é maior que 2, se for, reduzimos a tabela pela metade fazendo o table halving.

```python

    def delete(self, key): 
        index = self._hash(key)
        for i in range(self.capacity):
            new_index = (index + i) % self.capacity
            if self.table[new_index] is not None and self.table[new_index][0] == key:
                self.table[new_index] = None
                self.size -= 1
                return
        if self.size <= self.capacity * 0.50 and self.capacity > 2:
            self._resize(self.capacity // 2)

```


A função resize é escencial para conseguirmos fazer table doubling/halving. A partir dela, guardamos a tabela atual (com todos os seus elementos) e definimos a nova capacidade da tabela. Então criamos uma nova tabela vazia (com contador zerado) e, por fim, usamos um laço para reinserir os elementos guardados na nova tabela.


```python
    def _resize(self, new_capacity):
        old_table = self.table
        self.capacity = new_capacity
        self.table = [None] * self.capacity
        self.size = 0
        self.min = None
        self.max = None

        for entry in old_table:
            if entry is not None:
                self.insert(entry[0], entry[1])
```

A função get, por sua vez, busca uma chave, percorrendo a tabela com sondagem linear. Se

```python

    def get(self, key):
        index = self._hash(key)
        for i in range(self.capacity):
            idx = (index + i) % self.capacity
            entry = self.table[idx]
            if entry is None:
                continue 
            if entry[0] == key:
                return entry[1]
        return None

```


As três funções seguintes, são enscesiais para que a tabela se comprote como um dicionário. É a partir dessas funções que poderemos usar os cochetes na árvore vEB sem termos problemas de sintaxe. Sem essas três funções, todos os cochetes teriam que ser substituídos por ".get()". Enquanto usamos setitem e delitem para chamar insert e delete, usamos getitem para retornar a chave encontrada em get item. 


```python
    def __setitem__(self, key, value):
        self.insert(key, value)
        
    def __delitem__(self, key):
        self.delete(key)
    
    def __getitem__(self, key):
        return self.get(key)
```

<h3>Imprimir</h3> 


Para fazermos o processamento dos valores colocados na entrada e imprimirmos o resultado na saída, utilizaremos 3 funções.
```python
def process_file(input_path, output_path):
    veb = vEB(2**32)
    output_lines = []

    with open(input_path, 'r') as infile:
        lines = infile.readlines()
        print("[DEBUG] Conteúdo bruto do arquivo:")
        print(repr("".join(lines)))
        for line in lines:
            line = line.strip()
            print(f"Linha do arquivo: {line.strip()}")
            #print(f"Linha lida: '{line}'")  # DEBUG
            if not line:
                continue
            parts = line.split()

            if parts[0] == "INC":
                x = int(parts[1])
                #print(f"Inserindo: {x}")  # DEBUG
                veb.insert(x)
                output_lines.append(f"INC {x}")

            elif parts[0] == "REM":
                x = int(parts[1])
                veb.delete(x)
                output_lines.append(f"REM {x}")

            elif parts[0] == "SUC":
                x = int(parts[1])
                succ = veb.successor(x)
                output_lines.append(f"SUC {x}")
                output_lines.append(str(succ) if succ is not None else "None")

            elif parts[0] == "PRE":
                x = int(parts[1])
                pred = veb.predecessor(x)
                output_lines.append(f"PRE {x}")
                output_lines.append(str(pred) if pred is not None else "None")

            elif parts[0] == "IMP":
                if len(parts) != 1:
                    print(f"[AVISO] Comando IMP inválido: {' '.join(parts)} (deve ser só 'IMP')")
                    continue
                output_lines.append("IMP")
                imp_result = format_imp(veb)
                output_lines.append(imp_result)

    with open(output_path, 'w') as outfile:
        if output_lines:
            for line in output_lines:
                outfile.write(line + "\n")
        else:
            print("Nenhuma saída gerada, arquivo 'saida.txt' não foi escrito.")
    print("Conteúdo escrito em 'saida.txt':")
    with open(output_path, 'r') as f:
        print(f.read())

```

```python

def collect_cluster_values(veb, high):
    cluster = veb.cluster[high]
    if cluster is None or cluster.min is None:
        return []

  
    lows = collect_values(cluster)
    return [veb.index(high, low) for low in lows]

```
```python   
def format_imp(veb):
    if veb.min is None:
        return "Min: None"

    result = f"Min: {veb.min}"
    for high in range(veb.upper_sqrt):
        cluster = veb.cluster[high]
        if cluster is not None and cluster.min is not None:
            values = collect_cluster_values(veb, high)
            values_str = ", ".join(map(str, sorted(values)))
            result += f", C[{high}]: {values_str}"

    return result

```


```python 

def collect_values(veb):
    if veb is None or veb.min is None:
        return []

    if veb.universe_size == 2:
        vals = []
        if veb.min == 0:
            vals.append(0)
        if veb.max == 1:
            vals.append(1)
        return vals

    values = []
    values.append(veb.min)
    if veb.max != veb.min:
        values.append(veb.max)

    for high in range(veb.upper_sqrt):
        cluster = veb.cluster[high]
        if cluster is not None and cluster.min is not None:
            sub_values = collect_values(cluster)
            for low in sub_values:
                values.append(veb.index(high, low))

    return sorted(set(values)) 

```

```python
if __name__ == "__main__":
    print("Iniciando o processamento do arquivo 'entrada.txt'...")
    try:
        process_file("entrada.txt", "saida.txt")
        print("Processamento concluído. Veja o arquivo 'saida.txt'.")
    except Exception as e:
        print("Erro ao processar o arquivo:", e)
    import os
    print("Verificando existência do arquivo...")
    print("Caminho absoluto esperado:", os.path.abspath("entrada.txt"))
    print("Existe?", os.path.exists("entrada.txt"))
```
