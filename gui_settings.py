from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QCheckBox, QFormLayout, QPushButton, QFileDialog, QHBoxLayout, QLabel
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
        form.addRow("Load CSV:", self.load_btn)
        form.addRow("CSV File:", self.csv_file_edit)
        data_box.setLayout(form)

        models_box = QGroupBox("Models")
        form = QFormLayout()

        # ToolTip messages
        path_tooltip_message = "Replace sections of the path. This can be useful when storing\nmodels on a remote and mounting the remote file system to local.\nE.g. replace /home/user/designs with /mnt/cluster/designs"
        combo_tooltip_message = "Column name in the csv specifying the path of the structures.\nPaths in this column will be used to load the models."
        model_chkbox_message = "Whether or not to load and display this model in PyMOL"
        suffix_message = "Suffix to add to model name to avoid duplicates"

        # Model 1
        self.path_combo = QComboBox()
        self.path_combo.setToolTip(combo_tooltip_message)

        # Model 2
        self.path_2_combo = QComboBox()
        self.path_2_combo.setToolTip(combo_tooltip_message)
        self.load_model_2_chkbox = QCheckBox()
        self.load_model_2_chkbox.setToolTip(model_chkbox_message)
        self.model_2_suffix = QLineEdit()
        self.model_2_suffix.setToolTip(suffix_message)

        # Model 3
        self.path_3_combo = QComboBox()
        self.path_3_combo.setToolTip(combo_tooltip_message)
        self.load_model_3_chkbox = QCheckBox()
        self.load_model_3_chkbox.setToolTip(model_chkbox_message)
        self.model_3_suffix = QLineEdit()
        self.model_3_suffix.setToolTip(suffix_message)

        # replacing paths on load
        self.path_replace = QLineEdit(placeholderText='/remote/data', clearButtonEnabled=True)
        self.path_with = QLineEdit(placeholderText='/mount/data', clearButtonEnabled=True)
        self.path_replace.textChanged.connect(self.set_replace_text)
        self.path_with.textChanged.connect(self.set_replace_text)
        self.path_replace.setToolTip(path_tooltip_message)

        # Layout
        replacement_box = QHBoxLayout()
        for widget in [QLabel("Replace"), self.path_replace, QLabel("with"), self.path_with]:
            replacement_box.addWidget(widget)

        model2_hbox = QHBoxLayout()
        model2_hbox.addWidget(self.path_2_combo)
        model2_hbox.addWidget(self.load_model_2_chkbox)
        model2_hbox.addWidget(QLabel("        suffix:"))
        model2_hbox.addWidget(self.model_2_suffix)

        model3_hbox = QHBoxLayout()
        model3_hbox.addWidget(self.path_3_combo)
        model3_hbox.addWidget(self.load_model_3_chkbox)
        model3_hbox.addWidget(QLabel("        suffix:"))
        model3_hbox.addWidget(self.model_3_suffix)

        form.addRow("Model 1:", self.path_combo)
        form.addRow("Model 2:", model2_hbox)
        form.addRow("Model 3:", model3_hbox)
        form.addRow(replacement_box)
        models_box.setLayout(form)
        

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
        self.align_ref.setToolTip("Align the loaded models to the loaded reference model")
        self.ref_color_combo = QComboBox()
        color_tuples = cmd.get_color_indices()
        color_names = [name for name, index in color_tuples]
        self.ref_color_combo.addItems(sorted(color_names))
        self.ref_color_combo.setCurrentIndex(self.ref_color_combo.findText('gray'))
        self.ref_in_all_chckbox = QCheckBox()
        self.ref_in_all_chckbox.setToolTip("Will display reference structure in all slots if enabling grid mode")

        form.addRow("Load Reference:", self.ref_btn)
        form.addRow("Reference File:", self.ref_file_edit)
        form.addRow("Align models to reference:", self.align_ref)
        form.addRow("Color reference:", self.ref_color_combo)
        form.addRow("Display in all slots:", self.ref_in_all_chckbox)

        reference_box.setLayout(form)

        # Appearance Box
        appearance_box = QGroupBox("Appearance")
        form = QFormLayout()
        self.command_edit = QLineEdit(
            placeholderText="Command to run when loading structures",
            clearButtonEnabled=True
        )
        self.command_edit.setToolTip("This command will be executed when loading structures.\nPyMOL syntax e.g. color skyblue; show sticks; util.cnc")
        self.grid_mode_chkbox = QCheckBox()
        self.grid_mode_chkbox.setToolTip("Enable grid mode if multiple models are loaded")
        self.group_models_chkbox = QCheckBox()
        self.group_models_chkbox.setChecked(True)
        self.group_models_chkbox.setToolTip("Create groups with the different models")
        form.addRow("Load Command:", self.command_edit)
        form.addRow("Use grid mode:", self.grid_mode_chkbox)
        form.addRow("Group models:", self.group_models_chkbox)
        appearance_box.setLayout(form)

        ## Global Layout
        layout.addWidget(data_box)
        layout.addWidget(models_box)
        layout.addWidget(reference_box)
        layout.addWidget(appearance_box)


    def load_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(None, "Open CSV", "", "CSV Files (*.csv)")
        if not csv_path: return
        df = pd.read_csv(csv_path)
        df.reset_index(drop=True, inplace=True)
        self.plugin.df = df
        self.plugin.og_df = df.copy()
        self.plugin.numeric_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        self.plugin.not_numeric_cols = [c for c in df.columns if c not in self.plugin.numeric_cols]
        self.path_combo.clear()
        self.path_combo.addItems(self.plugin.not_numeric_cols)
        self.path_2_combo.clear()
        self.path_2_combo.addItems(self.plugin.not_numeric_cols)
        self.path_3_combo.clear()
        self.path_3_combo.addItems(self.plugin.not_numeric_cols)
        self.csv_file_edit.setText(str(csv_path))

        # updating scatter tab
        self.plugin.scatter_tab_obj.x_combo.clear()
        self.plugin.scatter_tab_obj.x_combo.addItems(self.plugin.numeric_cols)
        self.plugin.scatter_tab_obj.y_combo.clear()
        self.plugin.scatter_tab_obj.y_combo.addItems(self.plugin.numeric_cols)

        # updating classification tab
        self.plugin.classify_tab_obj.fasta_name_combo.clear()
        self.plugin.classify_tab_obj.fasta_name_combo.addItems(self.plugin.not_numeric_cols)
        self.plugin.classify_tab_obj.fasta_seq_combo.clear()
        self.plugin.classify_tab_obj.fasta_seq_combo.addItems(self.plugin.not_numeric_cols)
        self.plugin.classify_tab_obj.fasta_model.clear()
        self.plugin.classify_tab_obj.fasta_model.addItems(self.plugin.not_numeric_cols)

        # updating filter tab
        for filter in self.plugin.all_filters:
            filter.score_combo.addItems(self.plugin.numeric_cols)

        status_msg(f"Loaded {len(df)} models")

    def load_ref(self):
        ref_path, _ = QFileDialog.getOpenFileName(None, "Open reference structure", "", "Structure Files (*.pdb *.cif)")
        if not ref_path: return
        self.plugin.reference_structure = ref_path
        self.ref_file_edit.setText(str(ref_path))
        status_msg("loaded reference structure")

    def set_replace_text(self):
        self.plugin.path_replace = (self.path_replace.text(), self.path_with.text())