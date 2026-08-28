from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QApplication, QFileDialog
import json
import numpy as np
from .gui_scatter import ScatterTab
from .gui_settings import SettingTab
from .gui_filter import FilterTab
from .gui_tinder import TinderTab
from .gui_classification import ClassificationTab
from .utils import status_msg

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
        self.selected_indices = np.array([], dtype=int)
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


    def save(self):
        save_path, _ = QFileDialog.getSaveFileName(None, "Choose Location", "", "JSON Files (*.json)")

        status_msg("Save session...")
        state_dict = {
            "main": [
                self.selected_indices.tolist(), 
                self.good_models.tolist(), 
                self.bad_models.tolist(), 
                self.tinder_state
            ]
        }
        # Settings
        state_dict = self.setting_tab_obj.save(state_dict)

        # Filters
        state_dict = self.filter_tab_obj.save(state_dict)

        # Scatter Plot
        state_dict = self.scatter_tab_obj.save(state_dict)

        # Classification
        state_dict = self.classify_tab_obj.save(state_dict)

        # Tinder
        state_dict = self.tinder_tab_obj.save(state_dict)
        
        # write state dict
        with open(save_path, 'w') as f:
            json.dump(state_dict, f)

        status_msg(f'saved session to {save_path}', color="green")
        return


    def load(self):
        load_path, _ = QFileDialog.getOpenFileName(None, "Load Session", "", "JSON Files (*.json)")
        if not load_path: 
            return 
        status_msg("Loading session...")

        # load state dict
        with open(load_path, 'r') as f:
            state_dict = json.load(f)

        ## apply settings
        main_state = state_dict["main"]
        
        self.selected_indices = np.array(main_state[0])
        self.good_models = np.array(main_state[1])
        self.bad_models = np.array(main_state[2])
        self.tinder_state = main_state[3]

        # Settings
        self.setting_tab_obj.load(state_dict)

        # Filters
        self.filter_tab_obj.load(state_dict)

        # Scatter Plot
        self.scatter_tab_obj.load(state_dict)

        # Classification
        self.classify_tab_obj.load(state_dict)

        # Tinder
        self.tinder_tab_obj.load(state_dict)

        status_msg(f"loaded {load_path}", color="green")
        return 

    
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