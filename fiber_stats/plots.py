import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.stats import norm
import io

class PlotGenerator:
    """
    Gera gráficos estatísticos (Histogramas, Boxplots, Violin Plots) para os dados das fibras.
    """
    
    @staticmethod
    def _save_to_buffer(fig) -> io.BytesIO:
        """Salva a figura do matplotlib em um buffer de memória para não precisar gravar em disco."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        plt.close(fig)
        return buf

    @staticmethod
    def plot_histogram_with_normal(df: pd.DataFrame, column: str = "diameter_mean_um", 
                                   title: str = "Distribuição dos Diâmetros Médios") -> io.BytesIO:
        """
        Gera um histograma com a curva de distribuição normal sobreposta.
        """
        data = df[column].dropna()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(data, bins='auto', kde=False, stat='density', ax=ax, color='skyblue', label='Dados')
        
        # Ajusta a Normal
        mu, std = norm.fit(data)
        xmin, xmax = ax.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        
        ax.plot(x, p, 'k', linewidth=2, label=f'Ajuste Normal\n($\mu={mu:.2f},\ \sigma={std:.2f}$)')
        
        ax.set_title(title)
        ax.set_xlabel(f"{column} (µm)")
        ax.set_ylabel("Densidade")
        ax.legend()
        
        return PlotGenerator._save_to_buffer(fig)

    @staticmethod
    def plot_boxplot(df: pd.DataFrame, column: str = "diameter_mean_um", 
                     title: str = "Boxplot dos Diâmetros Médios") -> io.BytesIO:
        """Gera um Boxplot."""
        fig, ax = plt.subplots(figsize=(8, 2))
        sns.boxplot(x=df[column], ax=ax, color='lightgreen')
        ax.set_title(title)
        ax.set_xlabel(f"{column} (µm)")
        
        return PlotGenerator._save_to_buffer(fig)
        
    @staticmethod
    def plot_violinplot(df: pd.DataFrame, column: str = "diameter_mean_um", 
                        title: str = "Violin Plot dos Diâmetros Médios") -> io.BytesIO:
        """Gera um Violin Plot."""
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.violinplot(x=df[column], ax=ax, color='salmon', inner="quartile")
        ax.set_title(title)
        ax.set_xlabel(f"{column} (µm)")
        
        return PlotGenerator._save_to_buffer(fig)
