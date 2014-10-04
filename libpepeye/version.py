""" Version info for the Quick Analysis Tool
"""
import os

USE_PYQT = False # Use PySide if False

if USE_PYQT:
    # This is only needed for Python v2 but is harmless for Python v3.
    import sip
    sip.setapi('QVariant', 2)
    sip.setapi('QString', 2)
    

DEBUGGING = True # TODO: False

PROGRAM_NAME = 'pepeye'
PROGRAM_VERSION = '0.0.1'
PROGRAM_URL = 'https://github.com/titusjan/pepeye'
PROGRAM_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

__version__ = PROGRAM_VERSION
