# -*- mode: python ; coding: utf-8 -*-
import os
import pygame
font_path = os.path.dirname(pygame.__file__)
font = [p for p in os.listdir(font_path) if p[-4:] == '.ttf'][0]
font_path = os.path.join(font_path, font)
# font_path = 'freesansbold.ttf'
pathex = os.getcwd()

datas = [('preflop.pkl', '.'), (font_path, '.')]
if os.name == 'nt':
    datas += [('holes_operations.dll', '.'), ('assets\\*', 'assets')]
if os.name == 'posix':
    datas += [('holes_operations.so', '.'), ('assets/*', 'assets')]

block_cipher = None

a = Analysis(['StackTheDeck.py'],
             pathex=[pathex],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='StackTheDeck',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
