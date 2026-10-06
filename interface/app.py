import streamlit as st
import cv2
import numpy as np
import os
import io
import sys
import pandas as pd
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH para os imports funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scale_detector.detector import ScaleBarDetector
from ocr.reader import ScaleOCR
from calibration.calibrator import ImageCalibrator
from fiber_segmenter.segmenter import FiberSegmenter
from classifier.filter import ObjectClassifier
from measurements.analyzer import FiberAnalyzer
from measurements.thickness_map import ThicknessMapGenerator
from fiber_stats.calculator import StatsCalculator
from fiber_stats.plots import PlotGenerator
from utils.exporter import DataExporter, PDFReport

# ─────────────────────────────────────────────────────────────
# Configuração da Página
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MEV Fiber Analyzer",
    layout="wide",
    page_icon="🔬",
)

# ─────────────────────────────────────────────────────────────
# Inicialização dos Módulos (Cache de Recursos)
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    """
    Carrega todos os módulos do pipeline uma única vez e mantém em cache.

    Para ativar os modelos treinados, substitua None pelos caminhos reais
    dos pesos (.pt) em models/scale_detector_model e models/fiber_segmenter_model.
    """
    scale_model = r"c:\Users\patri\Desktop\PROJETO_MATERIAIS\models\segmenter_atual\weights\best.pt"
    seg_model   = r"c:\Users\patri\Desktop\PROJETO_MATERIAIS\models\segmenter_atual\weights\best.pt"

    detector   = ScaleBarDetector(scale_model)
    segmenter  = FiberSegmenter(seg_model)
    ocr        = ScaleOCR(gpu=False)   # False para garantir compatibilidade sem GPU
    classifier = ObjectClassifier()
    return detector, segmenter, ocr, classifier


detector, segmenter, ocr, classifier = load_models()
thickness_mapper = ThicknessMapGenerator()

# ─────────────────────────────────────────────────────────────
# Cabeçalho Principal
# ─────────────────────────────────────────────────────────────
st.title("🔬 Sistema de Análise de Fibras em MEV")
st.markdown(
    "Plataforma automatizada para segmentação e medição de fibras utilizando "
    "Deep Learning e Processamento Digital de Imagens."
)

# ─────────────────────────────────────────────────────────────
# Barra Lateral — Configurações
# ─────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Configurações")
modo = st.sidebar.radio("Modo de Operação", ["🖼️ Imagem Única", "📂 Lote (Pasta)"])

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetros de Classificação")
min_area      = st.sidebar.number_input("Área mínima (px²)", min_value=1, value=50)
max_area      = st.sidebar.number_input("Área máxima (px²)", min_value=1, value=1_000_000)
min_ar        = st.sidebar.number_input("Aspect Ratio mínimo", min_value=0.1, value=1.0, step=0.1)
thin_thresh   = st.sidebar.number_input("Limiar fibra fina (µm)", min_value=0.1, value=5.0, step=0.5)
thick_thresh  = st.sidebar.number_input("Limiar fibra grossa (µm)", min_value=0.1, value=15.0, step=0.5)

# ─────────────────────────────────────────────────────────────
# Funções Auxiliares
# ─────────────────────────────────────────────────────────────
def _run_pipeline(img_array: np.ndarray, um_per_pixel: float = 0.1):
    """
    Executa o pipeline completo de segmentação → medição → classificação.

    Args:
        img_array:    Imagem BGR lida pelo OpenCV.
        um_per_pixel: Calibração em µm/pixel. Padrão: 0.1 µm/px.

    Returns:
        Tuple(valid_masks, valid_diams, measurements, stats) ou None se sem fibras.
    """
    clf = ObjectClassifier(
        min_area=int(min_area),
        max_area=int(max_area),
        min_aspect_ratio=float(min_ar),
    )
    t_mapper = ThicknessMapGenerator(
        thin_threshold_um=float(thin_thresh),
        thick_threshold_um=float(thick_thresh),
    )

    masks = segmenter.segment(img_array)
    valid_masks, valid_diams, measurements = [], [], []

    for mask in masks:
        res = FiberAnalyzer.analyze_fiber(mask, um_per_pixel)
        if res["valid"] and clf.is_valid_fiber(res["raw_area_px"], res["aspect_ratio"]):
            valid_masks.append(mask)
            valid_diams.append(res["diameter_mean_um"])
            measurements.append(res)

    if not measurements:
        return None

    stats = StatsCalculator.calculate(measurements)
    thick_map = t_mapper.generate_map(img_array.shape, valid_masks, valid_diams)
    return valid_masks, valid_diams, measurements, stats, thick_map


