# EZCalour
Welcome to EZCalour, the point and click GUI for the [Calour](https://github.com/amnona/Calour) microbiome analysis software.

<div align="center">
        <img width="23%" src="https://github.com/amnona/EZCalour/blob/master/images/main_gui.png" alt="Main GUI" title="Main GUI"</img>
        <img width="39%" src="https://github.com/amnona/EZCalour/blob/master/images/heatmap.png" alt="Interactive heatmap" title="Interactive heatmap"</img>
        <img width="30%" src="https://github.com/amnona/EZCalour/blob/master/images/enriched.png" alt="DBBact enrichment" title="DBBact enrichment"</img>
</div>

## EZCalour installation
Simple installers (just download and run):

* [Windows](https://sourceforge.net/projects/ezcalour/files/ezcalour_installer.exe/download)

* [Mac OSX](https://sourceforge.net/projects/ezcalour/files/EZCalour.dmg/download) (open the .dmg file and drag the EZCalour icon to the applications folder icon)

Alternatively, you can install via console as part of the calour installation using [these instructions](https://github.com/amnona/EZCalour/blob/master/INSTALLATION.md)

## Documentation
Detailed documentation for using EZCalour can be found [here](https://github.com/amnona/EZCalour/blob/master/using-ezcalour.pdf)

## Simple analysis workflow:
### 1. Load the experiment:

**Amplicon experiment**

1a. Load the data using the "Load" button on the top-left corner

1b. Select the biom table file (mandatory), and the mapping file (optional)

1c. Select "amplicon experiment" from the Type combo box

**Metabolomics experiment**

1a. Load the data using the "Load" button on the top-left corner

1b. Select the csv bucket table file (mandatory), and the mapping file (optional)

1c. If each row in the csv bucket table corresponds to a sample, select "Metabolomics - samples are rows" from the Type combo box. Otherwise, select "Metabolomics - samples are columns"

1d. If you have a GNPS data file (see [here](https://github.com/amnona/gnps-calour) for instructions), you can supply this file in the GNPS file field, in order to get GNPS annotations for each metabolite

### 2. Filter the samples of interest
Select "Filter" in the "Samples" tab, select the values you want to keep (or throw away using the "negate" checkbox)

### 3. Cluster features (so similar behaving features will be close to each other)
Select "Cluster" in the "Features" tab. You can also enter a minimal threshold for keeping features (i.e. throw away features with reads sum over all samples < threshold).

### 4. Plot an interactive heatmap
Select the plot button at the bottom.

You can choose a sample field to sort by, as well as bars for the x and y axis

Keyboard shortcuts for the heatmap are described [here](http://biocore.github.io/calour/generated/calour.heatmap.plot.html#calour.heatmap.plot)

