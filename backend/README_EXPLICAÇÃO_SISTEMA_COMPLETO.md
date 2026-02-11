# SISTEMA MULTI-AGENTE DE EXPLORACAO - EXPLICACAO COMPLETA

## VISAO GERAL

Sistema de inteligencia artificial onde 3 grupos de agentes exploram um tabuleiro 10x10 competindo entre si.

---

## 1. TIPO DE AMBIENTE

### Caracteristicas:
- **Parcialmente Observavel**: Agentes nao veem todo o tabuleiro, apenas celulas adjacentes
- **Multiagente Competitivo**: 3 grupos competem entre si
- **Estocastico**: Posicao de bombas/tesouros muda a cada simulacao
- **Episodico**: Cada simulacao e independente
- **Dinamico**: Estado muda a cada movimento
- **Discreto**: Tabuleiro dividido em celulas, movimentos em 4 direcoes

### Elementos do Tabuleiro:
- **Celulas Livres (L)**: Seguras, podem passar
- **Bombas (B)**: Matam agente sem imunidade
- **Tesouros (T)**: Dao 1 imunidade ao agente
- **Bandeira (F)**: Objetivo da Abordagem C

---

## 2. TIPO DE AGENTES

### Grupo 1: Agentes BFS (Busca em Largura)
- **Tipo**: Agente Reativo Simples
- **Como funciona**: Escolhe proxima celula usando heuristica baseada em visao
- **Sem aprendizado**: Nao usa Machine Learning

### Grupo 2 e 3: Agentes ML (Machine Learning)
- **Tipo**: Agente Baseado em Utilidade
- **Como funciona**: Usa modelos treinados para avaliar cada celula candidata
- **Com aprendizado**: Aprende padroes offline e aplica online

---

## 3. ALGORITMOS DE ML

### SVM (Support Vector Machine)
**O que faz**: Desenha uma "linha" que separa boas celulas de ruins
**Como funciona**: 
- Olha 7 caracteristicas de cada celula
- Encontra melhor forma de separar celulas boas/medias/ruins
- Usa essa "regra" para avaliar novas celulas
**Analogia**: Como tracar linhas num mapa para separar regioes seguras de perigosas

### Arvore de Decisao
**O que faz**: Cria uma serie de perguntas para decidir
**Como funciona**:
- "Tem bomba perto?" -> SIM -> "Quantas?" -> 3+ -> RUIM!
- "Tem tesouro perto?" -> SIM -> BOM!
**Analogia**: Como um fluxograma de decisao

### Perceptron (Rede Neural Simples)
**O que faz**: Combina caracteristicas com pesos para dar pontuacao
**Como funciona**:
- Cada caracteristica tem um peso
- Score = (bombas_adj × peso1) + (tesouros_adj × peso2) + ...
- Aprende os melhores pesos com exemplos
**Analogia**: Como calcular nota final com pesos diferentes para cada prova

### MLP (Multi-Layer Perceptron)
**O que faz**: Perceptron com camdas extras (mais inteligente)
**Como funciona**:
- Camada 1 detecta padroes simples
- Camada 2 combina padroes em regras complexas
- Camada 3 da decisao final
**Analogia**: Como cerebro humano com neuronios conectados

---

## 4. MEMORIA COMPARTILHADA (CONHECIMENTO DO GRUPO)

### Localizacao: `backend/modelos/grupo.py`

```python
class ConhecimentoCompartilhado:
    celulas_exploradas = set()     # Todas celulas que QUALQUER agente visitou
    bombas_conhecidas = set()      # Bombas descobertas
    tesouros_conhecidos = set()    # Tesouros descobertos
    posicao_bandeira = None        # Onde esta a bandeira
```

### Como funciona:
1. Agente A pisa em celula (3,4) - Tesouro
2. Chama `conhecimento_grupo.registrar('T', (3,4))`
3. TODOS agentes do grupo agora sabem que (3,4) tem tesouro
4. Agente B, C, D evitam ir la (ja foi explorada)

### Arquivo: `backend/modelos/grupo.py` - Classe `ConhecimentoCompartilhado`

**Metodo principal:**
```python
def registrar(self, tipo, posicao):
    self.celulas_exploradas.add(posicao)
    if tipo == 'B':
        self.bombas_conhecidas.add(posicao)
    elif tipo == 'T':
        self.tesouros_conhecidos.add(posicao)
```

