from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QGroupBox, QFormLayout, QPushButton, QComboBox, QSpinBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import numpy as np
import pandas as pd
from .utils import status_msg, assign_colors
from .classification import mark_good, mark_bad
from .pymol_sync import sync_with_pymol

class ScatterTab:
    def __init__(self, plugin):
        self.plugin = plugin
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Controls
        control_box = QGroupBox("Controls")
        form = QFormLayout()
        self.x_combo = QComboBox()
        self.y_combo = QComboBox()
        self.plot_btn = QPushButton("Plot")
        self.plot_btn.clicked.connect(self.plot_scores)
        # TODO: classification
        # self.classify_good_btn = QPushButton("Mark Good")
        # self.classify_good_btn.clicked.connect(lambda: mark_good(self.plugin))
        self.classify_bad_btn = QPushButton("Mark Bad")
        self.classify_bad_btn.clicked.connect(lambda: mark_bad(self.plugin))
        self.sync_btn = QPushButton("Sync with PyMOL")
        self.sync_btn.clicked.connect(lambda: sync_with_pymol(self.plugin))
        self.max_models_spin = QSpinBox()
        self.max_models_spin.setRange(1,200)
        self.max_models_spin.setValue(10)

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

        # construct layout
        form.addRow("X-axis:", self.x_combo)
        form.addRow("X Min:", self.x_min_slider)
        form.addRow("X Max:", self.x_max_slider)
        form.addRow("Y-axis:", self.y_combo)
        form.addRow("Y Min:", self.y_min_slider)
        form.addRow("Y Max:", self.y_max_slider)
        form.addRow("Plot:", self.plot_btn)
        form.addRow("Max models:", self.max_models_spin)
        # TODO: classification
        #form.addRow("Mark Good:", self.classify_good_btn)
        #form.addRow("Mark Bad:", self.classify_bad_btn)
        form.addRow("Sync with PyMOL:", self.sync_btn)
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
        if self.plugin.df is None: return
        x = self.x_combo.currentText()
        y = self.y_combo.currentText()
        if x=="" or y=="": return

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
        self.scatter = self.ax.scatter(self.plugin.df[x], self.plugin.df[y], c=colors)

        # colors
        self.fc = self.scatter.get_facecolors()

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
        #TODO: color highlighting of selected data points
        #TODO: display selected / total number of datapoints
        df = self.plugin.df
        path_obj = Path(verts)
        pts = np.column_stack((df[self.x_combo.currentText()], df[self.y_combo.currentText()]))
        self.plugin.selected_indices = np.nonzero(path_obj.contains_points(pts))[0]

        # change alpha of selected / non selected points
        self.fc[:, -1] = 0.2
        self.fc[self.plugin.selected_indices, -1] = 1
        self.scatter.set_facecolors(self.fc)

        # update title
        self.ax.set_title(f"{len(self.plugin.selected_indices)} / {self.plugin.df.shape[0]}")
        self.canvas.draw()
        
        status_msg(f"{len(self.plugin.selected_indices)} / {self.plugin.df.shape[0]} designs selected")
