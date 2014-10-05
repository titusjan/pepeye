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




class StatsTableModel(QtCore.QAbstractTableModel):
    """ Model for a table view to access pstats from the Python profiles
    """
    def __init__(self, parent=None, statsObject=None):
        """ Constructor
        
            :param stats: profiler statistics object.
            :type  stats: pstats.Stats
        """
        super(StatsTableModel, self).__init__(parent)
        
        self._headerLabels = ['file:line', 'function', '1', '2', '3', '4']
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
        
            The statsObject.stats attribute is a dictionary where 
            the keys consist of a (file, line_nr, function) tuple and 
            the values consist of a (?, ?, ?, ?, caller_dict) tuple
        
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
            else:
                return Qt.AlignRight

        elif role == QtCore.Qt.DisplayRole:
            
            if col == 0:
                key = self._sortedKeys[row]
                return "{}:{}".format(key[0], key[1])
            elif col == 1:
                return str(self._sortedKeys[row][2])
            else:
                value = self._statsDict[self._sortedKeys[row]][col - 2]
                return "{:g}".format(value)

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
    
    