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


from ... import icons, __app__, __version__, __description__


class About(QtWidgets.QDialog):
    """The "About" message box."""
    title = 'About'
    vMargin = 30
    hMargin = 80

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.title)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.mainLayout.setContentsMargins(QtCore.QMargins(self.hMargin, self.vMargin, self.hMargin, self.vMargin))

        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setPixmap(icons.main.pixmap(128, 128))
        self.iconLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.mainLayout.addWidget(self.iconLabel, QtCore.Qt.AlignHCenter)

        self.titleLabel = QtWidgets.QLabel(f'<html><h1>{__app__} {__version__}</h1></html>')
        self.mainLayout.addWidget(self.titleLabel, QtCore.Qt.AlignHCenter)
        self.mainLayout.setAlignment(self.titleLabel, QtCore.Qt.AlignHCenter)

        self.blurbLabel = QtWidgets.QLabel(f'<html><h3>{__description__}</h3></html>')
        self.mainLayout.addWidget(self.blurbLabel, QtCore.Qt.AlignHCenter)
        self.mainLayout.setAlignment(self.blurbLabel, QtCore.Qt.AlignHCenter)

        self.authorLabel = QtWidgets.QLabel('<html><h4>made with ❤ by <a href="'
                                            'https://discoverygc.com/forums/member.php?action=profile&uid=32907">'
                                            'Biggles</a> (<a href="https://github.com/biqqles">biqqles</a>)'
                                            '</h4></html>')
        self.authorLabel.setOpenExternalLinks(True)
        self.mainLayout.addWidget(self.authorLabel, QtCore.Qt.AlignHCenter)
        self.mainLayout.setAlignment(self.authorLabel, QtCore.Qt.AlignHCenter)

        self.mainLayout.addStretch(40)

        self.licenceLabel = QtWidgets.QLabel('<html>This application is free software, released under the '
                                             '<a href="https://gnu.org/licenses/gpl.html">GNU General Public License '
                                             'v3.0</a> as is and with absolutely no warranty whatsoever.</html>')
        self.licenceLabel.setWordWrap(True)
        self.licenceLabel.setOpenExternalLinks(True)
        self.mainLayout.setAlignment(self.licenceLabel, QtCore.Qt.AlignCenter)
        self.mainLayout.addWidget(self.licenceLabel, QtCore.Qt.AlignHCenter)

        self.thanksLabel = QtWidgets.QLabel(
            '<html><h4>With thanks to:</h4><ul>'
            '<li><a href="'
            'https://discoverygc.com/forums/member.php?action=profile&uid=4734">Error</a> for the use of their '
            '<a href="https://github.com/AudunVN/Navmap">Online Navmap</a></li>'
            '<li>Icons made by:<ul>'
            '<li><a href="https://www.flaticon.com/authors/freepik">Freepik</a> from '
            '<a href="https://www.flaticon.com">www.flaticon.com</a></li>'
            '<li><a href="https://www.flaticon.com/authors/roundicons">Roundicons</a> from '
            '<a href="https://www.flaticon.com">www.flaticon.com</a></li>'
            '<li><a href="https://www.flaticon.com/authors/neungstockr">neungstockr</a> from '
            '<a href="https://www.flaticon.com">www.flaticon.com</a>.</li></ul></li>'
            '<li>See also the acknowledgements for <a href="https://github.com/biqqles/flair">flair</a> and '
            '<a href="https://github.com/biqqles/flint">flint</a>.</li>'
            '</ul></html>')
        self.thanksLabel.setOpenExternalLinks(True)
        self.mainLayout.addWidget(self.thanksLabel, QtCore.Qt.AlignHCenter)
