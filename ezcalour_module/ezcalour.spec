# -*- mode: python -*-

import imp
import os

block_cipher = None

calour_loc = imp.find_module("calour")[1]
dbbact_loc = imp.find_module("dbbact_calour")[1]
gnps_loc = imp.find_module("gnpscalour")[1]
pheno_loc = imp.find_module("phenocalour")[1]

cwd = os.getcwd()

a = Analysis(['ezcalour.py'],
             pathex=[cwd],
             binaries=[],
             datas=[('ui','ezcalour_module/ui'), ('ezcalour.config','ezcalour_module'), ('log.cfg','ezcalour_module'), (calour_loc+'/log.cfg', 'calour'), (calour_loc+'/calour.config', 'calour'), (dbbact_loc+'/log.cfg', 'dbbact_calour'), (pheno_loc+'/data','phenocalour/data'), (gnps_loc+'/log.cfg', 'gnpscalour')],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ezcalour',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
#          runtime_tmpdir=None,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ezcalour')
# app = BUNDLE(exe,
#              name='ezcalour.app',
#              icon=None,
#              bundle_identifier=None)
