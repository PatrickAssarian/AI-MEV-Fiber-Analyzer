from typing import Tuple, Optional

class ImageCalibrator:
    """
    Módulo responsável por calcular os fatores de conversão entre pixels e micrômetros (µm).
    """

    @staticmethod
    def calculate_calibration(bbox_width_pixels: int, scale_value_um: float) -> Tuple[Optional[float], Optional[float]]:
        """
        Calcula os fatores de calibração baseados na largura da barra de escala detectada
        e no valor lido pelo OCR (já convertido para micrômetros).
        
        Args:
            bbox_width_pixels (int): Largura do bounding box da barra de escala em pixels.
            scale_value_um (float): Valor numérico da escala em micrômetros lido pelo OCR.
            
        Returns:
            Tuple contendo:
                - pixels_por_micrometro (float): Quantos pixels representam 1 µm.
                - micrometros_por_pixel (float): O tamanho de 1 pixel em µm (Resolução espacial).
            Retorna (None, None) se os valores de entrada forem inválidos.
        """
        if bbox_width_pixels <= 0 or scale_value_um <= 0.0:
            return None, None
            
        pixels_per_um = bbox_width_pixels / scale_value_um
        um_per_pixel = scale_value_um / bbox_width_pixels
        
        return pixels_per_um, um_per_pixel
