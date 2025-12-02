import os
import shutil
import numpy as np
import pandas as pd
from pymol import cmd
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from .utils import status_msg


def classify(plugin, good: bool, enabled: bool):
    objects = cmd.get_object_list()
    if enabled:
        objects = [obj for obj in objects if obj in cmd.get_names("objects", enabled_only=1)]

    if len(objects) == 0: 
        if enabled: status_msg("No objects enabled", color="yellow")
        else: status_msg("No objects loaded", color="yellow")
        return

    # find indices
    objects = [f"{obj}." for obj in objects if obj != plugin.ref_obj_name]
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

    # update labels
    plugin.classify_tab_obj.good_label.setText(f"{len(plugin.good_models)}/{len(plugin.og_df)} good models")
    plugin.classify_tab_obj.bad_label.setText(f"{len(plugin.bad_models)}/{len(plugin.og_df)} bad models")


def export_csv(plugin):
    directory = QFileDialog.getExistingDirectory(
        None,
        caption="Choose export directory",
        directory=os.path.expanduser("~"), 
        options=QFileDialog.ShowDirsOnly # QFileDialog.DontUseNativeDialog
    )
    if not directory: return
    
    # save good models
    if len(plugin.good_models) > 0:
        good_model_file = os.path.join(directory, "good_models.csv")
        if os.path.exists(good_model_file):
            timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
            good_model_file = os.path.join(directory, f"good_models_{timestamp}.csv")
        export_df = plugin.og_df.loc[plugin.good_models].copy()
        export_df.to_csv(good_model_file)
        status_msg(f"saved {len(export_df)} good models to {good_model_file}", color="green")
    else: status_msg("no good models to export", color="yellow")
    
    # save bad models
    if len(plugin.bad_models) > 0:
        bad_model_file = os.path.join(directory, "bad_models.csv")
        if os.path.exists(bad_model_file):
            timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
            bad_model_file = os.path.join(directory, f"bad_models_{timestamp}.csv")
        export_df = plugin.df.loc[plugin.bad_models].copy()
        export_df.to_csv(bad_model_file)
        status_msg(f"saved {len(export_df)} bad models tp {bad_model_file}", color="green")
    else: status_msg("no bad models to export", color="yellow")

    return 


def copy_models(plugin):
    directory = QFileDialog.getExistingDirectory(
        None,
        caption="Choose export directory",
        directory=os.path.expanduser("~"), 
        options=QFileDialog.ShowDirsOnly
    )
    if not directory: return
    
    export_manager = {
        "good": [plugin.good_models],
        "bad": [plugin.bad_models]
    }
    
    for kind in export_manager:
        models = export_manager[kind][0]
        copied = 0
        if len(models) > 0:

            # create directory
            export_dir = os.path.join(directory, f"{kind}_models")
            if os.path.exists(export_dir):
                timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
                export_dir = os.path.join(directory, f"{kind}_models_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)

            # iterate over selected models of respective group
            selected_df = plugin.og_df.loc[models]
            for _, row in selected_df.iterrows():
                src_path = row[plugin.setting_tab_obj.path_combo.currentText()]
                if plugin.path_replace != None:
                    src_path = src_path.replace(plugin.path_replace[0], plugin.path_replace[1])
                if os.path.exists(src_path):
                    shutil.copy2(src_path, export_dir)
                    copied += 1
                else:
                    status_msg(f"failed to copy {src_path}", color="red")
            status_msg(f"copied {copied} models marked as {kind} to {export_dir}", color='green')

        else:
            status_msg(f"no {kind} models to export", color="yellow")
    return

# TODO: sequence from objects
def export_fasta(plugin):
    directory = QFileDialog.getExistingDirectory(
        None,
        caption="Choose export directory",
        directory=os.path.expanduser("~"), 
        options=QFileDialog.ShowDirsOnly
    )
    if not directory: return

    export_manager = {
        "good": plugin.good_models,
        "bad": plugin.bad_models
    }

    if plugin.classify_tab_obj.seq_from_models.isChecked():
        column_name = plugin.classify_tab_obj.fasta_model.currentText()

        for kind in export_manager:

            # load models into PyMOL
            if len(export_manager[kind]) > 0:
                cmd.delete("all")
                models = plugin.og_df.loc[export_manager[kind]][column_name].values

                if plugin.path_replace != None:
                    models = [m.replace(plugin.path_replace[0], plugin.path_replace[1]) for m in models]

                fasta_file = os.path.join(directory, f"{kind}_models.fasta")
                if os.path.exists(fasta_file):
                    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
                    fasta_file = os.path.join(directory, f"{kind}_models_{timestamp}.fasta")

                if plugin.classify_tab_obj.fasta_chain.currentText() == "all":
                    selection_str = "all"
                else:
                    selection_str = f"chain {plugin.classify_tab_obj.fasta_chain.currentText()}"

                with open(fasta_file, "w") as fobj:
                    count = 0
                    for model in models:
                        if os.path.exists(model):
                            cmd.load(model)
                            fasta_str = cmd.get_fastastr(selection_str)
                            if not fasta_str:
                                status_msg(f"failed to fetch sequence from {model} {selection_str}", color="yellow")
                                continue
                            fobj.writelines(fasta_str)
                            count += 1
                        else:
                            status_msg(f"failed to load {model}", color="yellow")

                        cmd.delete("all")
                
                status_msg(f"exported {count} sequences to {fasta_file}", color="green")

            else:
                status_msg(f"no {kind} models to export", color="yellow")

    else:
        # export with seq and name from csv
        name_col = plugin.classify_tab_obj.fasta_name_combo.currentText()
        seq_col = plugin.classify_tab_obj.fasta_seq_combo.currentText()

        for kind in export_manager:
            names = plugin.og_df.loc[export_manager[kind]][name_col].values
            seqs = plugin.og_df.loc[export_manager[kind]][seq_col].values

            if len(export_manager[kind]) > 0:
                fasta_file = os.path.join(directory, f"{kind}_models.fasta")
                if os.path.exists(fasta_file):
                    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
                    fasta_file = os.path.join(directory, f"{kind}_models_{timestamp}.fasta")
            
                with open(fasta_file, "w") as fobj:
                    for name, seq in zip(names, seqs):
                        fobj.writelines(f">{name}\n{seq}\n")
            
            else:
                status_msg(f"no {kind} models to export", color="yellow")

    return