---

## 5. MARCACAO DE CELULAS VISITADAS

### Acontece em 2 lugares:

#### A) Memoria Individual do Agente
**Arquivo**: `backend/modelos/agente.py`
```python
def mover(self, nova_posicao):
    self.celulas_visitadas.add(nova_posicao)  # Memoria pessoal
    self.historico.append(nova_posicao)       # Ultimas 10 posicoes
```

#### B) Memoria Compartilhada do Grupo
**Arquivo**: `backend/modelos/agente.py`
```python
def processar_celula(self, tipo, tabuleiro):
    # MARCA como explorada para TODO o grupo
    self.conhecimento_grupo.registrar(tipo, self.posicao)
```

### Fluxo completo:
```
1. Agente esta em (2,3)
2. Decide ir para (2,4)
3. chama agente.mover((2,4))           -> Adiciona em celulas_visitadas
4. chama agente.processar_celula(...)  -> Adiciona em conhecimento_grupo
5. Agora TODOS do grupo sabem sobre (2,4)
```

---

## 6. LOGICA DE MOVIMENTO (COMO AGENTE ANDA)

### Arquivo: `backend/simulacao/simulador.py` - Metodo `_executar_passo_grupo()`

### Passo a passo:

```
PASSO 1: Obter candidatas
   Arquivo: backend/algoritmos/busca_largura.py
   Metodo: obter_candidatas()
   
   Verifica vizinhos (cima, baixo, esquerda, direita):
   - Se nao visitada -> candidata_nova
   - Se visitada E livre -> candidata_livre_revisitada
   - Se bomba E tem imunidade -> candidata_bomba
   
   Retorna por prioridade:
   1. Novas
   2. Livres revisitadas
   3. Bombas (se tem imunidade)

PASSO 2: Decidir qual candidata escolher
   Arquivo: backend/modelos/agente.py
   Metodo: decidir_proxima_celula()
   
   SE agente tem ML:
      Para cada candidata:
         - Extrai 7 features
         - Cada modelo ML da uma pontuacao
         - Calcula media das pontuacoes
      Escolhe candidata com maior media
   
   SE agente NAO tem ML (BFS):
      Para cada candidata:
         - Avalia com heuristica (olha tipo + vizinhos)
         - Calcula score
      Escolhe candidata com maior score

PASSO 3: Mover
   Arquivo: backend/modelos/agente.py
   Metodo: mover()
   
   Atualiza posicao do agente
   Adiciona na memoria pessoal

PASSO 4: Processar celula
   Arquivo: backend/modelos/agente.py
   Metodo: processar_celula()
   
   Verifica tipo:
   - LIVRE: Nada acontece
   - TESOURO: +1 imunidade, remove tesouro
   - BOMBA: Se tem imunidade -> desativa; Senao -> morre
   - BANDEIRA: Marca vitoria
   
   REGISTRA na memoria compartilhada
```

---

## 7. COMUNICACAO ENTRE AGENTES DO GRUPO

### NAO ha comunicacao direta!

Agentes se "comunicam" atraves da **memoria compartilhada**:

```
Agente A descobre bomba em (5,6)
   ↓
Registra em conhecimento_grupo.bombas_conhecidas
   ↓
Agente B, ao decidir movimento, consulta conhecimento_grupo
   ↓
Ve que (5,6) tem bomba e evita
```

### Arquivo: `backend/modelos/grupo.py`

Cada grupo tem UMA instancia de `ConhecimentoCompartilhado` que TODOS os agentes do grupo acessam.

---

## 8. MARCACAO DE ENCONTRAR TESOURO

### Acontece em: `backend/modelos/agente.py` - Metodo `processar_celula()`

```python
elif tipo == TIPO_TESOURO:
    self.imunidades += 1                           # Agente ganha imunidade
    self.tesouros_encontrados += 1                 # Contador pessoal
    tabuleiro.coletar_tesouro(self.posicao, self.grupo)  # Remove do tabuleiro
    resultado['evento'] = 'tesouro'
```

### Tambem registra na memoria compartilhada:
```python
self.conhecimento_grupo.registrar('T', self.posicao)
```

