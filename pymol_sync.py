from pymol import cmd
from .utils import status_msg
import os

def sync_with_pymol(plugin):
    if plugin.df is None or len(plugin.selected_indices) == 0:
        status_msg("No models selected for PyMOL sync.")
        return

    # Access max_models_spin from scatter_tab object
    max_models = plugin.scatter_tab_obj.max_models_spin.value()

    selected = plugin.df.iloc[plugin.selected_indices]
    if len(selected) > max_models:
        selected = selected.sample(max_models)  # Random selection

    # loading selected models
    cmd.delete("all")
    loaded = 0
    for _, row in selected.iterrows():
        p = row[plugin.setting_tab_obj.path_combo.currentText()]
        if plugin.path_replace != None:
            p = p.replace(plugin.path_replace[0], plugin.path_replace[1])
        if os.path.exists(p):
            cmd.load(p)
            loaded += 1
        else:
            status_msg(f"file not found: {p}")

    # Execute on-load command
    if plugin.onloadCommand != None:
        cmd.do(plugin.setting_tab_obj.command_edit.text())

    # Load reference structure
    if plugin.reference_structure != None:
        cmd.load(plugin.reference_structure)
        ref_obj_name = os.path.basename(plugin.reference_structure).split(".")[0]
        cmd.color(plugin.setting_tab_obj.ref_color_combo.currentText(), ref_obj_name)

        # Align ref structure
        if plugin.setting_tab_obj.align_ref.isChecked():
            active_objects = cmd.get_object_list("enabled")
            for obj in active_objects:
                if obj != ref_obj_name:
                    cmd.align(obj, ref_obj_name)
    
    status_msg(f"Loaded {loaded} models into PyMOL")
