# Score Viewer Plugin
PyMOL plugin to load pdb/cif files directly from a csv file using a score-based selection of designs/models. 

## Installation
Download code, compress (.zip) and install using PyMOL's plugin manager. Restart PyMOL.

See also: https://pymolwiki.org/index.php/Plugins#Installing_Plugins

Tested with PyMOL 3.1.6.1

## Usage
- Open PyMOL
- Plugin -> Score Viewer, a window should appear
- Load csv file containing score values and paths to the pdb/cif files
- Switch to Scatter tab and plot scores
- Use mouse to select data points
- Click Sync with PyMOL to display the selected designs