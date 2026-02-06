# algoritmos/busca_largura.py - BFS

from collections import deque
from typing import List, Tuple, Set

class BuscaEmLargura:
    """Busca em Largura"""
    
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
    
    def obter_candidatas(self, posicao: Tuple[int, int], visitadas: Set, grupo: int, historico_recente: List = None, imunidades: int = 0) -> List[Tuple[int, int]]:
        """
        Prioriza células NÃO visitadas
        - Retorna células NOVAS adjacentes primeiro
        - Se não há novas, permite revisitar células LIVRES já exploradas
        - Se agente tem imunidade E não há candidatas, permite bombas
        """
        candidatas_novas = []
        candidatas_livres_revisitadas = []
        candidatas_bombas = []
        
        if historico_recente is None:
            historico_recente = []
        
        vizinhos = self.tabuleiro.obter_vizinhos(posicao)
        
        for vizinho in vizinhos:
            if vizinho in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                continue
            
            tipo_vizinho = self.tabuleiro.matriz[vizinho[0]][vizinho[1]]
            
            if vizinho not in visitadas:
                if tipo_vizinho == 'B':
                    candidatas_bombas.append(vizinho)
                else:
                    candidatas_novas.append(vizinho)
            elif tipo_vizinho == 'L' and vizinho in visitadas:
                if vizinho not in historico_recente[-2:]:
                    candidatas_livres_revisitadas.append(vizinho)
        
        if candidatas_novas:
            return candidatas_novas
        
        if candidatas_livres_revisitadas:
            return candidatas_livres_revisitadas
        
        if imunidades > 0 and candidatas_bombas:
            return candidatas_bombas[:1]
        
        return []