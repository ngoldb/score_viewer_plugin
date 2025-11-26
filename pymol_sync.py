import pymol
from pymol import cmd
from .utils import status_msg
import os
import numpy as np


def sync_with_pymol(plugin, selected_indices, exclude_classified, use_og_df: bool=False):

    # PyMOL is weird
    # Need to disable undo to fix broken Selectors
    # https://github.com/schrodinger/pymol-open-source/issues/336
    cmd.undo_disable()
    cmd.delete("all")

    if use_og_df: df = plugin.og_df
    else: df = plugin.df

    if df is None:
        status_msg("No data loaded - please load csv file first", color="yellow")
        return 

    if len(selected_indices) == 0:
        status_msg("No models selected for PyMOL sync.", color="yellow")
        return
    
    if exclude_classified:
        classified = np.hstack([plugin.good_models, plugin.bad_models])
        selected_indices = selected_indices[~np.isin(selected_indices, classified)]
        if len(selected_indices) == 0:
            status_msg("All selected models had alread been classified", color="yellow")
            return

    # Access max_models_spin from scatter_tab object
    max_models = plugin.scatter_tab_obj.max_models_spin.value()

    selected = df.loc[selected_indices]
    if len(selected) > max_models:
        selected = selected.sample(max_models)  # Random selection

    # managing grid modes
    columns = [plugin.setting_tab_obj.path_combo.currentText()]
    suffix = [""]

    if plugin.setting_tab_obj.load_model_2_chkbox.isChecked():
        columns.append(plugin.setting_tab_obj.path_2_combo.currentText())
        suffix.append(plugin.setting_tab_obj.model_2_suffix.text())

    if plugin.setting_tab_obj.load_model_3_chkbox.isChecked():
        columns.append(plugin.setting_tab_obj.path_3_combo.currentText())
        suffix.append(plugin.setting_tab_obj.model_3_suffix.text())

    # grid mode setup
    if plugin.setting_tab_obj.grid_mode_chkbox.isChecked():
        cmd.set("grid_mode", 1)
        cmd.set("grid_max", len(columns))
    else:
        cmd.set("grid_mode", 0)

    # Load reference structure
    ref_obj_name = None
    if plugin.reference_structure != None:
        cmd.load(plugin.reference_structure)
        ref_obj_name = os.path.basename(plugin.reference_structure).split(".")[0]
        cmd.color(plugin.setting_tab_obj.ref_color_combo.currentText(), ref_obj_name)

        # Display reference in first grid slot by default
        if plugin.setting_tab_obj.grid_mode_chkbox.isChecked():
            cmd.set("grid_slot", 1, ref_obj_name)
        if plugin.setting_tab_obj.grid_mode_chkbox.isChecked() and plugin.setting_tab_obj.ref_in_all_chckbox.isChecked():
            cmd.set("grid_slot", -2, ref_obj_name)
            print(f"display {ref_obj_name} in all slots")

    # loading selected models
    loaded = 0
    groups = {}
    for _, row in selected.iterrows():
        
        paths = row[columns].values
        
        if plugin.path_replace != None:
            paths = [p.replace(plugin.path_replace[0], plugin.path_replace[1]) for p in paths]
        
        # bug fix: will create too many grid slots
        for i, p in enumerate(paths):

            if os.path.exists(p):
                object_name = os.path.basename(p).split(".")[0]
                
                if suffix[i]:
                    object_name = object_name + "_" + suffix[i]

                cmd.load(p, object=object_name)
                loaded += 1

                # align model to reference
                if plugin.setting_tab_obj.align_ref.isChecked() and ref_obj_name != None:
                    try:
                        cmd.refresh()
                        status_msg(f"aligning {object_name} to {ref_obj_name}", color="yellow")
                        print(cmd.get_names("objects"))
                        cmd.align(object_name, ref_obj_name)
                    except pymol.CmdException as err:
                        status_msg(f"failed to align model {object_name} to {ref_obj_name}", color="red")
                
                # Set grid slots
                if plugin.setting_tab_obj.grid_mode_chkbox.isChecked():
                    cmd.set("grid_slot", i+1, object_name)

                # grouping
                if plugin.setting_tab_obj.group_models_chkbox.isChecked() and len(paths) > 1:
                    if i == 0:
                        # init group here
                        groupname = object_name + "_group"
                        groups[groupname] = [object_name]
                        # cmd.group(groupname, object_name)
                    else:
                        # add other models here
                        groups[groupname].append(object_name)
                        # cmd.group(groupname, object_name)

            else:
                status_msg(f"file not found: {p}", color="red")

    # Execute on-load command
    if plugin.setting_tab_obj.command_edit.text() != "":
        cmd.do(plugin.setting_tab_obj.command_edit.text())

    # color reference object
    if ref_obj_name != None:
        cmd.color(plugin.setting_tab_obj.ref_color_combo.currentText(), ref_obj_name)
    
    # create groups - seems more robust after alignment
    if plugin.setting_tab_obj.group_models_chkbox.isChecked() and len(paths) > 1:
        for group in groups:
            cmd.group(group, " ".join(groups[group]))
    
    cmd.center("all", animate=0)
    status_msg(f"Loaded {loaded} models into PyMOL")
