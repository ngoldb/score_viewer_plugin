# Idea from B. M. Wicky
# Through Inspection Never Discard Excellent pRoteins

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem
from .utils import status_msg
from .pymol_sync import sync_with_pymol


# TODO:
#   - add clear pending list button
#
# CURRENT BOX
# - show plots of scores (histograms) and highlight the currently loaded design's scores
# - display the name of the loaded design

class TinderTab():

    DESIGN_INDEX = Qt.UserRole

    def __init__(self, plugin):
        self.plugin = plugin

        ### Layout
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        ## Current Item
        current_box = QGroupBox("Current")
        form = QFormLayout()

        ## Progress box
        info_box = QGroupBox("Progress")
        box_layout = QHBoxLayout(info_box)

        # Left column contains models to be classified
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Pending"))

        self.pending_list = QListWidget()
        left_layout.addWidget(self.pending_list)

        # Right column contains classified models
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Classified"))

        self.completed_list = QListWidget()
        right_layout.addWidget(self.completed_list)

        # Add both columns to the box
        box_layout.addLayout(left_layout)
        box_layout.addLayout(right_layout)

        # will also need a start/stop button
        self.start_btn = QPushButton("Start Tinder Mode")
        self.start_btn.clicked.connect(self.toggle_state)

        # Add widgets to the main tab layout
        layout.addWidget(current_box)
        layout.addWidget(info_box)
        layout.addWidget(self.start_btn)


    def toggle_state(self):
        if self.plugin.tinder_state == False:
            self.start_btn.setText("Stop Tinder Mode")
            self.plugin.tinder_state = True
            status_msg("Starting Tinder Mode")
        else:
            self.start_btn.setText("Start Tinder Mode")
            self.plugin.tinder_state = False
            status_msg("Exit Tinder Mode")

    def add_pending_model(self, text, design_index):
        item = QListWidgetItem(text)
        item.setData(self.DESIGN_INDEX, design_index)
        self.pending_list.addItem(item)