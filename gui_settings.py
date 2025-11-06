from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QCheckBox, QFormLayout, QPushButton, QFileDialog
import numpy as np
import pandas as pd
from .utils import status_msg
from pymol import cmd

class SettingTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Data Source Box
        data_box = QGroupBox("Data Source")
        form = QFormLayout()
        self.load_btn = QPushButton("Browse")
        self.load_btn.clicked.connect(self.load_csv)
        self.csv_file_edit = QLineEdit(
            placeholderText='CSV file',
            readOnly=True
        )
        self.path_combo = QComboBox()

        # replacing paths on load
        self.path_replace = QLineEdit(placeholderText='/remote/data', clearButtonEnabled=True)
        self.path_with = QLineEdit(placeholderText='/mount/data', clearButtonEnabled=True)
        self.path_replace.textChanged.connect(self.set_replace_text)
        self.path_with.textChanged.connect(self.set_replace_text)

        form.addRow("Load CSV:", self.load_btn)
        form.addRow("CSV File:", self.csv_file_edit)
        form.addRow("Path:", self.path_combo)
        form.addRow("Path Replace:", self.path_replace)
        form.addRow("with:", self.path_with)

        data_box.setLayout(form)

        # Reference Structure Box
        reference_box = QGroupBox("Reference Structure")
        form = QFormLayout()
        
        self.ref_btn = QPushButton("Browse")
        self.ref_btn.clicked.connect(self.load_ref)
        self.ref_file_edit = QLineEdit(
            placeholderText="reference structure",
            readOnly=True
        )
        self.align_ref = QCheckBox()
        self.ref_color_combo = QComboBox()
        color_tuples = cmd.get_color_indices()
        color_names = [name for name, index in color_tuples]
        self.ref_color_combo.addItems(sorted(color_names))
        self.ref_color_combo.setCurrentIndex(self.ref_color_combo.findText('gray'))

        form.addRow("Load Reference:", self.ref_btn)
        form.addRow("Reference File:", self.ref_file_edit)
        form.addRow("Align models to reference:", self.align_ref)
        form.addRow("Color reference:", self.ref_color_combo)

        reference_box.setLayout(form)

        # Appearance Box
        appearance_box = QGroupBox("Appearance")
        form = QFormLayout()
        self.command_edit = QLineEdit(
            placeholderText="Command to run when loading structures",
            clearButtonEnabled=True
        )
        form.addRow("Load Command:", self.command_edit)
        appearance_box.setLayout(form)

        layout.addWidget(data_box)
        layout.addWidget(reference_box)
        layout.addWidget(appearance_box)

    def load_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(None, "Open CSV", "", "CSV Files (*.csv)")
        if not csv_path: return
        df = pd.read_csv(csv_path)
        if "path" not in df.columns: return
        self.plugin.df = df
        numeric_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        not_numeric_cols = [c for c in df.columns if c not in numeric_cols]
        self.plugin.scatter_tab_obj.x_combo.clear()
        self.plugin.scatter_tab_obj.x_combo.addItems(numeric_cols)
        self.plugin.scatter_tab_obj.y_combo.clear()
        self.plugin.scatter_tab_obj.y_combo.addItems(numeric_cols)
        self.path_combo.clear()
        self.path_combo.addItems(not_numeric_cols)
        self.csv_file_edit.setText(str(csv_path))
        status_msg(f"Loaded {len(df)} models")

    def load_ref(self):
        ref_path, _ = QFileDialog.getOpenFileName(None, "Open reference structure", "", "Structure Files (*.pdb *.cif)")
        if not ref_path: return
        self.plugin.reference_structure = ref_path
        self.ref_file_edit.setText(str(ref_path))
        status_msg("loaded reference structure")

    def set_replace_text(self):
        self.plugin.path_replace = (self.path_replace.text(), self.path_with.text())