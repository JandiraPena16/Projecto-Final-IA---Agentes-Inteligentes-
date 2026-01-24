# configuracoes.py - Configurações Globais do Sistema

# Tamanho do Tabuleiro
TAMANHO_TABULEIRO = 10

# Tipos de Células
TIPO_LIVRE = 'L'
TIPO_BOMBA = 'B'
TIPO_TESOURO = 'T'
TIPO_BANDEIRA = 'F'

# Limites de Agentes
MIN_AGENTES = 1
MAX_AGENTES = 10

# Limites de Bombas (percentagem)
MIN_PERCENTAGEM_BOMBAS = 0
MAX_PERCENTAGEM_BOMBAS = 100

# Algoritmos Disponíveis
ALGORITMOS = ['SVM', 'ARVORE_DECISAO', 'PERCEPTRON', 'MLP']

# Abordagens
ABORDAGEM_A = 'A'  # >50% tesouros
ABORDAGEM_B = 'B'  # Exploração completa
ABORDAGEM_C = 'C'  # Encontrar bandeira

# Servidor
HOST = '0.0.0.0'
PORTA = 5000