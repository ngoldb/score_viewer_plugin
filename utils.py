import numpy as np

def status_msg(msg):
    print(f"[ScoreViewer] {msg}")

def assign_colors(plugin):
    # All points have the same color; no good/bad highlighting
    colors = np.array(["blue"] * len(plugin.df), dtype="object")

    # color by classification
    if plugin.scatter_tab_obj.color_classes.isChecked():
        for good in plugin.good_models:
            colors[good] = "green"
        for bad in plugin.bad_models:
            colors[bad] = "red"

    return colors
