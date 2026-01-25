# algoritmos/busca_largura.py - BFS

from collections import deque
from typing import List, Tuple, Set

class BuscaEmLargura:
    """Busca em Largura"""
    
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
    
    def obter_candidatas(self, posicao: Tuple[int, int], visitadas: Set, grupo: int, historico_recente: List = None) -> List[Tuple[int, int]]:
        """
        ✅ CORRIGIDO: Prioriza células NÃO visitadas
        - Retorna células NOVAS adjacentes primeiro
        - Só retorna células já visitadas se NÃO houver novas (para passar)
        """
        candidatas_novas = []
        
        # ✅ NOVO: Histórico recente para evitar loops
        if historico_recente is None:
            historico_recente = []
        
        # Obter vizinhos diretos (apenas 4 direções, sem diagonal)
        vizinhos = self.tabuleiro.obter_vizinhos(posicao)
        
        for vizinho in vizinhos:
            # Verificar se não é bomba conhecida pelo grupo
            if vizinho in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                continue
            
            # ✅ PRIORIDADE: Células não visitadas
            if vizinho not in visitadas:
                candidatas_novas.append(vizinho)
        
        # ✅ Se há células NOVAS, retornar APENAS elas (não misturar com revisitadas)
        if candidatas_novas:
            return candidatas_novas
        
        # ✅ FALLBACK: Se NÃO há células novas, permitir revisitar LIVRES (para passar)
        # Mas usar busca expandida em vez de adjacentes
        return []  # Retorna vazio → simulador vai chamar busca_expandida