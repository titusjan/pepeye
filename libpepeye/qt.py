""" Qt specific stuff.

	Abstracts away the differences between PySide and PyQt

"""

USE_PYQT = False # Use PySide if False

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
    
        