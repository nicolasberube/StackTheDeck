from cx_Freeze import setup, Executable
import os
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
MKL_BUG_DIR = os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin')

mkl_files = ([os.path.join(MKL_BUG_DIR, f) for f in os.listdir(MKL_BUG_DIR)
              if f [:4] == 'mkl_'] +
             [os.path.join(MKL_BUG_DIR, 'libiomp5md.dll')])
assets_files = ([os.path.join('assets', f) for f in os.listdir('assets')] +
                ['preflop_hash.npy'])
assets_files = [(f, f) for f in assets_files]

buildOptions = dict(
    packages = [],
    excludes = [],
    include_files = mkl_files + assets_files
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
