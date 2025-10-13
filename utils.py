def status_msg(msg):
    print(f"[ScoreViewer] {msg}")

def assign_colors(plugin):
    # All points have the same color; no good/bad highlighting
    import numpy as np
    return np.array(["blue"] * len(plugin.df)) if plugin.df is not None else []
