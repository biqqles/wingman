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

This file defines the interface of the application's main window.
"""
from typing import Callable, Union
import logging

from PyQt5 import QtWidgets
from flint import cached

from ... import config, __app__
from . import merchant, navmap, roster, banner, menus, loading
from .navmap.navmap import Navmap
from .merchant.merchant import Merchant
from .roster.roster import Roster
from ...windows.boxes.expandedmap import ExpandedMap


class MainWindow(QtWidgets.QMainWindow):
    """The application's main window."""
    title = __app__
    initialDimensions = (1060, 610)

    def __init__(self):
        logging.info('Loading main window')
        super().__init__()
        self.setWindowTitle(self.title)
        self.resize(*self.initialDimensions)

        self.centralWidget = QtWidgets.QWidget()
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.centralWidget)

        self.tw = QtWidgets.QTabWidget(self.centralWidget)
        self.tw.setContentsMargins(0, 0, 0, 0)

        # Navmap tab

        self.tabMap = navmap.layout.NavmapTab(self.tw)
        self.tw.addTab(self.tabMap, self.tabMap.icon, self.tabMap.title)
        self.tw.currentChanged.connect(self.cueLazyLoadTab(self.tabMap, self.navmap))

        # Merchant tab

        self.tabMer = merchant.layout.MerchantTab(self.tw)
        self.tw.addTab(self.tabMer, self.tabMer.icon, self.tabMer.title)
        self.tw.currentChanged.connect(self.cueLazyLoadTab(self.tabMer, self.merchant))

        # Roster

        self.tabRoster = roster.layout.RosterTab(self.tw)
        self.tw.addTab(self.tabRoster, self.tabRoster.icon, self.tabRoster.title)
        self.tw.currentChanged.connect(self.cueLazyLoadTab(self.tabRoster, self.roster))

        self.centralLayout.addWidget(self.tw)

        # banner

        self.banner = banner.FlairBanner(self)

        # Menubar

        self.menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menubar)

        self.menubar.addMenu(menus.Utilities(self.menubar))
        self.menubar.addMenu(menus.File(self.menubar))
        self.menubar.addMenu(menus.Freelancer(self.menubar))
        self.menubar.addMenu(menus.Preferences(self.menubar))
        self.menubar.addMenu(menus.Help(self.menubar))

        self.show()
        self.tw.currentChanged.emit(0)

        self.indicator = loading.Indicator(self.statusBar())

    def resizeEvent(self, event):
        """Ensure banner "sticks" to the top right of the window."""
        self.banner.updatePosition()

    def closeEvent(self, event):
        """Write config to disk on close."""
        config.commit()

    def cueLazyLoadTab(self, layout, load: Callable[[], Union[Navmap, Merchant, Roster]]):
        """Cue a tab to be lazy loaded."""
        return lambda: load() if self.tw.currentWidget() is layout else None

    @cached  # bit of a hack - using flint's decorator
    def expandedMap(self) -> ExpandedMap:
        """Initialise the expanded map."""
        return ExpandedMap()

    @cached
    def navmap(self) -> Navmap:
        """Load Navmap."""
        return Navmap(self.tabMap, self.expandedMap())

    @cached
    def merchant(self) -> Merchant:
        """Load Merchant."""
        return Merchant(self.tabMer, self.expandedMap(), self.navmap())

    @cached
    def roster(self) -> Roster:
        """Load Roster."""
        return Roster(self.tabRoster)
