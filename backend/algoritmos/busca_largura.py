# algoritmos/busca_largura.py - BFS

from collections import deque
from typing import List, Tuple, Set

class BuscaEmLargura:
    """Busca em Largura"""
    
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
    
    def obter_candidatas(self, posicao: Tuple[int, int], visitadas: Set, grupo: int) -> List[Tuple[int, int]]:
        """Retorna células candidatas usando BFS"""
        candidatas = []
        fila = deque([posicao])
        visitadas_busca = {posicao}
        
        while fila:
            pos = fila.popleft()
            for vizinho in self.tabuleiro.obter_vizinhos(pos):
                if vizinho not in visitadas_busca:
                    visitadas_busca.add(vizinho)
                    
                    if vizinho not in visitadas:
                        # Verificar se não é bomba conhecida
                        if vizinho not in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                            candidatas.append(vizinho)
                    
                    if vizinho in visitadas:
                        tipo = self.tabuleiro.obter_tipo(vizinho)
                        if tipo == 'L':
                            fila.append(vizinho)
        
        return candidatas
