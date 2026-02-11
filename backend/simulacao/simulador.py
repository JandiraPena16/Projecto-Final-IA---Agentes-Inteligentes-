# simulacao/simulador.py - Motor de Simulação CORRIGIDO

import time
import random
from typing import Dict, List, Tuple, Set
from collections import deque
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
        
        # Guardar total de tesouros inicial (fixo)
        self.total_tesouros_inicial = len(self.tabuleiro.posicoes_tesouros)
        print(f"Total de tesouros no tabuleiro: {self.total_tesouros_inicial}")
        
        self.passo = 0
        self.completo = False
        self.sucesso = False
        self.razao = ""
        self.tempo_inicio = None
        self.tempo_fim = None
        self.grupo_vencedor = None  # rastrear grupo vencedor
    
    def _criar_grupos(self, config: Dict) -> List[Grupo]:
        """Cria os 3 grupos"""
        print("\n=== CRIAR GRUPOS ===")
        grupos = []
        
        # Todos agentes começam em (0,0)
        # Garantir que (0,0) seja livre
        if self.tabuleiro.matriz[0][0] != TIPO_LIVRE:
            # Se (0,0) não for livre, trocar com uma posição livre
            for i in range(TAMANHO_TABULEIRO):
                for j in range(TAMANHO_TABULEIRO):
                    if self.tabuleiro.matriz[i][j] == TIPO_LIVRE:
                        # Trocar conteúdos
                        temp = self.tabuleiro.matriz[0][0]
                        self.tabuleiro.matriz[0][0] = TIPO_LIVRE
                        self.tabuleiro.matriz[i][j] = temp
                        
                        # Atualizar registros
                        if temp == TIPO_BOMBA:
                            self.tabuleiro.posicoes_bombas.discard((0, 0))
                            self.tabuleiro.posicoes_bombas.add((i, j))
                        elif temp == TIPO_TESOURO:
                            self.tabuleiro.posicoes_tesouros.discard((0, 0))
                            self.tabuleiro.posicoes_tesouros.add((i, j))
                        elif temp == TIPO_BANDEIRA:
                            self.tabuleiro.posicao_bandeira = (i, j)
                        break
                if self.tabuleiro.matriz[0][0] == TIPO_LIVRE:
                    break
        
        posicao_inicial = (0, 0)
        print(f" Posição inicial confirmada: {posicao_inicial}")
        
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
                print(f"  Agente {i}: posição inicial {posicao_inicial}")
                
                agente = Agente(i, num_grupo, posicao_inicial)
                agente.definir_algoritmos(algoritmos_ml)
                agentes.append(agente)
            
            grupo = Grupo(num_grupo, agentes)
            
            # Registrar posição inicial (0,0) no conhecimento do grupo
            tipo_inicial = self.tabuleiro.obter_tipo(posicao_inicial)
            grupo.conhecimento.registrar(tipo_inicial, posicao_inicial)
            print(f" Posição inicial {posicao_inicial} registrada para Grupo {num_grupo}")
            
            grupos.append(grupo)
            print(f"Grupo {num_grupo} criado com {len(agentes)} agentes")
        
        # OPÇÃO 1: APENAS ABORDAGEM B - Marcar bombas como exploradas
        if self.abordagem == ABORDAGEM_B:
            print(f"\n🎯 ABORDAGEM B: Marcando bombas como exploradas...")
            num_bombas_marcadas = 0
            
            for grupo in grupos:
                for bomba_pos in self.tabuleiro.posicoes_bombas:
                    grupo.conhecimento.celulas_exploradas.add(bomba_pos)
                    num_bombas_marcadas += 1
                
                print(f"   Grupo {grupo.numero}: {len(self.tabuleiro.posicoes_bombas)} bombas pré-marcadas")
                print(f"   Células exploradas iniciais: {len(grupo.conhecimento.celulas_exploradas)}")
        
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
        
        #  DEBUG: Log se grupo não tem agentes vivos
        if not agentes_vivos:
            if self.passo % 10 == 0:  # Log a cada 10 passos
                print(f"  Grupo {grupo.numero}: todos os agentes mortos")
            return
        
        eventos = []  #   Registrar eventos para logs
        
        # Rastrear quais agentes já foram reportados como parados
        if not hasattr(self, 'agentes_parados_reportados'):
            self.agentes_parados_reportados = set()
        
        for agente in agentes_vivos:
            bfs = BuscaEmLargura(self.tabuleiro)
            
            todas_visitadas = agente.celulas_visitadas | grupo.conhecimento.celulas_exploradas
            
            # Passar histórico recente para evitar loops
            candidatas = bfs.obter_candidatas(
                agente.posicao, 
                todas_visitadas, 
                grupo.numero,
                agente.historico  # Últimas posições
            )
            
            #  Se não há candidatas adjacentes, tentar busca expandida
            if not candidatas:
                candidatas = self._busca_expandida(agente.posicao, todas_visitadas, grupo.numero)
                
                #  ANTI-LOOP: Remover próximo passo se for voltar para posição recente
                if candidatas and len(agente.historico) >= 2:
                    candidatas = [c for c in candidatas if c not in agente.historico[-3:]]
                
                if not candidatas:
                    # Só reportar "parado" 1 vez por agente
                    agente_id = (grupo.numero, agente.id)
                    if agente_id not in self.agentes_parados_reportados:
                        self.agentes_parados_reportados.add(agente_id)
                        eventos.append({
                            'tipo': 'sem_movimento',
                            'grupo': grupo.numero,
                            'agente': agente.id,
                            'posicao': agente.posicao,
                            'razao': 'Sem células disponíveis para explorar'
                        })
                        # Debug no backend
                        print(f"  Grupo {grupo.numero} Agente {agente.id}: PRESO em {agente.posicao}")
                    continue
            else:
                # Se agente voltou a ter candidatas, remover do set de parados
                agente_id = (grupo.numero, agente.id)
                self.agentes_parados_reportados.discard(agente_id)
            
            proxima = agente.decidir_proxima_celula(candidatas, self.tabuleiro, self.abordagem)
            if not proxima:
                eventos.append({
                    'tipo': 'sem_movimento',
                    'grupo': grupo.numero,
                    'agente': agente.id,
                    'posicao': agente.posicao,
                    'razao': 'ML não conseguiu decidir'
                })
                continue
            
            pos_anterior = agente.posicao
            agente.mover(proxima)
            tipo = self.tabuleiro.obter_tipo(proxima)
            resultado = agente.processar_celula(tipo, self.tabuleiro)

            # VERIFICAR VITÓRIA IMEDIATA (BANDEIRA)
            if resultado.get('vitoria'):
                self.completo = True
                self.sucesso = True
                self.grupo_vencedor = grupo.numero
                self.razao = f"Grupo {grupo.numero} encontrou a bandeira!"
                print(f"\n🏁 VITÓRIA! Grupo {grupo.numero} encontrou a bandeira em {proxima}!")
                return
            

            #  Registrar evento de movimento
            evento = {
                'tipo': 'movimento',
                'grupo': grupo.numero,
                'agente': agente.id,
                'de': pos_anterior,
                'para': proxima,
                'celula_tipo': tipo,
                'evento_celula': resultado['evento']
            }
            
            if not resultado['sobreviveu']:
                evento['tipo'] = 'morte'
                print(f"  ☠️ Agente {agente.id} (G{grupo.numero}) MORREU em {proxima}")
            
            eventos.append(evento)
        
        # Armazenar eventos para enviar ao frontend
        if not hasattr(self, 'eventos_passo'):
            self.eventos_passo = []
        
        # Acumular eventos de todos os grupos
        self.eventos_passo.extend(eventos)
    
    def _busca_expandida(self, posicao: Tuple[int, int], visitadas: Set, grupo: int, raio: int = 5) -> List[Tuple[int, int]]:
        """
         Busca expandida que PLANEJA rota até células não visitadas
        - Procura células não visitadas em um raio maior
        - Retorna o PRÓXIMO PASSO no caminho (não a célula distante!)
        """
        fila = deque([(posicao, [posicao])])  # (posição_atual, caminho_até_aqui)
        visitadas_busca = {posicao}
        proximos_passos = []  # Lista de próximos passos que levam a células não visitadas
        
        while fila and len(proximos_passos) < 10:
            pos_atual, caminho = fila.popleft()
            
            # Limite de profundidade
            if len(caminho) > raio:
                continue
            
            for vizinho in self.tabuleiro.obter_vizinhos(pos_atual):
                if vizinho not in visitadas_busca:
                    visitadas_busca.add(vizinho)
                    novo_caminho = caminho + [vizinho]
                    
                    #  Se vizinho NÃO foi visitado → encontrou objetivo!
                    if vizinho not in visitadas:
                        # Verificar se não é bomba conhecida
                        if vizinho not in self.tabuleiro.bombas_desativadas.get(grupo, set()):
                            # Retornar o PRÓXIMO PASSO (posição 1 do caminho, não a final)
                            if len(novo_caminho) >= 2:
                                proximo_passo = novo_caminho[1]  # Primeira célula após posição atual
                                if proximo_passo not in proximos_passos:
                                    proximos_passos.append(proximo_passo)
                    else:
                        # Se já foi visitada, mas é LIVRE, continuar busca através dela
                        tipo = self.tabuleiro.obter_tipo(vizinho)
                        if tipo == 'L':
                            fila.append((vizinho, novo_caminho))
        
        return proximos_passos
    
    def _verificar_termino(self):
        """
        CORRIGIDO: Verifica condições de término
        Só marca vitória quando objetivos realmente alcançados
        """
        # Todos mortos
        if all(g.todos_mortos() for g in self.grupos):
            self.completo = True
            self.sucesso = False
            self.razao = "Todos os agentes morreram"
            return
        
        # Abordagem A: >50% tesouros ENCONTRADOS (histórico)
        if self.abordagem == ABORDAGEM_A:
            # CORRIGIDO: Usar total FIXO de tesouros do início
            total_tesouros = self.total_tesouros_inicial
            
            # VALIDAÇÃO: Só marcar vitória se pelo menos 1 agente vivo
            for grupo in self.grupos:
                if not grupo.pelo_menos_um_vivo():
                    continue  # Grupo morto não pode vencer
                
                # Total de tesouros ENCONTRADOS pelo grupo (nunca diminui)
                tesouros_encontrados = self.tabuleiro.tesouros_coletados[grupo.numero]
                
                # VALIDAÇÃO: Deve ter MAIS de 50%, não apenas >=
                if total_tesouros > 0 and tesouros_encontrados > total_tesouros * 0.5:
                    self.completo = True
                    self.sucesso = True
                    self.grupo_vencedor = grupo.numero
                    self.razao = f"Grupo {grupo.numero} encontrou >50% tesouros ({tesouros_encontrados}/{total_tesouros})"
                    return
        
        # Abordagem B: Exploração completa
        elif self.abordagem == ABORDAGEM_B:
            total_celulas = TAMANHO_TABULEIRO * TAMANHO_TABULEIRO
            num_bombas = len(self.tabuleiro.posicoes_bombas)
            
            # DEBUG
            print(f"\n🔍 DEBUG Abordagem B:")
            print(f"   Total células no tabuleiro: {total_celulas}")
            print(f"   Bombas pré-marcadas: {num_bombas}")
            print(f"   Células a explorar: {total_celulas - num_bombas}")
            
            for grupo in self.grupos:
                # VALIDAÇÃO: Deve ter pelo menos 1 agente vivo
                vivo = grupo.pelo_menos_um_vivo()
                celulas_exploradas = len(grupo.conhecimento.celulas_exploradas)
                
                # DEBUG
                print(f"   Grupo {grupo.numero}: {celulas_exploradas}/{total_celulas} células | Vivo: {vivo}")
                
                if not vivo:
                    continue
                
                # VALIDAÇÃO: Deve explorar 100% das células
                if celulas_exploradas >= total_celulas:
                    self.completo = True
                    self.sucesso = True
                    self.grupo_vencedor = grupo.numero
                    self.razao = f"Grupo {grupo.numero} explorou completamente ({celulas_exploradas}/{total_celulas})"
                    print(f"   🏆 VITÓRIA DETECTADA: Grupo {grupo.numero}!")
                    return
        
        # Abordagem C: Encontrar bandeira
        elif self.abordagem == ABORDAGEM_C:
            for grupo in self.grupos:
                # VALIDAÇÃO: Verificar se realmente encontrou bandeira
                if grupo.conhecimento.posicao_bandeira:
                    # EXTRA: Validar que a posição é a bandeira real
                    if grupo.conhecimento.posicao_bandeira == self.tabuleiro.posicao_bandeira:
                        self.completo = True
                        self.sucesso = True
                        self.grupo_vencedor = grupo.numero
                        self.razao = f"Grupo {grupo.numero} encontrou bandeira em {grupo.conhecimento.posicao_bandeira}"
                        return
        
        # Timeout - se passar de 1000 passos, ninguém vence
        if self.passo >= 1000:
            self.completo = True
            self.sucesso = False
            self.razao = f"Timeout: {self.passo} passos sem vitória"
            return
    
    def obter_estado_atual(self) -> Dict:
        """
        Retorna estado atual com eventos para logs detalhados
        """
        agentes_estado = []
        
        for grupo in self.grupos:
            for agente in grupo.agentes:
                if agente.vivo:
                    agentes_estado.append({
                        'id': agente.id,
                        'grupo': agente.grupo,
                        'posicao': agente.posicao,
                        'vivo': agente.vivo,
                        'imunidades': agente.imunidades,
                        'tesouros': agente.tesouros_encontrados
                    })
        
        stats_grupos = []
        for g in self.grupos:
            vivos = len(g.obter_vivos())
            tesouros = sum(a.tesouros_encontrados for a in g.agentes)
            celulas = len(g.conhecimento.celulas_exploradas)
            
            stats_grupos.append({
                'grupo': g.numero,
                'vivos': vivos,
                'total': len(g.agentes),
                'tesouros': tesouros,
                'celulas_exploradas': celulas
            })
        
        #  Incluir eventos do passo
        eventos = getattr(self, 'eventos_passo', [])
        
        # Calcular tempo decorrido
        tempo_decorrido = 0.0
        if self.tempo_inicio:
            if self.tempo_fim:
                tempo_decorrido = self.tempo_fim - self.tempo_inicio
            else:
                tempo_decorrido = time.time() - self.tempo_inicio
        
        return {
            'passo': self.passo,
            'tempo_segundos': tempo_decorrido,  # ADICIONADO
            'agentes': agentes_estado,
            'grupos': stats_grupos,
            'tabuleiro': self.tabuleiro.exportar_matriz(),
            'completo': self.completo,
            'sucesso': self.sucesso,
            'razao': self.razao,
            'grupo_vencedor': self.grupo_vencedor,
            'eventos': eventos  # : Eventos para logs
        }
    
    def _gerar_resultado(self) -> Dict:
        """Gera resultado final"""
        tempo = self.tempo_fim - self.tempo_inicio if self.tempo_fim else 0
        
        stats_grupos = []
        for g in self.grupos:
            vivos = len(g.obter_vivos())
            total = len(g.agentes)
            tesouros = sum(a.tesouros_encontrados for a in g.agentes)
            celulas = len(g.conhecimento.celulas_exploradas)
            
            #  Estatísticas detalhadas por agente
            agentes_detalhes = []
            for agente in g.agentes:
                agentes_detalhes.append({
                    'id': agente.id,
                    'vivo': agente.vivo,
                    'tesouros': agente.tesouros_encontrados,
                    'bombas_acionadas': agente.bombas_acionadas,
                    'celulas_visitadas': len(agente.celulas_visitadas),
                    'posicao_morte': agente.posicao if not agente.vivo else None,
                    'passo_morte': agente.passos if not agente.vivo else None
                })
            
            stats_grupos.append({
                'grupo': g.numero,
                'vivos': vivos,
                'total': total,
                'tesouros': tesouros,
                'celulas_exploradas': celulas,
                'agentes': agentes_detalhes  
            })
            
            print(f"\nGrupo {g.numero} FINAL:")
            print(f"  Vivos: {vivos}/{total}")
            print(f"  Tesouros: {tesouros}")
            print(f"  Células exploradas: {celulas}")
        
        resultado = {
            'sucesso': self.sucesso,
            'razao': self.razao,
            'grupo_vencedor': self.grupo_vencedor,  
            'tempo_segundos': tempo,
            'passos': self.passo,
            'grupos': stats_grupos,
            'tabuleiro': self.tabuleiro.exportar_matriz()
        }
        
        print(f"\nTabuleiro exportado: {len(resultado['tabuleiro'])}x{len(resultado['tabuleiro'][0])}")
        
        return resultado
    
    def executar_passo(self) -> Dict:
        """
         Executa um único passo da simulação
        Retorna estado atual para animação em tempo real
        """
        if self.completo or self.passo >= 1000:
            return self.obter_estado_atual()
        
        if self.passo == 0:
            self.tempo_inicio = time.time()
        
        self.passo += 1
        
        #  Limpar eventos do passo anterior
        self.eventos_passo = []
        
        # Executar passo para cada grupo
        for grupo in self.grupos:
            if not grupo.todos_mortos():
                self._executar_passo_grupo(grupo)
        
        # Verificar condições de término
        self._verificar_termino()
        
        if self.completo and not self.tempo_fim:
            self.tempo_fim = time.time()
        
        return self.obter_estado_atual()