### E no tabuleiro:
**Arquivo**: `backend/modelos/tabuleiro.py`
```python
def coletar_tesouro(self, posicao, grupo):
    if posicao in self.posicoes_tesouros:
        self.posicoes_tesouros.remove(posicao)
        self.tesouros_por_grupo[grupo] = self.tesouros_por_grupo.get(grupo, 0) + 1
        self.matriz[x][y] = TIPO_LIVRE  # Celula vira livre
```

---

## 9. DATASET - COMO E CRIADO

### Arquivo: `backend/utilitarios/gerador_dados.py`

### Processo:

```
PASSO 1: Gerar ambientes aleatorios
   Funcao: gerar_ambientes(num=10)
   
   Para cada ambiente:
   - Cria tabuleiro 10x10
   - Coloca bombas aleatoriamente (20%)
   - Coloca tesouros aleatoriamente (10%)

PASSO 2: Simular movimentos
   Funcao: gerar_dataset(ambientes, num_amostras=1000)
   
   Para cada posicao em cada ambiente:
   - Obtem vizinhos
   - Para cada vizinho:
      * Extrai 7 features (x, y, bombas_adj, tesouros_adj, livres_adj, dist_centro, num_vizinhos)
      * Calcula label (0=ruim, 1=medio, 2=bom):
         - RUIM (0): Tem bomba OU muitas bombas perto
         - BOM (2): Tem tesouro OU muitos tesouros perto
         - MEDIO (1): Resto

PASSO 3: Salvar dataset
   Retorna: X (features), y (labels)
   X = array com 1000 linhas × 7 colunas
   y = array com 1000 labels (0, 1 ou 2)
```

### Features extraidas (7 no total):
1. **x**: Coordenada X da celula
2. **y**: Coordenada Y da celula
3. **bombas_adj**: Numero de bombas adjacentes
4. **tesouros_adj**: Numero de tesouros adjacentes
5. **livres_adj**: Numero de celulas livres adjacentes
6. **dist_centro**: Distancia Manhattan ate centro do tabuleiro
7. **num_vizinhos**: Total de vizinhos (2 nos cantos, 3 nas bordas, 4 no meio)

---

## 10. TREINAMENTO DOS MODELOS

### Arquivo: `backend/treinar_modelos.py`

### Comando: `python treinar_modelos.py`

### Processo:

```
PASSO 1: Gerar dados
   Chama gerador_dados.gerar_dataset()
   Resultado: X (1000 amostras × 7 features), y (1000 labels)

PASSO 2: Treinar cada modelo

   SVM:
   from sklearn.svm import SVC
   modelo = SVC(kernel='rbf', C=1.0, gamma='scale')
   modelo.fit(X, y)
   
   Arvore de Decisao:
   from sklearn.tree import DecisionTreeClassifier
   modelo = DecisionTreeClassifier(max_depth=10)
   modelo.fit(X, y)
   
   Perceptron:
   from sklearn.neural_network import MLPClassifier
   modelo = MLPClassifier(hidden_layers=(10,), max_iter=100)
   modelo.fit(X, y)
   
   MLP:
   modelo = MLPClassifier(hidden_layers=(20, 10), max_iter=200)
   modelo.fit(X, y)

PASSO 3: Salvar modelos
   import pickle
   with open('modelos_treinados/svm.pkl', 'wb') as f:
       pickle.dump(modelo, f)
   
   (Repete para cada modelo)
```

### Resultado: 4 arquivos .pkl em `backend/modelos_treinados/`
- svm.pkl
- arvore_decisao.pkl
- perceptron.pkl
- mlp.pkl

---

## 11. PREPROCESSAMENTO E NORMALIZACAO

### IMPORTANTE: **NAO ha normalizacao explicita!**

Porque?
- Features ja estao em escalas similares:
  - Coordenadas: 0-9
  - Contadores: 0-4
  - Distancia: 0-18

### Preprocessamento acontece em:
**Arquivo**: `backend/modelos/agente.py` - Metodo `_extrair_features()`

