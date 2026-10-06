import os
import cv2
import logging
from tqdm import tqdm
from scale_detector.detector import ScaleBarDetector
from fiber_segmenter.segmenter import FiberSegmenter
from ocr.reader import ScaleOCR
from calibration.calibrator import ImageCalibrator
from classifier.filter import ObjectClassifier
from measurements.analyzer import FiberAnalyzer
from measurements.thickness_map import ThicknessMapGenerator
from fiber_stats.calculator import StatsCalculator
from utils.exporter import DataExporter

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PipelineConfig:
    def __init__(self):
        self.scale_model_path = None
        self.seg_model_path = None
        self.output_dir = "results"
        self.default_um_per_pixel = 0.1 # Fallback
        self.thin_thresh = 5.0
        self.thick_thresh = 15.0

class FiberAnalysisPipeline:
    """
    Orquestrador central do sistema de análise de fibras.
    """
    def __init__(self, config: PipelineConfig):
        self.config = config
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        logging.info("Inicializando módulos...")
        self.scale_detector = ScaleBarDetector(config.scale_model_path)
        self.ocr = ScaleOCR(gpu=True)
        self.segmenter = FiberSegmenter(config.seg_model_path)
        self.classifier = ObjectClassifier()
        self.thickness_mapper = ThicknessMapGenerator(config.thin_thresh, config.thick_thresh)
        
    def process_image(self, image_path: str):
        """Processa uma única imagem."""
        filename = os.path.basename(image_path)
        name, _ = os.path.splitext(filename)
        out_dir = os.path.join(self.config.output_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        
        logging.info(f"[{name}] Lendo imagem...")
        img = cv2.imread(image_path)
        if img is None:
            logging.error(f"Falha ao ler {image_path}")
            return None
            
        # 1. Escala
        bbox, scale_crop = self.scale_detector.detect(img)
        um_per_pixel = self.config.default_um_per_pixel
        
        if bbox is not None and scale_crop is not None:
            val, unit, val_um = self.ocr.read_scale(scale_crop)
            if val_um is not None:
                width_px = bbox[2] - bbox[0]
                _, calc_um_px = ImageCalibrator.calculate_calibration(width_px, val_um)
                if calc_um_px is not None:
                    um_per_pixel = calc_um_px
                    logging.info(f"[{name}] Calibração: {um_per_pixel:.4f} µm/px")
                    
        # 2. Segmentação
        logging.info(f"[{name}] Segmentando fibras...")
        masks = self.segmenter.segment(img)
        
        # 3. Medição e Classificação
        logging.info(f"[{name}] Analisando {len(masks)} objetos detectados...")
        valid_masks = []
        valid_diams = []
        measurements = []
        
        for mask in masks:
            res = FiberAnalyzer.analyze_fiber(mask, um_per_pixel)
            if res["valid"]:
                if self.classifier.is_valid_fiber(res["raw_area_px"], res["aspect_ratio"]):
                    valid_masks.append(mask)
                    valid_diams.append(res["diameter_mean_um"])
                    measurements.append(res)
                    
        # 4. Estatísticas
        if measurements:
            stats = StatsCalculator.calculate(measurements)
            df = stats["dataframe"]

            # 5. Exportação — todos os formatos
            DataExporter.save_csv(df,   os.path.join(out_dir, "resultados.csv"))
            DataExporter.save_excel(df, os.path.join(out_dir, "resultados.xlsx"))
            DataExporter.save_json(df,  os.path.join(out_dir, "resultados.json"))

            # Imagem original + mapa de espessura
            DataExporter.save_image(img,      os.path.join(out_dir, "original.png"))
            thick_map = self.thickness_mapper.generate_map(img.shape, valid_masks, valid_diams)
            DataExporter.save_image(thick_map, os.path.join(out_dir, "mapa_espessura.png"))

            logging.info(f"[{name}] Finalizado. Fibras válidas: {len(valid_masks)}")
            return stats
        else:
            logging.warning(f"[{name}] Nenhuma fibra válida encontrada.")
            return None
            
    def process_batch(self, input_dir: str):
        """Processa todas as imagens em um diretório."""
        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
        logging.info(f"Iniciando processamento em lote de {len(files)} imagens.")
        
        all_stats = []
        for file in tqdm(files, desc="Processando Lote"):
            path = os.path.join(input_dir, file)
            stats = self.process_image(path)
            if stats:
                all_stats.append(stats)
                
        logging.info("Processamento em lote concluído.")
        return all_stats

if __name__ == "__main__":
    config = PipelineConfig()
    pipeline = FiberAnalysisPipeline(config)
    # Exemplo de uso
    # pipeline.process_batch("dataset/raw")
