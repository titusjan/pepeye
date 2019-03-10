""" 
    Main window functionality
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import cProfile
import logging
import os
import pstats
import sys

from .version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_URL, DEBUGGING
from .qt import Qt, QtCore, QtGui, QtWidgets, APPLICATION_INSTANCE

from .statstablemodel import StatsTableModel
from .togglecolumn import ToggleColumnTableView

logger = logging.getLogger(__name__)



def createBrowser(fileName = None, selfProfFile=None, **kwargs):
    """ Opens an MainWindow window
    """
    # Assumes qt.getQApplicationInstance() has been executed.
    browser = MainWindow(**kwargs)
    browser.show()

    if sys.platform.startswith('darwin'):
        browser.raise_()

    QtWidgets.QApplication.instance().processEvents()

    #profFileName = None

    if selfProfFile:
        profiler = cProfile.Profile()
        profiler.enable()

    if fileName is not None:
        browser.openStatsFile(fileName)

    if selfProfFile:
        logger.info("Saving profiling information to {}".format(selfProfFile))
        profStats = pstats.Stats(profiler)
        profStats.dump_stats(selfProfFile)

        QtWidgets.QApplication.instance().processEvents()
        sys.exit(3)

    return browser
        
        
def execute():
    """ Executes all browsers by starting the Qt main application
    """  
    logger.info("Starting the browser(s)...")
    app = APPLICATION_INSTANCE
    exit_code = app.exec_()
    logger.info("Browser(s) done...")
    return exit_code


def browse(fileName = None, **kwargs):
    """ Opens and executes a main window
    """
    _object_browser = createBrowser(fileName = fileName, **kwargs)
    exit_code = execute()
    return exit_code

        
# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 


class MainWindow(QtWidgets.QMainWindow):
    """ pepyeye main application window.
    """
    _nInstances = 0
    
    def __init__(self, reset = False):
        """ Constructor
            :param reset: If true the persistent settings, such as column widths, are reset. 
        """
        super(MainWindow, self).__init__()

        MainWindow._nInstances += 1
        self._InstanceNr = self._nInstances        
        
        # Model
        self._statsTableModel = StatsTableModel(parent=self, statsObject=None)
        #self._proxyTableModel = QtWidgets.QSortFilterProxyModel(parent = self)
        # self._proxyTableModel = StatsTableProxyModel(parent = self)
        # self._proxyTableModel.setSourceModel(self._statsTableModel)
        # self._proxyTableModel.setSortRole(StatsTableModel.SORT_ROLE)
        # self._proxyTableModel.setDynamicSortFilter(True)
        # self._proxyTableModel.setSortCaseSensitivity(Qt.CaseInsensitive)

        # Views
        self.__setupActions()
        self.__setupMenu()
        self.__setupViews()
        self.setWindowTitle("{}".format(PROGRAM_NAME))
        app = QtWidgets.QApplication.instance()
        app.lastWindowClosed.connect(app.quit) 

        self._readViewSettings(reset = reset)
            
        logger.debug("MainWindow constructor finished")
     

    def __setupActions(self):
        """ Creates the main window actions.
        """
        pass
                  
                              
    def __setupMenu(self):
        """ Sets up the main menu.
        """
        fileMenu = self.menuBar().addMenu("&File")
        openAction = fileMenu.addAction("&Open...", self.openStatsFile)
        openAction.setShortcut("Ctrl+O")
        fileMenu.addAction("C&lose", self.closeWindow, "Ctrl+W")
        fileMenu.addAction("E&xit", self.quitApplication, "Ctrl+Q")
        if DEBUGGING is True:
            fileMenu.addSeparator()
            fileMenu.addAction("&Test", self.myTest, "Ctrl+T")
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def __setupViews(self):
        """ Creates the UI widgets. 
        """
        #self.mainWidget = QtWidgets.QWidget(self)
        #self.setCentralWidget(self.mainWidget)
        
        self.mainSplitter = QtWidgets.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(self.mainSplitter)

        # Table view
        self.tableView = ToggleColumnTableView(self)
        #self.tableView.setModel(self._statsTableModel)
        self.tableView.setModel(self._statsTableModel)
        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(StatsTableModel.COL_CUM_TIME, Qt.DescendingOrder)
        self.tableView.setTextElideMode(Qt.ElideMiddle)
        self.tableView.setWordWrap(False)
        self.tableView.setShowGrid(False)
        self.tableView.setCornerButtonEnabled(False)
        #self.tableView.verticalHeader().hide()
        #self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # needed?
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.addHeaderContextMenu(enabled = {'function': False}, checked = {})

        # Set font so that all table cells have the same font size (was not the case one Windows 10)
        font = QtGui.QFont()
        if sys.platform == 'linux':
            pixelSize = 10
        elif sys.platform == 'win32' or sys.platform == 'cygwin':
            pixelSize = 13
        elif sys.platform == 'darwin':
            pixelSize = 13
        else:
            pixelSize = 13

        font.setPixelSize(pixelSize)
        self.tableView.setFont(font)

        self.mainSplitter.addWidget(self.tableView)
        
        tableHorHeader = self.tableView.horizontalHeader()
        tableHorHeader.setSectionsMovable(True)
        tableHorHeader.setTextElideMode(Qt.ElideMiddle)
        tableHorHeader.setStretchLastSection(False)
        
        tableVerHeader = self.tableView.verticalHeader()
        tableVerHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        self.label = QtWidgets.QLabel("Hi there", parent=self)
        self.mainSplitter.addWidget(self.label)
        
        # Connect signals
        pass

    # End of setup_methods
    
    def loadStatsFile(self, fileName):
        """ Loads a pstats file and updates the table model
        """
        logger.debug("Loading file: {}".format(fileName))
        self.setWindowTitle("{} -- {}".format(os.path.basename(fileName), PROGRAM_NAME))
        pStats = pstats.Stats(fileName)
        self._statsTableModel.setStats(statsObject=pStats)
        #pStats.strip_dirs()
        #pStats.calc_callees()
        

    def openStatsFile(self, fileName=None):
        """ Lets the user select a pstats file and opens it.
        """
        if not fileName:
            fileName = QtWidgets.QFileDialog.getOpenFileName(self,
                caption = "Choose a pstats file", directory = '', 
                filter='All files (*);;Profile statistics (*.prof; *.pro)')
            fileName = fileName[0]

        if fileName:
            logger.info("Loading data from: {!r}".format(fileName))
            try:
                self.loadStatsFile(fileName)
            except Exception as ex:
                if DEBUGGING:
                    raise
                else:
                    logger.error("Error opening file: %s", ex)
                    QtWidgets.QMessageBox.warning(self, "Error opening file", str(ex))
    
    
    def _settingsGroupName(self, prefix):
        """ Creates a setting group name based on the prefix and instance number
        """
        settingsGroup = "window{:02d}-{}".format(self._InstanceNr, prefix)
        logger.debug("  settings group is: {!r}".format(settingsGroup))
        return settingsGroup    
        
    
    def _readViewSettings(self, reset=False):
        """ Reads the persistent program settings
        
            :param reset: If True, the program resets to its default settings
        """ 
        pos = QtCore.QPoint(20 * self._InstanceNr, 20 * self._InstanceNr)
        windowSize = QtCore.QSize(1024, 700)
        
        if reset:
            logger.debug("Resetting persistent view settings")
        else:
            logger.debug("Reading view settings for window: {:d}".format(self._InstanceNr))
            settings = QtCore.QSettings()
            settings.beginGroup(self._settingsGroupName('view'))
            pos = settings.value("main_window/pos", pos)
            windowSize = settings.value("main_window/size", windowSize)
            splitter_state = settings.value("main_splitter/state")
            if splitter_state:
                self.mainSplitter.restoreState(splitter_state)
            self.tableView.readViewSettings('table/header_state', settings, reset) 
            settings.endGroup()
            
        logger.debug("windowSize: {!r}".format(windowSize))
        self.resize(windowSize)
        self.move(pos)


    def _writeViewSettings(self):
        """ Writes the view settings to the persistent store
        """         
        logger.debug("Writing view settings for window: {:d}".format(self._InstanceNr))
        
        settings = QtCore.QSettings()
        settings.beginGroup(self._settingsGroupName('view'))
        self.tableView.writeViewSettings("table/header_state", settings)
        settings.setValue("main_splitter/state", self.mainSplitter.saveState())        
        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.endGroup()
            

    def myTest(self):
        """ Function for testing """
        logger.debug("myTest")
        logger.debug("row height: {}".format(self.tableView.rowHeight(0)))
        
    def about(self):
        """ Shows the about message window. """
        message = u"{} version {}\n\n{}""".format(PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_URL)
        QtWidgets.QMessageBox.about(self, "About {}".format(PROGRAM_NAME), message)

    def closeWindow(self):
        """ Closes the window """
        self.close()
        
    def quitApplication(self):
        """ Closes all windows """
        app = QtWidgets.QApplication.instance()
        app.closeAllWindows()

    def closeEvent(self, event):
        """ Close all windows (e.g. the L0 window).
        """
        logger.debug("closeEvent")
        self._writeViewSettings()
        self.close()
        event.accept()
            

