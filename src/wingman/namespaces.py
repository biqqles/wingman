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

This file contains core utility namespaces used throughout the
application.
"""
import atexit
import configparser
import logging
from io import BytesIO

from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageQt


class Configuration(configparser.ConfigParser):
    """A class providing a persistent configuration store. The configuration is written to storage on program exit.

    Todo: will need some way of supporting deltas on updates."""

    def __init__(self, path):
        super().__init__(self, allow_no_value=True)
        self.path = path
        self.optionxform = str  # override default behaviour of converting all keys to lowercase
        atexit.register(self.commit)

        try:
            with open(self.path) as f:
                self.read_file(f)

            self.paths = self['paths']
            self.install = self.paths['freelancer_dir']
            self.my_games = self.paths['my_games']
            self.dsace = self.paths['dsace']
            self.launcher_accounts = self.paths['accounts']

            self.migrations()

            self.urls = self['urls']
            self.navmap = self['urls']['navmap']
        except (FileNotFoundError, KeyError):
            logging.warning('Config missing or corrupt, reverting to defaults')
            self.createFile()
            self.__init__(self.path)

    def commit(self, path=None):
        """Commit the configuration to disk."""
        path = path or self.path
        with open(path, 'w') as fh:
            self.write(fh)

    def saveAs(self, export_path: str):
        """Save/export the configuration to another file at `export_path`."""
        self.commit(export_path)

    def reset(self):
        """Reset the configuration to the defaults."""
        self.createFile()

    def createFile(self):
        """Create a new configuration file."""
        self.read_string(self.loadDefaults())
        self.commit()

    def migrations(self):
        """Perform any migrations from the current config to an updated version."""
        defaults = configparser.ConfigParser()
        defaults.read_string(self.loadDefaults())
        self['urls'] = defaults['urls']

    @staticmethod
    def loadDefaults() -> str:
        """Load the default configuration from resources."""
        file = QtCore.QFile(':/config/default')
        file.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text)
        return QtCore.QTextStream(file).readAll()


class Icons:
    """Set the icons of the interface depending on whether the background colour is light (meaning that dark icons
    should be used) or dark (meaning that light icons should be used)"""
    monochrome = ['universe', 'jump', 'expand', 'open', 'cc', 'left', 'right', 'swap']

    def __init__(self):
        prefix = ':/dark/' if self.determineLuminance() else ':/light/'

        for icon in self.monochrome:
            setattr(self, icon, QtGui.QIcon(prefix + icon))

        self.main = QtGui.QIcon(':/general/main')  # todo: make static class
        self.navmap = QtGui.QIcon(':/general/navmap')
        self.merchant = QtGui.QIcon(':/general/merchant')
        self.roster = QtGui.QIcon(':/general/roster')

        # Linux only:
        self.open = QtGui.QIcon.fromTheme('document-save')
        self.copy = QtGui.QIcon.fromTheme('edit-copy')

    @staticmethod
    def determineLuminance(threshold=200) -> bool:
        """Determine whether this platform has a light or dark theme by testing the background colour of a push
        button. `threshold` is the threshold average luminance to be considered a "bright" theme."""
        button = QtWidgets.QPushButton()
        colour = button.palette().color(button.backgroundRole())
        luminance = sum(colour.getRgb()) / 3
        return luminance > threshold

    @staticmethod
    def loadTGA(tga: bytes) -> QtGui.QPixmap:
        """Load a TGA image as a QPixmap. For some reason, some images accepted by Freelancer do not load in PyQt - but
        they do with the help of Pillow."""
        image = ImageQt.ImageQt(Image.open(BytesIO(tga)))
        return QtGui.QPixmap.fromImage(image)
