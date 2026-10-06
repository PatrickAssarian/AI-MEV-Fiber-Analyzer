import pandas as pd
import numpy as np
from typing import List, Dict, Any

class StatsCalculator:
    """
    Módulo para cálculo das estatísticas das fibras medidas.
    """
    
    @staticmethod
    def calculate(measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula estatísticas básicas para um conjunto de medições.
        
        Args:
            measurements: Lista de dicionários, onde cada dict é o resultado do FiberAnalyzer.
            
        Returns:
            Dict com estatísticas descritivas (média, mediana, moda, std, cv) e o DataFrame base.
        """
        # Filtra apenas medições válidas
        valid_measurements = [m for m in measurements if m.get("valid", False)]
        
        if not valid_measurements:
            return {"error": "Nenhuma medição válida fornecida."}
            
        df = pd.DataFrame(valid_measurements)
        
        stats = {
            "total_fibers": len(df),
            "dataframe": df
        }
        
        # Colunas numéricas que queremos analisar
        target_cols = [
            "diameter_mean_um", "diameter_max_um", "diameter_min_um",
            "length_um", "area_um2", "circularity", "aspect_ratio"
        ]
        
        for col in target_cols:
            if col in df.columns:
                series = df[col]
                mean_val = series.mean()
                std_val = series.std()
                
                stats[col] = {
                    "mean": mean_val,
                    "median": series.median(),
                    "mode": series.mode()[0] if not series.mode().empty else None,
                    "std": std_val,
                    "min": series.min(),
                    "max": series.max(),
                    "cv": (std_val / mean_val * 100) if mean_val > 0 else 0 # Coeficiente de Variação (%)
                }
                
        return stats
