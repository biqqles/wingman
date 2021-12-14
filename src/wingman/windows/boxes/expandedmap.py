"""
Copyright © 2016-$today.year biqqles.

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
"""
from functools import partial

from PyQt5 import QtCore, QtWidgets
import flint as fl

from ... import config
from ...widgets.mapview import MapView


class ExpandedMap(MapView):
    """A windowed variant of MapView that can be used, for example, to display a universe map or an expanded
    system map."""
    INITIAL_SIZE = (800, 800)

    def __init__(self):
        super().__init__(url=config.expanded_navmap)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.controlsFrame.hide()

        # customise context menu
        self.menu.clear()
        showOorp = QtWidgets.QAction('Show inaccessible systems', checkable=True, checked=False)
        showOorp.toggled.connect(partial(self.setState, 'wingman.showOorp'))
        self.actions = [showOorp, self.saveAction]
        self.menu.addActions(self.actions)

    def heightForWidth(self, width: int) -> int:
        """Should always be square."""
        return width

    def display(self):
        """Display an expanded map."""
        self.resize(*self.INITIAL_SIZE)
        self.show()

    def displayEntity(self, entity: fl.entities.Entity):
        """Display an expanded system map."""
        super().displayEntity(entity)
        self.setWindowModality(QtCore.Qt.NonModal)
        self.disconnectDisplayChanged()
        self.displayChanged.connect(lambda: self.setWindowTitle(self.getDisplayed().title()))
        self.display()

    def displayUniverse(self, highlightedSystem=None):
        """Display an expanded universe map."""
        super().displayUniverse()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Sirius')
        self.display()

        self.page().runJavaScript(f'wingman.highlightSystem({highlightedSystem!r})')
        self.disconnectDisplayChanged()
        self.displayChanged.connect(self.hide)

    def onUrlChange(self):
        """Reimplement to avoid injecting the JS we do with the base class."""
        self.page().runJavaScript('currentSystemNickname', self.emitDisplayChanged)

    def disconnectDisplayChanged(self):
        """Disconnect the displayChanged signal."""
        try:
            self.displayChanged.disconnect()
        except TypeError:  # raised when no callbacks are connected
            pass
