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
from typing import Tuple, Optional
from collections import defaultdict

from PyQt5 import QtCore, QtGui, QtWidgets
import flint as fl

from .... import config, icons
from ...boxes import expandedmap
from ....models import items, selectors
from .layout import MerchantTab
from ..navmap.navmap import Navmap


class Merchant:
    """Implements the 'Merchant' tab's behaviour."""

    def __init__(self, widget: MerchantTab, expandedMap: expandedmap.ExpandedMap, navmap: Navmap):
        # initialise Merchant tab
        self.config = config['merchant']
        self.widget = widget
        self.expandedMap = expandedMap
        self.navmap = navmap
        self.lastDestination: Optional[fl.entities.System] = None

        # create models
        systemsModel = selectors.SystemSelectionModel()
        self.widget.originSelector.setModel(systemsModel)
        self.widget.originMapButton.clicked.connect(lambda:
                                                    self.openUniverseMap(self.widget.originSelector))
        self.widget.destinationSelector.setModel(systemsModel)
        self.widget.destinationMapButton.clicked.connect(lambda:
                                                         self.openUniverseMap(self.widget.destinationSelector))

        self.widget.reputationSelector.setModel(selectors.FactionSelectionModel())

        # connections
        self.widget.originSelector.currentIndexChanged.connect(self.display)
        self.widget.destinationLabel.toggled.connect(self.onDestinationToggled)
        self.widget.destinationSelector.currentIndexChanged.connect(self.display)
        self.widget.reputationLabel.clicked.connect(self.display)
        self.widget.reputationSelector.currentIndexChanged.connect(self.display)
        self.widget.swapButton.clicked.connect(self.swapSystems)

        # customise table and model
        self.widget.mainTable.selectionModel().selectionChanged.connect(self.onSelectedRowChanged)

        # finally, display last settings
        self.selectedSystems = \
            (items.fl.systems.get(self.config['lastOrigin']), items.fl.systems.get(self.config['lastDestination']))

    def openUniverseMap(self, selector: QtWidgets.QComboBox):
        """Open the universe map, passing its choice to the given combo box."""
        self.expandedMap.displayUniverse()
        self.expandedMap.displayChanged.connect(lambda n:
                                                selector.setCurrentIndex(selector.findData(items.fl.systems[n])))

    def onDestinationToggled(self, toggled: bool):
        """Handle the specific destination check box being toggled."""
        self.widget.destinationSelector.setEnabled(toggled)
        self.widget.destinationMapButton.setEnabled(toggled)
        if not toggled:
            self.lastDestination = self.widget.destinationSelector.currentData()
            self.widget.destinationSelector.setCurrentIndex(-1)
        elif self.lastDestination:
            self.widget.destinationSelector.setCurrentIndex(
                self.widget.destinationSelector.findData(self.lastDestination))
        self.display()

    def onSelectedRowChanged(self, selected, deselected):
        """Handle the table's selected row being changed."""
        if not selected.indexes():
            return
        originBase, originSystem, destinationBase, destinationSystem, commodity, profit = \
            (item.data(QtCore.Qt.UserRole) for item in selected.indexes())

        # display commodity icon
        self.updateInfoPanel(profit)

        # display commodity name
        links = []
        for system in items.fl.maps.inter_system_route(originBase.system(), destinationBase.system()):
            links.append(f'<a href="{system.nickname}">{system.name()}</a>')
        self.widget.infoRouteLabel.setText('Route: ' + ', '.join(links))
        self.widget.infoRouteLabel.linkActivated.connect(lambda n: self.navmap.showFromExternal(items.fl.systems[n]))

    def updateInfoPanel(self, data: items.ProfitItem.ProfitData):
        """Update the info side panel."""
        self.widget.infoIcon.setPixmap(icons.loadTGA(data.commodity.icon()))  # update commodity icon

        # update labels
        self.widget.infoNameLabel.setText(f'<b>{data.commodity.name()}</b>')
        self.widget.infoBuyLabel.setText(f'<b>Buy: ${data.buyPrice:,}</b><br/>{data.buyBase.name()}')
        self.widget.infoSellLayout.setText(f'<b>Sell: ${data.sellPrice:,}</b><br/>{data.sellBase.name()}')

    def display(self):
        """Display a table of the best commodities to take to and from the selected systems."""
        originSystem = self.widget.originSelector.itemData(self.widget.originSelector.currentIndex())
        destinationSystem = self.widget.destinationSelector.itemData(self.widget.destinationSelector.currentIndex()) \
            if self.widget.destinationLabel.isChecked() else None
        iff = self.widget.reputationSelector.itemData(self.widget.reputationSelector.currentIndex()) \
            if self.widget.reputationLabel.isChecked() else None

        self.widget.swapButton.setEnabled(bool(destinationSystem))

        data = self.calculateRoutes(originSystem, destinationSystem, iff)
        self.widget.mainTable.populate(list(data))
        self.widget.mainTable.sortByColumn(5, QtCore.Qt.DescendingOrder)  # sort by 'credits/unit' column
        self.widget.mainTable.selectRow(0)

        self.config['lastOrigin'] = originSystem.nickname
        self.config['lastDestination'] = destinationSystem.nickname if destinationSystem else ''

    def swapSystems(self):
        """Swap the currently selected origin and destination systems."""
        self.selectedSystems = reversed(self.selectedSystems)

    @property
    def selectedSystems(self) -> Tuple[fl.entities.System, fl.entities.System]:
        """Return the entities of the selected origin and destination system, respectively."""
        return self.widget.originSelector.currentData(), self.widget.destinationSelector.currentData()

    @selectedSystems.setter
    def selectedSystems(self, newSystems: Tuple[items.fl.entities.System, items.fl.entities.System]):
        """Set the selected origin and destination system."""
        origin, destination = newSystems
        if origin:
            self.widget.originSelector.setCurrentIndex(self.widget.originSelector.findData(origin))
        if destination:
            self.widget.destinationSelector.setCurrentIndex(self.widget.destinationSelector.findData(destination))
        else:
            self.widget.destinationSelector.setCurrentText('')

    @staticmethod
    def calculateRoutes(origin: items.fl.entities.System, destination: items.Optional[items.fl.entities.System] = None,
                        iff: items.Optional[items.fl.entities.Faction] = None):
        """Calculate the optimum commodities to trade between system A (`origin`) and system B (`destination`).
        The latter is optional; if it is not provided the function will return the optimum commodities to buy in
        system A and sell at any location. The optional `iff` parameter allows the bases to be searched to be restricted
        to those dockable by that faction."""
        originSells = defaultdict(list)
        for base in origin.bases():
            if iff and not iff.can_dock_at(base):
                continue
            for good, price in base.universe_base().sells().items():
                originSells[good].append((price, base))

        if destination:
            destinationBases = destination.bases()
        else:
            destinationBases = {b for s in items.fl.systems for b in s.bases()}

        destBuys = defaultdict(list)
        for base in destinationBases:
            if iff and not iff.can_dock_at(base):
                continue
            for good, price in base.universe_base().buys().items():
                destBuys[good].append((price, base))

        for good in originSells:  # for each commodity that are sold in the origin system
            if good not in destBuys:  # if somewhere buys the commodity in the destination
                continue
            for destPrice, destBase in destBuys[good]:  # look through each base in destination
                for originPrice, originBase in originSells[good]:  # look through each base in origin
                    if destPrice > originPrice:
                        yield [items.BaseItem(originBase), items.SystemItem(originBase.system()),
                               items.BaseItem(destBase), items.SystemItem(destBase.system()),
                               items.CommodityItem(good.commodity()),
                               items.ProfitItem(originPrice, originBase, destPrice, destBase, good.commodity())]