def _build_exports(img_name: str, df: pd.DataFrame, stats: dict) -> dict:
    """
    Gera todos os buffers de exportação em memória (CSV, Excel, JSON, PDF).

    Args:
        img_name: Nome base da imagem (sem extensão).
        df:       DataFrame com os resultados por fibra.
        stats:    Dicionário de estatísticas de StatsCalculator.

    Returns:
        Dicionário com chaves 'csv', 'excel', 'json', 'pdf' (BytesIO ou bytes).
    """
    csv_buf = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    excel_buf = io.BytesIO()
    df.to_excel(excel_buf, index=False, engine="openpyxl")
    excel_buf.seek(0)

    json_buf = df.to_json(orient="records", indent=4, force_ascii=False).encode("utf-8")

    # Gera gráficos para o PDF (buffers independentes)
    hist_pdf   = PlotGenerator.plot_histogram_with_normal(df)
    box_pdf    = PlotGenerator.plot_boxplot(df)
    violin_pdf = PlotGenerator.plot_violinplot(df)

    pdf = PDFReport()
    pdf_buf = io.BytesIO()
    import tempfile, os as _os
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    pdf.generate_report(stats, hist_pdf, box_pdf, tmp_path, violin_buf=violin_pdf)
    with open(tmp_path, "rb") as f:
        pdf_data = f.read()
    _os.remove(tmp_path)

    return {"csv": csv_buf, "excel": excel_buf.read(), "json": json_buf, "pdf": pdf_data}


def _show_export_buttons(img_name: str, exports: dict) -> None:
    """Renderiza os botões de download de todos os formatos de exportação."""
    st.write("### 4. Exportar Dados")
    cols = st.columns(4)
    cols[0].download_button(
        "⬇️ CSV", data=exports["csv"],
        file_name=f"{img_name}_resultados.csv", mime="text/csv"
    )
    cols[1].download_button(
        "⬇️ Excel", data=exports["excel"],
        file_name=f"{img_name}_resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    cols[2].download_button(
        "⬇️ JSON", data=exports["json"],
        file_name=f"{img_name}_resultados.json", mime="application/json"
    )
    cols[3].download_button(
        "⬇️ PDF", data=exports["pdf"],
        file_name=f"{img_name}_relatorio.pdf", mime="application/pdf"
    )