```python
def _extrair_features(self, celula, tabuleiro):
    x, y = celula
    vizinhos = tabuleiro.obter_vizinhos(celula)
    
    # Contar tipos de vizinhos
    bombas_adj = 0
    tesouros_adj = 0
    livres_adj = 0
    
    for vx, vy in vizinhos:
        tipo = tabuleiro.matriz[vx][vy]
        if tipo == TIPO_BOMBA:
            bombas_adj += 1
        elif tipo == TIPO_TESOURO:
            tesouros_adj += 1
        elif tipo == TIPO_LIVRE:
            livres_adj += 1
    
    # Calcular distancia ao centro
    centro = TAMANHO_TABULEIRO // 2
    dist_centro = abs(x - centro) + abs(y - centro)
    
    # Retornar array com 7 features
    return np.array([x, y, bombas_adj, tesouros_adj, livres_adj, dist_centro, len(vizinhos)])
```

**Nenhuma normalizacao aplicada** - valores brutos sao usados.

---

## 12. USO DOS DADOS TREINADOS (RUNTIME)

### Carregamento: `backend/servidor.py`

```python
import pickle

# Carregar modelos salvos
with open('modelos_treinados/svm.pkl', 'rb') as f:
    modelo_svm = pickle.load(f)

# (Repete para outros modelos)
```

### Uso durante simulacao: `backend/modelos/agente.py`

```python
def decidir_proxima_celula(self, candidatas, tabuleiro, abordagem):
    if self.algoritmos_ml:  # Se agente tem ML
        scores = []
        for celula in candidatas:
            # 1. Extrair features da celula
            features = self._extrair_features(celula, tabuleiro)
            
            # 2. Cada modelo da sua predicao
            score_total = 0
            for modelo_ml in self.algoritmos_ml:
                predicao = modelo_ml.prever(features)  # Retorna 0, 1 ou 2
                score_total += predicao
            
            # 3. Calcular media
            score_medio = score_total / len(self.algoritmos_ml)
            scores.append((celula, score_medio))
        
        # 4. Ordenar e escolher melhor
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
```

### Wrapper dos modelos: `backend/algoritmos/`

Cada algoritmo tem uma classe wrapper:

```python
class AlgoritmoSVM:
    def __init__(self, modelo_treinado):
        self.modelo = modelo_treinado
    
    def prever(self, features):
        # features = [x, y, bombas_adj, tesouros_adj, livres_adj, dist_centro, num_vizinhos]
        predicao = self.modelo.predict([features])[0]
        # Retorna 0 (ruim), 1 (medio) ou 2 (bom)
        return predicao
```

---

## 13. MARCACAO DE VITORIAS (POR ABORDAGEM)

### Arquivo: `backend/simulacao/simulador.py`

### Abordagem A: Coletar >50% dos tesouros
**Verificacao**: Metodo `_verificar_condicoes_termino()`

```python
if self.abordagem == ABORDAGEM_A:
    total_tesouros = len(self.tabuleiro.posicoes_tesouros_iniciais)
    
    for grupo in self.grupos:
        tesouros_grupo = self.tabuleiro.tesouros_por_grupo.get(grupo.numero, 0)
        percentagem = (tesouros_grupo / total_tesouros) * 100
        
        if percentagem > 50:
            self.completo = True
            self.sucesso = True
            self.grupo_vencedor = grupo.numero
            self.razao = f"Grupo {grupo.numero} coletou {percentagem:.1f}% dos tesouros"
            return True
```

### Abordagem B: Explorar 100% do tabuleiro
**Verificacao**: Metodo `_verificar_condicoes_termino()`

```python
elif self.abordagem == ABORDAGEM_B:
    for grupo in self.grupos:
        celulas_exploradas = len(grupo.conhecimento.celulas_exploradas)
        
        if celulas_exploradas >= 100:  # 10x10 = 100 celulas
            self.completo = True
            self.sucesso = True
            self.grupo_vencedor = grupo.numero
            self.razao = f"Grupo {grupo.numero} explorou 100% do tabuleiro"
            return True
```

**Nota**: Bombas sao pre-marcadas como exploradas no inicio!

### Abordagem C: Encontrar a bandeira
**Verificacao**: Metodo `_executar_passo_grupo()`

```python
resultado = agente.processar_celula(tipo, self.tabuleiro)

if resultado.get('vitoria'):  # Se encontrou bandeira
    self.completo = True
    self.sucesso = True
    self.grupo_vencedor = grupo.numero
    self.razao = f"Grupo {grupo.numero} encontrou a bandeira!"
    return  # Termina imediatamente
```

