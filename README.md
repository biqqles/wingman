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

After installation the application should be available either from your desktop's application menu or, if you ran pip with sudo, by running `wingman` in a terminal.

To upgrade, run `python3 -m pip install -U wingman`. To uninstall, run `python3 -m pip uninstall wingman`.

Note that the latest version available on PyPI may not match the latest version number for Windows because minor bugfix releases that only affect Windows are not published on PyPI.

The application will probably be installable on macOS using the above commands but I'm unable to test this platform myself. If someone was able to try it out that would be great.

#### Native styling
Because the PyQt wheels do not include platform-specific style plugins, Wingman will run with the default Fusion theme when using pip-installed PyQt5. This works OK, but if you prefer native theming (e.g. Breeze on a KDE system) you need to install the PyQt5 packages from your distro's package manager rather than pip. Unless you want to build PyQt from source, **this is only possible if your distro provides a PyQt5 package for Python 3.7 or higher**. This rules out Ubuntu LTS, as at the time of writing packages are built only for Python 3.6.

- Uninstall the `PyQt5` and `PyQtWebEngine` packages with pip
- Install `python-pyqt5` and `python-pyqtwebengine` (e.g. if you use pacman) or `python3-pyqt5` and `python3-pyqt5.qtwebengine` (if you use apt) with your package manager


## Building and packaging
### CI
A [workflow](.github/workflows/build.yml) exists that produces automated builds for Linux and Windows.

### Local
#### Prerequisites (for all platforms)
Ensure the development dependencies in `requirements.txt` are installed. To build on Windows you will additionally need to install the requirements of the application itself listed in `setup.py`.

#### For Windows
From the root directory, `cd packaging/windows`.

Run `build.bat` to build a one folder application and an installer. The application is built against Python 3.8, the [last version](https://bugs.python.org/issue32592) to support Windows 7.

#### For Linux
From the root directory, `cd packaging/linux` and run `build.sh` to build a source distribution.

To install your locally-built distribution, run `pip install dist/wingman-*.tar.gz`.