# ─────────────────────────────────────────────────────────────
# Processamento — Imagem Única
# ─────────────────────────────────────────────────────────────
def process_single_image(img_array: np.ndarray, img_name: str) -> None:
    """
    Executa e exibe o pipeline completo para uma única imagem MEV.

    Etapas:
        1. Detecção da barra de escala + OCR + calibração
        2. Segmentação + medição + classificação
        3. Visualização (original, mapa de espessura)
        4. Estatísticas (tabela, histograma, boxplot, violin plot)
        5. Exportação (CSV, Excel, JSON, PDF)
    """
    # ── 1. Detecção de Escala ──────────────────────────────────
    st.write("### 1. Detecção de Escala")
    col1, col2 = st.columns(2)

    bbox, crop = detector.detect(img_array)
    um_per_pixel = 0.1  # fallback padrão

    if bbox is not None and crop is not None:
        col1.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), caption="Barra de Escala Detectada")
        val, unit, val_um = ocr.read_scale(crop)

        if val_um:
            width_px = bbox[2] - bbox[0]
            _, calc_um_px = ImageCalibrator.calculate_calibration(width_px, val_um)
            if calc_um_px:
                um_per_pixel = calc_um_px
                col2.success(f"**Escala Lida:** {val} {unit}")
                col2.info(f"**Calibração:** {um_per_pixel:.4f} µm/pixel")
            else:
                col2.warning("Erro ao calibrar — usando padrão (0.1 µm/px).")
        else:
            col2.warning("Texto da escala não lido — usando padrão (0.1 µm/px).")
    else:
        st.warning("Barra de escala não detectada — usando padrão (0.1 µm/px).")

    # ── 2. Segmentação e Medição ───────────────────────────────
    st.write("### 2. Segmentação e Medição")
    with st.spinner("Segmentando e medindo fibras..."):
        result = _run_pipeline(img_array, um_per_pixel)

    if result is None:
        st.error("Nenhuma fibra válida encontrada para medição.")
        return

    valid_masks, valid_diams, measurements, stats, thick_map = result
    st.success(f"✅ {len(valid_masks)} fibras válidas segmentadas e medidas!")

    # ── 3. Visualização ────────────────────────────────────────
    col_img1, col_img2 = st.columns(2)
    col_img1.image(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB), caption="Imagem Original")
    col_img2.image(
        cv2.cvtColor(thick_map, cv2.COLOR_BGR2RGB),
        caption="Mapa de Espessura  (🔵 Fina | 🟢 Média | 🔴 Grossa)",
    )

    # ── 4. Estatísticas ────────────────────────────────────────
    st.write("### 3. Resultados Estatísticos")
    df = stats["dataframe"]
    st.dataframe(df, use_container_width=True)

    # Três gráficos em colunas
    col_p1, col_p2, col_p3 = st.columns(3)
    hist_buf   = PlotGenerator.plot_histogram_with_normal(df)
    box_buf    = PlotGenerator.plot_boxplot(df)
    violin_buf = PlotGenerator.plot_violinplot(df)

    col_p1.image(hist_buf,   caption="Histograma + Distribuição Normal")
    col_p2.image(box_buf,    caption="Boxplot")
    col_p3.image(violin_buf, caption="Violin Plot")

    # ── 5. Exportação ──────────────────────────────────────────
    exports = _build_exports(img_name, df, stats)
    _show_export_buttons(img_name, exports)


# ─────────────────────────────────────────────────────────────
# Processamento — Lote (Pasta)
# ─────────────────────────────────────────────────────────────
VALID_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}


