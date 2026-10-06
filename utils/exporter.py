import pandas as pd
import cv2
import numpy as np
import os
import io
import tempfile
from typing import Dict, Any, List, Optional
from fpdf import FPDF  # requires fpdf2
from fpdf.enums import XPos, YPos


class DataExporter:
    """
    Gerencia a exportação dos resultados analíticos e das imagens para diversos formatos.
    """

    @staticmethod
    def save_csv(df: pd.DataFrame, filepath: str) -> None:
        """Salva o DataFrame em formato CSV."""
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

    @staticmethod
    def save_excel(df: pd.DataFrame, filepath: str) -> None:
        """Salva o DataFrame em formato Excel (.xlsx)."""
        df.to_excel(filepath, index=False, engine="openpyxl")

    @staticmethod
    def save_json(df: pd.DataFrame, filepath: str) -> None:
        """Salva o DataFrame em formato JSON."""
        df.to_json(filepath, orient="records", indent=4, force_ascii=False)

    @staticmethod
    def save_image(img: np.ndarray, filepath: str) -> None:
        """Salva uma imagem NumPy/OpenCV em disco."""
        cv2.imwrite(filepath, img)


class PDFReport(FPDF):
    """
    Geração do relatório em PDF formatado com resultados numéricos e gráficos.

    Herda de FPDF (fpdf2) para construção de documentos PDF multi-página.
    Os gráficos são embutidos através de buffers BytesIO, utilizando arquivos
    temporários do sistema operacional para compatibilidade com a biblioteca FPDF.
    """

    def header(self) -> None:
        """Cabeçalho padrão presente em todas as páginas."""
        self.set_font("helvetica", "B", 15)
        self.cell(
            0, 10,
            "Relatório de Análise de Fibras (MEV)",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(5)

    def footer(self) -> None:
        """Rodapé com número de página."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

    def add_summary_table(self, stats: Dict[str, Any]) -> None:
        """
        Adiciona a tabela de resumo estatístico dos diâmetros ao relatório.

        Args:
            stats: Dicionário retornado por StatsCalculator.calculate().
        """
        self.set_font("helvetica", "B", 12)
        self.cell(
            0, 10, "Resumo Estatístico dos Diâmetros",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        self.ln(2)

        self.set_font("helvetica", "", 10)
        diam_stats = stats.get("diameter_mean_um", {})

        if not diam_stats:
            self.cell(0, 10, "Dados não disponíveis.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        data = [
            ("Total de Fibras Válidas", str(stats.get("total_fibers", 0))),
            ("Média (µm)", f"{diam_stats.get('mean', 0):.2f}"),
            ("Mediana (µm)", f"{diam_stats.get('median', 0):.2f}"),
            ("Desvio Padrão (µm)", f"{diam_stats.get('std', 0):.2f}"),
            ("Coef. de Variação (%)", f"{diam_stats.get('cv', 0):.2f}"),
            ("Mínimo (µm)", f"{diam_stats.get('min', 0):.2f}"),
            ("Máximo (µm)", f"{diam_stats.get('max', 0):.2f}"),
        ]

        for row in data:
            self.cell(80, 8, row[0], border=1)
            self.cell(50, 8, row[1], border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(10)

    def add_plot(self, plot_buffer: io.BytesIO, title: str) -> None:
        """
        Incorpora um gráfico (BytesIO de PNG) ao PDF.

        Usa um arquivo temporário gerenciado pelo sistema operacional (tempfile)
        para garantir compatibilidade com fpdf2 e evitar conflitos de permissão
        ao rodar no Streamlit ou em ambientes de produção.

        Args:
            plot_buffer: Buffer BytesIO contendo a imagem PNG do gráfico.
            title:       Título a exibir acima do gráfico.
        """
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # ---- CORREÇÃO: usa tempfile em vez de gravar no CWD ----
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(plot_buffer.getbuffer())
            tmp_path = tmp.name

        try:
            self.image(tmp_path, x=10, w=150)
        finally:
            os.remove(tmp_path)  # sempre limpa, mesmo em caso de exceção

        self.ln(5)

    def generate_report(
        self,
        stats: Dict[str, Any],
        hist_buf: io.BytesIO,
        box_buf: io.BytesIO,
        output_path: str,
        violin_buf: Optional[io.BytesIO] = None,
    ) -> None:
        """
        Gera o relatório PDF completo.

        Página 1: tabela de resumo + histograma.
        Página 2: boxplot (+ violin plot, se fornecido).

        Args:
            stats:       Resultado de StatsCalculator.calculate().
            hist_buf:    Buffer BytesIO com o histograma PNG.
            box_buf:     Buffer BytesIO com o boxplot PNG.
            output_path: Caminho de saída do arquivo .pdf.
            violin_buf:  Buffer BytesIO opcional com o violin plot PNG.
        """
        self.add_page()
        self.add_summary_table(stats)
        self.add_plot(hist_buf, "Distribuição dos Diâmetros")

        self.add_page()
        self.add_plot(box_buf, "Boxplot dos Diâmetros")

        if violin_buf is not None:
            self.add_plot(violin_buf, "Violin Plot dos Diâmetros")

        self.output(output_path)
