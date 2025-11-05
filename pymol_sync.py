from pymol import cmd
from .utils import status_msg
import os

def sync_with_pymol(plugin):
    #TODO: on load command
    if plugin.df is None or len(plugin.selected_indices) == 0:
        status_msg("No models selected for PyMOL sync.")
        return

    # Access max_models_spin from scatter_tab object
    max_models = plugin.scatter_tab_obj.max_models_spin.value()

    selected = plugin.df.iloc[plugin.selected_indices]
    if len(selected) > max_models:
        selected = selected.sample(max_models)  # Random selection

    cmd.delete("all")
    for _, row in selected.iterrows():
        p = row["path"]
        if os.path.exists(p):
            cmd.load(p)
    
    if plugin.onloadCommand != None:
        cmd.do(plugin.onloadCommand)
        status_msg('on Load Command')

    status_msg(f"Loaded {len(selected)} models into PyMOL")
