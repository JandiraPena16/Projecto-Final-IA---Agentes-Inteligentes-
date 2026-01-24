# algoritmos/mlp.py - MLP

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AlgoritmoMLP:
    """MLP com 3 neurónios na camada oculta"""
    
    def __init__(self):
        self.modelo = MLPClassifier(hidden_layer_sizes=(3,), max_iter=200, random_state=42)
        self.scaler = StandardScaler()
        self.treinado = False
        self.nome = "MLP"
    
    def treinar(self, X, y):
        """Treina modelo"""
        X_norm = self.scaler.fit_transform(X)
        self.modelo.fit(X_norm, y)
        self.treinado = True
    
    def prever(self, features: np.ndarray) -> float:
        """Prediz score"""
        if not self.treinado:
            return 0.5
        
        X_norm = self.scaler.transform(features.reshape(1, -1))
        prob = self.modelo.predict_proba(X_norm)[0]
        if len(prob) == 3:
            return prob[1] * 1.0 + prob[2] * 2.0 - prob[0] * 1.5
        return prob[1] if len(prob) > 1 else 0.5
    
    def salvar(self, caminho: str):
        """Salva modelo"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'wb') as f:
            pickle.dump({'modelo': self.modelo, 'scaler': self.scaler}, f)
    
    def carregar(self, caminho: str) -> bool:
        """Carrega modelo"""
        if os.path.exists(caminho):
            with open(caminho, 'rb') as f:
                dados = pickle.load(f)
                self.modelo = dados['modelo']
                self.scaler = dados['scaler']
                self.treinado = True
            return True
        return False
