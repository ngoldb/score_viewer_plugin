from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSizePolicy, QComboBox, QFormLayout, QPushButton, QDoubleSpinBox, QCheckBox, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import pandas as pd
from .utils import status_msg


class FilterTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Filter 1
        filter_1 = Filter(1, self.plugin)

        # Filter 2
        filter_2 = Filter(2, self.plugin)

        # Filter Button
        self.filter_data_button = QPushButton("Filter Data")
        self.filter_data_button.clicked.connect(self.filter_data)
        self.all_filter_label = QLabel("")
        self.filter_data_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.all_filter_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout.addWidget(filter_1.filter_box)
        layout.addWidget(filter_2.filter_box)
        layout.addWidget(self.filter_data_button)
        layout.addWidget(self.all_filter_label)

        self.plugin.all_filters = [
            filter_1,
            filter_2
        ]
    
    def filter_data(self):
        try:
            mask = pd.Series(True, index=self.plugin.og_df.index)
        except AttributeError as e:
            status_msg("Filter Tab: No data available. Please load a csv file in settings tab first!")
            return
        
        for f in self.plugin.all_filters:
            if f.apply:
                mask &= self.plugin.og_df[f.score].between(f.min_value, f.max_value)
        
        self.plugin.df = self.plugin.og_df[mask]
        self.all_filter_label.setText(f"{self.plugin.df.shape[0]}/{self.plugin.og_df.shape[0]} designs")
        status_msg(f"{self.plugin.df.shape[0]}/{self.plugin.og_df.shape[0]} designs pass all filters")


class Filter:
    def __init__(self, i, plugin):
        self.plugin = plugin
        self.filter_box = QGroupBox(f"Filter {i}")
        self.form = QFormLayout()
        self.chkbox = QCheckBox()
        self.score_combo = QComboBox()
        self.min_spin = QDoubleSpinBox()
        self.max_spin = QDoubleSpinBox()

        # Labels
        self.font = QFont()
        self.font.setItalic(True)
        self.min_label = QLabel("")
        self.min_label.setFont(self.font)
        self.max_label = QLabel("")
        self.max_label.setFont(self.font)
        self.apply_label = QLabel("")
        self.apply_label.setFont(self.font)

        self.chkbox.stateChanged.connect(self.update_filter)
        self.score_combo.currentTextChanged.connect(self.update_filter)
        self.min_spin.valueChanged.connect(self.update_filter)
        self.max_spin.valueChanged.connect(self.update_filter)

        # create layout
        self.form.addRow("Score:", self.score_combo)
        self.hbox_min = QHBoxLayout()
        self.hbox_min.addWidget(self.min_spin)
        self.hbox_min.addWidget(self.min_label)
        self.form.addRow("min:", self.hbox_min)
        self.hbox_max = QHBoxLayout()
        self.hbox_max.addWidget(self.max_spin)
        self.hbox_max.addWidget(self.max_label)
        self.form.addRow("max:", self.hbox_max)
        self.hbox_apply = QHBoxLayout()
        self.hbox_apply.addWidget(self.chkbox)
        self.hbox_apply.addWidget(self.apply_label)
        self.form.addRow("Apply filter:", self.hbox_apply)
        self.filter_box.setLayout(self.form)

        # init helpers
        self.apply = self.chkbox.isChecked()
        self.score = self.score_combo.currentText()
        self.min_value = self.min_spin.value()
        self.max_value = self.max_spin.value()

    def update_filter(self):
        self.apply = self.chkbox.isChecked()
        self.score = self.score_combo.currentText()
        self.min_value = self.min_spin.value()
        self.max_value = self.max_spin.value()

        # get max and min values of score
        data_min_value = self.plugin.df[self.score].min()
        data_max_value = self.plugin.df[self.score].max()
        self.min_label.setText(str(data_min_value))
        self.max_label.setText(str(data_max_value))

        # TODO needs bug fix
        # programatically setting the value blocks the spin box for the user
        # prevent box being stuck when updating value
        # self.min_spin.blockSignals(True)
        # self.max_spin.blockSignals(True)
        # self.min_spin.setValue(data_min_value)
        # self.max_spin.setValue(data_max_value)
        # self.min_spin.blockSignals(False)
        # self.max_spin.blockSignals(False)

        if self.apply:
            all_models = self.plugin.og_df.shape[0]
            passing_models = self.plugin.og_df[self.plugin.og_df[self.score].between(self.min_value, self.max_value)]
            self.apply_label.setText(f"{passing_models.shape[0]} / {all_models} designs pass")
        else:
            self.apply_label.setText("")