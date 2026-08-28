from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSizePolicy, QComboBox, QFormLayout, QPushButton, QDoubleSpinBox, QCheckBox, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import pandas as pd
from .utils import status_msg


class FilterTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        self.data_filtered = False

        # Filter 1
        filter_1 = Filter(1, self.plugin)

        # Filter 2
        filter_2 = Filter(2, self.plugin)

        # Filter 3
        filter_3 = Filter(3, self.plugin)

        # Filter Button
        self.filter_data_button = QPushButton("Filter Data")
        self.filter_data_button.clicked.connect(self.filter_data)
        self.all_filter_label = QLabel("")
        self.filter_data_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.all_filter_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout.addWidget(filter_1.filter_box)
        layout.addWidget(filter_2.filter_box)
        layout.addWidget(filter_3.filter_box)
        layout.addWidget(self.filter_data_button)
        layout.addWidget(self.all_filter_label)

        self.plugin.all_filters = [
            filter_1,
            filter_2,
            filter_3
        ]
    
    def filter_data(self):
        try:
            mask = pd.Series(True, index=self.plugin.og_df.index)
        except AttributeError as e:
            status_msg("Filter Tab: No data available. Please load a csv file in settings tab first!", color="yellow")
            return
        
        for f in self.plugin.all_filters:
            if f.apply:
                mask &= self.plugin.og_df[f.score].between(f.min_value, f.max_value)
        
        # preserves original indexing of the df
        self.plugin.df = self.plugin.og_df[mask]
        self.all_filter_label.setText(f"{self.plugin.df.shape[0]}/{self.plugin.og_df.shape[0]} designs pass all filters")

        # call plotting function to update plot
        # TODO positional selection changes --> wrong dots in scatter plot are highlighted
        #      - reset entire selection (as in except block)
        #.     - correct positional selection
        try: 
            self.plugin.scatter_tab_obj.plot_scores()
        except IndexError as err:
            # this is because previously selected data points are not in the filtered df anymore
            # need to reset lasso selection
            self.plugin.scatter_tab_obj.positional_selected = []
            self.plugin.selected_indices = []
            self.plugin.scatter_tab_obj.plot_scores()

        status_msg(f"{self.plugin.df.shape[0]}/{self.plugin.og_df.shape[0]} designs pass all filters")


    def save(self, state_dict):
        filters = []

        for filter in self.plugin.all_filters:
            filters.append(
                [
                    filter.score_combo.currentText(),
                    filter.min_spin.value(),
                    filter.max_spin.value(),
                    filter.chkbox.isChecked()
                ]
            )

        filter_settings = {
            "filters": filters,
            "is_filtered": self.data_filtered
        }
        state_dict['FilterTab'] = filter_settings

        return state_dict


    def load(self, state_dict):
        filter_settings = state_dict["FilterTab"]
        filters = filter_settings['filters']

        for i, filter in enumerate(self.plugin.all_filters):
            filter.score_combo.setCurrentIndex(filter.score_combo.findText(filters[i][0]))
            filter.min_spin.setValue(filters[i][1])
            filter.max_spin.setValue(filters[i][2])
            filter.chkbox.setChecked(filters[i][3])

        if filter_settings['is_filtered']:
            self.filter_data()

        return 


class Filter:
    def __init__(self, i, plugin):
        self.plugin = plugin
        self.filter_box = QGroupBox(f"Filter {i}")
        self.form = QFormLayout()
        self.chkbox = QCheckBox()
        self.score_combo = QComboBox()
        self.min_spin = QDoubleSpinBox()
        self.max_spin = QDoubleSpinBox()

        for sb in [self.min_spin, self.max_spin]:
            sb.setDecimals(3)
            sb.setRange(-9999, 9999)
            sb.setSingleStep(0.1)

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
        try:
            data_min_value = self.plugin.og_df[self.score].min()
            data_max_value = self.plugin.og_df[self.score].max()
            self.min_label.setText(str(data_min_value))
            self.max_label.setText(str(data_max_value))
        except TypeError as e:
            status_msg("Filter Tab: No data available. Please load a csv file in settings tab first!", color="yellow")
            return

        if self.apply:
            all_models = self.plugin.og_df.shape[0]
            passing_models = self.plugin.og_df[self.plugin.og_df[self.score].between(self.min_value, self.max_value)]
            self.apply_label.setText(f"{passing_models.shape[0]} / {all_models} designs pass")
        else:
            self.apply_label.setText("")