from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import seaborn as sns
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, leaves_list
from pymol import cmd
from .utils import status_msg

class HeatmapTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        self.compute_btn = QPushButton("Compute RMSD Heatmap")
        self.compute_btn.clicked.connect(self.compute_heatmap)
        layout.addWidget(self.compute_btn)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def compute_heatmap(self):
        if len(self.plugin.selected_indices) == 0: return
        df = self.plugin.df.iloc[self.plugin.selected_indices]
        file_paths = df["path"].tolist()
        labels = [fp.split("/")[-1] for fp in file_paths]

        rmsd = self.compute_rmsd_matrix(file_paths)
        linkage_matrix = linkage(squareform(rmsd), method="average")
        order = leaves_list(linkage_matrix)
        sorted_rmsd = rmsd[order][:, order]
        sorted_labels = [labels[i] for i in order]

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        sns.heatmap(sorted_rmsd, xticklabels=sorted_labels, yticklabels=sorted_labels, cmap="viridis", ax=ax)
        ax.set_title("RMSD Heatmap")
        self.fig.tight_layout()
        self.canvas.draw()
        status_msg("RMSD heatmap computed.")

    def compute_rmsd_matrix(self, file_paths):
        n = len(file_paths)
        rmsd = np.zeros((n,n))
        cmd.delete("all")
        names = []
        for i, p in enumerate(file_paths):
            obj = f"m{i}"
            cmd.load(p, obj)
            names.append(obj)
        for i in range(n):
            for j in range(i+1,n):
                try: val = cmd.align(names[i], names[j], cycles=0)[0]
                except: val = np.nan
                rmsd[i,j] = rmsd[j,i] = val
        return rmsd
