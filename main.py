from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget
import numpy as np
from .gui_scatter import ScatterTab
from .gui_heatmap import HeatmapTab
from .gui_settings import SettingTab
from .gui_filter import FilterTab
from .gui_classification import ClassificationTab

class ScoreViewerPlugin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Score Viewer")
        self.resize(600, 800)

        # Helper variables
        self.path_replace = None
        self.reference_structure = None

        # Data containers
        self.df = None
        self.og_df = None
        self.selected_indices = []
        self.all_filters = []
        self.good_models = np.array([], dtype=int)
        self.bad_models = np.array([], dtype=int)

        # Tabs
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Keep tab objects for access to controls
        self.scatter_tab_obj = ScatterTab(self)
        self.heatmap_tab_obj = HeatmapTab(self)
        self.setting_tab_obj = SettingTab(self)
        self.filter_tab_obj = FilterTab(self)
        self.classify_tab_obj = ClassificationTab(self)

        self.tabs.addTab(self.setting_tab_obj.widget, "Settings")
        self.tabs.addTab(self.filter_tab_obj.widget, "Filter")
        self.tabs.addTab(self.scatter_tab_obj.widget, "Scatter Plot")
        self.tabs.addTab(self.classify_tab_obj.widget, "Classification")
        # self.tabs.addTab(self.heatmap_tab_obj.widget, "RMSD Heatmap")
        
