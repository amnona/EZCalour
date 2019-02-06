# -*- mode: python -*-

import imp

block_cipher = None

calour_loc = imp.find_module("calour")[1]
dbbact_loc = imp.find_module("dbbact_calour")[1]
gnps_loc = imp.find_module("gnpscalour")[1]
pheno_loc = imp.find_module("phenocalour")[1]

a = Analysis(['ezcalour.py'],
             pathex=['/Users/amnon/miniconda3/envs/ezinstall/lib/python3.5/site-packages/ezcalour_module'],
             binaries=[],
             datas=[('ui','ezcalour_module/ui'), (calour_loc+'/log.cfg', 'calour'), (dbbact_loc+'/log.cfg', 'dbbact_calour'), (pheno_loc+'/data','phenocalour/data'), (gnps_loc+'/log.cfg', 'gnpscalour')],
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
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ezcalour')
