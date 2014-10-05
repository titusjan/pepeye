""" 
    Stats table model functionality
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import logging, pstats

from .qt import QtCore, Qt
from .utils import check_class
    
logger = logging.getLogger(__name__)


class StatRow(object):
    """ Class that contains the data for one profile statistic
    """
    def __init__(self, statsKey, statsValue):
        """ Constructor which is intialized from a key, value pair of a pstats.stats
            dictionary.
            
            :param stats_key: (file, line_nr, function) tuple
            :param stats_value: (prim_calls, n_calls, time, cum_time, caller_dict) tuple
        """
        (self.fileName, self.lineNr, self.functionName) = statsKey 
        (self.nPrimCalls, self.nCalls, self.time, self.cumTime, _) = statsValue

    @property
    def fileAndLine(self):
        """ File name and line number separated by a colon"""
        return "{}:{}".format(self.fileName, self.lineNr)
        
    @property
    def timePerCall(self):
        """ Seconds spend per function call."""
        return self.time / self.nCalls
    
    @property
    def cumTimePerCall(self):
        """ Cumulative time spend per function call."""
        return self.cumTime / self.nPrimCalls
          
          

class StatsTableModel(QtCore.QAbstractTableModel):
    """ Model for a table view to access pstats from the Python profiles
    """
    SORT_ROLE = Qt.UserRole
    
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
    
    def __init__(self, parent=None, statsObject=None):
        """ Constructor
        
            :param stats: profiler statistics object.
            :type  stats: pstats.Stats
        """
        super(StatsTableModel, self).__init__(parent)
        self._nCols = len(self.HEADER_LABELS)

        # These attributes will be set in setStats        
        self._statsObject = None
        self._statRows = []
        self._nRows = 0
        
    @property
    def headerLabels(self):
        "Returns list of header labels"
        return self.HEADER_LABELS
        

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
            self._statRows = []
            self._nRows = 0
        else:
            self._statsObject = statsObject
            self._statRows = [StatRow(k, v) for (k, v) in statsObject.stats.iteritems()]
            self._nRows = len(self._statRows)

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
            # The cast to int is necessary to avoid a bug in PySide, See:
            # https://bugreports.qt-project.org/browse/PYSIDE-20
            if col <= 1:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight | Qt.AlignVCenter)
                
        elif role == Qt.DisplayRole:
            
            stat = self._statRows[row]
            
            if col == StatsTableModel.COL_FILE_LINE:
                return stat.fileAndLine
            elif col == StatsTableModel.COL_FUNCTION: 
                return stat.functionName
            elif col == StatsTableModel.COL_N_CALLS:
                return str(stat.nCalls)
            elif col == StatsTableModel.COL_TIME:
                return "{:.3f}".format(stat.time)
            elif col == StatsTableModel.COL_TIME_PER_CALL:
                return "{:.4f}".format(stat.timePerCall)
            elif col == StatsTableModel.COL_PRIM_CALLS:
                return str(stat.nPrimCalls)
            elif col == StatsTableModel.COL_CUM_TIME:
                return "{:.3f}".format(stat.cumTime)
            elif col == StatsTableModel.COL_CUM_TIME_PER_CALL:
                return "{:.4f}".format(stat.cumTimePerCall)
            else:
                assert False, "BUG: column number = {}".format(col)

        elif role == StatsTableModel.SORT_ROLE:
            
            stat = self._statRows[row]
            
            if col == StatsTableModel.COL_FILE_LINE:
                return stat.fileAndLine
            elif col == StatsTableModel.COL_FUNCTION: 
                return stat.functionName
            elif col == StatsTableModel.COL_N_CALLS:
                return stat.nCalls
            elif col == StatsTableModel.COL_TIME:
                return stat.time
            elif col == StatsTableModel.COL_TIME_PER_CALL:
                return stat.timePerCall
            elif col == StatsTableModel.COL_PRIM_CALLS:
                return stat.nPrimCalls
            elif col == StatsTableModel.COL_CUM_TIME:
                return stat.cumTime
            elif col == StatsTableModel.COL_CUM_TIME_PER_CALL:
                return stat.cumTimePerCall
            else:
                assert False, "BUG: column number = {}".format(col)
           
        else: # other display roles
            return None 


    def headerData(self, section, orientation, role):
        """ Returns the data for the given role and section in the header with the 
            specified orientation.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.HEADER_LABELS[section]
            else:
                return str(section + 1)
        else:
            return None
    
    