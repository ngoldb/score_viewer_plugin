from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from .utils import status_msg

# Good/Bad classification remains but does not affect colors
def mark_good(plugin):
    if len(plugin.selected_indices) == 0: return
    paths = set(plugin.df.iloc[plugin.selected_indices]["path"])
    status_msg(f"Marked {len(paths)} as GOOD")

def mark_bad(plugin):
    if len(plugin.selected_indices) == 0: return
    paths = set(plugin.df.iloc[plugin.selected_indices]["path"])
    status_msg(f"Marked {len(paths)} as BAD")

def export_models(plugin, kind="good"):
    data = set(plugin.df.iloc[plugin.selected_indices]["path"]) if len(plugin.selected_indices) > 0 else set()
    if not data:
        QMessageBox.information(None, "No Data", f"No {kind} models to export.")
        return
    path, _ = QFileDialog.getSaveFileName(None, f"Export {kind.capitalize()} Models", f"{kind}_models.csv", "CSV Files (*.csv)")
    if not path: return
    pd.DataFrame({"path": sorted(data)}).to_csv(path, index=False)
    status_msg(f"Exported {len(data)} {kind} models to {path}")
