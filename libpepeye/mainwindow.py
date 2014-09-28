""" 
    Quick Analysis Tool 2

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import logging, sys

from .version import PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_URL, DEBUGGING, USE_PYQT
from .utils import check_class

if USE_PYQT:
    from PyQt4 import QtCore, QtGui
else:
    from PySide import QtCore, QtGui

logger = logging.getLogger(__name__)



def loggingBasicConfig(level = 'WARN'):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)


def getQApplicationInstance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()

    if app is None:
        app = QtGui.QApplication(sys.argv)
    check_class(app, QtGui.QApplication)
    
    app.setApplicationName(PROGRAM_NAME)
    app.setApplicationVersion(PROGRAM_VERSION)
    app.setOrganizationName("titusjan")
    app.setOrganizationDomain("titusjan.nl")    
    
    return app


def createBrowser(*args, **kwargs):
    """ Opens an OjbectBrowser window
    """
    app = getQApplicationInstance()
    browser = MainWindow(*args, **kwargs)
    browser.show()
    return browser, app # TODO: make qt stuff module
        
        
def execute():
    """ Executes all browsers by starting the Qt main application
    """  
    logger.info("Starting the browser(s)...")
    app = getQApplicationInstance()
    exit_code = app.exec_()
    logger.info("Browser(s) done...")
    return exit_code


def browse(*args, **kwargs):
    """ Opens and executes a browser window
    """
    _object_browser, _app = createBrowser(*args, **kwargs)
    exit_code = execute()
    return exit_code
    

        
# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201 


class MainWindow(QtGui.QMainWindow):
    """ QAT main application window.
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
        pass

        # Views
        self.__setupActions()
        self.__setupMenu()
        self.__setupViews()
        self.setWindowTitle("{}".format(PROGRAM_NAME))
        app = QtGui.QApplication.instance()
        app.lastWindowClosed.connect(app.quit) 

        self._readViewSettings(reset = reset) # TODO: enable
        
        # Update views with model
        pass
    
        logger.debug("MainWindow constructor finished")
     

    def __setupActions(self):
        """ Creates the main window actions.
        """
        pass
                              
                              
    def __setupMenu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("C&lose", self.closeWindow, "Ctrl+W")
        file_menu.addAction("E&xit", self.quitApplication, "Ctrl+Q")
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.myTest, "Ctrl+T")
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def __setupViews(self):
        """ Creates the UI widgets. 
        """
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        
        # Connect signals
        pass

    # End of setup_methods
    
    
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
        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size())
        settings.endGroup()
            

    def myTest(self):
        """ Function for testing """
        logger.debug("myTest")
        
    def about(self):
        """ Shows the about message window. """
        message = u"{} version {}\n\n{}""".format(PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_URL)
        QtGui.QMessageBox.about(self, "About {}".format(PROGRAM_NAME), message)

    def closeWindow(self):
        """ Closes the window """
        self.close()
        
    def quitApplication(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

    def closeEvent(self, event):
        """ Close all windows (e.g. the L0 window).
        """
        logger.debug("closeEvent")
        self._writeViewSettings()  # TODO: enable
        self.close()
        event.accept()
            

