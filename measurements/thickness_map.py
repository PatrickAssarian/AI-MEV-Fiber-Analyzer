import numpy as np
import cv2
from typing import List, Tuple

class ThicknessMapGenerator:
    """
    Gera o mapa de espessura (colorizado) baseado nos diâmetros das fibras segmentadas.
    """
    
    def __init__(self, thin_threshold_um: float = 5.0, thick_threshold_um: float = 15.0):
        """
        Inicializa os thresholds de cores.
        
        Args:
            thin_threshold_um: Abaixo deste valor, fibra é considerada 'fina' (Azul).
            thick_threshold_um: Acima deste valor, fibra é 'grossa' (Vermelha).
                                Entre thin e thick é 'média' (Verde).
        """
        self.thin_thresh = thin_threshold_um
        self.thick_thresh = thick_threshold_um
        
    def _get_color(self, diameter_um: float) -> Tuple[int, int, int]:
        """Retorna a cor BGR baseada na espessura."""
        if diameter_um < self.thin_thresh:
            return (255, 0, 0) # Azul (BGR)
        elif diameter_um > self.thick_thresh:
            return (0, 0, 255) # Vermelho (BGR)
        else:
            return (0, 255, 0) # Verde (BGR)
            
    def generate_map(self, original_shape: Tuple[int, int], masks: List[np.ndarray], diameters_um: List[float]) -> np.ndarray:
        """
        Gera uma imagem onde as fibras segmentadas são coloridas de acordo com sua espessura média.
        
        Args:
            original_shape: (height, width) da imagem base.
            masks: Lista de máscaras binárias.
            diameters_um: Lista com os diâmetros médios correspondentes a cada máscara.
            
        Returns:
            np.ndarray: Imagem colorida (BGR) do mapa de espessuras.
        """
        thickness_map = np.zeros((original_shape[0], original_shape[1], 3), dtype=np.uint8)
        
        if len(masks) != len(diameters_um):
            raise ValueError("O número de máscaras deve ser igual ao número de diâmetros calculados.")
            
        for mask, diam in zip(masks, diameters_um):
            color = self._get_color(diam)
            
            # Cria a máscara colorida apenas onde a máscara binária é 255
            colored_mask = np.zeros_like(thickness_map)
            colored_mask[mask > 127] = color
            
            # Adiciona ao mapa geral (cv2.add lida com sobreposições somando e saturando em 255, 
            # ou podemos apenas substituir os valores, optarei por max() para não corromper a cor em sobreposições)
            thickness_map = np.maximum(thickness_map, colored_mask)
            
        return thickness_map
