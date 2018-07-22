# Using EZCalour
EZCalour is a point and click GUI for the [Calour](https://github.com/amnona/Calour) microbiome analysis package.

EZCalour can be used to read, process, and plot interactive heatmaps from microbiome experiments.

## General concepts
Each dataset is called an experiment. All experiments are displayed in the main list in the EZCalour window. Following each processing step, a new experiment is created. Right clicking on an experiment enables deleting from memory and saving of the experiments.

On the right hand side, There are three tabs - for processing samples, features and analysis. Commands from a given tab relate to the appropriate axis (i.e. Filter from the sample tab filters samples, whereas Filter from the features tab filters features). Commands work on the selected experiment from the main list.

In order the plot the interactive heatmap of an experiment, it needs to be selected from the main list, and then press the "Plot" button (located at the lower left side)

## Loading data
EZCalour works with microbiome BIOM tables, metabolomics MZMine2 tables, or any CSV text file.
Besides the main table, ezcalour can also load a tab-separated mapping file, containing information about each sample.

In order to load an experiment, click on the "Load" button (located at the top left side).

Mandatory fields:
=================
"Table file" : name of the biom or mzmine2 table (can click the "D" button for GUI file selection)
"Type": the type of the table file:
- "Amplicon" for a microbiome biom table. When loading, the table is normalized by TSS to 10000 reads/sample. Samples with <1000 reads are dropped.
- "MZMine2" for an MZMine2 metabolomics table
- "TSV" for a general tab separated table (Each sample is a column, each feature is a row)

Optional fields:
================
"Map file" : name of the sample TSV mapping file

"GNPS file" : For mass-spec, the per-metabolite info file (see [here](http://biocore.github.io/calour/generated/calour.io.read_ms.html#calour.io.read_ms))

"New name" : the name for the experiment in the main list (defaults to the table file name)

## Processing data

### Sample

#### Sort
Sort the samples according to the selected field.

Sorting is conservative, meaning samples with same value in the field retain the previous order. So in order to sort by two fields (i.e. "Disease" and "Day" within each disease), sort first by the second field (i.e. "Day") and then by the first (i.e. "Disease").

Mandatory fields:
=================
"Field": select the sample metadata field to sort by

Optional fields:
================
"New name" : the name for the experiment in the main list (defaults to the table file name)

#### Filter
Keep or remove samples with specified mapping file field values

Mandatory fields:
=================
"Field": select the sample metadata field to sort by

"value": the values to filter for the field.

Optional fields:
================
"neagte": if checked, remove samples with the selected values, otherwise keep samples with selected values

"New name" : the name for the experiment in the main list (defaults to the table file name)

