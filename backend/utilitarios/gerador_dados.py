# utilitarios/gerador_dados.py - Gerador de Dados de Treino

import numpy as np
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuracoes import *

class GeradorDados:
    """Gera dados sintéticos para treino"""
    
    def __init__(self, num_ambientes: int = 1000):
        self.num_ambientes = num_ambientes
    
    def gerar_tabuleiro_aleatorio(self):
        """Gera um tabuleiro aleatório"""
        matriz = [[TIPO_LIVRE for _ in range(TAMANHO_TABULEIRO)] for _ in range(TAMANHO_TABULEIRO)]
        
        perc = random.uniform(0.5, 0.8)
        num_bombas = int(TAMANHO_TABULEIRO * TAMANHO_TABULEIRO * perc)
        num_tesouros = random.randint(5, 10)
        
        posicoes = [(i, j) for i in range(TAMANHO_TABULEIRO) for j in range(TAMANHO_TABULEIRO)]
        random.shuffle(posicoes)
        
        for i in range(num_bombas):
            x, y = posicoes[i]
            matriz[x][y] = TIPO_BOMBA
        
        for i in range(num_bombas, num_bombas + num_tesouros):
            if i < len(posicoes):
                x, y = posicoes[i]
                matriz[x][y] = TIPO_TESOURO
        
        return matriz
    
    def extrair_features(self, matriz, x, y):
        """Extrai features da célula"""
        bombas_adj = 0
        tesouros_adj = 0
        livres_adj = 0
        num_viz = 0
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < TAMANHO_TABULEIRO and 0 <= ny < TAMANHO_TABULEIRO:
                num_viz += 1
                tipo = matriz[nx][ny]
                if tipo == TIPO_BOMBA:
                    bombas_adj += 1
                elif tipo == TIPO_TESOURO:
                    tesouros_adj += 1
                elif tipo == TIPO_LIVRE:
                    livres_adj += 1
        
        centro = TAMANHO_TABULEIRO // 2
        dist = abs(x - centro) + abs(y - centro)
        
        return [x, y, bombas_adj, tesouros_adj, livres_adj, dist, num_viz]
    
    def gerar_dataset(self):
        """Gera dataset completo"""
        print(f"Gerando {self.num_ambientes} ambientes...")
        
        X = []
        y = []
        
        for i in range(self.num_ambientes):
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{self.num_ambientes}")
            
            matriz = self.gerar_tabuleiro_aleatorio()
            
            for x in range(TAMANHO_TABULEIRO):
                for y_coord in range(TAMANHO_TABULEIRO):
                    features = self.extrair_features(matriz, x, y_coord)
                    
                    tipo = matriz[x][y_coord]
                    if tipo == TIPO_BOMBA:
                        label = 0  # Perigoso
                    elif tipo == TIPO_TESOURO:
                        label = 2  # Valioso
                    else:
                        label = 1  # Seguro
                    
                    X.append(features)
                    y.append(label)
        
        print(f"Dataset gerado: {len(X)} amostras")
        return np.array(X), np.array(y)
