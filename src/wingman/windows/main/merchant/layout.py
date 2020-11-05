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
from PyQt5 import QtCore, QtWidgets

from ....widgets import buttons
from .... import icons

from ....widgets.simpletable import SimpleTable


class MerchantTab(QtWidgets.QWidget):
    """Defines the layout of the merchant tab."""
    title = 'Merchant'
    icon = icons.merchant

    def __init__(self, parent: QtWidgets.QTabWidget):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.tableLayout = QtWidgets.QVBoxLayout()
        self.controlsLayout = QtWidgets.QHBoxLayout()
        self.originLabel = QtWidgets.QLabel('Origin', self)
        self.controlsLayout.addWidget(self.originLabel)

        self.originSelector = QtWidgets.QComboBox(self)
        self.originSelector.setToolTip('Origin system')
        self.originSelector.setEditable(True)
        self.originSelector.setMinimumHeight(30)
        self.controlsLayout.addWidget(self.originSelector)

        self.originMapButton = buttons.UniverseMapButton(self)
        self.controlsLayout.addWidget(self.originMapButton)

        self.controlsLayout.addSpacing(25)
        self.swapButton = buttons.SquareButton(parent=self, icon=icons.swap, tooltip='Swap systems')
        self.swapButton.setToolTip('Swap systems')
        self.controlsLayout.addWidget(self.swapButton)

        self.controlsLayout.addSpacing(25)

        self.destinationLabel = QtWidgets.QCheckBox('Destination', self)
        self.controlsLayout.addWidget(self.destinationLabel)

        self.destinationSelector = QtWidgets.QComboBox(self)
        self.destinationSelector.setToolTip('Destination system')  # todo make this combobox a widget
        self.destinationSelector.setEditable(True)
        self.destinationSelector.setEnabled(False)
        self.destinationSelector.lineEdit().setPlaceholderText('Anywhere')
        self.destinationSelector.setMinimumHeight(30)
        self.controlsLayout.addWidget(self.destinationSelector)

        self.destinationMapButton = buttons.UniverseMapButton(self)
        self.controlsLayout.addWidget(self.destinationMapButton)

        self.controlsLayout.addSpacing(40)

        self.advancedButton = QtWidgets.QPushButton('Advanced')
        self.advancedButton.setCheckable(True)
        self.controlsLayout.addWidget(self.advancedButton)

        self.controlsLayout.setStretch(1, 1)
        self.controlsLayout.setStretch(7, 1)
        self.tableLayout.addLayout(self.controlsLayout)

        # "additional controls" - since we want to selectively show/hide this layout it needs to be given a QWidget
        self.advancedControls = QtWidgets.QWidget()
        self.advancedControlsLayout = QtWidgets.QHBoxLayout()
        self.advancedControls.setLayout(self.advancedControlsLayout)

        self.contrabandCheck = QtWidgets.QCheckBox('Include contraband')
        self.advancedControlsLayout.addWidget(self.contrabandCheck)

        self.reputationLabel = QtWidgets.QCheckBox('Dockable by:')
        self.advancedControlsLayout.addWidget(self.reputationLabel)

        self.reputationSelector = QtWidgets.QComboBox()
        self.reputationSelector.setEnabled(False)
        self.reputationLabel.toggled.connect(self.reputationSelector.setEnabled)
        self.advancedControlsLayout.addWidget(self.reputationSelector)

        self.advancedControlsLayout.setAlignment(QtCore.Qt.AlignRight)

        self.tableLayout.addWidget(self.advancedControls)

        # button controls visibility; hidden by default
        self.advancedControls.hide()
        self.advancedButton.toggled.connect(self.advancedControls.setVisible)

        self.mainTable = SimpleTable(['Origin base', 'Origin system', 'Destination base', 'Destination system',
                                      'Commodity', 'Credits/unit'])
        self.mainTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableLayout.addWidget(self.mainTable)

        self.mainLayout.addLayout(self.tableLayout)

        self.infoLayout = QtWidgets.QVBoxLayout()
        self.infoLayout.setAlignment(QtCore.Qt.AlignHCenter)

        # a label which displays a commodity icon
        self.infoIcon = QtWidgets.QLabel()
        self.infoIcon.setFixedSize(128, 128)
        self.infoIcon.setScaledContents(True)
        self.infoIcon.setAlignment(QtCore.Qt.AlignCenter)
        self.infoLayout.addWidget(self.infoIcon, QtCore.Qt.AlignHCenter)

        self.infoNameLabel = QtWidgets.QLabel()
        self.infoNameLabel.setMaximumWidth(128)
        self.infoNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.infoNameLabel.setTextFormat(QtCore.Qt.RichText)
        self.infoNameLabel.setWordWrap(True)
        self.infoLayout.addWidget(self.infoNameLabel)

        self.infoBuyLabel = QtWidgets.QLabel()
        self.infoBuyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.infoBuyLabel.setTextFormat(QtCore.Qt.RichText)
        self.infoBuyLabel.setWordWrap(True)
        self.infoLayout.addWidget(self.infoBuyLabel)

        self.infoSellLayout = QtWidgets.QLabel()
        self.infoSellLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.infoSellLayout.setTextFormat(QtCore.Qt.RichText)
        self.infoSellLayout.setWordWrap(True)
        self.infoLayout.addWidget(self.infoSellLayout)
        self.infoLayout.addStretch(1)

        self.infoDivider = QtWidgets.QFrame()
        self.infoDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.infoLayout.addWidget(self.infoDivider)

        self.infoRouteLabel = QtWidgets.QLabel('Route')
        self.infoRouteLabel.setMaximumWidth(128)
        self.infoRouteLabel.setWordWrap(True)
        self.infoLayout.addWidget(self.infoRouteLabel)

        self.mainLayout.addLayout(self.infoLayout)
