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
    
    #def __str__(self):
        #return f"vEB(capacity={self.capacity}, size={self.size}, min={self.min}, max={self.max})"

    #def __repr__(self):
       # return self.__str__()

    def minimum(self):
        return self.min

    def maximum(self):
        return self.max
    
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
        # print(f"DEBUG testing: self.cluster[{high}] = {self.cluster[high]}")

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
                   

class HashTable:
    def __init__(self, initial_capacity=2):
        self.capacity = initial_capacity
        self.table = [None] * self.capacity
        self.size = 0
        self.min = None
        self.max = None

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

    def __setitem__(self, key, value):
        self.insert(key, value)
        
    def __delitem__(self, key):
        self.delete(key)
    
    def __getitem__(self, key):
        return self.get(key)

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

def collect_cluster_values(veb, high):
    cluster = veb.cluster[high]
    if cluster is None or cluster.min is None:
        return []

  
    lows = collect_values(cluster)
    return [veb.index(high, low) for low in lows]
   
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
    

    
   


    
