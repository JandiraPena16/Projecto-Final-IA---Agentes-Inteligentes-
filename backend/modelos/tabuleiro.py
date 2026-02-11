# modelos/tabuleiro.py - Ambiente de Exploração

import random
from collections import deque
from typing import Tuple, Set, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuracoes import *

class Tabuleiro:
    """Representa o ambiente 10x10 de exploração"""
    
    def __init__(self, percentagem_bombas: int = 50, usar_bandeira: bool = False):
        self.tamanho = TAMANHO_TABULEIRO
        self.matriz = [[TIPO_LIVRE for _ in range(self.tamanho)] for _ in range(self.tamanho)]
        
        # Converter percentagem para decimal
        perc_bombas = percentagem_bombas / 100.0
        num_bombas = int(self.tamanho * self.tamanho * perc_bombas)
        num_tesouros = random.randint(5, 10)
        
        # Posições disponíveis
        posicoes = [(i, j) for i in range(self.tamanho) for j in range(self.tamanho)]
        random.shuffle(posicoes)
        
        # Colocar bombas
        self.posicoes_bombas = set()
        for i in range(num_bombas):
            x, y = posicoes[i]
            self.matriz[x][y] = TIPO_BOMBA
            self.posicoes_bombas.add((x, y))
        
        # Colocar tesouros
        self.posicoes_tesouros = set()
        for i in range(num_bombas, num_bombas + num_tesouros):
            if i < len(posicoes):
                x, y = posicoes[i]
                self.matriz[x][y] = TIPO_TESOURO
                self.posicoes_tesouros.add((x, y))
        
        # Colocar bandeira
        self.posicao_bandeira = None
        if usar_bandeira and num_bombas + num_tesouros < len(posicoes):
            x, y = posicoes[num_bombas + num_tesouros]
            self.matriz[x][y] = TIPO_BANDEIRA
            self.posicao_bandeira = (x, y)
        
        # Estado
        self.celulas_exploradas = {1: set(), 2: set(), 3: set()}
        self.bombas_desativadas = {1: set(), 2: set(), 3: set()}
        self.tesouros_coletados = {1: 0, 2: 0, 3: 0}
        
        # Verificar resolubilidade
        if not self._verificar_resolubilidade():
            self.__init__(percentagem_bombas, usar_bandeira)
    
    def _verificar_resolubilidade(self) -> bool:
        """Verifica se existe caminho explorável"""
        celula_inicial = None
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.matriz[i][j] == TIPO_LIVRE:
                    celula_inicial = (i, j)
                    break
            if celula_inicial:
                break
        
        if not celula_inicial:
            return False
        
        visitadas = set()
        fila = deque([celula_inicial])
        visitadas.add(celula_inicial)
        
        while fila:
            x, y = fila.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.tamanho and 0 <= ny < self.tamanho and 
                    (nx, ny) not in visitadas):
                    tipo = self.matriz[nx][ny]
                    if tipo in [TIPO_LIVRE, TIPO_TESOURO, TIPO_BANDEIRA]:
                        visitadas.add((nx, ny))
                        fila.append((nx, ny))
        
        tesouros_acessiveis = len(self.posicoes_tesouros & visitadas)
        return tesouros_acessiveis > 0
    
    def obter_tipo(self, posicao: Tuple[int, int]) -> str:
        """Retorna tipo da célula"""
        x, y = posicao
        return self.matriz[x][y]
    
    def obter_vizinhos(self, posicao: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Retorna vizinhos válidos (4 direções)"""
        x, y = posicao
        vizinhos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                vizinhos.append((nx, ny))
        return vizinhos
    
    def marcar_explorada(self, posicao: Tuple[int, int], grupo: int):
        """Marca célula como explorada"""
        self.celulas_exploradas[grupo].add(posicao)
    
    def desativar_bomba(self, posicao: Tuple[int, int], grupo: int):
        """
        - Desativa bomba APENAS para o grupo
        - Bomba permanece no tabuleiro global
        - Mas fica registrada como desativada para esse grupo específico
        """
        self.bombas_desativadas[grupo].add(posicao)
        
        # Não remover da matriz global - outros grupos ainda veem como bomba
        # Apenas registrar que este grupo a desativou
    
    def coletar_tesouro(self, posicao: Tuple[int, int], grupo: int):
        """
        Remove tesouro do tabuleiro quando coletado
        Tesouros só podem ser encontrados uma vez
        """
        if posicao in self.posicoes_tesouros:
            # Remover tesouro do conjunto
            self.posicoes_tesouros.discard(posicao)
            
            # Transformar célula em LIVRE
            x, y = posicao
            self.matriz[x][y] = TIPO_LIVRE
            
            # Incrementar contador do grupo
            self.tesouros_coletados[grupo] += 1
            
            return True
        return False
    
    def exportar_matriz(self):
        """Retorna cópia da matriz"""
        return [linha[:] for linha in self.matriz]
