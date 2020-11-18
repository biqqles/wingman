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
from typing import Callable, Union, Type
import logging

from PyQt5 import QtWidgets, QtGui
from flint import cached

from ... import config, __app__
from . import merchant, navmap, roster, banner, menus, loading
from .navmap.navmap import Navmap
from .merchant.merchant import Merchant
from .roster.roster import Roster
from ...windows.boxes.expandedmap import ExpandedMap
from ...windows.database.layout import Database


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

        # Tab widget

        self.tw = QtWidgets.QTabWidget(self.centralWidget)
        self.tw.setContentsMargins(0, 0, 0, 0)

        self.tabMap = self.addTab(navmap.layout.NavmapTab(self.tw), self.navmap)
        self.tabMer = self.addTab(merchant.layout.MerchantTab(self.tw), self.merchant)
        self.tabRoster = self.addTab(roster.layout.RosterTab(self.tw), self.roster)
        self.dbShortcut = self.addPseudoTab(Database)

        self.centralLayout.addWidget(self.tw)

        # Banner

        self.banner = banner.FlairBanner(self)

        # Menu bar

        menuBar = self.menuBar()
        menuBar.addMenu(menus.Utilities(menuBar))
        menuBar.addMenu(menus.File(menuBar))
        menuBar.addMenu(menus.Freelancer(menuBar))
        menuBar.addMenu(menus.Preferences(menuBar))
        menuBar.addMenu(menus.Help(menuBar))

        self.show()
        self.tw.currentChanged.emit(0)
        logging.info('Main window loaded')

        self.indicator = loading.Indicator(self.statusBar())

    def resizeEvent(self, event):
        """Ensure banner "sticks" to the top right of the window."""
        self.banner.updatePosition()

    def closeEvent(self, event):
        """Write config to disk on close."""
        config.commit()

    def addTab(self, page, load):
        """Add a tab page to the central tab widget. Tab page titles should include an ampersand to provide them with
        an Alt- hotkey. Returns the added page."""
        index = self.tw.addTab(page, page.icon, page.title)
        self.tw.setTabToolTip(index, page.tooltip)
        self.tw.currentChanged.connect(self.cueLazyLoadTab(page, load))
        return page

    def addPseudoTab(self, window: Type[Database]):
        """Add a "pseudo" tab to the central tab widget. Clicking on such a tab should open a new window rather than
        displaying something in the tab widget. Returns the shortcut created for the new tab."""
        index = self.tw.tabBar().addTab(f'&{window.title}')
        self.tw.setTabToolTip(index, f'{window.tooltip} (opens in a new window)')
        self.tw.setTabEnabled(index, False)  # display differently to "real" tabs
        self.tw.tabBarClicked.connect(lambda i: window().exec() if i == -1 else None)
        # spoof Alt- hotkey provided to "real" tabs
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(f'Alt+{window.title[0]}'), self)
        shortcut.activated.connect(lambda: self.tw.tabBarClicked.emit(-1))
        return shortcut

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
