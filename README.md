# StackTheDeck

This project is a simple Python game coded with pygame where you play as the dealer in a 2 player Texas Hold'em poker game where you're trying to make your friend win.

Current version 0.1 (working prototype)

# How to download the game

## Method 1: Use the Windows 10 installer

[Download the installer of the game](https://www.dropbox.com/s/0m2hz51cwocpbow/StackTheDeck-0.1-amd64.msi?dl=0), select a directory to install the game in, then open StackTheDeck.exe.

To remove the game, simply delete the directory and the installer.

## Method 2: Download python

Download and install [Anaconda](https://docs.conda.io/en/latest/miniconda.html).

Open the Anaconda Powershell Prompt that came with the installation

Type the following 3 command line to create an environment with the appropriate packages

```
conda create -n stackthedeck numpy tqdm python=3.6
conda activate stackthedeck
python -m pip intall -U pygame --user
```
Download the files through the green button **Clone or download** - **Download .ZIP** on the top right corner of this page. Then, from the Anaconda Powershell Prompt, use commands like ```cd``` to go in the downloaded directory, and type

```
python StackTheDeck.py
```

# Package dependancies

```
numpy=1.18.1
tqdm=4.45.0
pip:
  pygame=1.9.6
```
# Notes on creating the installer

The installer was created with ```cx_freeze``` through the command ```python setup.py bdist_msi```.

The setup.py file needed been crafted to include all the game assets in the build, as well as missing Intel MKL libraries that are not included by default by cx_freeze. See the setup.py file for more information. This results in a humongous 240 Mb installer file, or more than 600 Mb of uncompiled .dll files. I suspect this to be entirely because of the current dependancy on numpy.
