from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGroupBox, QFormLayout, QCheckBox, QHBoxLayout, QLabel, QComboBox, QListWidget
from PyQt5.QtGui import QFont
import numpy as np

from pymol import cmd

from .utils import status_msg
from .pymol_sync import sync_with_pymol
from .classification import classify, export_csv, copy_models, export_fasta

# TODO
# SCROLL LIST
#  - list with model names of good and bad models
#  - if clicked --> model should be shown in PyMOL

class ClassificationTab:
    def __init__(self, plugin):
        self.plugin = plugin

        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        ## Settings Box
        settings_box = QGroupBox("")
        form = QFormLayout()
        self.exclude_chk_box = QCheckBox()
        self.exclude_chk_box.setToolTip("Models which had already been classified will not be loaded again")
        self.exclude_chk_box.setChecked(True)
        self.show_good_button = QPushButton("Load Good")
        self.show_good_button.clicked.connect(lambda: sync_with_pymol(self.plugin, self.plugin.good_models, False, True))
        self.show_bad_button = QPushButton("Load Bad")
        self.show_bad_button.clicked.connect(lambda: sync_with_pymol(self.plugin, self.plugin.bad_models, False, True))
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart)

        # Lists of classified models
        list_box = QHBoxLayout()
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("Bad models"))
        self.bad_models_list = QListWidget()
        left_column.addWidget(self.bad_models_list)

        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("Good models"))
        self.good_models_list = QListWidget()
        right_column.addWidget(self.good_models_list)

        list_box.addLayout(left_column)
        list_box.addLayout(right_column)

        # Construct Layout
        self.button_box = QHBoxLayout()
        for b in [self.show_good_button, self.show_bad_button, self.restart_button]:
            self.button_box.addWidget(b)
        form.addRow(list_box)
        form.addRow("Exclude already classified:", self.exclude_chk_box)
        form.addRow(self.button_box)
        settings_box.setLayout(form)
        
        ## Classification Box
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

        italic_font = QFont()
        italic_font.setItalic(True)
        info_box = QHBoxLayout()
        self.good_label = QLabel()
        self.bad_label = QLabel()
        self.good_label.setFont(italic_font)
        self.bad_label.setFont(italic_font)
        info_box.addWidget(self.good_label)
        info_box.addWidget(self.bad_label)

        form.addRow(all_box)
        form.addRow(enabled_box)
        form.addRow(info_box)
        classify_box.setLayout(form)

        ## Export Box
        export_box = QGroupBox("Export")
        form = QFormLayout()
        self.export_csv_button = QPushButton("Export to csv")
        self.copy_button = QPushButton("Copy classified models")
        self.copy_button.setToolTip("Copy models classified as good or bad to a directory")
        self.export_csv_button.setToolTip("Export scores of good and bad models to csv files")
        self.export_csv_button.clicked.connect(lambda: export_csv(self.plugin))
        self.copy_button.clicked.connect(lambda: copy_models(self.plugin))

        button_box = QHBoxLayout()
        for widget in [self.export_csv_button, self.copy_button]: 
            button_box.addWidget(widget)
        
        # Fasta Export
        self.fasta_name_combo = QComboBox()
        self.fasta_name_combo.setToolTip("The name of the column in the csv containing the names")
        self.fasta_seq_combo = QComboBox()
        self.fasta_seq_combo.setToolTip("The name of the column in the csv containing the sequences")
        self.seq_from_models = QCheckBox()
        self.seq_from_models.setToolTip("Load models into PyMOL and get sequences from models")
        self.fasta_model = QComboBox()
        self.fasta_model.setToolTip("Which model to load to derive the sequence from")
        self.fasta_chain = QComboBox()
        self.fasta_chain.setToolTip("The chain identifier")
        self.fasta_chain.addItems(['all', "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"])
        self.export_fasta_button = QPushButton("Export to fasta")
        self.export_fasta_button.clicked.connect(lambda: export_fasta(self.plugin))

        fasta_box_1 = QHBoxLayout()
        fasta_box_1.addWidget(QLabel("Name:"))
        fasta_box_1.addWidget(self.fasta_name_combo)
        fasta_box_1.addWidget(QLabel("|     Sequence:"))
        fasta_box_1.addWidget(self.fasta_seq_combo)
        fasta_box_1.addStretch()

        fasta_box_2 = QHBoxLayout()
        fasta_box_2.addWidget(self.seq_from_models)
        fasta_box_2.addWidget(QLabel("  Sequence from models"))
        fasta_box_2.addWidget(self.fasta_model)
        fasta_box_2.addWidget(QLabel("Chain"))
        fasta_box_2.addWidget(self.fasta_chain)
        fasta_box_2.addStretch()

        form.addRow(button_box)
        form.addRow(QLabel("")) # vertical space
        form.addRow(QLabel("Fasta Export:"))
        form.addRow(fasta_box_1)
        form.addRow(fasta_box_2)
        form.addRow(self.export_fasta_button)
        export_box.setLayout(form)

        # Layout
        for box in [settings_box, classify_box, export_box]:
            layout.addWidget(box)
    
    
    def restart(self):
        self.plugin.good_models = np.array([], dtype=int)
        self.plugin.bad_models = np.array([], dtype=int)
        self.plugin.scatter_tab_obj.plot_scores()
        self.good_label.setText(f"{len(self.plugin.good_models)}/{len(self.plugin.og_df)} good models")
        self.bad_label.setText(f"{len(self.plugin.bad_models)}/{len(self.plugin.og_df)} bad models")
        self.good_models_list.clear()
        self.bad_models_list.clear()
        status_msg("restarted calssification")
