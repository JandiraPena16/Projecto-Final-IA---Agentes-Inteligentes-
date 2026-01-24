# simulacao/simulador.py - Motor de Simulação CORRIGIDO

import time
import random
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configuracoes import *
from modelos.tabuleiro import Tabuleiro
from modelos.agente import Agente
from modelos.grupo import Grupo
from algoritmos.busca_largura import BuscaEmLargura

class Simulador:
    """Coordena simulação completa"""
    
    def __init__(self, config: Dict):
        print("\n=== CRIAR SIMULADOR ===")
        print(f"Config: {config}")
        
        self.config = config
        self.abordagem = config['abordagem']
        self.num_agentes = config['num_agentes']
        
        print(f"Abordagem: {self.abordagem}")
        print(f"Num agentes: {self.num_agentes}")
        
        # Criar tabuleiro
        usar_bandeira = (self.abordagem == ABORDAGEM_C)
        print(f"Usar bandeira: {usar_bandeira}")
        
        self.tabuleiro = Tabuleiro(config.get('percentagem_bombas', 50), usar_bandeira)
        print(f"Tabuleiro criado: {self.tabuleiro.tamanho}x{self.tabuleiro.tamanho}")
        print(f"Bombas: {len(self.tabuleiro.posicoes_bombas)}")
        print(f"Tesouros: {len(self.tabuleiro.posicoes_tesouros)}")
        
        # Criar grupos
        self.grupos = self._criar_grupos(config)
        print(f"Grupos criados: {len(self.grupos)}")
        
        self.passo = 0
        self.completo = False
        self.sucesso = False
        self.razao = ""
        self.tempo_inicio = None
        self.tempo_fim = None
    
    def _criar_grupos(self, config: Dict) -> List[Grupo]:
        """Cria os 3 grupos"""
        print("\n=== CRIAR GRUPOS ===")
        grupos = []
        
        # Posições iniciais
        posicoes_livres = [(i, j) for i in range(TAMANHO_TABULEIRO) 
                          for j in range(TAMANHO_TABULEIRO)
                          if self.tabuleiro.matriz[i][j] == TIPO_LIVRE]
        
        print(f"Posições livres disponíveis: {len(posicoes_livres)}")
        random.shuffle(posicoes_livres)
        
        idx = 0
        
        for num_grupo in [1, 2, 3]:
            print(f"\n--- Grupo {num_grupo} ---")
            agentes = []
            
            # Algoritmos ML
            algoritmos_ml = []
            if num_grupo == 2:
                algoritmos_ml = config.get('algoritmos_grupo2', [])
            elif num_grupo == 3:
                algoritmos_ml = config.get('algoritmos_grupo3', [])
            
            print(f"Algoritmos ML: {[alg.nome if hasattr(alg, 'nome') else str(type(alg)) for alg in algoritmos_ml]}")
            
            for i in range(self.num_agentes):
                if idx < len(posicoes_livres):
                    pos = posicoes_livres[idx]
                    idx += 1
                else:
                    pos = random.choice(posicoes_livres)
                
                print(f"  Agente {i}: posição inicial {pos}")
                
                agente = Agente(i, num_grupo, pos)
                agente.definir_algoritmos(algoritmos_ml)
                agentes.append(agente)
            
            grupo = Grupo(num_grupo, agentes)
            grupos.append(grupo)
            print(f"Grupo {num_grupo} criado com {len(agentes)} agentes")
        
        return grupos
    
    def executar(self) -> Dict:
        """Executa simulação"""
        print("\n" + "="*60)
        print("INICIAR EXECUÇÃO DA SIMULAÇÃO")
        print("="*60)
        
        self.tempo_inicio = time.time()
        
        while not self.completo and self.passo < 1000:
            self.passo += 1
            
            if self.passo % 10 == 0:
                print(f"\nPasso {self.passo}...")
            
            for grupo in self.grupos:
                if not grupo.todos_mortos():
                    self._executar_passo_grupo(grupo)
            
            self._verificar_termino()
        
        self.tempo_fim = time.time()
        
        print("\n" + "="*60)
        print("SIMULAÇÃO CONCLUÍDA")
        print(f"Sucesso: {self.sucesso}")
        print(f"Razão: {self.razao}")
        print(f"Passos: {self.passo}")
        print(f"Tempo: {self.tempo_fim - self.tempo_inicio:.2f}s")
        print("="*60)
        
        return self._gerar_resultado()
    
    def _executar_passo_grupo(self, grupo: Grupo):
        """Executa passo para um grupo"""
        agentes_vivos = grupo.obter_vivos()
        
        if self.passo == 1:
            print(f"\nGrupo {grupo.numero}: {len(agentes_vivos)} agentes vivos")
        
        for agente in agentes_vivos:
            bfs = BuscaEmLargura(self.tabuleiro)
            
            todas_visitadas = agente.celulas_visitadas | grupo.conhecimento.celulas_exploradas
            candidatas = bfs.obter_candidatas(agente.posicao, todas_visitadas, grupo.numero)
            
            if not candidatas:
                if self.passo <= 5:
                    print(f"  Agente {agente.id} (G{grupo.numero}): sem candidatas")
                continue
            
            proxima = agente.decidir_proxima_celula(candidatas, self.tabuleiro)
            if not proxima:
                continue
            
            pos_anterior = agente.posicao
            agente.mover(proxima)
            tipo = self.tabuleiro.obter_tipo(proxima)
            resultado = agente.processar_celula(tipo, self.tabuleiro)
            
            if self.passo <= 5:
                print(f"  Agente {agente.id} (G{grupo.numero}): {pos_anterior} → {proxima} [{tipo}]")
            
            if not resultado['sobreviveu']:
                print(f"  ☠️ Agente {agente.id} (G{grupo.numero}) MORREU em {proxima}")
    
    def _verificar_termino(self):
        """Verifica condições de término"""
        # Todos mortos
        if all(g.todos_mortos() for g in self.grupos):
            self.completo = True
            self.sucesso = False
            self.razao = "Todos os agentes morreram"
            return
        
        # Abordagem A
        if self.abordagem == ABORDAGEM_A:
            total_tesouros = sum(self.tabuleiro.tesouros_coletados.values())
            total_disponiveis = len(self.tabuleiro.posicoes_tesouros)
            
            if total_disponiveis > 0 and total_tesouros > total_disponiveis * 0.5:
                self.completo = True
                self.sucesso = True
                self.razao = f"Mais de 50% tesouros encontrados ({total_tesouros}/{total_disponiveis})"
                return
        
        # Abordagem B
        elif self.abordagem == ABORDAGEM_B:
            total_exp = len(self.tabuleiro.celulas_exploradas[1] | 
                           self.tabuleiro.celulas_exploradas[2] | 
                           self.tabuleiro.celulas_exploradas[3])
            
            if total_exp == TAMANHO_TABULEIRO * TAMANHO_TABULEIRO:
                if any(g.pelo_menos_um_vivo() for g in self.grupos):
                    self.completo = True
                    self.sucesso = True
                    self.razao = "Exploração completa com sobrevivente"
                    return
        
        # Abordagem C
        elif self.abordagem == ABORDAGEM_C:
            for grupo in self.grupos:
                if grupo.conhecimento.posicao_bandeira:
                    self.completo = True
                    self.sucesso = True
                    self.razao = f"Grupo {grupo.numero} encontrou bandeira"
                    return
    
    def _gerar_resultado(self) -> Dict:
        """Gera resultado final"""
        tempo = self.tempo_fim - self.tempo_inicio
        
        stats_grupos = []
        for g in self.grupos:
            vivos = len(g.obter_vivos())
            total = len(g.agentes)
            tesouros = sum(a.tesouros_encontrados for a in g.agentes)
            celulas = len(g.conhecimento.celulas_exploradas)
            
            stats_grupos.append({
                'grupo': g.numero,
                'vivos': vivos,
                'total': total,
                'tesouros': tesouros,
                'celulas_exploradas': celulas
            })
            
            print(f"\nGrupo {g.numero} FINAL:")
            print(f"  Vivos: {vivos}/{total}")
            print(f"  Tesouros: {tesouros}")
            print(f"  Células exploradas: {celulas}")
        
        resultado = {
            'sucesso': self.sucesso,
            'razao': self.razao,
            'tempo_segundos': tempo,
            'passos': self.passo,
            'grupos': stats_grupos,
            'tabuleiro': self.tabuleiro.exportar_matriz()
        }
        
        print(f"\nTabuleiro exportado: {len(resultado['tabuleiro'])}x{len(resultado['tabuleiro'][0])}")
        
        return resultado