# modelos/agente.py - Agente Explorador

import numpy as np
from typing import Tuple, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuracoes import *

class Agente:
    """Agente que explora o tabuleiro"""
    
    def __init__(self, id_agente: int, grupo: int, posicao_inicial: Tuple[int, int]):
        self.id = id_agente
        self.grupo = grupo
        self.posicao = posicao_inicial
        self.vivo = True
        self.imunidades = 0
        self.celulas_visitadas = {posicao_inicial}
        self.historico = [posicao_inicial]
        self.conhecimento_grupo = None
        self.algoritmos_ml = []
        self.tesouros_encontrados = 0
        self.bombas_acionadas = 0
        self.passos = 0
    
    def definir_conhecimento_grupo(self, conhecimento):
        """Liga ao conhecimento compartilhado"""
        self.conhecimento_grupo = conhecimento
    
    def definir_algoritmos(self, algoritmos: List):
        """Define algoritmos de ML"""
        self.algoritmos_ml = algoritmos
    
    def decidir_proxima_celula(self, candidatas: List[Tuple[int, int]], tabuleiro, abordagem: str = None) -> Optional[Tuple[int, int]]:
        """
        NOVO: TODOS os agentes veem células adjacentes!
        - Avalia cada candidata vendo o que tem ao redor
        - Evita bombas, prefere tesouros
        - Usa ML se disponível, senão usa heurística simples
        """
        if not candidatas:
            return None
        
        # Se tem ML, usar predições dos modelos
        if self.algoritmos_ml:
            scores = []
            for celula in candidatas:
                features = self._extrair_features(celula, tabuleiro)
                score_total = sum(alg.prever(features) for alg in self.algoritmos_ml)
                score_medio = score_total / len(self.algoritmos_ml)
                scores.append((celula, score_medio))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[0][0]
        
        # ✅ SEM ML: Usar heurística baseada em visão
        # Agora TODOS os agentes veem o que tem ao redor!
        scores = []
        for celula in candidatas:
            score = self._avaliar_celula_heuristica(celula, tabuleiro, abordagem)
            scores.append((celula, score))
        
        # Ordenar por score (maior = melhor)
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    


    def _avaliar_celula_heuristica(self, celula: Tuple[int, int], tabuleiro, abordagem: str = None) -> float:
        x, y = celula
        
        tipo_celula = tabuleiro.matriz[x][y]
        
        if tipo_celula == TIPO_BOMBA:
            return -10000.0
        
        if abordagem == 'A':
            if tipo_celula == TIPO_TESOURO:
                return 10000.0
            elif tipo_celula == TIPO_LIVRE:
                return 100.0
        
        elif abordagem == 'B':
            if tipo_celula == TIPO_TESOURO:
                return 10000.0
            elif tipo_celula == TIPO_LIVRE:
                return 100.0
        
        elif abordagem == 'C':
            if tipo_celula == TIPO_BANDEIRA:
                return 100000.0
            elif tipo_celula == TIPO_TESOURO:
                return 10000.0
            elif tipo_celula == TIPO_LIVRE:
                return 100.0
        
        score = 100.0
        
        vizinhos = tabuleiro.obter_vizinhos(celula)
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
        
        score += tesouros_adj * 10.0
        score += livres_adj * 1.0
        score -= bombas_adj * 50.0
        
        centro = TAMANHO_TABULEIRO // 2
        dist_centro = abs(x - centro) + abs(y - centro)
        score -= dist_centro * 0.1
        
        return score




    
    def _extrair_features(self, celula: Tuple[int, int], tabuleiro) -> np.ndarray:
        """Extrai features da célula"""
        x, y = celula
        vizinhos = tabuleiro.obter_vizinhos(celula)
        
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
        
        centro = TAMANHO_TABULEIRO // 2
        dist_centro = abs(x - centro) + abs(y - centro)
        
        return np.array([x, y, bombas_adj, tesouros_adj, livres_adj, dist_centro, len(vizinhos)])
    
    def mover(self, nova_posicao: Tuple[int, int]):
        """Move para nova posição"""
        self.posicao = nova_posicao
        self.celulas_visitadas.add(nova_posicao)
        self.historico.append(nova_posicao)
        
        # ✅ NOVO: Manter apenas últimas 10 posições (evitar memória infinita)
        if len(self.historico) > 10:
            self.historico = self.historico[-10:]
        
        self.passos += 1
    
    def processar_celula(self, tipo: str, tabuleiro):
        """Processa interação com célula"""
        resultado = {'tipo': tipo, 'sobreviveu': True, 'evento': None}
        
        # ✅ CRÍTICO: Registrar TODAS as células exploradas (inclusive livres)
        self.conhecimento_grupo.registrar(tipo, self.posicao)
        
        if tipo == TIPO_LIVRE:
            resultado['evento'] = 'livre'
        
        elif tipo == TIPO_BOMBA:
            if self.imunidades > 0:
                self.imunidades -= 1
                tabuleiro.desativar_bomba(self.posicao, self.grupo)
                resultado['evento'] = 'bomba_desativada'
            else:
                self.vivo = False
                self.bombas_acionadas += 1
                resultado['sobreviveu'] = False
                resultado['evento'] = 'morte'
        
        elif tipo == TIPO_TESOURO:
            self.imunidades += 1
            self.tesouros_encontrados += 1
            tabuleiro.coletar_tesouro(self.posicao, self.grupo)
            resultado['evento'] = 'tesouro'
        
        elif tipo == TIPO_BANDEIRA:
            resultado['evento'] = 'bandeira'
            resultado['vitoria'] = True 
        
        return resultado