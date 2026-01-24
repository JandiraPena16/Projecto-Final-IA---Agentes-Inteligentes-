# treinar_modelos.py - Script para Treinar os 4 Algoritmos

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilitarios.gerador_dados import GeradorDados
from algoritmos.svm import AlgoritmoSVM
from algoritmos.arvore_decisao import AlgoritmoArvore
from algoritmos.perceptron import AlgoritmoPerceptron
from algoritmos.mlp import AlgoritmoMLP

print("=" * 60)
print("TREINO DOS MODELOS DE APRENDIZAGEM")
print("=" * 60)

# Gerar dados
print("\n1. Gerando dados de treino...")
gerador = GeradorDados(num_ambientes=10)
X, y = gerador.gerar_dataset()

print(f"\nDados gerados:")
print(f"  - {len(X)} amostras")
print(f"  - {X.shape[1]} features")
print(f"  - Classes: {set(y)}")

# Criar diretório para modelos
os.makedirs('modelos_treinados', exist_ok=True)

# Treinar SVM
print("\n2. Treinando SVM...")
svm = AlgoritmoSVM()
svm.treinar(X, y)
svm.salvar('modelos_treinados/svm.pkl')
print("   ✓ SVM treinado e salvo")

# Treinar Árvore
print("\n3. Treinando Árvore de Decisão...")
arvore = AlgoritmoArvore()
arvore.treinar(X, y)
arvore.salvar('modelos_treinados/arvore_decisao.pkl')
print("   ✓ Árvore treinada e salva")

# Treinar Perceptron
print("\n4. Treinando Perceptron...")
perceptron = AlgoritmoPerceptron()
perceptron.treinar(X, y)
perceptron.salvar('modelos_treinados/perceptron.pkl')
print("   ✓ Perceptron treinado e salvo")

# Treinar MLP
print("\n5. Treinando MLP...")
mlp = AlgoritmoMLP()
mlp.treinar(X, y)
mlp.salvar('modelos_treinados/mlp.pkl')
print("   ✓ MLP treinado e salvo")

print("\n" + "=" * 60)
print("✓ TODOS OS MODELOS TREINADOS COM SUCESSO!")
print("=" * 60)
print("\nAgora pode executar: python servidor.py")
