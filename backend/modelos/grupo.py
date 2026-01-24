# modelos/grupo.py - Gerenciador de Grupos

from typing import List, Set, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ConhecimentoCompartilhado:
    """Conhecimento compartilhado entre agentes"""
    
    def __init__(self, numero_grupo: int):
        self.numero_grupo = numero_grupo
        self.celulas_exploradas = set()
        self.bombas_conhecidas = set()
        self.tesouros_conhecidos = set()
        self.posicao_bandeira = None
    
    def registrar(self, tipo: str, posicao: Tuple[int, int]):
        """Registra descoberta"""
        self.celulas_exploradas.add(posicao)
        if tipo == 'bomba' or tipo == 'bomba_desativada':
            self.bombas_conhecidas.add(posicao)
        elif tipo == 'tesouro':
            self.tesouros_conhecidos.add(posicao)
        elif tipo == 'bandeira':
            self.posicao_bandeira = posicao


class Grupo:
    """Gerencia grupo de agentes"""
    
    def __init__(self, numero: int, agentes: List):
        self.numero = numero
        self.agentes = agentes
        self.conhecimento = ConhecimentoCompartilhado(numero)
        
        for agente in self.agentes:
            agente.definir_conhecimento_grupo(self.conhecimento)
    
    def obter_vivos(self) -> List:
        """Retorna agentes vivos"""
        return [a for a in self.agentes if a.vivo]
    
    def todos_mortos(self) -> bool:
        """Verifica se todos morreram"""
        return all(not a.vivo for a in self.agentes)
    
    def pelo_menos_um_vivo(self) -> bool:
        """Verifica se há sobrevivente"""
        return any(a.vivo for a in self.agentes)
