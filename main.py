from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from .gui_scatter import ScatterTab
from .gui_heatmap import HeatmapTab
from .gui_settings import SettingTab

class ScoreViewerPlugin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Score Viewer")
        self.resize(600, 800)
        self.onloadCommand = None

        # Data containers
        self.df = None
        self.selected_indices = []

        # Tabs
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Keep tab objects for access to controls
        self.scatter_tab_obj = ScatterTab(self)
        self.heatmap_tab_obj = HeatmapTab(self)
        self.setting_tab_obj = SettingTab(self)

        self.tabs.addTab(self.setting_tab_obj.widget, "Settings")
        self.tabs.addTab(self.scatter_tab_obj.widget, "Scatter Plot")
        self.tabs.addTab(self.heatmap_tab_obj.widget, "RMSD Heatmap")
        
