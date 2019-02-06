# -*- mode: python -*-

block_cipher = None


a = Analysis(['ezcalour.py'],
             pathex=['/Users/amnon/miniconda3/envs/ezinstall/lib/python3.5/site-packages/ezcalour_module'],
             binaries=[],
             datas=[('../calour/log.cfg', 'calour'), ('ui','ezcalour_module/ui'), ('../dbbact_calour/log.cfg', 'dbbact_calour'), ('../phenocalour/data','phenocalour/data'), ('../gnpscalour/log.cfg', 'gnpscalour')],
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
