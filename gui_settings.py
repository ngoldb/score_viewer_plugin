from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QPushButton, QComboBox, QSpinBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import numpy as np
import pandas as pd
from .utils import status_msg, assign_colors
from .classification import mark_good, mark_bad
from .pymol_sync import sync_with_pymol

class SettingTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        control_box = QGroupBox("Controls")
        form = QFormLayout()
        self.load_btn = QPushButton("Load CSV")
        self.load_btn.clicked.connect(self.load_csv)

        form.addRow("Load CSV:", self.load_btn)
        control_box.setLayout(form)
        layout.addWidget(control_box)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(None, "Open CSV", "", "CSV Files (*.csv)")
        if not path: return
        df = pd.read_csv(path)
        if "path" not in df.columns: return
        self.plugin.df = df
        numeric_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        self.plugin.scatter_tab_obj.x_combo.clear(); self.plugin.scatter_tab_obj.x_combo.addItems(numeric_cols)
        self.plugin.scatter_tab_obj.y_combo.clear(); self.plugin.scatter_tab_obj.y_combo.addItems(numeric_cols)
        status_msg(f"Loaded {len(df)} models")