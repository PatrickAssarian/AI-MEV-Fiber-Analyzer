import numpy as np

class ObjectClassifier:
    """
    Filtro/Classificador para remover objetos inválidos (ruído, aglomerados, impurezas).
    No momento, atua como um filtro heurístico baseado em propriedades geométricas.
    Poderá ser substituído por um modelo de Machine Learning (ex: Random Forest, SVM ou PyTorch).
    """
    
    def __init__(self, min_area: int = 50, max_area: int = 1000000, min_aspect_ratio: float = 2.0):
        """
        Inicializa o classificador com regras base.
        
        Args:
            min_area (int): Área mínima em pixels para não ser considerado ruído.
            max_area (int): Área máxima em pixels para não ser considerado aglomerado.
            min_aspect_ratio (float): Razão de aspecto mínima (comprimento / largura) para ser considerado fibra.
        """
        self.min_area = min_area
        self.max_area = max_area
        self.min_aspect_ratio = min_aspect_ratio
        
    def classify(self, area: float, aspect_ratio: float) -> str:
        """
        Classifica o objeto com base nas suas propriedades.
        
        Args:
            area (float): Área do objeto em pixels.
            aspect_ratio (float): Razão de aspecto do objeto.
            
        Returns:
            str: Categoria ("Fibra", "Ruído", "Aglomerado", "Impureza").
        """
        if area < self.min_area:
            return "Ruído"
        elif area > self.max_area:
            return "Aglomerado"
        elif aspect_ratio < self.min_aspect_ratio:
            return "Impureza"
        else:
            return "Fibra"

    def is_valid_fiber(self, area: float, aspect_ratio: float) -> bool:
        """
        Verifica se o objeto é uma fibra válida para medição.
        """
        return self.classify(area, aspect_ratio) == "Fibra"
