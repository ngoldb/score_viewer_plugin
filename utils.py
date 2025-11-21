import numpy as np

def status_msg(msg):
    print(f"[ScoreViewer] {msg}")


def assign_colors(plugin):
    # All points have the same color; no /bad highlighting
    colors = np.array(["blue"] * len(plugin.df), dtype="object")

    # color by classification
    # we are plotting on plugin.df but the classified models might not be present
    # e.g. due to filtering. Therefore need to adjust the indexing
    if plugin.scatter_tab_obj.color_classes.isChecked():
        for i, idx in enumerate(plugin.df.index):
            if idx in plugin.good_models:
                colors[i] = "green"
            if idx in plugin.bad_models:
                colors[i] = "red"

    return colors
