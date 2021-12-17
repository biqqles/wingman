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

This file defines the behaviour of the Navmap tab.
"""
from PyQt5 import QtCore, QtWidgets
import flint as fl

from .... import config, IS_WIN
from ....widgets import mapview
from ...boxes import expandedmap
from .layout import NavmapTab

if IS_WIN:
    import flair


class Navmap:
    """Implements the 'Navmap' tab."""
    def __init__(self, widget: NavmapTab, expandedMap: expandedmap.ExpandedMap):
        """Initialise tab"""
        self.widget = widget
        self.expandedMap = expandedMap

        self.mapView: mapview.MapView = self.widget.navmap
        self.tabWidget: QtWidgets.QTabWidget = self.widget.parent().parent()

        self.config = config['navmap']

        self.searchableEntities = fl.systems + fl.bases
        self.currentSystem = fl.systems.get(self.config['last']) or fl.systems['li01']

        # set up search field with completer
        completer = QtWidgets.QCompleter()
        completer.setModel(QtCore.QStringListModel(e.name() for e in self.searchableEntities))
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setWrapAround(True)
        self.widget.searchEdit.setCompleter(completer)

        # connections
        self.mapView.displayChanged.connect(self.onDisplayChange)
        self.widget.searchEdit.textEdited.connect(self.onSearchTextEdited)
        # textEdited is only emitted on user input, but completer counts as programmatic
        completer.activated.connect(self.onSearchTextEdited)
        completer.highlighted.connect(self.onSearchTextEdited)
        # navmap buttons
        self.mapView.backButton.clicked.connect(self.widget.gotoRadioButton.click)
        self.mapView.forwardButton.clicked.connect(self.widget.gotoRadioButton.click)
        self.mapView.expandButton.clicked.connect(self.displayExpandedMap)
        self.widget.universeButton.clicked.connect(self.displayUniverseMap)

        self.mapView.navmapReady.connect(lambda: self.mapView.setDisplayed(self.currentSystem.name()))
        self.onDisplayChange(self.currentSystem.nickname)

        if IS_WIN:
            self.widget.followRadioButton.setEnabled(flair.state.running)
            flair.events.freelancer_started.connect(lambda: self.widget.followRadioButton.setEnabled(True))
            flair.events.freelancer_started.connect(lambda: self.widget.followRadioButton.setChecked(True))
            flair.events.freelancer_stopped.connect(lambda: self.widget.followRadioButton.setEnabled(False))
            flair.events.freelancer_stopped.connect(lambda: self.widget.gotoRadioButton.setChecked(True))
            flair.events.system_changed.connect(self.onFlairSystemChanged)
            self.widget.followRadioButton.toggled.connect(self.onFollowModeEnabled)

    def onDisplayChange(self, nickname):
        """Handle the mapview changing."""
        entity = self.searchableEntities.get(nickname)
        self.widget.infocard.setInfocard(nickname, entity)

        if entity:
            self.widget.searchEdit.setText(entity.name())  # update search field
        if isinstance(entity, fl.entities.System):
            self.searchableEntities += entity.contents()  # load system contents
            self.mapView.displayConnMenu(entity)
            self.currentSystem = entity
            self.config['last'] = nickname

    def onSearchTextEdited(self, query: str):
        """Handle the search field's text being edited by the user."""
        self.widget.gotoRadioButton.setChecked(True)
        self.mapView.displayName(query)

    def onFollowModeEnabled(self):
        """Handle follow mode being enabled."""
        if flair.state.system is not None:
            self.mapView.displayName(flair.state.system)

    def onFlairSystemChanged(self, system: str):
        """Handle a system_changed event from flair."""
        if self.widget.followRadioButton.isChecked():
            self.mapView.displayName(system)

    def displayExpandedMap(self):
        """Display an expanded map of the current system."""
        self.expandedMap.displayEntity(self.currentSystem)

    def displayUniverseMap(self):
        """Display an expanded universe map. Selecting a system will display it in the main navmap."""
        self.expandedMap.displayUniverse(highlightedSystem=self.currentSystem.nickname)
        self.expandedMap.displayChanged.connect(lambda n: self.mapView.displayEntity(fl.systems[n]))
        self.widget.gotoRadioButton.setChecked(True)

    def showFromExternal(self, entity: fl.entities.Entity):
        """Switch to the Navmap tab and show `entity` on the map."""
        self.mapView.displayEntity(entity)
        self.tabWidget.setCurrentWidget(self.widget)
        self.widget.activateWindow()