**Vitoria marca imediatamente** em `processar_celula()`:
```python
elif tipo == TIPO_BANDEIRA:
    resultado['evento'] = 'bandeira'
    resultado['vitoria'] = True
```

---

## 14. FLUXO COMPLETO DE UMA SIMULACAO

```
1. INICIO (servidor.py)
   - Carregar modelos ML treinados
   - Usuario cria simulacao (escolhe abordagem, num agentes, % bombas)

2. CRIAR SIMULACAO (simulador.py - __init__)
   - Criar tabuleiro 10x10
   - Colocar bombas aleatoriamente
   - Colocar tesouros aleatoriamente
   - Colocar bandeira (se Abordagem C)
   - Criar 3 grupos de agentes em (0,0)
   - Se Abordagem B: Pre-marcar bombas como exploradas

3. EXECUTAR PASSOS (simulador.py - executar_passo)
   Para cada grupo:
      Para cada agente vivo:
         A. Obter candidatas (busca_largura.py)
            - Verifica vizinhos
            - Filtra por visitadas
            - Retorna opcoes disponiveis
         
         B. Decidir proxima celula (agente.py)
            - Se tem ML: usa modelos para avaliar
            - Se nao tem ML: usa heuristica
            - Escolhe melhor opcao
         
         C. Mover (agente.py)
            - Atualiza posicao
            - Adiciona em memoria pessoal
         
         D. Processar celula (agente.py)
            - Verifica tipo da celula
            - Aplica efeitos (tesouro, bomba, bandeira)
            - Registra em memoria compartilhada
         
         E. Verificar vitoria
            - Checa condicoes da abordagem
            - Se ganhou: marca vencedor e termina

4. ENVIAR ESTADO PARA FRONTEND
   - Estado do tabuleiro
   - Posicoes dos agentes
   - Eventos (movimentos, mortes, tesouros)
   - Progresso de cada grupo

5. REPETIR ate:
   - Alguem vencer
   - Todos agentes morrerem
   - Atingir limite de passos (1000)
```

---

## 15. ESTRUTURA DE ARQUIVOS

```
backend/
├── servidor.py                    # API Flask, carrega modelos
├── treinar_modelos.py            # Script de treinamento
├── configuracoes.py              # Constantes globais
│
├── modelos/
│   ├── agente.py                 # Classe Agente (movimento, decisao)
│   ├── grupo.py                  # Classe Grupo (memoria compartilhada)
│   └── tabuleiro.py              # Classe Tabuleiro (grid, celulas)
│
├── simulacao/
│   └── simulador.py              # Logica principal da simulacao
│
├── algoritmos/
│   ├── busca_largura.py          # BFS para obter candidatas
│   ├── svm.py                    # Wrapper SVM
│   ├── arvore_decisao.py         # Wrapper Arvore
│   ├── perceptron.py             # Wrapper Perceptron
│   └── mlp.py                    # Wrapper MLP
│
├── utilitarios/
│   └── gerador_dados.py          # Gera dataset para treino
│
└── modelos_treinados/            # Modelos .pkl salvos
    ├── svm.pkl
    ├── arvore_decisao.pkl
    ├── perceptron.pkl
    └── mlp.pkl
```

---

## 16. RESUMO SIMPLES

### O que e o sistema?
Competicao entre 3 grupos de agentes explorando tabuleiro com obstaculos.

### Como funciona?
1. Agentes veem apenas celulas adjacentes
2. Decidem para onde ir (usando ML ou heuristica)
3. Movem e descobrem o que tem na celula
4. Compartilham descobertas com grupo
5. Repetem ate alguem vencer

### Como agentes aprendem?
- ML: Treinados offline com 1000 exemplos
- BFS: Usa regras programadas (heuristica)

### Como comunicam?
Atraves de memoria compartilhada - quando um descobre algo, todos do grupo sabem.

### Como ganham?
- Abordagem A: Coletar mais de 50% dos tesouros
- Abordagem B: Explorar 100% do tabuleiro
- Abordagem C: Encontrar a bandeira primeiro

---

FIM DO README
