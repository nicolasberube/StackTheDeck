# StackTheDeck

This project is a simple Python game coded with pygame where you play as the dealer in a 2 player Texas Hold'em poker game where you're trying to make your friend win.

Current version 0.1 (working prototype)

# Download the game

### Standalone executable

[Windows .exe file](https://github.com/nicolasberube/StackTheDeck/raw/master/StackTheDeck.exe)

[Mac/Unix executable file](https://github.com/nicolasberube/StackTheDeck/raw/master/StackTheDeck.app/Contents/MacOS/StackTheDeck)

For a Mac .app file that does not launch a console every time, you can download all files through the green button **Clone or download** - **Download .ZIP** on the top right corner of this page. You will find the file StackTheDeck.app in the folder, which is the only file you will need. I'm not aware of any native Git method to download only the .app file.

### Alternate method: Download python

Download and install [Anaconda](https://docs.conda.io/en/latest/miniconda.html).

Open the Anaconda Powershell Prompt that came with the installation

Type the following 3 command line to create an environment with the appropriate packages

```
conda create -n stackthedeck python=3.6
conda activate stackthedeck
python -m pip install pygame
```
Download the files through the green button **Clone or download** - **Download .ZIP** on the top right corner of this page. Then, from the Anaconda Powershell Prompt, use commands like ```cd``` to go in the downloaded directory, and type

```
python StackTheDeck.py
```

# Project files

* **compute_preflop.py**: Computes *preflop.pkl*
* **cx_setup.py**: cx_freeze setup file installer for Windows. Use with ```python cx_setup.py bdist_msi```
* **freesansbold.ttf**: Default font for pygame. Optional file.
* **holes_operations_win.c**: External C code for Windows. Must be compiled in a .dll with Visual Studio
* **holes_operations_mac.c**: External C code for Mac. Must be compiled in a .so with ```python so_setup.py build_ext --inplace```
* **holes_operations.dll**: C library for Windows
* **holes_operations.so**: C library for Mac
* **preflop.pkl**: pre flop probabilities data
* **StackTheDeck.py**: Main game code
* **StackTheDeck-0.1-amd64.msi**: cx_freeze game installer for Windows. Alternative to the .exe file.
* **StackTheDeck.exe**: PyInstaller standalone .exe for Windows

# Notes on package dependancies

The only necessary package for executing the game is ```pygame=1.9.6```. However, many packages were used for the development of the game. ```tqdm=4.45.0``` is used to compute the pre-flop probabilities. An older version of ```setuptools=44.0.0``` is used for proper use of ```pyinstaller=3.6``` to create the executable. ```cx-freeze=6.1``` is used to create an alternate installer.

I also use homemade .c libraries to circumvent the dependency on ```numpy```. The creation of a standalone executable from Python that uses numpy creates up to 600 Mb of mkl files.
