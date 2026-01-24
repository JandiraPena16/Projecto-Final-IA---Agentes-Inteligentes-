# algoritmos/arvore_decisao.py - Árvore de Decisão

import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle
import os

class AlgoritmoArvore:
    """Árvore de Decisão"""
    
    def __init__(self):
        self.modelo = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
        self.treinado = False
        self.nome = "ARVORE_DECISAO"
    
    def treinar(self, X, y):
        """Treina modelo"""
        self.modelo.fit(X, y)
        self.treinado = True
    
    def prever(self, features: np.ndarray) -> float:
        """Prediz score"""
        if not self.treinado:
            return 0.5
        
        prob = self.modelo.predict_proba(features.reshape(1, -1))[0]
        if len(prob) == 3:
            return prob[1] * 1.0 + prob[2] * 2.0 - prob[0] * 1.5
        return prob[1] if len(prob) > 1 else 0.5
    
    def salvar(self, caminho: str):
        """Salva modelo"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'wb') as f:
            pickle.dump(self.modelo, f)
    
    def carregar(self, caminho: str) -> bool:
        """Carrega modelo"""
        if os.path.exists(caminho):
            with open(caminho, 'rb') as f:
                self.modelo = pickle.load(f)
                self.treinado = True
            return True
        return False
