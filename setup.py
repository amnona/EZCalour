#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2015--, calour development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

version = '0.9'

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: BSD License',
    'Environment :: Console',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows']


description = 'EZCalour: GUI frontend tool for Calour microbiome analysis software'

with open('README.md') as f:
    long_description = f.read()

keywords = 'microbiome heatmap analysis bioinformatics GUI',

setup(name='ezcalour',
      version=version,
      license='GPL',
      description=description,
      long_description=long_description,
      keywords=keywords,
      classifiers=classifiers,
      author="calour development team",
      maintainer="calour development team",
      url='http://microbio.me/calour',
      test_suite='nose.collector',
      packages=find_packages(),
      package_data={'ezcalour_module': ['ui/*.ui', 'log.cfg', 'ezcalour.config', 'ezcalour.config.bak']},
      # scripts=['ezcalour_module/ezcalour.py'],
      entry_points={
          'console_scripts': [
              'ezcalour = ezcalour_module.ezcalour:main']},
      install_requires=[
          'pyqt5',
          'matplotlib',
          'numpy',
          'calour@https://github.com/biocore/calour/tarball/master#egg=calour',
          'dbbact-calour@https://github.com/amnona/dbbact-calour/tarball/master#egg=dbbact-calour'
      ],
      extras_require={'test': ["nose", "pep8", "flake8"],
                      'coverage': ["coverage"],
                      'doc': ["Sphinx >= 1.4"]}
      )
