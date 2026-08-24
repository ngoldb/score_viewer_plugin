from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QShortcut
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

        # Tinder Shortcuts
        self.left_shortcut = QShortcut(
            QKeySequence(Qt.Key_Left),
            self
        )
        self.right_shortcut = QShortcut(
            QKeySequence(Qt.Key_Right),
            self
        )

        # TODO
        # currently only works in the score viewer window and only
        # if not in Settings tab
        self.left_shortcut.setContext(Qt.ApplicationShortcut)
        self.right_shortcut.setContext(Qt.ApplicationShortcut)
        self.left_shortcut.setEnabled(False)
        self.right_shortcut.setEnabled(False)

        # left arrow key: reject model, right arrow key: accept model
        self.left_shortcut.activated.connect(lambda: self.tinder_tab_obj.cycle_model(good=False))
        self.right_shortcut.activated.connect(lambda: self.tinder_tab_obj.cycle_model(good=True))

