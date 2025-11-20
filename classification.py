import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
import numpy as np
from .utils import status_msg

from pymol import cmd


def classify(plugin, good: bool, enabled: bool):
    objects = cmd.get_object_list()
    if enabled:
        objects = [obj for obj in objects if obj in cmd.get_names("objects", enabled_only=1)]

    if len(objects) == 0: 
        if enabled: status_msg("No objects enabled")
        else: status_msg("No objects loaded")
        return

    # find indices
    selected = plugin.df.loc[
        plugin.df[plugin.setting_tab_obj.path_combo.currentText()].str.contains("|".join(objects))
    ].index
    selected = np.array(selected)

    # Adding models only if not yet present in group
    # removing entries from other group if present
    if good:
        group = "good"
        other_group = "bad"
        to_add = ~np.isin(selected, plugin.good_models)
        plugin.good_models = np.hstack([plugin.good_models, selected[to_add]])
        plugin.good_models = np.sort(plugin.good_models)
        
        to_remove = np.isin(plugin.bad_models, selected[to_add])
        plugin.bad_models = plugin.bad_models[~to_remove]
        plugin.bad_models = np.sort(plugin.bad_models)

    else:
        group = "bad"
        other_group = "good"
        to_add = ~np.isin(selected, plugin.bad_models)
        plugin.bad_models = np.hstack([plugin.bad_models, selected[to_add]])
        plugin.bad_models = np.sort(plugin.bad_models)
        
        to_remove = np.isin(plugin.good_models, selected[to_add])
        plugin.good_models = plugin.good_models[~to_remove]
        plugin.good_models = np.sort(plugin.good_models)

    # user information
    if sum(~to_add) != 0:
        status_msg(f"{sum(~to_add)} of {len(selected)} models were already classified as {group}")
    if sum(to_remove) != 0:
        status_msg(f"{sum(to_remove)} models found in {other_group} - removing from {other_group} and classify as {group}")
    status_msg(f"marked {to_add.sum()} models as {group}")

    # call plot scores to update coloring
    plugin.scatter_tab_obj.plot_scores()


# TODO
# export fasta
# export scores (csv)
# export models (copy files)

def export_csv(plugin):
    directory = QFileDialog.getExistingDirectory(
        None,
        caption="Choose export directory",
        directory=os.path.expanduser("~"), 
        options=QFileDialog.ShowDirsOnly # QFileDialog.DontUseNativeDialog
    )
    # save good models
    if len(plugin.good_models) > 0:
        good_model_file = os.path.join(directory, "good_models.csv")
        if os.path.exists(good_model_file):
            timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
            good_model_file = os.path.join(directory, f"good_models_{timestamp}.csv")
        export_df = plugin.df.iloc[plugin.good_models].copy()
        export_df.to_csv(good_model_file)
        status_msg(f"saved {len(export_df)} good models to {good_model_file}")
    else: status_msg("no good models to export")
    
    # save bad models
    if len(plugin.bad_models) > 0:
        bad_model_file = os.path.join(directory, "bad_models.csv")
        if os.path.exists(bad_model_file):
            timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
            bad_model_file = os.path.join(directory, f"bad_models_{timestamp}.csv")
        export_df = plugin.df.iloc[plugin.bad_models].copy()
        export_df.to_csv(bad_model_file)
        status_msg(f"saved {len(export_df)} bad models tp {bad_model_file}")
    else: status_msg("no bad models to export")

    return 

def export_models(plugin, kind="good"):
    data = set(plugin.df.iloc[plugin.selected_indices]["path"]) if len(plugin.selected_indices) > 0 else set()
    if not data:
        QMessageBox.information(None, "No Data", f"No {kind} models to export.")
        return
    path, _ = QFileDialog.getSaveFileName(None, f"Export {kind.capitalize()} Models", f"{kind}_models.csv", "CSV Files (*.csv)")
    if not path: return
    pd.DataFrame({"path": sorted(data)}).to_csv(path, index=False)
    status_msg(f"Exported {len(data)} {kind} models to {path}")