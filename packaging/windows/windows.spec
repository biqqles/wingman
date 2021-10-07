# -*- mode: python -*-
# pyinstaller spec file for wingman

import os
import PyQt5

QT_BIN = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'bin')
ROOT = os.path.dirname(os.path.dirname(os.getcwd()))

a = Analysis([os.path.join(ROOT, 'src', 'wingman', 'main.py')],
             pathex=[os.path.join(ROOT, 'src'), QT_BIN],
             datas=[('../../LICENSE.txt', '.'), ('../../README.md', '.'), ('wingman.cp38-win32.pyd', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=None)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Wingman',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          uac_admin=False,
          icon=os.path.join(ROOT, 'icons', 'general', 'wingman.ico'))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               debug=False,
               name='Wingman')
