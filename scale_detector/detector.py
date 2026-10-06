import os
import cv2
import numpy as np
from typing import Tuple, Optional, Union
from ultralytics import YOLO

class ScaleBarDetector:
    """
    Detector de Barra de Escala em imagens MEV utilizando YOLOv11.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa o detector carregando os pesos do YOLO.
        
        Args:
            model_path (str): Caminho para o arquivo de pesos do modelo (.pt).
                              Se None, inicializa sem modelo para fins de mock/testes.
        """
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
            
    def detect(self, image: Union[str, np.ndarray]) -> Tuple[Optional[Tuple[int, int, int, int]], Optional[np.ndarray]]:
        """
        Detecta a barra de escala e retorna o Bounding Box e a imagem recortada.
        
        Args:
            image (str | np.ndarray): Caminho da imagem ou array numpy (BGR).
            
        Returns:
            Tuple: 
                - bbox (x1, y1, x2, y2) em pixels ou None se não encontrar.
                - crop (np.ndarray) da barra de escala recortada ou None.
        """
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image}")
        else:
            img = image
            
        if self.model is None:
            # Fallback mock mode (se não houver modelo carregado, simula uma detecção na base da imagem)
            h, w = img.shape[:2]
            # Mock de bbox no canto inferior direito
            x1, y1, x2, y2 = int(w * 0.7), int(h * 0.9), int(w * 0.95), int(h * 0.98)
            crop = img[y1:y2, x1:x2]
            return (x1, y1, x2, y2), crop
            
        # Limiar de confiança para a barra de escala
        results = self.model(img, conf=0.1, verbose=False)
        
        # Assume-se que a classe 1 seja 'ScaleBar' e pega a de maior confiança
        best_box = None
        best_conf = 0.0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Verifica se é a classe ScaleBar (índice 1 no data.yaml)
                if int(box.cls[0].item()) != 1:
                    continue
                    
                conf = box.conf.item()
                if conf > best_conf:
                    best_conf = conf
                    best_box = box.xyxy[0].cpu().numpy().astype(int)
                    
        if best_box is not None:
            x1, y1, x2, y2 = best_box
            crop = img[y1:y2, x1:x2]
            return (x1, y1, x2, y2), crop
            
        return None, None
