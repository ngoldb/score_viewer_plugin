from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QApplication
import numpy as np
from .gui_scatter import ScatterTab
from .gui_settings import SettingTab
from .gui_filter import FilterTab
from .gui_tinder import TinderTab
from .gui_classification import ClassificationTab

# TODO
# save score_viewer session to resume?
class ScoreViewerPlugin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Score Viewer")
        self.resize(600, 800)

        # Helper variables
        self.path_replace = None
        self.reference_structure = None
        self.ref_obj_name = None

        # Data containers
        self.df = None
        self.og_df = None
        self.selected_indices = []
        self.all_filters = []
        self.good_models = np.array([], dtype=int)
        self.bad_models = np.array([], dtype=int)
        self.tinder_state = False

        # Tabs
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Keep tab objects for access to controls
        self.scatter_tab_obj = ScatterTab(self)
        self.setting_tab_obj = SettingTab(self)
        self.filter_tab_obj = FilterTab(self)
        self.classify_tab_obj = ClassificationTab(self)
        self.tinder_tab_obj = TinderTab(self)
        
        self.tabs.addTab(self.setting_tab_obj.widget, "Settings")
        self.tabs.addTab(self.filter_tab_obj.widget, "Filter")
        self.tabs.addTab(self.scatter_tab_obj.widget, "Scatter Plot")
        self.tabs.addTab(self.classify_tab_obj.widget, "Classification")
        self.tabs.addTab(self.tinder_tab_obj.widget, "Tinder")

        # Keyboard event filter
        self.key_filter = ArrowKeyFilter(self)
        QApplication.instance().installEventFilter(self.key_filter)


class ArrowKeyFilter(QObject):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def eventFilter(self, obj, event):
        if not self.plugin.tinder_state:
            return False

        if event.type() != QEvent.KeyPress:
            return False

        # left arrow key: classify model as bad
        if event.key() == Qt.Key_Left:
            self.plugin.tinder_tab_obj.cycle_model(good=False)
            return True

        # right arrow key: classify model as good
        if event.key() == Qt.Key_Right:
            self.plugin.tinder_tab_obj.cycle_model(good=True)
            return True

        return False