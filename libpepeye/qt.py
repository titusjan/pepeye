""" Qt specific stuff.

	Abstracts away the differences between PySide and PyQt

"""

USE_PYQT = True # Use PySide if False

if USE_PYQT:
    # This is only needed for Python v2 but is harmless for Python v3.
    import sip
    sip.setapi('QVariant', 2)
    sip.setapi('QString', 2)
    

if USE_PYQT:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import Qt
else:
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt


import sys
from .version import PROGRAM_NAME, PROGRAM_VERSION
from .utils import check_class
    
 
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

# Keep a reference so that we canRun once so that we can call libpepeye.browse without 
# having to call getQApplicationInstance them selves (lets see if this is a good idea)
APPLICATION_INSTANCE = getQApplicationInstance()



           