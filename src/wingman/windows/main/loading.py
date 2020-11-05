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

This file defines a loading indicator that displays the progress
of flint lazy-loading at application start.
"""
from PyQt5 import QtCore, QtWidgets
import flint as fl


class Thread(QtCore.QThread):
    """Run expensive routines in flint in a thread."""
    jobFinished = QtCore.pyqtSignal(str)

    def run(self):
        """Call flint functions and emit a signal when each one is complete."""
        fl.get_systems()
        self.jobFinished.emit('systems')
        fl.maps.generate_universe_graph()
        self.jobFinished.emit('universe')
        fl.get_equipment()
        self.jobFinished.emit('equipment')
        fl.get_goods()
        self.jobFinished.emit('goods')
        fl.routines.get_markets()
        self.jobFinished.emit('markets')

    TOTAL_CALLS = 5  # total number of flint calls made


class Indicator:
    """An indicator of loading progress on the status bar.
    TODO: delete when finished."""
    def __init__(self, statusBar: QtWidgets.QStatusBar):
        self.statusBar = statusBar
        self.thread = Thread()

        self.bar = QtWidgets.QProgressBar()
        self.bar.setValue(0)
        self.statusBar.addPermanentWidget(self.bar)

        self.thread.jobFinished.connect(self.update)
        self.thread.start()

    def update(self, name):
        """Update the status bar indicator. If loading is complete, clear and hide the bar."""
        newValue = self.bar.value() + (100 / Thread.TOTAL_CALLS)
        self.statusBar.showMessage(f'Loading {name}...')
        self.bar.setValue(newValue)

        if newValue == 100:
            self.statusBar.removeWidget(self.bar)
            self.statusBar.clearMessage()
            self.statusBar.hide()
