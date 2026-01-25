# algoritmos/busca_largura.py - BFS

from collections import deque
from typing import List, Tuple, Set

class BuscaEmLargura:
    """Busca em Largura"""
    
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
    
    def obter_candidatas(self, posicao: Tuple[int, int], visitadas: Set, grupo: int) -> List[Tuple[int, int]]:
        """
        ✅ CORRIGIDO: Retorna APENAS vizinhos adjacentes (1 casa de distância)
        Agentes só podem se mover para cima, baixo, esquerda ou direita
        """
        candidatas = []
        
        # Obter vizinhos diretos (apenas 4 direções, sem diagonal)
        vizinhos = self.tabuleiro.obter_vizinhos(posicao)
        
        for vizinho in vizinhos:
            # Não revisitar células já exploradas
            if vizinho in visitadas:
                continue
            
            # Verificar se não é bomba conhecida pelo grupo
            if vizinho in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                continue
            
            # Adicionar à lista de candidatas
            candidatas.append(vizinho)
        
        return candidatas
