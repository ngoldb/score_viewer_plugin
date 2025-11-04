from .main import ScoreViewerPlugin
from pymol.plugins import addmenuitemqt

plugin_dialog = None
def __init_plugin__(app=None):
    global plugin_dialog
    if plugin_dialog is None:
        plugin_dialog = ScoreViewerPlugin()
    addmenuitemqt("Score Viewer", lambda: plugin_dialog.show())
