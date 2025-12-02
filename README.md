# Score Viewer Plugin
PyMOL plugin to load pdb/cif files directly from a csv file using a score-based selection of designs/models. 
Tested with PyMOL 3.1.6.1 and 2.5.5

## Installation

### Installation with PyMOL plugin manager
Open PyMOL and navigate to Plugin > Plugin Manager > Install New Plugin. You can choose to download the code and install from the local file or you can download the code directly from the Github repo. 

![PyMOL Plugin Manager: Install New Plugin](./media/plugin_manager.png)

#### Local file
Download the code as archive (.zip) from GitHub to your computer (Code > Download ZIP). In PyMOL's plugin manager click "Choose File..." and select the zip archive you just downloaded from Github. Follow the instructions. Usually it is best to install in the default directory suggested by the Plugin Manager. Restart PyMOL. 

#### Download Code through PyMOL's Plugin Manager
Alternatively, navigate to Plugin > Plugin Manager > Install New Plugin. Copy the url to the GitHub repo
```
https://github.com/ngoldb/score_viewer_plugin
```
into the URL field and click "Fetch". Select the default directory suggested by the Plugin Manager.

Check here for more information about plugins in PyMOL: https://pymolwiki.org/index.php/Plugins#Installing_Plugins

### Using git
Navigate to the PyMOL plugin directory and clone the GitHub repo.

For MacOS:
```
cd /Applications/PyMOL.app/Contents/lib/python3.10/site-packages/pmg_tk/startup
git clone https://github.com/ngoldb/score_viewer_plugin.git
```

See here for more information on how to find the correct directory: https://pymol.org/plugins.html

## Usage
To start Score Viewer open PyMOL and select Plugin > Score Viewer. A new window should open. Score Viewer has multiple tabs to organise the different options and functions. A usual workflow would start on the left and proceed to the right (Settings, Filter, Scatter Plot, Classification). Most options should be intuitive. Many buttons and checkboxes have Tip Tools, which show a more detailed message when hovering the mouse over the widget.

### Settings
This tab allows users to define general settings in Score Viewer. First, select a csv file to load. This csv file should contain the scores (e.g. from AlphaFold predictions, rmsd calculations, etc.) and the paths to the models. The text box below the browse button is just displaying the file path of the currently selected csv file. 

#### Models
The "Models" box allows the user to choose up to 3 models to be loaded per design simultaneously. This can be useful if you generated multiple models during the design (e.g. backbone from RFDiffusion and prediction from AlphaFold). Select the column names of the csv from the dropdown menus to specify which models to use. The checkbox next to the dropdown allows to enable or disable loading of the respective model. PyMOL does not allow objects to have the same name. If the different models have the same name, but are located in different directories, you can add a suffix to the object names of models 2 and 3. \
Beneath the model selection you find two text fields to dynamically replace substrings of the path stored in the csv file. For example, if you mounted a remote file system to your local computer, you can replace the paths accordingly to load the models from the mounted file system:\
For example you can replace ```/home/user/project/predictions``` with ```/mount/project/predictions```

#### Reference Structure
Here you can load a reference structure. If you check "Align models to reference" all models will automatically be aligned to the reference structure (or at least alignment will be attempted... PyMOL is not great at this). You can choose a color for the reference from the dropdown menu. If you are loading multiple models per design and enabled grid mode (see below), you can choose to display the reference structure in all grid slots by checking the respective option. By default the reference will only be shown in the first grid slot.

#### Appearance
Here you can modify the appearance of the loaded models. The "Load Command" needs to be in PyMOL syntax (e.g. ```color red; show sticks``` to color the models red and display side chains as sticks). If you are loading multiple models per design (see above), you can display the models in grid mode: models 1-3 will be arranged from left to right in individual slots. The last option "Group models" will group the models per design keeping the PyMOL gui tidy. 

Note: \
Score Viewer will set the maximal number of allowed grid slots to the number of models selected per design (1, 2, or 3). If you want to manually change the grid layout you may need to change this setting again using e.g.```set grid_max, 4``` to increase the maximum number of grid slots to 4.

### Filter
Here the input data can be filtered. One can select different scores and filter for designs where the respective score is between the user provided minium and maximum value. Data points not passing filters will not be plotted or loaded in the subsequent steps. Typically, one would remove e.g. low confidence designs here (e.g. by filtering plddt to be between 0.8 and 1.0). \
Start by selecting the score to be filtered from the dropdown menu. If there are no scores displayed, you need to load a csv file first. Once a score was selected, the minimum and maximum values of the respective metric will be displayed next to the spin box. Enter the minimum and maximum values for the filter and check "Apply filter". The number of designs passing the filter will be displayed.\
Proceed with the additional filters in the same way. Note that individual filters are independent from each other. Once you are done setting up all filters, click the button at the bottom to filter the input data. The number of designs passing all filters will be displayed and the scatter plot should be updated automatically.

### Scatter Plot
This is interactive scatter plot. You can choose the scores to be plotted on x and y axis. Use the sliders to adjust the axis range (very hacky zoom tool, but it works). You can adjust the styling of the plot (marker size and alpha). Click "Plot" to update the scatter plot.\
You can no use your mouse as a lasso selection to select the data points you are interested in. The selected data points will be highlighted and the number of selected designs will be displayed on top of the scatter plot. Click "Sync with PyMOL" to load the selected models into the 3D viewer of PyMOL (this will reset the 3D viewer and delete all currently loaded models). To prevent PyMOL from crashing when loading many models, there is a spin box allowing the user to specify the maximum number of models to be loaded (default: 10). If the number of selected models exceeds the maximum number specified, a random selection will be loaded. You can use PyMOL just as usual to explore the models.

Note: \
Score Viewer will disable PyMOL's undo function for nostalgic reasons (and stability: if undo is not disabled, ```align``` will fail after 4 executions)

### Calssification
You can classify designs into two categories: good or bad using the buttons in this menu. The first box contains buttons to load designs, which had already been classified as either good or bad and to restart the classification. Note that for loading good or bad models, the maximal number of models specified in the Scatter Plot Tab will apply. There is also the option to exclude already classified designs, which is enabled by default. It will prevent from loading alread classified designs into PyMOL when you click "Sync with PyMOL" (in the Scatter Plot Tab). \
The second box ("Classify") contains the buttons to classify the models. You can choose to either mark enabled models or all models (which are currently loaded in PyMOL) as good or bad. After starting the classification, the number of good and bad models will be displayed below the buttons. A design can never be in both good and bad models. If you re-classify a model, the most recent classification will be applied (e.g. if the model was already classified as good, but you reload it and classify it as good, the model will be removed from good and added to bad). In such cases Score Viewer will provide a status message. In general, this should not happen if you are using the option to exclude already classified models from being loaded again. Be careful with the classification: there is no undo! \
The last box ("Export") allows to export the classified models. You can export the csv with the good and bad models, copy the classified models, and export the sequences of selected models to a fasta file. Score Viewer will not overwrite the export. If a file already exists, it will append a timestamp to prevent overwriting files. Copy models will create two directories with good and bad models, respectively. \
For export to fasta format you can choose to export the names and sequences from the csv file (first option, default). If you check "Sequence from models" you can select the models to load from the dropdown menu and select the chains to export. Score Viewer will then load the models into PyMOL and derive the sequence of the selected chain using PyMOL's ```cmd.get_fastastr()``` function. This can be helpful if you forgot to save the sequence and design names in the csv file.
