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
from collections import defaultdict
import os
from functools import partial

from PyQt5 import QtWebEngineWidgets, QtCore, QtWidgets, QtGui
import flint as fl

from ..buttons import SquareButton
from ... import config, icons, NAVMAP_DIR


class MapView(QtWebEngineWidgets.QWebEngineView):
    """A widget that attempts to display Space's Online Navmap <http://space.discoverygc.com/navmap/> in such a way
    that it is seamlessly integrated into the native application."""
    navmapReady = QtCore.pyqtSignal()  # emitted once the navmap is fully initialised
    displayChanged = QtCore.pyqtSignal(str)  # emitted when the displayed nickname changes

    def __init__(self, parent=None, url=config.navmap):
        """Initialise the widget."""
        super().__init__(parent)

        self.setMinimumSize(512, 512)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                 QtWidgets.QSizePolicy.MinimumExpanding))

        # set a placeholder page while the navmap loads
        # interestingly adding or omitting !r (repr) from the colour changes what gets displayed
        self.setHtml(f'<body style="background-color: {self.getBackgroundColour().name()}"></body>')

        # load the real page
        self.mainPage = self.createPage(url)
        self.waitForHookLoaded()  # todo: try to do this asynchronously

        # create control panel
        self.controlsFrame = QtWidgets.QFrame(self)
        self.controlsFrame.setMinimumHeight(135)
        controlsLayout = QtWidgets.QVBoxLayout(self.controlsFrame)
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        controlsLayout.setSpacing(5)
        self.connInfoB = SquareButton(icon=icons.jump, tooltip='Connected systems')
        controlsLayout.addWidget(self.connInfoB)
        self.forwardB = SquareButton(icon=icons.right, tooltip='Forward')
        self.forwardB.clicked.connect(self.goForward)
        controlsLayout.addWidget(self.forwardB)
        self.backB = SquareButton(icon=icons.left, tooltip='Back')
        self.backB.clicked.connect(self.goBack)
        controlsLayout.addWidget(self.backB)
        self.expandB = SquareButton(icon=icons.expand, tooltip='Show expanded map')
        controlsLayout.addWidget(self.expandB)
        self.controlsFrame.setLayout(controlsLayout)
        self.controlsFrame.show()
        self.controlsFrame.lower()

        # create context menu
        self.menu = QtWidgets.QMenu()
        self.showLabels = QtWidgets.QAction('Show labels', checkable=True, checked=True)
        self.showLabels.toggled.connect(partial(self.setState, 'wingman.showLabels'))
        self.showZones = QtWidgets.QAction('Show nebulae', checkable=True, checked=True)
        self.showZones.toggled.connect(partial(self.setState, 'wingman.showZones'))
        self.showWrecks = QtWidgets.QAction('Show wrecks', checkable=True, checked=True)
        self.showWrecks.toggled.connect(partial(self.setState, 'wingman.showWrecks'))

        self.menu.addActions([self.showLabels, self.showWrecks, self.showZones])
        self.menu.addAction('Save map as image').triggered.connect(self.saveAsImage)

        # configure settings
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.SpatialNavigationEnabled, True)
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)

        # initialise history
        self.backStack = []
        self.forwardsStack = []

    def onHookLoaded(self):
        """After the hook has been loaded, perform final modifications to the navmap, make any necessary connections
        and signal that the navmap is fully ready."""
        self.setPage(self.mainPage)
        self.page().runJavaScript(f'wingman.setBackgroundColour({self.getBackgroundColour().name()!r})')

        self.history().clear()  # a fresh start is always nice!
        self.controlsFrame.raise_()
        self.urlChanged.connect(self.onUrlChange)
        self.navmapReady.emit()

    def onUrlChange(self):
        """Handle a URL change. Wait for the variable to set, then emit loadCompleted."""
        self.page().runJavaScript('wingman.onDisplayChanged()')
        # update state of forward/backward navigation buttons and history queue
        if self.getDisplayed() and '_' not in self.getDisplayed():
            if not self.backStack or self.getDisplayed() != self.backStack[-1]:
                self.backStack.append(self.getDisplayed())

        self.backB.setEnabled(bool(len(self.backStack) - 1))
        self.forwardB.setEnabled(bool(self.forwardsStack))

        # get the nickname of the currently displayed entity and emit displayChanged
        self.page().runJavaScript('currentSystemNickname', self.emitDisplayChanged)

    def displayEntity(self, entity: fl.entities.Entity):
        """Change the displayed object (system or solar) to the given item."""
        self.displayName(entity.name())

    def displayName(self, name: str):
        """Attempt to display a map for `entityName`."""
        self.page().runJavaScript(f'wingman.displayMap({name.title()!r})')

    def displayUniverse(self):
        """Display universe map."""
        self.page().runJavaScript("wingman.displayUniverseMap()")

    def getDisplayed(self):
        """Parse URL to resolve selected object (system/base/planet) name, or 'Sirius' if the universe map is
        displayed. """
        fragment = self.url().fragment().split('&')[0]
        return fragment.replace('%20', ' ')[2:].title().replace('%27', "'") if fragment else 'Sirius'

    def setDisplayed(self, entityName):
        """Set the URL fragment to the display name of an entity, causing it to be displayed (assuming it is in the
        navmap's search array. This is useful for guaranteeing a display update, for example if Wingman's hook may have
        not loaded yet."""
        url = self.url()
        query, noClick = list(url.fragment().split('&'))
        url.setFragment(f'q={entityName}&{noClick}')
        self.setUrl(url)
        self.onUrlChange()

    def emitDisplayChanged(self, newNickname: str):
        """Emit displayChanged if required."""
        try:
            if newNickname != 'Sirius':
                self.displayChanged.emit(newNickname)
        except RuntimeError:  # thrown if process is killed
            return

    def setState(self, selector: str, state: bool):
        """Set the state of a switch in the navmap using its selector."""
        self.page().runJavaScript(f'wingman.setState({selector}, {str(state).lower()})')

    def displayConnMenu(self, forSystem: fl.entities.System):
        """Add a menu of connected systems, sorted by system name. Clicking on these systems will display that
        system."""
        menu = QtWidgets.QMenu()
        menu.setToolTipsVisible(True)

        # group jumps by system
        connections = defaultdict(list)
        for jump, system in forSystem.connections().items():
            connections[system].append(jump)

        for system, jumps in sorted(connections.items(), key=lambda s_j: s_j[0].name()):
            action = menu.addAction(f'{system.name()} ({", ".join(j.type() for j in jumps)})')
            action.triggered.connect(lambda _, system=system: self.displayEntity(system))
            action.setToolTip(", ".join(j.sector() for j in jumps))
        self.connInfoB.setMenu(menu)

    def saveAsImage(self):
        """Show a dialogue allowing the user to save the currently displayed map as a PNG image."""
        defaultPath = os.path.expanduser('~/{}.png').format(self.getDisplayed())
        path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     'Save map as image',
                                                     defaultPath,
                                                     'Portable Network Graphics image (*.png)')[0]

        # draw the image, hiding the controls and restoring them afterwards
        # consider also temporarily setting the background to colour of forums (#090909) so it blends in well
        self.controlsFrame.hide()

        image = QtGui.QImage(self.geometry().width(), self.geometry().height(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter()
        painter.begin(image)
        self.render(painter)
        painter.end()

        self.controlsFrame.show()

        if path:
            image.save(path)

    def contextMenuEvent(self, event):
        """Provides a context menu that contains options to change the display settings of the map and save it as an
        image."""
        self.menu.exec(self.mapToGlobal(QtCore.QPoint(event.pos())))

    def resizeEvent(self, event):
        """Handle a resize event so that the widget stays square."""
        self.setFixedWidth(self.height())
        self.controlsFrame.move(self.width() - 30, 0)  # keep controls stuck to top right

    def waitForHookLoaded(self, wingman=None):
        """Block until the hook has been loaded."""
        if wingman is None:
            try:
                self.mainPage.runJavaScript('try {wingman} catch(error) {null}', self.waitForHookLoaded)
            except RuntimeError:  # thrown if process is killed
                return
        else:
            self.onHookLoaded()

    def goForward(self):
        """Go forwards in history."""
        self.backStack.append(self.getDisplayed())
        self.displayName(self.forwardsStack.pop())

    def goBack(self):
        """Go backwards in history."""
        self.forwardsStack.append(self.getDisplayed())
        self.backStack.pop()
        self.displayName(self.backStack.pop())

    def getBackgroundColour(self) -> QtGui.QColor:
        """Get the background colour of this widget's parent, or failing that, a generic QWidget.

        This is only an approximation as the "backgroundRole" colour of a widget may not be its actual, displayed
        colour (see <https://stackoverflow.com/a/23020483>)."""
        backgroundWidget = self.parentWidget() if self.parentWidget() else QtWidgets.QWidget()
        return backgroundWidget.palette().color(backgroundWidget.backgroundRole())

    @classmethod
    def createPage(cls, navmapUrl: str) -> QtWebEngineWidgets.QWebEnginePage:
        """Create the main page for the application, displaying a suitably modified Online Navmap."""
        page = QtWebEngineWidgets.QWebEnginePage()
        page.profile().setCachePath(NAVMAP_DIR)  # link cache directory
        page.setUrl(QtCore.QUrl(navmapUrl))

        hookSource = cls.getHookSource()
        # create and inject script
        script = QtWebEngineWidgets.QWebEngineScript()
        script.setSourceCode(hookSource)
        script.setName('navmap.js')
        script.setWorldId(QtWebEngineWidgets.QWebEngineScript.MainWorld)
        script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
        page.scripts().insert(script)

        return page

    @classmethod
    def getHookSource(cls) -> str:
        """Load custom JavaScript from resources, or from a file if it exists (useful for debugging)."""
        if os.path.isfile(cls.JS_DEV_PATH):
            return open(cls.JS_DEV_PATH).read()

        file = QtCore.QFile(cls.JS_RESOURCE)
        if file.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text):
            return QtCore.QTextStream(file).readAll()
        raise FileNotFoundError("MapView: couldn't load hook source")

    JS_DEV_PATH = './widgets/mapview/navmap.js'
    JS_RESOURCE = ':/javascript/navmap.js'
