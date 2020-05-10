from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.

# Pygame default font
import os
import pygame
font_path = os.path.dirname(pygame.__file__)
font = [p for p in os.listdir(font_path) if p[-4:] == '.ttf'][0]
font_path = os.path.join(font_path, font)
# font_path = 'freesansbold.ttf'

lib_files = ['holes_operations.dll', 'preflop.pkl', font_path]
assets_files = [os.path.join('assets', f) for f in os.listdir('assets')]
assets_files = [(f, f) for f in assets_files]

# If using , you need to include the following files
# PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
# MKL_BUG_DIR = os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin')
# lib_files += ([os.path.join(MKL_BUG_DIR, f) for f in os.listdir(MKL_BUG_DIR)
#                if f [:4] == 'mkl_'] +
#               [os.path.join(MKL_BUG_DIR, 'libiomp5md.dll')])


buildOptions = dict(
    packages = [],
    excludes = [],
    include_files = lib_files + assets_files
    )

# base = 'Console'
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('StackTheDeck.py', base=base, targetName = 'StackTheDeck')
]

setup(name='StackTheDeck',
      version = '0.1',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
