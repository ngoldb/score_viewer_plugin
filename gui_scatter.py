from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QGroupBox, QCheckBox, QFormLayout, QLabel, QPushButton, QComboBox, QSpinBox, QHBoxLayout, QDoubleSpinBox, QListWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import os
import numpy as np
import pandas as pd
from .utils import status_msg, assign_colors
from .pymol_sync import sync_with_pymol



class ScatterTab:

    MODEL_INDEX = Qt.UserRole

    def __init__(self, plugin):
        self.plugin = plugin
        self.positional_selected = []
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Controls
        control_box = QGroupBox("Controls")
        form = QFormLayout()
        self.x_combo = QComboBox()
        self.y_combo = QComboBox()
        self.plot_btn = QPushButton("Plot")
        self.plot_btn.clicked.connect(self.plot_scores)
        self.sync_btn = QPushButton("Sync with PyMOL")
        self.tinder_btn = QPushButton("Add to tinder")
        self.tinder_btn.clicked.connect(self.add2tinder)
        self.sync_btn.clicked.connect(lambda: sync_with_pymol(self.plugin, self.plugin.selected_indices, self.plugin.classify_tab_obj.exclude_chk_box.isChecked()))
        self.max_models_spin = QSpinBox()
        self.max_models_spin.setRange(1,200)
        self.max_models_spin.setValue(10)
        self.max_models_spin.setToolTip("Maximum number of models to load into PyMOL. Can be useful to prevent PyMOL\nfrom crashing. If the selected number of models exceeds the maximum\nspecified here, a random subset will be loaded.")
        self.color_classes = QCheckBox()
        self.color_classes.setToolTip("Colors data points according to classification (good: green, bad: red)")
        self.color_classes.setChecked(True)

        # Min / Max sliders for Zoom
        self.x_min_slider = QSlider()
        self.x_max_slider = QSlider()
        self.y_min_slider = QSlider()
        self.y_max_slider = QSlider()
        for s in [self.x_min_slider, self.x_max_slider, self.y_min_slider, self.y_max_slider]:
            s.setOrientation(1)  # Horizontal
            s.setMinimum(0)
            s.setMaximum(100)
            s.valueChanged.connect(self.plot_scores)
        
        # set defaults
        self.x_min_slider.setValue(0)
        self.y_min_slider.setValue(0)
        self.x_max_slider.setValue(100)
        self.y_max_slider.setValue(100)

        ## construct layout
        # X-axis settings
        self.x_hbox = QHBoxLayout()
        for w in [QLabel("X-axis:"), self.x_combo, QLabel("min:"), self.x_min_slider, QLabel("max:"), self.x_max_slider]:
            self.x_hbox.addWidget(w)
        form.addRow(self.x_hbox)

        # Y-axis settings
        self.y_hbox = QHBoxLayout()
        for w in [QLabel("Y-axis:"), self.y_combo, QLabel("min:"), self.y_min_slider, QLabel("max:"), self.y_max_slider]:
            self.y_hbox.addWidget(w)
        form.addRow(self.y_hbox)

        plot_setting_box_1 = QHBoxLayout()
        plot_setting_box_1.addWidget(QLabel("Max models to load:"))
        plot_setting_box_1.addWidget(self.max_models_spin)
        plot_setting_box_1.addStretch()
        plot_setting_box_1.addWidget(QLabel("Color classification:"))
        plot_setting_box_1.addWidget(self.color_classes)
        form.addRow(plot_setting_box_1)

        plot_setting_box_2 = QHBoxLayout()
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setDecimals(2)
        self.alpha_spin.setRange(0.2, 1)
        self.alpha_spin.setSingleStep(0.1)
        self.alpha_spin.setValue(1)
        self.alpha_spin.valueChanged.connect(self.plot_scores)

        self.marker_size_spin = QSpinBox()
        self.marker_size_spin.setRange(0, 100)
        self.marker_size_spin.setSingleStep(2)
        self.marker_size_spin.setValue(14)
        self.marker_size_spin.valueChanged.connect(self.plot_scores)

        plot_setting_box_2.addWidget(QLabel("Scatter Alpha:"))
        plot_setting_box_2.addWidget(self.alpha_spin)
        plot_setting_box_2.addStretch()
        plot_setting_box_2.addWidget(QLabel("Marker Size:"))
        plot_setting_box_2.addWidget(self.marker_size_spin)

        form.addRow(plot_setting_box_2)

        self.btn_hbox = QHBoxLayout()
        self.btn_hbox.addWidget(self.plot_btn)
        self.btn_hbox.addWidget(self.sync_btn)
        self.btn_hbox.addWidget(self.tinder_btn)
        form.addRow(self.btn_hbox)
        control_box.setLayout(form)
        layout.addWidget(control_box)

        # Scatter plot canvas
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)
        self.scatter = None
        self.lasso = None

    def plot_scores(self):
        if self.plugin.df is None: 
            status_msg("no data loaded", color="yellow")
            return
        x = self.x_combo.currentText()
        y = self.y_combo.currentText()
        if x=="" or y=="": 
            status_msg("no variables selected for plotting", color="yellow")
            return

        x_data = self.plugin.df[x]
        y_data = self.plugin.df[y]
        x_min, x_max = np.min(x_data), np.max(x_data)
        y_min, y_max = np.min(y_data), np.max(y_data)

        # Convert slider 0-100 to data range
        x_range_min = x_min + (x_max-x_min)*self.x_min_slider.value()/100
        x_range_max = x_min + (x_max-x_min)*self.x_max_slider.value()/100
        y_range_min = y_min + (y_max-y_min)*self.y_min_slider.value()/100
        y_range_max = y_min + (y_max-y_min)*self.y_max_slider.value()/100

        self.ax.clear()
        colors = assign_colors(self.plugin)
        self.scatter = self.ax.scatter(self.plugin.df[x], self.plugin.df[y], c=colors, s=self.marker_size_spin.value())

        # colors
        self.fc = self.scatter.get_facecolors()
        if len(self.positional_selected) != 0:
            self.fc[:, -1] = 0.1
            self.fc[self.positional_selected, -1] = self.alpha_spin.value()
        else:
            self.fc[:, -1] = self.alpha_spin.value()
        self.scatter.set_facecolors(self.fc)

        # axes
        self.ax.set_xlabel(x)  # Axis labels
        self.ax.set_ylabel(y)
        self.ax.set_title(f"{len(self.plugin.selected_indices)} / {self.plugin.df.shape[0]}")
        self.ax.set_xlim(x_range_min - x_range_min*0.02, x_range_max + x_range_max*0.02)
        self.ax.set_ylim(y_range_min - y_range_min*0.02, y_range_max + y_range_max*0.02)

        self.canvas.draw()
        if self.lasso: self.lasso.disconnect_events()
        self.lasso = LassoSelector(self.ax, onselect=self.on_lasso_select)


    def on_lasso_select(self, verts):
        df = self.plugin.df
        path_obj = Path(verts)
        pts = np.column_stack((df[self.x_combo.currentText()], df[self.y_combo.currentText()]))

        # ensure selection on df index, not positional indexing of array!
        self.positional_selected = np.nonzero(path_obj.contains_points(pts))[0]
        self.plugin.selected_indices = df.index[self.positional_selected]

        # change alpha of selected / non selected points
        if len(self.positional_selected) != 0:
            self.fc[:, -1] = 0.1
            self.fc[self.positional_selected, -1] = self.alpha_spin.value()
        else:
            self.fc[:, -1] = self.alpha_spin.value()
        self.scatter.set_facecolors(self.fc)

        # update title
        self.ax.set_title(f"{len(self.plugin.selected_indices)} / {self.plugin.df.shape[0]}")
        self.canvas.draw()
        
        status_msg(f"{len(self.plugin.selected_indices)}/{self.plugin.df.shape[0]} designs selected")


    def add2tinder(self):
        '''adds the selected models to tinder tab pending list'''
        
        if len(self.plugin.selected_indices) == 0:
            status_msg("No designs selected. Use the lasso tool to select designs first!", color="yellow")

        else:
            # get the first path variable from settings tab
            path_column = self.plugin.setting_tab_obj.path_combo.currentText()

            # get items currently in pending and completed lists
            all_pending = []
            all_completed = []
            for i in range(self.plugin.tinder_tab_obj.pending_list.count()):
                item = self.plugin.tinder_tab_obj.pending_list.item(i)
                all_pending.append(item.data(self.MODEL_INDEX))
            for i in range(self.plugin.tinder_tab_obj.completed_list.count()):
                item = self.plugin.tinder_tab_obj.completed_list.item(i)
                all_completed.append(item.data(self.MODEL_INDEX))

            # add all selected models to the pending list in tinder
            added = 0
            for selected_index in self.plugin.selected_indices:
                if selected_index in all_completed or selected_index in all_pending:
                    continue

                object_name = os.path.basename(self.plugin.og_df.loc[selected_index][path_column])
                self.plugin.tinder_tab_obj.add_pending_model(object_name, selected_index)
                added += 1 

            status_msg(f"{added} designs added to Tinder selection")