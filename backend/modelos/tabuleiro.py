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
        
        # Rastrear quais grupos ja coletaram cada tesouro
        # Estrutura: { posicao: set(grupos_que_ja_coletaram) }
        self.tesouros_coletados_por_grupo = {}
        
        # Rastrear quais grupos ja pisaram em cada bomba
        # Estrutura: { posicao: set(grupos_que_ja_pisaram) }
        self.bombas_pisadas_por_grupo = {}
        
        # Guardar total inicial de tesouros (nunca muda)
        self.posicoes_tesouros_iniciais = set(self.posicoes_tesouros)
        
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
    
    def grupo_ja_pisou_bomba(self, posicao: Tuple[int, int], grupo: int) -> bool:
        """Verifica se este grupo ja pisou na bomba nesta posicao"""
        grupos_que_pisaram = self.bombas_pisadas_por_grupo.get(posicao, set())
        return grupo in grupos_que_pisaram

    def desativar_bomba(self, posicao: Tuple[int, int], grupo: int):
        """
        NOVA LOGICA:
        - Regista que este grupo pisou na bomba (perde imunidade)
        - A bomba so desaparece do tabuleiro quando os 3 grupos pisaram
        - Para o grupo que pisou, a bomba fica em bombas_desativadas (evita voltar)
        - A logica de evitar bombas no BFS nao muda
        """
        # Registar que este grupo pisou
        if posicao not in self.bombas_pisadas_por_grupo:
            self.bombas_pisadas_por_grupo[posicao] = set()

        self.bombas_pisadas_por_grupo[posicao].add(grupo)

        # Para este grupo, marcar como desativada (nao volta a pisar)
        self.bombas_desativadas[grupo].add(posicao)

        print(f"  Bomba em {posicao}: grupo {grupo} pisou. "
              f"Grupos que ja pisaram: {self.bombas_pisadas_por_grupo[posicao]}")

        # So remove do tabuleiro quando os 3 grupos pisaram
        grupos_que_pisaram = self.bombas_pisadas_por_grupo[posicao]
        if len(grupos_que_pisaram) >= 3:
            self.posicoes_bombas.discard(posicao)
            x, y = posicao
            self.matriz[x][y] = TIPO_LIVRE
            print(f"  Bomba em {posicao} REMOVIDA do tabuleiro (3 grupos pisaram)")
    
    def grupo_ja_coletou_tesouro(self, posicao: Tuple[int, int], grupo: int) -> bool:
        """Verifica se este grupo já coletou o tesouro nesta posição"""
        grupos_que_coletaram = self.tesouros_coletados_por_grupo.get(posicao, set())
        return grupo in grupos_que_coletaram
    
    def coletar_tesouro(self, posicao: Tuple[int, int], grupo: int) -> bool:
        """
        NOVA LOGICA:
        - Cada grupo pode coletar o tesouro UMA vez (ganha imunidade)
        - O tesouro so desaparece do tabuleiro quando os 3 grupos o coletaram
        - Se o grupo ja coletou este tesouro antes, nao faz nada
        
        Retorna True se este grupo coletou agora, False se ja tinha coletado
        """
        # Verificar se o tesouro ainda existe no tabuleiro OU se ja foi coletado por algum grupo
        # (pode estar como LIVRE no tabuleiro mas ainda nao coletado pelos 3 grupos)
        posicao_conhecida = (posicao in self.posicoes_tesouros or
                             posicao in self.tesouros_coletados_por_grupo)
        
        if not posicao_conhecida:
            return False
        
        # Verificar se este grupo ja coletou
        if self.grupo_ja_coletou_tesouro(posicao, grupo):
            return False
        
        # Registar que este grupo coletou
        if posicao not in self.tesouros_coletados_por_grupo:
            self.tesouros_coletados_por_grupo[posicao] = set()
        
        self.tesouros_coletados_por_grupo[posicao].add(grupo)
        self.tesouros_coletados[grupo] += 1
        
        print(f"  Tesouro em {posicao}: grupo {grupo} coletou. "
              f"Grupos que ja coletaram: {self.tesouros_coletados_por_grupo[posicao]}")
        
        # So remove do tabuleiro quando os 3 grupos coletaram
        grupos_que_coletaram = self.tesouros_coletados_por_grupo[posicao]
        if len(grupos_que_coletaram) >= 3:
            self.posicoes_tesouros.discard(posicao)
            x, y = posicao
            self.matriz[x][y] = TIPO_LIVRE
            print(f"  Tesouro em {posicao} REMOVIDO do tabuleiro (3 grupos coletaram)")
        
        return True
    
    def exportar_matriz(self):
        """Retorna cópia da matriz"""
        return [linha[:] for linha in self.matriz]