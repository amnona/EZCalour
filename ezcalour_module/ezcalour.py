#!/usr/bin/env python

# Calour GUI - a full GUI wrapping for calour functions

# ----------------------------------------------------------------------------
# Copyright (c) 2016--,  Calour development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

# for pyinstaller multiprocessing bug (see https://stackoverflow.com/questions/32672596/pyinstaller-loads-script-multiple-times, https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support)
import multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()

import inspect
import os
import sys


# change the app directory so will work in macOS X application
def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

os.chdir(get_script_dir())


import sys
from logging import getLogger, basicConfig
from logging.config import fileConfig
import argparse
import traceback
import json

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout,
                             QWidget, QPushButton, QLabel,
                             QComboBox, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QDialog, QDialogButtonBox, QApplication, QListWidget)
import matplotlib
import numpy as np
# we need this because of the skbio import that probably imports pyplot?
# must have it before importing calour (Since it imports skbio)
matplotlib.use("Qt5Agg")

import calour as ca
from ezcalour_module.util import get_ui_file_name, get_res_file_name
from ezcalour_module import __version__

logger = getLogger(__name__)
# set the logger output according to log.cfg
try:
    # setting False allows other logger to print log.
    log = get_res_file_name('log.cfg')
    print('loading log config file %s' % log)
    fileConfig(log, disable_existing_loggers=False)
    # fileConfig(log, disable_existing_loggers=False)
except:
    print('FAILED log config file load for %s' % log)
    basicConfig(format='%(levelname)s:%(message)s')


