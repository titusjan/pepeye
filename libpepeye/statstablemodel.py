""" 
    Stats table model functionality
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import logging, pstats

from .version import USE_PYQT
from .utils import check_class

if USE_PYQT:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import Qt
else:
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt
    
logger = logging.getLogger(__name__)


# Stats key tuple indices
IDX_FILE = 0
IDX_LINE = 1
IDX_FUNCTION = 2

# Stats value tuple indices
IDX_PRIM_CALLS = 0
IDX_N_CALLS = 1
IDX_TIME = 2
IDX_CUM_TIME = 3

COL_FILE_LINE = 0
COL_FUNCTION = 1
COL_N_CALLS = 2
COL_TIME = 3
COL_TIME_PER_CALL = 4
COL_PRIM_CALLS = 5
COL_CUM_TIME = 6
COL_CUM_TIME_PER_CALL = 7

HEADER_LABELS = [
    'file:line', 'function', 
    'calls', 'time', 'time per call',  
    'primitive calls', 'cumulative time', 'cumulative time per call']


class StatsTableModel(QtCore.QAbstractTableModel):
    """ Model for a table view to access pstats from the Python profiles
    """
    def __init__(self, parent=None, statsObject=None):
        """ Constructor
        
            :param stats: profiler statistics object.
            :type  stats: pstats.Stats
        """
        super(StatsTableModel, self).__init__(parent)
        
        self._headerLabels = HEADER_LABELS
        self._nCols = len(self._headerLabels)

        # These attributes will be set in setStats        
        self._statsObject = None
        self._statsDict = {}
        self._sortedKeys = []
        self._nRows = 0
        
    @property
    def headerLabels(self):
        "Returns list of header labels"
        return self._headerLabels
        

    def setStats(self, statsObject):
        """ Sets the statistics
        
            The statsObject.stats attribute is a dictionary where the keys consist of a 
            (file, line_nr, function) tuple and the values consist of a 
            (primitive_calls, n_calls, time, cumulative_time, caller_dict) tuple

            Primitive calls are calls that where not induced via recursion
        
            :param statsObject: profiler statistics. Use None to clear.
            :type  statsObject: pstats.Stats or None
        """
        check_class(statsObject, pstats.Stats, allow_none=True)
        self.beginResetModel()
        if statsObject is None:
            self._statsObject = None
            self._statsDict = {}
            self._sortedKeys = []
            self._nRows = 0
        else:
            self._statsObject = statsObject
            self._statsDict = statsObject.stats
            self._sortedKeys = self._statsDict.keys()
            self._nRows = len(self._sortedKeys)

        self.endResetModel()
        

    def rowCount(self, parent):
        """ Returns the number of columns for the children of the given parent.
        """
        return self._nRows

    def columnCount(self, parent):
        """ Returns the number of rows under the given parent. 
            When the parent is valid it means that rowCount is returning the number of 
            children of parent. 
        """
        return self._nCols

    def data(self, index, role):
        """ Returns the data stored under the given role for the item referred to by the index.
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
                
        if not (0 <= col < self._nCols):
            return None
        
        if not (0 <= row < self._nRows):
            return None
        
        if role == Qt.TextAlignmentRole:
            if col <= 1:
                return Qt.AlignLeft
                #return Qt.AlignTop
            else:
                #return Qt.AlignBottom
                return Qt.AlignRight
                #return Qt.AlignRight | Qt.AlignBottom
                #return  Qt.AlignBottom.AlignRight
                
        elif role == QtCore.Qt.DisplayRole:
            
            key = self._sortedKeys[row]
            value = self._statsDict[key]
            
            if col == COL_FILE_LINE:
                return "{}:{}".format(key[IDX_FILE], key[IDX_LINE])
            elif col == COL_FUNCTION: 
                return str(key[IDX_FUNCTION])
            elif col == COL_N_CALLS:
                return str(value[IDX_N_CALLS])
            elif col == COL_TIME:
                return "{:.3f}".format(value[IDX_TIME])
            elif col == COL_TIME_PER_CALL:
                return "{:.4f}".format(value[IDX_TIME] / value[IDX_N_CALLS])
            elif col == COL_PRIM_CALLS:
                return str(value[IDX_PRIM_CALLS])
            elif col == COL_CUM_TIME:
                return "{:.3f}".format(value[IDX_CUM_TIME])
            elif col == COL_CUM_TIME_PER_CALL:
                return "{:.4f}".format(value[IDX_CUM_TIME] / value[IDX_PRIM_CALLS])
            else:
                assert False, "BUG: column number = {}".format(col)

        else: # other display roles
            return None 


    def headerData(self, section, orientation, role):
        """ Returns the data for the given role and section in the header with the 
            specified orientation.
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._headerLabels[section]
            else:
                return str(section + 1)
        else:
            return None
    
    