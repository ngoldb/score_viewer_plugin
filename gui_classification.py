from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGroupBox, QFormLayout, QCheckBox, QHBoxLayout
import numpy as np

from pymol import cmd
from .classification import classify
from .pymol_sync import sync_with_pymol
from .utils import status_msg

# TODO
# add export gui
class ClassificationTab:
    def __init__(self, plugin):
        self.plugin = plugin

        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Settings Box
        settings_box = QGroupBox("Classify")
        form = QFormLayout()
        self.exclude_chk_box = QCheckBox()
        self.exclude_chk_box.setToolTip("Models which had already been classified will not be loaded again")
        self.exclude_chk_box.setChecked(True)
        self.show_good_button = QPushButton("Load Good")
        self.show_good_button.clicked.connect(lambda: sync_with_pymol(self.plugin, self.plugin.good_models, False))
        self.show_bad_button = QPushButton("Load Bad")
        self.show_bad_button.clicked.connect(lambda: sync_with_pymol(self.plugin, self.plugin.bad_models, False))
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart)

        self.button_box = QHBoxLayout()
        for b in [self.show_good_button, self.show_bad_button, self.restart_button]:
            self.button_box.addWidget(b)
        form.addRow("Exclude already classified:", self.exclude_chk_box)
        form.addRow(self.button_box)
        settings_box.setLayout(form)
        
        # Classification
        classify_box = QGroupBox("Classify")
        form = QFormLayout()
        all_box = QHBoxLayout()
        self.all_good_button = QPushButton("Mark all good")
        self.all_bad_button = QPushButton("Mark all bad")
        self.all_good_button.clicked.connect(lambda: classify(self.plugin, good=True, enabled=False))
        self.all_bad_button.clicked.connect(lambda: classify(self.plugin, good=False, enabled=False))
        all_box.addWidget(self.all_good_button)
        all_box.addWidget(self.all_bad_button)
        enabled_box = QHBoxLayout()
        self.enabled_good_button = QPushButton("Mark enabled good")
        self.enabled_bad_button = QPushButton("Mark enabled bad")
        self.enabled_good_button.clicked.connect(lambda: classify(self.plugin, good=True, enabled=True))
        self.enabled_bad_button.clicked.connect(lambda: classify(self.plugin, good=False, enabled=True))
        enabled_box.addWidget(self.enabled_good_button)
        enabled_box.addWidget(self.enabled_bad_button)

        form.addRow(all_box)
        form.addRow(enabled_box)
        classify_box.setLayout(form)

        # Export Box
        export_box = QGroupBox("Export")
        form = QFormLayout()
        self.export_fasta_button = QPushButton("Export to fasta")
        self.export_csv_button = QPushButton("Export to csv")
        form.addRow(self.export_fasta_button, self.export_csv_button)
        export_box.setLayout(form)

        # Layout
        for box in [settings_box, classify_box]: # export_box
            layout.addWidget(box)
    
    
    def restart(self):
        self.plugin.good_models = np.array([], dtype=int)
        self.plugin.bad_models = np.array([], dtype=int)
        self.plugin.scatter_tab_obj.plot_scores()
        status_msg("restarted calssification")