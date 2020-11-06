"""
Copyright © 2016-2017, 2020 biqqles.

This file is part of Wingman.

Wingman is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wingman is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Wingman.  If not, see <http://www.gnu.org/licenses/>.

This file initialises the application.
"""
__app__ = 'Wingman'
__version__ = 'v0.3'
__description__ = 'A companion for Discovery Freelancer'

import os
import logging
import signal
import sys

# noinspection PyUnresolvedReferences
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets  # WebEngine must be imported here before QApp init
from . import resources  # register resources
from . import namespaces

try:
    # noinspection PyUnresolvedReferences
    import flair
    IS_WIN = True
except ImportError:
    IS_WIN = False

# paths relative to app data directory
NAVMAP_DIR = 'navmap'
CONFIG_FILE = 'wingman.cfg'
ROSTER_FILE = 'roster.json'
LOG_FILE = 'wingman.log'

# initialise QApplication
app = QtWidgets.QApplication([__app__.lower()])
app.setApplicationDisplayName(__app__)
app.setApplicationName(__app__.lower())
app.setWindowIcon(QtGui.QIcon(':/general/main'))

# switch current working directory to a suitable location to store app data
dataLocation = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppLocalDataLocation)
os.makedirs(dataLocation, exist_ok=True)
os.chdir(dataLocation)

# configure logging
# noinspection PyArgumentList
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    handlers=[  # log to file and stdout
                            logging.FileHandler(LOG_FILE),
                            logging.StreamHandler()
                        ]
                    )


def exception_hook(ex_type, value, traceback):
    """Handle uncaught exceptions. Log to file and stdout and, if a window is showing, to an error dialogue."""
    if ex_type is KeyboardInterrupt:
        return sys.__excepthook__(ex_type, value, traceback)

    logging.error('Uncaught exception!', exc_info=(ex_type, value, traceback))

    if app.activeWindow():
        QtWidgets.QErrorMessage(app.activeWindow()).showMessage(repr(value), repr(value))


sys.excepthook = exception_hook
signal.signal(signal.SIGINT, signal.SIG_DFL)  # force Python to handle SIGINT even during app.exec


logging.info('Application start')
logging.info(f'Working directory: {os.getcwd()}')

# initialise namespaces
icons = namespaces.Icons()
config = namespaces.Configuration(CONFIG_FILE)

# platform specific initialisation
if IS_WIN:
    font = app.font()
    font.setFamily('Segoe UI')
    font.setPointSizeF(font.pointSize() * 1.2)
    app.setFont(font)
else:
    if QtWidgets.QStyleFactory.keys() == ['Windows', 'Fusion']:
        logging.warning("Native Qt style not available. Defaulting to Fusion - the application may not render "
                        "correctly. To fix this, install the PyQt5 packages from your distro's repos, not pip.")
