# Wingman
[Jump to source](src/wingman) | [Project thread](https://discoverygc.com/forums/showthread.php?tid=150721) | [Screenshots](https://discoverygc.com/forums/showthread.php?tid=150721#anchor-gallery)

**Wingman** is a powerful desktop companion application specifically crafted for [Discovery Freelancer](https://discoverygc.com/). Intended to be a modern addition to the venerable [FLStat](http://adoxa.altervista.org/freelancer/tools.html#flstat) and [Freelancer Companion](http://wiz0u.free.fr/prog/flc/), it seeks to bring a wealth of new features to the community.

Wingman features:

- *Navmap*: a beautiful navigation aid integrating and extending @[Error](https://github.com/AudunVN)'s [Online Navmap](https://github.com/AudunVN/Navmap)
- *Merchant*: a powerful trading assistant
- *Roster*: a record of your in-game characters and their attributes
- *Database*: an information-dense overview of the game's world
- Augmentation of the game client, including clipboard access, named screenshots and new commands
- Display of infocards with full rich text formatting, plus TGA icons
- Full cross-platform support, with downloads for Windows and Linux

Under the hood, Wingman combines my two libraries for Freelancer - [flint](https://github.com/biqqles/flint) (to read the game's static data) and [flair](https://github.com/biqqles/flair) (to hook the client) - with a rich graphical interface implemented in PyQt.

Wingman is free software, released under the GNU General Public License, version 3.0.

### Suggestions
See [Issues](https://github.com/biqqles/wingman/issues?q=is%3Aissue+is%3Aopen+label%3A%22feature+request%22) for a list of new features that are currently planned. To be maximally useful Wingman should be community-led, so please feel free to make your own either in the project thread or here on GitHub.


## Installation
### Installing on Windows
The minimum supported Windows version is Windows 7.

Download and run the installer. After installation Wingman can be launched from the Start Menu.

Alternatively, if you have Python 3.7 or higher installed, you can use the installation instructions for Linux (ignoring those about native styling, since this is not an issue on Windows). However, this will not create a Start Menu entry or desktop icon and you will need to start the process as administrator manually, or create a custom shortcut.

### Installing on Linux
Assuming you have Python 3.7 or higher installed and available as `python3`, simply run `python3 -m pip install wingman`.

After installation the application should be available either from your desktop's application menu or, if you ran pip with sudo, by running `wingman` in a terminal. (You may need to log in and out to get the icon to show.)

To uninstall, run `python3 -m pip uninstall wingman`.

The application will probably be installable on macOS using the above commands but I'm unable to test this platform myself. If someone was able to try it out that would be great.

#### Native styling
Because the PyQt wheels do not include platform-specific style plugins, Wingman will run with the default Fusion theme when using pip-installed PyQt5. This works OK, but if you prefer native theming (e.g. Breeze on a KDE system) you need to install the PyQt5 packages from your distro's package manager rather than pip. Unless you want to build PyQt from source, **this is only possible if your distro provides a PyQt5 package for Python 3.7 or higher**. This rules out Ubuntu LTS, as at the time of writing packages are built only for Python 3.6.
many
- Uninstall the `PyQt5` and `PyQtWebEngine` packages with pip
- Install `python-pyqt5` and `python-pyqtwebengine` (e.g. if you use pacman) or `python3-pyqt5` and `python3-pyqt5.qtwebengine` (if you use apt) with your package manager


## Building and packaging
### Prerequisites (for all platforms)
Ensure PyQt5 is installed. The included `pyrcc5` utility is required for building.

For both platforms (Windows and Linux), the first step is always to compile a fresh copy of the Qt resource file containing the icons and text files the application needs, using `pyrcc5`. From the root directory, run `pyrcc5 src/resources.qrc -o src/wingman/resources.py`

### For Windows
From the root directory, `cd packaging/windows`. Ensure that [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/) is installed, in addition to the application's own requirements.

Now run `build.bat` to build a one folder application and an installer.

### For Linux
Again from the root directory, run `python setup.py sdist` to build a source distribution.

To now install your locally-built distribution, run `pip install dist/wingman-*.tar.gz`.
