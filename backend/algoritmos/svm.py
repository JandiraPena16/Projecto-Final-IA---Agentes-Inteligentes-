# algoritmos/svm.py - SVM

import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AlgoritmoSVM:
    """Support Vector Machine"""
    
    def __init__(self):
        self.modelo = SVC(kernel='rbf', C=1.0, probability=True, random_state=42)
        self.scaler = StandardScaler()
        self.treinado = False
        self.nome = "SVM"
    
    def treinar(self, X, y):
        """Treina o modelo"""
        X_norm = self.scaler.fit_transform(X)
        self.modelo.fit(X_norm, y)
        self.treinado = True
    
    def prever(self, features: np.ndarray) -> float:
        """Prediz score da célula"""
        if not self.treinado:
            return 0.5
        
        X_norm = self.scaler.transform(features.reshape(1, -1))
        prob = self.modelo.predict_proba(X_norm)[0]
        
        # Score: valoriza seguro/valioso, penaliza perigoso
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
