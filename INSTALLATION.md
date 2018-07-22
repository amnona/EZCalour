# Installing and running EZCalour

Calour is a point and click GUI for the [Calour](https://github.com/amnona/Calour) microbiome analysis package

## Installation instructions:

### 1. Install Calour:

Follow instructions [Here](https://github.com/biocore/calour/blob/master/INSTALL.md)

### 2. Install EZCalour:
2a. Activate the calour conda environment:

```
source activate calour
```

2b. Install EZCalour from the github repo:

```
pip install git+git://github.com/amnona/EZCalour.git
```

## Running EZCalour:
1. Activate the calour conda environment:

```
source activate calour
```

2. Run EZCalour:

```
ezcalour.py
```

### 3. Additional command line options for ezcalour:
- To view the ezcalour and calour version info:

```
ezcalour.py --version
```

- To enable verbose debug messages:

```
ezcalour.py --log-level 10
```

- To view additional command line options for ezcalour, type:

```
ezcalour.py --help
```

EZCalour usage instructions can be found [Here](http://https://github.com/amnona/EZCalour/USAGE.md)
