# algoritmos/busca_largura.py - BFS

from collections import deque
from typing import List, Tuple, Set
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuracoes import TIPO_LIVRE, TIPO_BOMBA, TIPO_TESOURO, TIPO_BANDEIRA

class BuscaEmLargura:
    """Busca em Largura"""
    
    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro
    
    def obter_candidatas(self, posicao: Tuple[int, int], visitadas: Set, grupo: int, historico_recente: List = None, imunidades: int = 0) -> List[Tuple[int, int]]:
        """
        Prioridade de retorno:
        1. Celulas NOVAS nao visitadas (melhor caso)
        2. Celulas LIVRES visitadas fora do historico recente (evitar loop)
        3. Celulas LIVRES visitadas mesmo que no historico (agente nao fica preso)
        4. Bombas (apenas se tem imunidade)
        """
        candidatas_novas = []
        candidatas_livres_sem_historico = []
        candidatas_livres_com_historico = []
        candidatas_bombas = []

        if historico_recente is None:
            historico_recente = []

        vizinhos = self.tabuleiro.obter_vizinhos(posicao)

        for vizinho in vizinhos:
            if vizinho in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                continue

            vx, vy = vizinho
            tipo_vizinho = self.tabuleiro.matriz[vx][vy]

            if vizinho not in visitadas:
                # Celula nova: separar bomba de nao-bomba
                if tipo_vizinho == TIPO_BOMBA:
                    candidatas_bombas.append(vizinho)
                else:
                    candidatas_novas.append(vizinho)

            elif tipo_vizinho == TIPO_LIVRE:
                # Celula livre ja visitada: separar por historico
                if len(historico_recente) < 2 or vizinho not in historico_recente[-2:]:
                    candidatas_livres_sem_historico.append(vizinho)
                else:
                    # Esta no historico recente mas guardamos como ultimo recurso
                    candidatas_livres_com_historico.append(vizinho)

        # 1. Melhor opcao: celula nova
        if candidatas_novas:
            return candidatas_novas

        # 2. Livre visitada fora do historico recente
        if candidatas_livres_sem_historico:
            return candidatas_livres_sem_historico

        # 3. NOVO: Livre visitada mesmo que seja celula anterior
        #    Agente retrocede em vez de ficar preso
        if candidatas_livres_com_historico:
            return candidatas_livres_com_historico

        # 4. Bomba apenas se tem imunidade
        if imunidades > 0 and candidatas_bombas:
            return candidatas_bombas[:1]

        return []