def process_batch_mode() -> None:
    """
    Interface de processamento em lote: varre uma pasta, processa cada imagem
    e salva os resultados (CSV, Excel, JSON, mapa de espessura) em 'results/'.
    """
    st.write("### Processamento em Lote")
    st.info(
        "Informe o caminho absoluto de uma pasta com imagens MEV. "
        "Os resultados serão salvos em `results/<nome_da_imagem>/`."
    )

    folder_path = st.text_input("📁 Caminho da pasta de imagens:", placeholder="Ex.: C:/imagens_mev")

    if not st.button("▶️ Iniciar Processamento em Lote"):
        return

    # ── Validação da pasta ────────────────────────────────────
    if not folder_path or not os.path.isdir(folder_path):
        st.error("Caminho inválido ou pasta não encontrada. Verifique e tente novamente.")
        return

    image_files = [
        Path(folder_path) / f
        for f in os.listdir(folder_path)
        if Path(f).suffix.lower() in VALID_EXTS
    ]

    if not image_files:
        st.warning("Nenhuma imagem válida encontrada na pasta informada.")
        return

    st.write(f"**{len(image_files)} imagens encontradas.** Iniciando pipeline...")

    results_root = Path("results")
    results_root.mkdir(exist_ok=True)

    progress_bar = st.progress(0, text="Aguarde…")
    log_area     = st.empty()
    summary_rows = []
    errors       = []

    for idx, img_path in enumerate(image_files, start=1):
        img_name = img_path.stem
        progress_bar.progress(idx / len(image_files), text=f"[{idx}/{len(image_files)}] {img_path.name}")

        # ── Lê a imagem ──────────────────────────────────────
        file_bytes = np.frombuffer(img_path.read_bytes(), dtype=np.uint8)
        img_array  = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img_array is None:
            errors.append(f"❌ Não foi possível ler: {img_path.name}")
            log_area.text("\n".join(errors))
            continue

        # ── Calibração ────────────────────────────────────────
        um_per_pixel = 0.1
        bbox, crop   = detector.detect(img_array)
        if bbox is not None and crop is not None:
            val, unit, val_um = ocr.read_scale(crop)
            if val_um:
                width_px = bbox[2] - bbox[0]
                _, calc_um_px = ImageCalibrator.calculate_calibration(width_px, val_um)
                if calc_um_px:
                    um_per_pixel = calc_um_px

        # ── Pipeline ──────────────────────────────────────────
        result = _run_pipeline(img_array, um_per_pixel)
        if result is None:
            errors.append(f"⚠️ Nenhuma fibra válida em: {img_path.name}")
            log_area.text("\n".join(errors))
            continue

        valid_masks, valid_diams, measurements, stats, thick_map = result
        df = stats["dataframe"]

        # ── Salva resultados ──────────────────────────────────
        out_dir = results_root / img_name
        out_dir.mkdir(parents=True, exist_ok=True)

        DataExporter.save_csv(df,    str(out_dir / "resultados.csv"))
        DataExporter.save_excel(df,  str(out_dir / "resultados.xlsx"))
        DataExporter.save_json(df,   str(out_dir / "resultados.json"))
        DataExporter.save_image(img_array,  str(out_dir / "original.png"))
        DataExporter.save_image(thick_map,  str(out_dir / "mapa_espessura.png"))

        # Resumo por imagem
        diam_s = stats.get("diameter_mean_um", {})
        summary_rows.append({
            "Imagem":          img_path.name,
            "Fibras Válidas":  stats.get("total_fibers", 0),
            "Média µm":        round(diam_s.get("mean",   0), 2),
            "Mediana µm":      round(diam_s.get("median", 0), 2),
            "Desvio Padrão µm": round(diam_s.get("std",  0), 2),
            "CV %":            round(diam_s.get("cv",     0), 2),
            "Calibração µm/px": round(um_per_pixel, 5),
        })

    progress_bar.empty()

    # ── Relatório Final do Lote ───────────────────────────────
    st.write("---")
    if summary_rows:
        st.success(f"✅ Processamento concluído! {len(summary_rows)} imagens analisadas com sucesso.")
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True)

        # Download do resumo consolidado
        csv_summary = summary_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "⬇️ Download Resumo Geral (CSV)",
            data=csv_summary,
            file_name="resumo_lote.csv",
            mime="text/csv",
        )

    if errors:
        with st.expander(f"⚠️ {len(errors)} aviso(s) / erro(s)"):
            for e in errors:
                st.write(e)


# ─────────────────────────────────────────────────────────────
# Roteamento Principal
# ─────────────────────────────────────────────────────────────
if modo == "🖼️ Imagem Única":
    uploaded_file = st.file_uploader(
        "Envie uma imagem MEV",
        type=["jpg", "jpeg", "png", "tif", "tiff", "bmp"],
    )
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img_array  = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img_array is None:
            st.error("Não foi possível decodificar a imagem. Tente outro arquivo.")
        else:
            process_single_image(img_array, Path(uploaded_file.name).stem)
else:
    process_batch_mode()
