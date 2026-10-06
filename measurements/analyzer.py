import numpy as np
import cv2
from scipy.ndimage import distance_transform_edt
from skimage.morphology import skeletonize
from skimage.measure import regionprops, label
import math
from typing import Dict, Any

class FiberAnalyzer:
    """
    Realiza medições em fibras utilizando Geometria Computacional e Processamento Digital de Imagens (sem IA).
    """
    
    @staticmethod
    def analyze_fiber(mask: np.ndarray, um_per_pixel: float) -> Dict[str, Any]:
        """
        Analisa uma única máscara de fibra e extrai suas propriedades morfológicas.
        
        Args:
            mask (np.ndarray): Máscara binária da fibra (uint8, 255 para fibra, 0 para fundo).
            um_per_pixel (float): Fator de calibração espacial (µm/pixel). Se for 1.0, retorna em pixels.
            
        Returns:
            Dict: Dicionário contendo Área, Perímetro, Comprimento, Diâmetro (Médio, Máx, Mín),
                  Circularidade, Aspect Ratio e um indicativo se a medição falhou.
        """
        # Garante que seja booleana para as funções do skimage
        binary_mask = mask > 127
        
        if not np.any(binary_mask):
            return {"valid": False}
            
        # Calcula Distance Transform
        distance_map = distance_transform_edt(binary_mask)
        
        # Extrai o esqueleto (linha central da fibra)
        skeleton = skeletonize(binary_mask)
        
        # O diâmetro local é 2 * a distância até a borda (Distance Transform) nos pixels do esqueleto
        local_radii = distance_map[skeleton]
        local_diameters = local_radii * 2.0
        
        if len(local_diameters) == 0:
            return {"valid": False}
            
        # Diâmetros em pixels
        diam_mean_px = np.mean(local_diameters)
        diam_max_px = np.max(local_diameters)
        diam_min_px = np.min(local_diameters)
        
        # Extração de propriedades de região (Area, Perimeter, Bounding Box)
        labeled_mask = label(binary_mask)
        props = regionprops(labeled_mask)[0]
        
        area_px2 = props.area
        perimeter_px = props.perimeter
        
        # Comprimento aproximado: metade do perímetro
        # Melhor aproximação: número de pixels no esqueleto
        length_px = np.sum(skeleton)
        
        # Aspect Ratio = Comprimento / Diâmetro Médio
        aspect_ratio = length_px / diam_mean_px if diam_mean_px > 0 else 0
        
        # Circularidade = 4 * pi * Area / (Perimetro^2) (1 = círculo perfeito)
        circularity = (4 * math.pi * area_px2) / (perimeter_px ** 2) if perimeter_px > 0 else 0
        
        # Conversão para micrômetros
        return {
            "valid": True,
            "area_um2": area_px2 * (um_per_pixel ** 2),
            "perimeter_um": perimeter_px * um_per_pixel,
            "length_um": length_px * um_per_pixel,
            "diameter_mean_um": diam_mean_px * um_per_pixel,
            "diameter_max_um": diam_max_px * um_per_pixel,
            "diameter_min_um": diam_min_px * um_per_pixel,
            "circularity": circularity,
            "aspect_ratio": aspect_ratio,
            "raw_area_px": area_px2 # Mantém para passar ao classificador
        }