class AppWindow(QtWidgets.QMainWindow):
    # the experiments loaded for analysis
    _explist = {}

    def __init__(self, load_exp=None):
        '''Start the gui and load data if supplied

        Parameters
        ----------
        load_exp : list of (table_file_name, map_file_name, study_name) or None (optional)
            load the experiments in the list upon startup
        '''
        super().__init__()
        # load the gui
        uic.loadUi(get_ui_file_name('CalourGUI.ui'), self)

        # handle button clicks
        self.wLoad.clicked.connect(self.load)
        self.wPlot.clicked.connect(self.plot)

        # the experiment list right mouse menu
        self.wExperiments.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.wExperiments.customContextMenuRequested.connect(self.listItemRightClicked)

        # add functions
        # init the action group list
        action_groups = ['sample', 'feature', 'analysis']
        self.actions = {}
        for caction in action_groups:
            self.actions[caction] = {}

        # Add 'sample' buttons
        sample_buttons = ['Sort', 'Filter', 'Cluster', 'Join fields', 'Filter by original reads', 'Normalize', 'Merge']
        self.add_buttons('sample', sample_buttons)

        feature_buttons = ['Cluster', 'Filter min reads', 'Filter taxonomy', 'Filter fasta', 'Filter prevalence', 'Filter mean', 'Sort abundance', 'Collapse taxonomy']
        self.add_buttons('feature', feature_buttons)

        analysis_buttons = ['Diff. abundance', 'Correlation', 'Enrichment']
        self.add_buttons('analysis', analysis_buttons)

        # load experiments supplied
        if load_exp is not None:
            for cdata in load_exp:
                study_name = cdata[2]
                if study_name is None:
                    study_name = cdata[0]
                exp = ca.read_amplicon(cdata[0], cdata[1], normalize=10000, min_reads=None)
                exp._studyname = study_name
                self.addexp(exp)
        self.setWindowTitle('EZCalour version %s' % __version__)
        self.show()

    def add_buttons(self, group, button_list):
        '''Add buttons to the specified divider list and link to functions

        Function names should be similar to button name, only lowercase and space replace by '_' and '.' removed,
        with 'group'_ before

        Parameters
        ----------
        group : str
            tab to add the buttons to ('sample', 'feature', 'analysis')
        button_list : list of str
            list of button names. should have a corresponding function with same name
        '''
        for cbutton in button_list:
            cfunc_name = '%s_%s' % (group.lower(), cbutton.lower().replace(' ', '_').replace('.', ''))
            try:
                self.add_action_button(group, cbutton, getattr(self, cfunc_name))
            except:
                logger.warn('function %s not found - cannot add button' % cfunc_name)

    def get_exp_from_selection(self):
        '''Get the experiment from the selection in wExperiments

        Returns
        -------
        expdat : Experiment
            the first selected experiment in the wExperiments list
        '''
        item = self.wExperiments.selectedItems()[0]
        cname = str(item.text())
        if cname not in self._explist:
            logger.warn('experiment not found. name=%s' % cname)
            return None
        expdat = self._explist[cname]
        return expdat

    def plot(self):
        # global x
        '''
        Plot the experiment
        '''
        expdat = self.get_exp_from_selection()
        sort_field_vals = ['<none>'] + list(expdat.sample_metadata.columns)
        res = dialog([{'type': 'label', 'label': 'Plot experiment %s' % expdat._studyname},
                      {'type': 'combo', 'label': 'Field', 'items': sort_field_vals},
                      {'type': 'bool', 'label': 'sort', 'default': True},
                      {'type': 'bool', 'label': 'show taxonomy', 'default': False},
                      {'type': 'select', 'label': 'sample bars', 'items': expdat.sample_metadata.columns},
                      {'type': 'select', 'label': 'feature bars', 'items': expdat.feature_metadata.columns},
                      {'type': 'bool', 'label': 'show colorbar labels'},
                      {'type': 'bool', 'label': 'use dbBact', 'default': True}], expdat=expdat)
        if res is None:
            return
        if res['Field'] == '<none>':
            field = None
        else:
            field = res['Field']
        if res['sort'] and field is not None:
            logger.debug('sort')
            newexp = expdat.sort_samples(field)
        else:
            newexp = expdat
        xargs = get_config_values('plot')
        if res['show taxonomy']:
            feature_field = 'taxonomy'
        else:
            feature_field = None
        if res['use dbBact']:
            databases = ['dbbact']
        else:
            databases = []
        newexp.plot(gui='qt5', sample_field=field, feature_field=feature_field, databases=databases, barx_fields=res['sample bars'], bary_fields=res['feature bars'], barx_label=res['show colorbar labels'], bary_label=res['show colorbar labels'], **xargs)
        # app = QtCore.QCoreApplication.instance()
        # app.references.add(x)

    def sample_sort(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Sort Samples'},
                      {'type': 'field', 'label': 'Field'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-sort-%s' % (expdat._studyname, res['field'])
        newexp = expdat.sort_by_metadata(res['field'], axis=0)
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def sample_merge(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Merge samples based on similar field values'},
                      {'type': 'field', 'label': 'Field'},
                      {'type': 'combo', 'label': 'Method', 'items': ['mean', 'random', 'sum']},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-merge-%s' % (expdat._studyname, res['field'])
        newexp = expdat.merge_identical(res['field'], method=res['Method'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def sample_cluster(self):
        expdat = self.get_exp_from_selection()
        newexp = expdat.cluster_data(axis=1)
        newexp._studyname = newexp._studyname + '-cluster-samples'
        self.addexp(newexp)

    def sample_filter(self):
        expdat = self.get_exp_from_selection()
        logger.debug('filter samples for study: %s' % expdat._studyname)
        res = dialog([{'type': 'label', 'label': 'Filter Samples'},
                      {'type': 'field', 'label': 'Field'},
                      {'type': 'value_multi_select', 'label': 'value'},
                      {'type': 'bool', 'label': 'negate'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            if res['negate']:
                res['new name'] = '%s-%s-not-%s' % (expdat._studyname, res['field'], res['value'])
            else:
                res['new name'] = '%s-%s-%s' % (expdat._studyname, res['field'], res['value'])

        newexp = expdat.filter_samples(res['field'], res['value'], negate=res['negate'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def sample_normalize(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Normalize reads per sample'},
                      {'type': 'int', 'label': 'Reads per sample', 'default': 10000, 'max': 100000},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-normalize' % (expdat._studyname)
        newexp = expdat.normalize(res['Reads per sample'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def sample_join_fields(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Join Fields'},
                      {'type': 'combo', 'label': 'Field1', 'items': expdat.sample_metadata.columns},
                      {'type': 'combo', 'label': 'Field2', 'items': expdat.sample_metadata.columns},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-join-%s-%s' % (expdat._studyname, res['Field1'], res['Field2'])
        newexp = expdat.join_metadata_fields(field1=res['Field1'], field2=res['Field2'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def sample_filter_by_original_reads(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Filter Original Reads'},
                      {'type': 'int', 'label': 'Orig Reads', 'max': 100000, 'default': 10000},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-min-%d' % (expdat._studyname, res['Orig Reads'])
        newexp = expdat.filter_orig_reads(minreads=res['Orig Reads'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_filter_min_reads(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Filter minimal reads per feature'},
                      {'type': 'int', 'label': 'min reads', 'max': 50000, 'default': 10},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-minreads-%d' % (expdat._studyname, res['min reads'])
        newexp = expdat.filter_abundance(cutoff=res['min reads'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_filter_taxonomy(self):
        expdat = self.get_exp_from_selection()
        if not isinstance(expdat, ca.AmpliconExperiment):
            logger.warn('Experiment in not an amplicon experiment (it is %s) - cannot filter' % type(expdat))
        res = dialog([{'type': 'label', 'label': 'Filter Taxonomy'},
                      {'type': 'string', 'label': 'Taxonomy'},
                      {'type': 'bool', 'label': 'Exact'},
                      {'type': 'bool', 'label': 'Negate'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-tax-%s' % (expdat._studyname, res['Taxonomy'])
        newexp = expdat.filter_taxonomy(res['Taxonomy'], negate=res['Negate'], substring=not(res['Exact']))
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_cluster(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Cluster Features'},
                      {'type': 'int', 'label': 'min reads', 'max': 50000, 'default': 10},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-cluster-features-min-%d' % (expdat._studyname, res['min reads'])
        newexp = expdat.cluster_features(min_abundance=res['min reads'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_filter_fasta(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Filter Fasta'},
                      {'type': 'filename', 'label': 'Fasta File'},
                      {'type': 'bool', 'label': 'Negate'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-cluster-fasta-%s' % (expdat._studyname, res['Fasta File'])
        newexp = expdat.filter_fasta(filename=res['Fasta File'], negate=res['Negate'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_filter_prevalence(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Filter minimal prevalence per feature'},
                      {'type': 'label', 'label': '(fraction of samples where feature is present)'},
                      {'type': 'float', 'label': 'min fraction', 'max': 1, 'default': 0.5},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-minreads-%f' % (expdat._studyname, res['min fraction'])
        newexp = expdat.filter_prevalence(fraction=res['min fraction'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_filter_mean(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Filter by minimal mean per feature'},
                      {'type': 'label', 'label': '(mean frequency in all samples)'},
                      {'type': 'float', 'label': 'mean', 'max': 1, 'default': 0.01},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-minreads-%f' % (expdat._studyname, res['mean'])
        newexp = expdat.filter_mean_abundance(cutoff=res['mean'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_sort_abundance(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Sort features by abundance'},
                      {'type': 'field', 'label': 'Field', 'withnone': True},
                      {'type': 'value', 'label': 'value'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-sort-abundance' % expdat._studyname
        # newexp = expdat.sort_abundance(field=res['field'], value=res['value'])
        if res['field'] is None:
            subset = None
        else:
            subset = {res['field']: [res['value']]}
        newexp = expdat.sort_abundance(subgroup=subset)
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def feature_collapse_taxonomy(self):
        expdat = self.get_exp_from_selection()
        if not isinstance(expdat, ca.AmpliconExperiment):
            raise ValueError("Can only collapse taxonomy for AmpliconExperiment (select in load)\nCurrent exp type is %s" % type(expdat))
        res = dialog([{'type': 'label', 'label': 'Collapse features by taxonomy'},
                      {'type': 'combo', 'label': 'level', 'items': ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-collapse-taxonomy-%s' % (expdat._studyname, res['level'])
        newexp = expdat.collapse_taxonomy(level=res['level'])
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def analysis_diff_abundance(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Differential abundance'},
                      {'type': 'field', 'label': 'Field', 'withnone': True},
                      # {'type': 'value', 'label': 'Value group 1'},
                      {'type': 'value_multi_select', 'label': 'Value group 1'},
                      # {'type': 'value', 'label': 'Value group 2'},
                      {'type': 'value_multi_select', 'label': 'Value group 2'},
                      {'type': 'float', 'label': 'FDR level', 'default': 0.1, 'max': 1},
                      {'type': 'combo', 'label': 'Method', 'items': ['rankmean', 'mean', 'binary']},
                      {'type': 'bool', 'label': 'Use random seed', 'default': False},
                      {'type': 'int', 'label': 'random seed', 'default': 2018, 'max': 9999999},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-diff-%s' % (expdat._studyname, res['field'])
        if res['Method'] == 'rankmean':
            method = 'meandiff'
            transform = 'rankdata'
        elif res['Method'] == 'mean':
            method = 'meandiff'
            transform = None
        elif res['Method'] == 'binary':
            method = 'meandiff'
            transform = 'binarydata'
        # if no value supplied for group2, make it None instead of '' so will use all other samples...
        if res['Value group 2'] == '' or res['Value group 2'] == ['']:
            print('pita')
            res['Value group 2'] = None
        kwa = {}
        if res['Use random seed']:
            kwa['random_seed'] = res['random seed']
        newexp = expdat.diff_abundance(field=res['field'], val1=res['Value group 1'], val2=res['Value group 2'], alpha=res['FDR level'], method=method, transform=transform, **kwa)
        if newexp is None:
                QtWidgets.QMessageBox.information(self, "No enriched terms found", "No enriched annotations found")
                return
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def analysis_correlation(self):
        expdat = self.get_exp_from_selection()
        res = dialog([{'type': 'label', 'label': 'Correlation'},
                      {'type': 'field', 'label': 'Field', 'withnone': True},
                      {'type': 'combo', 'label': 'Method', 'items': ['spearman', 'pearson']},
                      {'type': 'bool', 'label': 'ignore zeros'},
                      {'type': 'string', 'label': 'new name'}], expdat=expdat)
        if res is None:
            return
        if res['new name'] == '':
            res['new name'] = '%s-correlation-%s' % (expdat._studyname, res['field'])
        newexp = expdat.correlation(field=res['field'], method=res['Method'], nonzero=res['ignore zeros'])
        if newexp is None:
                QtWidgets.QMessageBox.information(self, "No enriched terms found", "No enriched annotations found")
                return
        newexp._studyname = res['new name']
        self.addexp(newexp)

    def analysis_enrichment(self):
        expdat = self.get_exp_from_selection()
        if '_calour_stat' not in expdat.feature_metadata.columns:
            QtWidgets.QMessageBox.warning(self, "Problem", "Enrichment plot only works on\ndiff. abundance/correlation\nresult experiments")
            return
        names1 = expdat.feature_metadata['_calour_direction'][expdat.feature_metadata['_calour_stat'] > 0]
        names2 = expdat.feature_metadata['_calour_direction'][expdat.feature_metadata['_calour_stat'] < 0]
        if len(names1) > 0:
            names1 = names1.values[0]
        else:
            names1 = 'Group1'
        if len(names2) > 0:
            names2 = names2.values[0]
        else:
            names2 = 'Group2'

        res = dialog([{'type': 'label', 'label': 'Differential abundance enrichment'},
                      {'type': 'label', 'label': 'Group1: %s' % names1},
                      {'type': 'label', 'label': 'Group2: %s' % names2},
                      {'type': 'bool', 'label': 'show legend'},
                      {'type': 'int', 'label': 'min. experiments'},
                      ], expdat=expdat)
        if res is None:
            return

        ax, newexp = expdat.plot_diff_abundance_enrichment(ignore_exp=True, min_exps=res['min. experiments'], show_legend=res['show legend'])
        ax.get_figure().show()

    def add_action_button(self, group, name, function):
        self.actions[group][name] = QPushButton(text=name)
        if group == 'sample':
            self.wSample.addWidget(self.actions[group][name])
        elif group == 'feature':
            self.wFeature.addWidget(self.actions[group][name])
        elif group == 'analysis':
            self.wAnalysis.addWidget(self.actions[group][name])

        self.actions[group][name].clicked.connect(function)

    def listItemRightClicked(self, QPos):
        self.listMenu = QtWidgets.QMenu()
        menurename = self.listMenu.addAction("Rename")
        menurename.triggered.connect(self.menuRename)
        menuremove = self.listMenu.addAction("Delete")
        menuremove.triggered.connect(self.menuRemove)
        menusave = self.listMenu.addAction("Save biom")
        menusave.triggered.connect(self.menuSave)
        menuinfo = self.listMenu.addAction("Info")
        menuinfo.triggered.connect(self.expinfo)
        menusavecommands = self.listMenu.addAction("Save commands")
        menusavecommands.triggered.connect(self.menuSaveCommands)
        parentPosition = self.wExperiments.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def expinfo(self):
        expdat = self.get_exp_from_selection()
        logger.debug('getting experiment info')
        data_file = expdat.exp_metadata.get('data_file', 'NA')
        map_file = expdat.exp_metadata.get('sample_metadata_file', 'NA')
        title = 'experiment info for %s' % expdat._studyname
        commands = []
        commands.append('data file: %s' % data_file)
        commands.append('map file: %s' % map_file)
        commands.append('%r' % expdat)
        commands.append('------------')
        for x in expdat._call_history:
            commands.append(str(x))
        listwin = SListWindow(listdata=commands, listname=title)
        listwin.exec_()

    def menuRename(self):
        expdat = self.get_exp_from_selection()
        val, ok = QtWidgets.QInputDialog.getText(self, 'Rename experiment', 'old name=%s' % expdat._studyname)
        if ok:
            self.removeexp(expdat)
            expdat._studyname = val
            self.addexp(expdat)

    def menuRemove(self):
        if len(self.wExperiments.selectedItems()) > 1:
            if QtWidgets.QMessageBox.warning(self, "Remove experiments?", "Remove %d experiments?" % len(self.wExperiments.selectedItems()),
                                             QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        for currentItemName in self.wExperiments.selectedItems():
            currentItemName = str(currentItemName.text())
            cexp = self._explist[currentItemName]
            self.removeexp(cexp)

    def menuSave(self):
        expdat = self.get_exp_from_selection()
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save experiment')
        fname = str(fname)
        if fname == '':
            return
        logger.debut('saving')
        # TODO: change to hdf5 once biom bug is solved
        expdat.save_biom(fname, fmt='json')
        logger.info('saved biom table to file %s' % fname)

    def menuSaveCommands(self):
        expdat = self.get_exp_from_selection()
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save commands')
        fname = str(fname)
        if fname == '':
            return
        logger.debug('saving commands')
        data_file = expdat.exp_metadata.get('data_file', 'NA')
        map_file = expdat.exp_metadata.get('sample_metadata_file', 'NA')
        with open(fname, 'w') as fl:
            fl.write('Command history for biom table %s, sample metadata file %s\n' % (data_file, map_file))
            for ccommand in expdat._call_history:
                fl.write('%s\n' % ccommand)
        logger.info('saved commands to file %s' % fname)

    def addexp(self, expdat):
        '''Add a new experiment to the list of experiments

        Parameters
        ----------
        expdat : Experiment
            the experiment to add (note it needs also the _studyname field)
        '''

        # make sure the experiment is not already in the list
        # if so, give a new unique name
        expname = expdat._studyname
        cnum = 2
        expnames = [cexp._studyname for cexp in self._explist.values()]
        while expname in expnames:
            expname = expdat._studyname + '(' + str(cnum) + ')'
            cnum += 1
        expdat._studyname = expname
        expdname = '%s (%s-S, %s-F)' % (expname, expdat.shape[0], expdat.shape[1])
        expdat._displayname = expdname
        self._explist[expdname] = expdat
        self.wExperiments.addItem(expdname)
        self.wExperiments.clearSelection()
        self.wExperiments.setCurrentRow(self.wExperiments.count() - 1)
        logger.debug('experiment %s added' % expname)

    def removeexp(self, exp):
        """
        remove an experiment from the list (and clear)
        """
        expdname = exp._displayname
        del self._explist[expdname]
        items = self.wExperiments.findItems(expdname, QtCore.Qt.MatchExactly)
        for item in items:
            self.wExperiments.takeItem(self.wExperiments.row(item))

    def load(self):
        win = LoadWindow()
        res = win.exec_()
        if res == QtWidgets.QDialog.Accepted:
            tablefname = str(win.wTableFile.text())
            mapfname = str(win.wMapFile.text())
            if mapfname == '':
                mapfname = None
            gnpsfname = str(win.wGNPSFile.text())
            if gnpsfname == '':
                gnpsfname = None
            expname = str(win.wNewName.text())
            exptype = str(win.wType.currentText())
            if exptype == 'Amplicon':
                try:
                    expdat = ca.read_amplicon(tablefname, mapfname, normalize=10000, min_reads=None)
                except Exception as e:
                    logger.warn('Load for amplicon biom table %s map %s failed:\n%s' % (tablefname, mapfname, e))
                    return
            elif exptype == 'Metabolomics (MZMine2)':
                try:
                    expdat = ca.read_ms(tablefname, mapfname, gnps_file=gnpsfname, normalize=None)
                except Exception as e:
                    logger.warn('Load for mzmine2 table %s map %s failed:\n%s' % (tablefname, mapfname, e))
                    return
            elif exptype == 'Tab separated text (TSV)':
                try:
                    expdat = ca.read(tablefname, mapfname, normalize=None, data_file_type='tsv')
                except Exception as e:
                    logger.warn('Load for tsv file table %s map %s failed\n%s' % (tablefname, mapfname, e))
                    return
            expdat._studyname = expname
            self.addexp(expdat)
            # for biom table show the number of reads`


class LoadWindow(QtWidgets.QDialog):
    def __init__(self):
        super(LoadWindow, self).__init__()
        uic.loadUi(get_ui_file_name('CalourGUILoad.ui'), self)
        self.wTableFileList.clicked.connect(self.browsetable)
        self.wMapFileList.clicked.connect(self.browsemap)
        self.wGNPSFileList.clicked.connect(self.browsegnps)
        self.wType.currentIndexChanged.connect(self.typechange)

    def typechange(self):
        # enable the gnps file widget only if metabolomics experiment
        exptype = str(self.wType.currentText())
        if exptype in ['Metabolomics (MZMine2)']:
            self.wGNPSFile.setEnabled(True)
            self.wGNPSFileList.setEnabled(True)
            self.wGNPSLabel.setEnabled(True)
        else:
            self.wGNPSFile.setEnabled(False)
            self.wGNPSFileList.setEnabled(False)
            self.wGNPSLabel.setEnabled(False)

    def browsegnps(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open map file')
        fname = str(fname)
        self.wGNPSFile.setText(fname)

    def browsemap(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open map file')
        fname = str(fname)
        self.wMapFile.setText(fname)

    def browsetable(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open table file')
        fname = str(fname)
        self.wTableFile.setText(fname)
        mname = os.path.dirname(fname) + '/map.txt'
        self.wMapFile.setText(mname)
        pname = os.path.basename(fname)
        self.wNewName.setText(pname)


def dialog(items, expdat=None, title=None):
    '''Create a dialog with the given items for then experiment

    Parameters
    ----------
    items : list of dict
        Entry for each item to display. fields in the dict are:
            'type' :
                'string' : a string (single line)
                'field' : a field from the sample_metadata
                'value' : a value input for the field in the field item
                'bool' : a boolean
                'label' : a label to display (text in 'label' field)
            'default' : the value to initialize the item to
            'label' : str
                label of the item (also the name in the output dict)
    expdat : Experiment (optional)
        the experiment to use to get the field/values items (needed if item is 'field'/'value')
    title : str (optional)
        title of the dialog

    Returns
    -------
    output : dict or None
        if cancel was selected, return None
        otherwise, a dict with label as key, value as val
    '''
    class DialogWindow(QDialog):
        def __init__(self, items, title=None, expdat=None):
            super().__init__()
            self.additional_info = {}
            self._expdat = expdat
            if title:
                self.setWindowTitle(title)

            self.main_widget = QWidget(self)
            self.layout = QVBoxLayout(self)

            self.widgets = {}
            for idx, citem in enumerate(items):
                if citem['type'] == 'label':
                    widget = QLabel(text=citem.get('label'))
                    self.add(widget)
                elif citem['type'] == 'string':
                    widget = QLineEdit(citem.get('default'))
                    self.add(widget, label=citem.get('label'), name=citem.get('label'))
                elif citem['type'] == 'int':
                    widget = QSpinBox()
                    if 'max' in citem:
                        widget.setMaximum(citem['max'])
                    if 'default' in citem:
                        widget.setValue(citem.get('default'))
                    self.add(widget, label=citem.get('label'), name=citem.get('label'))
                elif citem['type'] == 'float':
                    widget = QDoubleSpinBox()
                    if 'max' in citem:
                        widget.setMaximum(citem['max'])
                    if 'default' in citem:
                        widget.setValue(citem.get('default'))
                    self.add(widget, label=citem.get('label'), name=citem.get('label'))
                elif citem['type'] == 'combo':
                    widget = QComboBox()
                    widget.addItems(citem.get('items'))
                    self.add(widget, label=citem.get('label'), name=citem.get('label'))
                elif citem['type'] == 'field':
                    if expdat is None:
                        logger.warn('Experiment is empty for dialog %s' % title)
                        return None
                    widget = QComboBox()
                    if citem.get('withnone', False):
                        items = ['<none>'] + list(expdat.sample_metadata.columns.values)
                    else:
                        items = expdat.sample_metadata.columns.values
                    widget.addItems(items)
                    self.add(widget, label=citem.get('label'), name='field')
                elif citem['type'] == 'value':
                    if expdat is None:
                        logger.warn('Experiment is empty for dialog %s' % title)
                        return None
                    widget = QLineEdit()
                    self.add(widget, label=citem.get('label'), name=citem.get('label'), addbutton=True)
                elif citem['type'] == 'value_multi_select':
                    if expdat is None:
                        logger.warn('Experiment is empty for dialog %s' % title)
                        return None
                    widget = QLineEdit()
                    self.add(widget, label=citem.get('label'), name=citem.get('label'), add_select_button=citem, idx=idx)
                elif citem['type'] == 'filename':
                    widget = QLineEdit()
                    self.add(widget, label=citem.get('label'), name=citem.get('label'), addfilebutton=True)
                elif citem['type'] == 'bool':
                    widget = QCheckBox()
                    if 'default' in citem:
                        widget.setChecked(citem.get('default'))
                    self.add(widget, label=citem.get('label'), name=citem.get('label'))
                elif citem['type'] == 'select':
                    widget = QLabel('<None>')
                    citem['selected'] = []
                    self.add(widget, label=citem.get('label'), name=citem.get('label'), add_select_button=citem, idx=idx)

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

            buttonBox.accepted.connect(self.accept)
            buttonBox.rejected.connect(self.reject)

            self.layout.addWidget(buttonBox)

        def add(self, widget, name=None, label=None, addbutton=False, addfilebutton=False, add_select_button=None, idx=None):
            '''Add the widget to the dialog

            Parameters
            ----------
            widget
            name: str or None, optional
                the name of the data field for obtaining the value when ok clicked
            label: str or None, optional
                The label to add to the widget (to display in the dialog)
            addbutton: bool, optional
                True to add a button which opens the selection from field dialog
            addfilebutton: bool, optional
                True to add a file select dialog button
            add_select_button: item or None, optional
                not None to add a button opening a multi select dialog for values from the 'items' field. If 'items' field is None, select from current 'field' values
            '''
            hlayout = QHBoxLayout()
            if label is not None:
                label_widget = QLabel(label)
                hlayout.addWidget(label_widget)
            hlayout.addWidget(widget)
            if addbutton:
                bwidget = QPushButton(text='...')
                bwidget.clicked.connect(lambda: self.field_vals_click(widget))
                hlayout.addWidget(bwidget)
            if addfilebutton:
                bwidget = QPushButton(text='...')
                bwidget.clicked.connect(lambda: self.file_button_click(widget))
                hlayout.addWidget(bwidget)
            if add_select_button is not None:
                bwidget = QPushButton(text='...', parent=widget)
                bwidget.clicked.connect(lambda: self.select_items_click(widget, add_select_button))
                hlayout.addWidget(bwidget)
            self.layout.addLayout(hlayout)
            self.widgets[name] = widget

        def field_vals_click(self, widget):
            cfield = str(self.widgets['field'].currentText())
            if cfield not in self._expdat.sample_metadata.columns:
                return
            val, ok = QtWidgets.QInputDialog.getItem(self, 'Select value', 'Field=%s' % cfield, list(set(self._expdat.sample_metadata[cfield].astype(str))))
            if ok:
                widget.setText(val)

        def file_button_click(self, widget):
            fname, _x = QtWidgets.QFileDialog.getOpenFileName(self, 'Open fasta file')
            fname = str(fname)
            if fname != '':
                widget.setText(fname)

        def select_items_click(self, widget, item):
            select_items = item.get('items')

            # set the values according to the field if it is a field multi-select
            if select_items is None:
                cfield = str(self.widgets['field'].currentText())
                select_items = list(set(self._expdat.sample_metadata[cfield].astype(str)))

            selected = select_list_items(select_items)
            # set the selected list text in the text widget
            if len(selected) == 0:
                selected_str = '<None>'
            else:
                selected_str = ','.join(selected)
            widget.setText(selected_str)
            item['selected'] = selected

        def get_output(self, items):
            output = {}
            for citem in items:
                cname = citem.get('label')
                if citem['type'] == 'string':
                    output[cname] = str(self.widgets[cname].text())
                if citem['type'] == 'int':
                    output[cname] = self.widgets[cname].value()
                if citem['type'] == 'float':
                    output[cname] = self.widgets[cname].value()
                elif citem['type'] == 'combo':
                    output[cname] = str(self.widgets[cname].currentText())
                elif citem['type'] == 'field':
                    output['field'] = str(self.widgets['field'].currentText())
                    if output['field'] == '<none>':
                        output['field'] = None
                elif citem['type'] == 'value':
                    cval = str(self.widgets[cname].text())
                    if str(self.widgets['field'].currentText()) != '<none>':
                        # convert the value from str to the field dtype
                        cval = _value_to_dtype(cval, self._expdat, self.widgets['field'].currentText())
                    output[cname] = cval
                elif citem['type'] == 'filename':
                    output[cname] = str(self.widgets[cname].text())
                elif citem['type'] == 'bool':
                    output[cname] = self.widgets[cname].checkState() > 0
                elif citem['type'] == 'select':
                    output[cname] = citem['selected']
                elif citem['type'] == 'value_multi_select':
                    output[cname] = citem.get('selected', '')
            return output

    aw = DialogWindow(items, expdat=expdat)
    aw.show()
    # if app_created:
    #     app.references.add(self.aw)
    aw.adjustSize()
    res = aw.exec_()
    # if cancel pressed - return None
    if not res:
        return None
    output = aw.get_output(items)
    return output


class SelectListWindow(QtWidgets.QDialog):
    def __init__(self, all_items):
        super().__init__()
        uic.loadUi(get_ui_file_name('list_select.ui'), self)
        self.wAdd.clicked.connect(self.add)
        self.wRemove.clicked.connect(self.remove)

        for citem in all_items:
            self.wListAll.addItem(citem)

    def add(self):
        items = self.wListAll.selectedItems()
        for citem in items:
            cname = str(citem.text())
            self.wListSelected.addItem(cname)
            self.wListAll.takeItem(self.wListAll.row(citem))

    def remove(self):
        items = self.wListSelected.selectedItems()
        for citem in items:
            cname = str(citem.text())
            self.wListAll.addItem(cname)
            self.wListSelected.takeItem(self.wListSelected.row(citem))


def select_list_items(all_items):
        win = SelectListWindow(all_items)
        res = win.exec_()
        if res == QtWidgets.QDialog.Accepted:
            selected = [str(win.wListSelected.item(i).text()) for i in range(win.wListSelected.count())]
            return selected
        else:
            return []


class SListWindow(QtWidgets.QDialog):
    def __init__(self, listdata=[], listname=None):
        '''Create a list window with items in the list and the listname as specified

        Parameters
        ----------
        listdata: list of str, optional
            the data to show in the list
        listname: str, optional
            name to display above the list
        '''
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if listname is not None:
            self.setWindowTitle(listname)

        self.layout = QVBoxLayout(self)

        self.w_list = QListWidget()
        self.layout.addWidget(self.w_list)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(buttonBox)

        for citem in listdata:
            self.w_list.addItem(citem)

        self.show()
        self.adjustSize()


def init_qt5():
    '''Init the qt5 event loop

    Parameters
    ----------

    Returns
    -------
    app :
        QCoreApplication
    app_created : bool
        True if a new QApplication was created, False if using existing one
    '''
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        # app = QApplication(sys.argv)
        app = QApplication(sys.argv)
        app_created = True
        logger.debug('Qt app created')
    logger.debug('Qt app is %s' % app)
    if not hasattr(app, 'references'):
        app.references = set()

    return app, app_created


def _value_to_dtype(val, exp, field):
    '''Get the value converted to the field dtype

    Parameters
    ----------
    val : str
        the value to convet from
    exp : Experiment
        containing the field
    field : str
        name of the field in experiment sample metadata to take the new type from

    Returns
    any_type
        the value converted to the exp/field data type
    '''
    svalue = np.array([val])
    svalue = svalue.astype(exp.sample_metadata[field].dtype)
    svalue = svalue[0]
    return svalue


def exception_hook(exception_type, value, traceback_info):
    '''Used to disable Abort trap exiting the program on unhandled exceptions
    This way a failed button will not crash everything
    '''
    sys.__excepthook__(exception_type, value, traceback)

    msg = 'Error enountered - details:\n'
    # Turn the traceback into a string.
    # msg += "\n".join(traceback.format_tb(traceback_info))
    msg += "\n%s: %s" % (exception_type.__name__, value)

    QtWidgets.QMessageBox.information(None, "Error enountered", msg)


def get_config_file():
    '''Get the ezcalour config file location

    If the environment EZCALOUR_CONFIG_FILE is set, take the config file from it
    otherwise return EZCALOUR_PACKAGE_LOCATION/ezcalour_module/ezcalour.config

    Returns
    -------
    config_file_name : str
        the full path to the calour config file
    '''
    if 'EZCALOUR_CONFIG_FILE' in os.environ:
        config_file_name = os.environ['EZCALOUR_CONFIG_FILE']
        logger.debug('Using calour config file %s from EZCALOUR_CONFIG_FILE variable' % config_file_name)
    else:
        config_file_name = get_res_file_name('ezcalour.config')
    return config_file_name

######################
# json comments functions modified from:
# https://pypi.python.org/pypi/jsoncomment/0.2.3
######################


def comment_json_loads(custom_json_string, *args, **kwargs):
    lines = custom_json_string.splitlines()
    standard_json = json_preprocess(lines)
    return json.loads(standard_json, *args, **kwargs)


def comment_json_load(custom_json_file, *args, **kwargs):
    return comment_json_loads(custom_json_file.read(), *args, **kwargs)


def json_preprocess(lines):
    # Comments
    COMMENT_PREFIX = ("#", ";")
    MULTILINE_START = "/*"
    MULTILINE_END = "*/"

    # Data strings
    LONG_STRING = '"""'

    standard_json = ""
    is_multiline = False
    keep_trail_space = 0

    for line in lines:

        # 0 if there is no trailing space
        # 1 otherwise
        keep_trail_space = int(line.endswith(" "))

        # Remove all whitespace on both sides
        line = line.strip()

        # Skip blank lines
        if len(line) == 0:
            continue

        # Skip single line comments
        if line.startswith(COMMENT_PREFIX):
            continue

        # Mark the start of a multiline comment
        # Not skipping, to identify single line comments using
        #   multiline comment tokens, like
        #   /***** Comment *****/
        if line.startswith(MULTILINE_START):
            is_multiline = True

        # Skip a line of multiline comments
        if is_multiline:
            # Mark the end of a multiline comment
            if line.endswith(MULTILINE_END):
                is_multiline = False
            continue

        # Replace the multi line data token to the JSON valid one
        if LONG_STRING in line:
            line = line.replace(LONG_STRING, '"')

        standard_json += line + " " * keep_trail_space

    # Removing non-standard trailing commas
    standard_json = standard_json.replace(",]", "]")
    standard_json = standard_json.replace(",}", "}")

    return standard_json


def get_config_values(section=None, config_file_name=None):
    '''Read the config json file and return the dict associated with section

    Parameters
    ----------
    section : str or None
        The config file section to read. if None return all file
        Note: the config file is a json dict file, each section is a key
        If section is not found, return empty dict {}
    config_file_name: str or None
        name of json config file to use
        None to load the default ezcalour config file
    '''
    if config_file_name is None:
        config_file_name = get_config_file()
    try:
        with open(config_file_name) as f:
            conf = dict(comment_json_load(f))
        if section is None:
            return conf
        if section not in conf:
            return {}
        return conf[section]
    except:
        logger.warn('Failed reading ezcalour config file %s section %s' % (config_file_name, section))
        return {}


def main():
    parser = argparse.ArgumentParser(description='GUI for Calour microbiome analysis')
    parser.add_argument('--table', help='biom table to load on startup', default=None)
    parser.add_argument('--map', help='mapping file to load on startup', default=None)
    parser.add_argument('--name', help='loaded study name', default=None)
    parser.add_argument('--log-level', help='debug messages level. use 10 for full debug information, 20 for INFO, 30 for WARNING', default=20, type=int)
    parser.add_argument('--version', help='print version information', action='store_true')

    args = parser.parse_args()

    if args.version:
        print("EZCalour version %s" % __version__)
        print("Using Calour versuin %s" % ca.__version__)
        try:
            dbbact = ca.database._get_database_class('dbbact')
            print("Using dbbact-calour verion %s" % dbbact.version())
        except:
            print("dbbact-calour not installed")
        exit(0)

    if args.table is None:
        load_exp = None
    else:
        load_exp = [(args.table, args.map, args.name)]

    ca.set_log_level(args.log_level)
    logger.setLevel(args.log_level)

    # ca.set_log_level('INFO')
    # logger.setLevel('INFO')

    logger.info('Using ezcalour configuration file %s' % get_config_file())

    logger.info('starting Calour GUI')
    app = QtWidgets.QApplication(sys.argv)
    app, app_created = init_qt5()
    sys.excepthook = exception_hook
    window = AppWindow(load_exp=load_exp)
    # window = AppWindow(load_exp=None)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
