# Idea from B. M. Wicky
# Through Inspection Never Discard Excellent pRoteins

from pymol import cmd

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem
from .utils import status_msg
from .pymol_sync import sync_with_pymol
from .classification import classify


# TODO:
# CURRENT BOX
# - show plots of scores (histograms) and highlight the currently loaded design's scores

class TinderTab:

    MODEL_INDEX = Qt.UserRole

    def __init__(self, plugin):
        self.plugin = plugin
        self.current_item = QListWidgetItem("None")
        self.current_item_name = QLabel(self.current_item.text())

        ### Layout
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        ## Current Item
        current_box = QGroupBox("Current")
        form = QFormLayout()
        form.addRow("Current model:", self.current_item_name)
        current_box.setLayout(form)

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

        # buttons
        self.start_btn = QPushButton("Start Tinder Mode")
        self.start_btn.clicked.connect(self.toggle_state)

        self.clear_btn = QPushButton("Clear pending list")
        self.clear_btn.clicked.connect(self.clear_pending)

        # Add widgets to the main tab layout
        layout.addWidget(current_box)
        layout.addWidget(info_box)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.clear_btn)


    def toggle_state(self):

        if self.plugin.tinder_state == False:

            if self.pending_list.count() == 0:
                status_msg("No pending models! Please add models first.", color="yellow")
                return 
            
            self.start_btn.setText("Stop Tinder Mode")
            self.plugin.tinder_state = True
            status_msg("Starting Tinder Mode")

            # load first model as current model:    
            self.current_item = self.pending_list.item(0)
            index = self.current_item.data(self.MODEL_INDEX)
            sync_with_pymol(self.plugin, selected_indices=[index], exclude_classified=False, use_og_df=True)
            self.current_item_name.setText(self.current_item.text())

            # update window title
            self.plugin.setWindowTitle("Score Viewer: Tinder Mode")

        else:
            self.start_btn.setText("Start Tinder Mode")
            self.plugin.tinder_state = False
            status_msg("Exit Tinder Mode")
            cmd.delete("all")
            self.current_item = QListWidgetItem("None")
            self.current_item_name.setText(self.current_item.text())
            
            # update window title
            self.plugin.setWindowTitle("Score Viewer")


    def clear_pending(self):
        self.pending_list.clear()


    def add_pending_model(self, text, model_index):
        item = QListWidgetItem(text)
        item.setData(self.MODEL_INDEX, model_index)
        self.pending_list.addItem(item)


    def add_completed_model(self, text, model_index):
        item = QListWidgetItem(text)
        item.setData(self.MODEL_INDEX, model_index)
        self.completed_list.addItem(item)

    
    def cycle_model(self, good: bool):

        # classify the loaded model (currently being displayed in PyMOL)
        classify(self.plugin, good=good, enabled=True)

        # update pending and completed lists
        classified_item = self.pending_list.takeItem(0)
        self.completed_list.addItem(classified_item)

        # sync new model
        next_item = self.pending_list.item(0)
        if next_item == None:
            status_msg("finished classification of all pending models!", color="yellow")
            self.toggle_state()
        else:
            selected_index = next_item.data(self.MODEL_INDEX)
            sync_with_pymol(self.plugin, selected_indices=[selected_index], exclude_classified=False, use_og_df=True)
            self.current_item = next_item
            self.current_item_name.setText(self.current_item.text())


    def save(self, state_dict):
        pending_list = []
        completed_list = []

        for i in range(self.pending_list.count()):
            item = self.pending_list.item(i)
            pending_list.append([item.text(), int(item.data(self.MODEL_INDEX))]) # [display name, model index]

        for i in range(self.completed_list.count()):
            item = self.completed_list.item(i)
            completed_list.append([item.text(), int(item.data(self.MODEL_INDEX))]) # [display name, model index]

        state_dict['TinderTab'] = {
            "pending_list": pending_list,
            "completed_list": completed_list
        }
        return state_dict


    def load(self, state_dict):
        tinder_settings = state_dict['TinderTab']

        for item_data in tinder_settings['pending_list']:
            self.add_pending_model(item_data[0], item_data[1])

        for item_data in tinder_settings['completed_list']:
            self.add_completed_model(item_data[0], item_data[1])

        # hacky but works
        self.toggle_state()
        self.toggle_state()

        return 