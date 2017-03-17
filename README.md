# EZCalour
Full GUI for [Calour](https://github.com/amnona/Calour) functions

## Installation:
1. Install Calour:

Follow instructions [Here](https://github.com/amnona/Calour)

2. Install EZCalour:

```
pip install git+git://github.com/amnona/EZCalour.git
```
## Usage:
To run EZCalour, just type from a command prompt:
```
source activate calour
```

```
ezcalour.py
```

Keyboard shortcuts for the heatmap are described [here](http://biocore.github.io/calour/generated/calour.heatmap.plot.html#calour.heatmap.plot)

## Simple analysis workflow:
1. Load the experiment:

**Amplicon experiment**

1a. Load the data using the "Load" button on the top-left corner

1b. Select the biom table file (mandatory), and the mapping file (optional)

1c. Select "amplicon experiment" from the Type combo box

**Metabolomics experiment**

1a. Load the data using the "Load" button on the top-left corner

1b. Select the csv bucket table file (mandatory), and the mapping file (optional)

1c. If each row in the csv bucket table corresponds to a sample, select "Metabolomics - samples are rows" from the Type combo box. Otherwise, select "Metabolomics - samples are columns"

1d. If you have a GNPS data file (see [here](https://github.com/amnona/gnps-calour) for instructions), you can supply this file in the GNPS file field, in order to get GNPS annotations for each metabolite

2. Filter the samples of interest using "Filter" in the "Samples" tab

3. Cluster features (so similar behaving features will be close to each other) using "Cluster" in the "Features" tab

4. Plot
