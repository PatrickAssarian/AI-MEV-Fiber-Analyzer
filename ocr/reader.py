import re
import easyocr
import numpy as np
from typing import Tuple, Optional, Union

class ScaleOCR:
    """
    Módulo OCR para leitura do valor numérico e unidade da barra de escala.
    Utiliza EasyOCR e Expressões Regulares (Regex).
    """
    
    def __init__(self, gpu: bool = True):
        """
        Inicializa o leitor OCR.
        
        Args:
            gpu (bool): Se True, tenta usar a GPU (CUDA) se disponível.
        """
        # Inicializa o EasyOCR para o idioma inglês (comum em MEV)
        self.reader = easyocr.Reader(['en'], gpu=gpu)
        
        # Regex para capturar número inteiro ou decimal seguido de uma unidade opcional de espaçamento e texto
        # Ex: "10 um", "500 nm", "1.5 mm", "20µm"
        self.pattern = re.compile(r"([0-9]+[.,]?[0-9]*)\s*([a-zA-Zµμ]+)")

    def _convert_to_micrometers(self, value: float, unit: str) -> Optional[float]:
        """
        Converte um valor com base em sua unidade para micrômetros (µm).
        """
        unit = unit.lower()
        if unit in ["um", "µm", "μm"]:
            return value
        elif unit == "nm":
            return value / 1000.0
        elif unit == "mm":
            return value * 1000.0
        elif unit == "cm":
            return value * 10000.0
        else:
            return None # Unidade desconhecida

    def read_scale(self, image: Union[str, np.ndarray]) -> Tuple[Optional[float], Optional[str], Optional[float]]:
        """
        Lê o texto da imagem da barra de escala, extrai o valor e converte para micrômetros.
        
        Args:
            image (str | np.ndarray): Imagem recortada da barra de escala.
            
        Returns:
            Tuple contendo:
                - valor original (float)
                - unidade original (str)
                - valor convertido para micrômetros (float)
            Retorna (None, None, None) se não conseguir ler.
        """
        results = self.reader.readtext(image, detail=0) # detail=0 retorna apenas a lista de strings
        
        # Concatena todos os textos lidos (caso tenha lido quebrado)
        full_text = " ".join(results)
        
        if not full_text:
            return None, None, None
            
        match = self.pattern.search(full_text)
        
        if match:
            # Troca vírgula por ponto para conversão float (ex: 1,5 -> 1.5)
            val_str = match.group(1).replace(",", ".")
            try:
                value = float(val_str)
                unit = match.group(2)
                value_in_um = self._convert_to_micrometers(value, unit)
                return value, unit, value_in_um
            except ValueError:
                pass
                
        return None, None, None
