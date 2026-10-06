import os
import cv2
import numpy as np
from typing import List, Tuple, Union, Optional
from ultralytics import YOLO

class FiberSegmenter:
    """
    Segmentador de Fibras em imagens MEV utilizando YOLOv11-Seg.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa o segmentador carregando os pesos do YOLO-Seg.
        
        Args:
            model_path (str): Caminho para o arquivo de pesos (.pt).
                              Se None, inicializa mock mode para testes.
        """
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
            
    def segment(self, image: Union[str, np.ndarray], conf_threshold: float = 0.5) -> List[np.ndarray]:
        """
        Segmenta a imagem e retorna uma lista de máscaras binárias isoladas para cada fibra.
        
        Args:
            image (str | np.ndarray): Caminho ou array (BGR) da imagem a ser segmentada.
            conf_threshold (float): Limiar mínimo de confiança para as detecções.
            
        Returns:
            List[np.ndarray]: Lista de máscaras binárias (uint8) com as mesmas dimensões da
                              imagem original, contendo 255 nos pixels da fibra e 0 no fundo.
        """
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image}")
        else:
            img = image
            
        masks_list = []
        
        if self.model is None:
            # Mock mode: cria máscaras fictícias (ex: retângulos horizontais no meio)
            h, w = img.shape[:2]
            mock_mask1 = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mock_mask1, (int(w*0.2), int(h*0.3)), (int(w*0.8), int(h*0.35)), 255, -1)
            
            mock_mask2 = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mock_mask2, (int(w*0.1), int(h*0.6)), (int(w*0.9), int(h*0.65)), 255, -1)
            
            return [mock_mask1, mock_mask2]
            
        # Limiar reduzido provisoriamente para V1.0
        results = self.model(img, conf=0.001, verbose=False)
        
        # Pega a primeira predição (única imagem enviada)
        result = results[0]
        
        if result.masks is None:
            return masks_list
            
        # Extrai os dados das máscaras
        masks_tensor = result.masks.data
        boxes = result.boxes
        
        original_shape = img.shape[:2]
        
        # Redimensiona e converte as máscaras para o tamanho original e tipo uint8
        for i, mask in enumerate(masks_tensor):
            # Filtra apenas a classe Fiber (índice 0 no yaml)
            if int(boxes.cls[i].item()) != 0:
                continue
                
            # Move o tensor para CPU e converte para NumPy
            mask_np = mask.cpu().numpy()
            
            # O YOLO pode redimensionar a máscara para o tamanho fixo da rede (ex: 640x640), 
            # então precisamos fazer um resize para o tamanho original da imagem.
            mask_resized = cv2.resize(mask_np, (original_shape[1], original_shape[0]), interpolation=cv2.INTER_NEAREST)
            
            # Converte para binário 0 ou 255
            mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
            
            masks_list.append(mask_binary)
            
        return masks_list
