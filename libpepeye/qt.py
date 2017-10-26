""" Qt specific stuff.

	Abstracts away the differences between PySide and PyQt

"""
import logging, os, sys

from .utils import environment_var_to_bool

logger = logging.getLogger(__name__)

# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)
USE_QTPY = environment_var_to_bool(os.environ.get('PEPEYE_USE_QTPY', False))

if USE_QTPY:
    logger.debug("PEPEYE_USE_QTPY = {}, using qtpy to find Qt bindings".format(USE_QTPY))

    import qtpy._version
    from qtpy import QtCore, QtGui, QtWidgets, QtSvg
    from qtpy.QtCore import Qt
    from qtpy.QtCore import Signal as QtSignal
    from qtpy.QtCore import Slot as QtSlot
    from qtpy import PYQT_VERSION
    from qtpy import QT_VERSION

    QT_API = qtpy.API
    QT_API_NAME = qtpy.API_NAME
    QTPY_VERSION = '.'.join(map(str, qtpy._version.version_info))
    ABOUT_QT_BINDINGS = "{} (api {}, qtpy: {})".format(QT_API_NAME, QT_API, QTPY_VERSION)

    if qtpy._version.version_info <= (1, 1, 2):
        # At least commit e863f422c7ef78f66223adaa40d52cba4a3b2fce
        logger.warning("You need qtpy version > 1.1.2, got: {}".format(QTPY_VERSION))

    # PySide in combination with Python-3 gives the following error:
    # TypeError: unhashable type: 'PgImagePlot2dCti'
    # I don't know a fix and as long as the future of PySide2 is unclear I won't spend time on it.
    if QT_API == 'pyside' and PY3:
        raise ImportError("PySide in combination with Python 3 is buggy in Pepeye and supported.")

else:
    logger.debug("PEPEYE_USE_QTPY = {}, using PyQt5 directly".format(USE_QTPY))

    from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
    from PyQt5.QtCore import Qt
    from PyQt5.QtCore import pyqtSignal as QtSignal
    from PyQt5.QtCore import pyqtSlot as QtSlot
    from PyQt5.Qt import PYQT_VERSION_STR as PYQT_VERSION
    from PyQt5.Qt import QT_VERSION_STR as QT_VERSION

    QT_API = ''
    QT_API_NAME = 'PyQt5'
    QTPY_VERSION = ''
    ABOUT_QT_BINDINGS = 'PyQt5'



import sys
from .version import PROGRAM_NAME, PROGRAM_VERSION
from .utils import check_class


def getQApplicationInstance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtWidgets.QApplication.instance()

    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    check_class(app, QtWidgets.QApplication)

    app.setApplicationName(PROGRAM_NAME)
    app.setApplicationVersion(PROGRAM_VERSION)
    app.setOrganizationName("titusjan")
    app.setOrganizationDomain("titusjan.nl")

    return app

# Keep a reference so that we canRun once so that we can call libpepeye.browse without
# having to call getQApplicationInstance them selves (lets see if this is a good idea)
APPLICATION_INSTANCE = getQApplicationInstance()

