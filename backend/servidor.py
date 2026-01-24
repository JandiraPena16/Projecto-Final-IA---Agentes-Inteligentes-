# servidor_tempo_real.py - API com suporte a tempo real

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from configuracoes import *
from simulacao.simulador import Simulador
from algoritmos.svm import AlgoritmoSVM
from algoritmos.arvore_decisao import AlgoritmoArvore
from algoritmos.perceptron import AlgoritmoPerceptron
from algoritmos.mlp import AlgoritmoMLP

app = Flask(__name__)
CORS(app)

MODELOS = {}
SIMULACAO_ATUAL = None

def carregar_modelos():
    global MODELOS
    print("\nCarregando modelos...")
    
    svm = AlgoritmoSVM()
    if svm.carregar('modelos_treinados/svm.pkl'):
        MODELOS['SVM'] = svm
        print("  ✓ SVM")
    
    arvore = AlgoritmoArvore()
    if arvore.carregar('modelos_treinados/arvore_decisao.pkl'):
        MODELOS['ARVORE_DECISAO'] = arvore
        print("  ✓ Árvore")
    
    perceptron = AlgoritmoPerceptron()
    if perceptron.carregar('modelos_treinados/perceptron.pkl'):
        MODELOS['PERCEPTRON'] = perceptron
        print("  ✓ Perceptron")
    
    mlp = AlgoritmoMLP()
    if mlp.carregar('modelos_treinados/mlp.pkl'):
        MODELOS['MLP'] = mlp
        print("  ✓ MLP")

@app.route('/')
def home():
    return jsonify({'status': 'online', 'modelos': list(MODELOS.keys())})

@app.route('/simular_tempo_real', methods=['POST'])
def simular_tempo_real():
    """Cria simulação e retorna estado inicial"""
    global SIMULACAO_ATUAL
    
    dados = request.json
    
    alg_g2_nomes = dados.get('algoritmos_grupo2', [])
    alg_g3_nomes = dados.get('algoritmos_grupo3', [])
    
    if set(alg_g2_nomes) == set(alg_g3_nomes):
        return jsonify({'erro': 'Algoritmos devem ser diferentes!'}), 400
    
    alg_g2 = [MODELOS[nome] for nome in alg_g2_nomes if nome in MODELOS]
    alg_g3 = [MODELOS[nome] for nome in alg_g3_nomes if nome in MODELOS]
    
    config = {
        'abordagem': dados.get('abordagem', 'A'),
        'num_agentes': dados.get('num_agentes', 3),
        'percentagem_bombas': dados.get('percentagem_bombas', 50),
        'algoritmos_grupo2': alg_g2,
        'algoritmos_grupo3': alg_g3
    }
    
    try:
        SIMULACAO_ATUAL = Simulador(config)
        
        # Estado inicial
        estado = {
            'passo': 0,
            'completo': False,
            'tabuleiro': SIMULACAO_ATUAL.tabuleiro.exportar_matriz(),
            'grupos': obter_estado_grupos(SIMULACAO_ATUAL),
            'posicoes_agentes': obter_posicoes_agentes(SIMULACAO_ATUAL)
        }
        
        return jsonify(estado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/proximo_passo', methods=['POST'])
def proximo_passo():
    """Executa próximo passo da simulação"""
    global SIMULACAO_ATUAL
    
    if not SIMULACAO_ATUAL:
        return jsonify({'erro': 'Nenhuma simulação ativa'}), 400
    
    if SIMULACAO_ATUAL.completo:
        return jsonify({
            'completo': True,
            'sucesso': SIMULACAO_ATUAL.sucesso,
            'razao': SIMULACAO_ATUAL.razao
        })
    
    # Executar 1 passo
    SIMULACAO_ATUAL.passo += 1
    
    for grupo in SIMULACAO_ATUAL.grupos:
        if not grupo.todos_mortos():
            SIMULACAO_ATUAL._executar_passo_grupo(grupo)
    
    SIMULACAO_ATUAL._verificar_termino()
    
    # Estado atualizado
    estado = {
        'passo': SIMULACAO_ATUAL.passo,
        'completo': SIMULACAO_ATUAL.completo,
        'sucesso': SIMULACAO_ATUAL.sucesso if SIMULACAO_ATUAL.completo else None,
        'razao': SIMULACAO_ATUAL.razao if SIMULACAO_ATUAL.completo else None,
        'tabuleiro': SIMULACAO_ATUAL.tabuleiro.exportar_matriz(),
        'grupos': obter_estado_grupos(SIMULACAO_ATUAL),
        'posicoes_agentes': obter_posicoes_agentes(SIMULACAO_ATUAL)
    }
    
    return jsonify(estado)

def obter_estado_grupos(sim):
    """Extrai estado dos grupos"""
    stats = []
    for g in sim.grupos:
        stats.append({
            'grupo': g.numero,
            'vivos': len(g.obter_vivos()),
            'total': len(g.agentes),
            'tesouros': sum(a.tesouros_encontrados for a in g.agentes),
            'celulas_exploradas': len(g.conhecimento.celulas_exploradas)
        })
    return stats

def obter_posicoes_agentes(sim):
    """Extrai posições de todos agentes vivos"""
    posicoes = []
    for g in sim.grupos:
        for a in g.obter_vivos():
            posicoes.append({
                'grupo': g.numero,
                'id': a.id,
                'posicao': list(a.posicao)
            })
    return posicoes

@app.route('/simular', methods=['POST'])
def simular():
    """Simulação completa (modo original)"""
    dados = request.json
    
    alg_g2_nomes = dados.get('algoritmos_grupo2', [])
    alg_g3_nomes = dados.get('algoritmos_grupo3', [])
    
    if set(alg_g2_nomes) == set(alg_g3_nomes):
        return jsonify({'erro': 'Algoritmos devem ser diferentes!'}), 400
    
    alg_g2 = [MODELOS[nome] for nome in alg_g2_nomes if nome in MODELOS]
    alg_g3 = [MODELOS[nome] for nome in alg_g3_nomes if nome in MODELOS]
    
    config = {
        'abordagem': dados.get('abordagem', 'A'),
        'num_agentes': dados.get('num_agentes', 3),
        'percentagem_bombas': dados.get('percentagem_bombas', 50),
        'algoritmos_grupo2': alg_g2,
        'algoritmos_grupo3': alg_g3
    }
    
    try:
        simulador = Simulador(config)
        resultado = simulador.executar()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    carregar_modelos()
    
    print("\n" + "="*60)
    print("🚀 SERVIDOR INICIADO (MODO TEMPO REAL)")
    print("="*60)
    print(f"URL: http://localhost:{PORTA}")
    print("="*60 + "\n")
    
    app.run(host=HOST, port=PORTA, debug=True)