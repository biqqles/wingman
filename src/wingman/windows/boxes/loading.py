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
"""
import sys

from PyQt5 import QtCore, QtWidgets
import flint as fl


class LoadingFiles(QtWidgets.QProgressDialog):
    """Display a loading dialogue to inform the user that flint is processing the game files. This should be shown
    after paths have been configured, but before anything else."""
    class LoadingThread(QtCore.QThread):
        jobFinished = QtCore.pyqtSignal(str)

        def run(self):
            """This is a bit of a hack. Run expensive routines in flint before loading the rest of the application."""
            fl.get_systems()
            self.jobFinished.emit('Systems')
            fl.maps.generate_universe_graph()
            self.jobFinished.emit('Universe')
            fl.get_equipment()
            self.jobFinished.emit('Equipment')
            fl.get_goods()
            self.jobFinished.emit('Goods')
            fl.routines.get_markets()
            self.jobFinished.emit('Markets')

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Reading game data')
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)

        # QProgressDialog claims to "return a size that fits the contents of the progress dialog" but this is
        # absolutely not the case. As a hack, but not one that's too bad, increase its suggested size by ~50%
        self.setMinimumWidth(int(self.width() * 1.5))

        self.setRange(0, 0)
        self.setMinimumDuration(0)
        self.show()
        self.canceled.connect(lambda: sys.exit(2))

        self.thread = self.LoadingThread()
        self.thread.jobFinished.connect(self.setLabelText)
        # disconnecting canceled is required because it is emitted when the window is closed, contrary to the docs
        self.thread.finished.connect(lambda: self.canceled.disconnect() or self.close())
        self.thread.start()
