""" 
    Stats table model functionality
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import logging, pstats, os

from .qt import QtCore, QtWidgets, Qt
from .utils import check_class
    
logger = logging.getLogger(__name__)


class StatRow(object):
    """ Class that contains the data for one profile statistic
    """
    def __init__(self, statsKey, statsValue):
        """ Constructor which is initialized from a key, value pair of a pstats.stats
            dictionary.
            
            :param stats_key: (file, line_nr, function) tuple
            :param stats_value: (prim_calls, n_calls, time, cum_time, caller_dict) tuple
        """
        (self.filePath, self.lineNr, self.functionName) = statsKey
        (self.numPrimCalls, self.numCalls, self.time, self.cumTime, self.callers) = statsValue
        
        self.fileAndLine = "{}:{}".format(os.path.basename(self.filePath), self.lineNr)
        self.pathAndLine = "{}:{}".format(self.filePath, self.lineNr)
        self.timePerCall = self.time / self.numCalls
        self.cumTimePerCall = self.cumTime / self.numPrimCalls

    # Sorting keys

    @classmethod
    def keyPathAndLine(cls, statRow):
        return (statRow.pathAndLine, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyFileAndLine(cls, statRow):
        return (statRow.pathAndLine, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyFunctionName(cls, statRow):
        return (statRow.functionName, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyNumCalls(cls, statRow):
        return (statRow.numCalls, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyTime(cls, statRow):
        return (statRow.time, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyTimePerCall(cls, statRow):
        return (statRow.timePerCall, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyNumPrimCalls(cls, statRow):
        return (statRow.numPrimCalls, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyCumTime(cls, statRow):
        return (statRow.cumTime, statRow.filePath, statRow.lineNr, statRow.functionName)

    @classmethod
    def keyCumTimePerCall(cls, statRow):
        return (statRow.cumTimePerCall, statRow.filePath, statRow.lineNr, statRow.functionName)



class StatsTableModel(QtCore.QAbstractTableModel):
    """ Model for a table view to access pstats from the Python profiles
    """
    SORT_ROLE = Qt.UserRole
    
    COL_PATH_LINE = 0
    COL_FILE_LINE = 1
    COL_FUNCTION = 2
    COL_NUM_CALLS = 3
    COL_TIME = 4
    COL_TIME_PER_CALL = 5
    COL_NUM_PRIM_CALLS = 6
    COL_CUM_TIME = 7
    COL_CUM_TIME_PER_CALL = 8


    HEADER_LABELS = [
        'path:line',
        'file:line',
        'function',
        'calls',
        'time',
        'time per call',
        'primitive calls',
        'Σ time',           # cumulative time
        'Σ time per call'
    ]

    SORT_KEY_METHODS = [
        StatRow.keyPathAndLine,
        StatRow.keyFileAndLine,
        StatRow.keyFunctionName,
        StatRow.keyNumCalls,
        StatRow.keyTime,
        StatRow.keyTimePerCall,
        StatRow.keyNumPrimCalls,
        StatRow.keyCumTime,
        StatRow.keyCumTimePerCall
    ]

    def __init__(self, parent=None):
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
        self._sortIdx = dict()

        self._toolTips = {
            self.COL_PATH_LINE: "Path to file plus line number",
            self.COL_FILE_LINE: "Base file name plus line number",
            self.COL_FUNCTION: "Function name",
            self.COL_NUM_CALLS: "Number of calls of this function",
            self.COL_TIME: "The total time spent in the given function "
                           "(excluding time made in calls to sub-functions)",
            self.COL_TIME_PER_CALL: "Time divided by the number of calls",
            self.COL_NUM_PRIM_CALLS: "Number of non-recursive calls of this function.",
            self.COL_CUM_TIME: "The cumulative time spent in this and all subfunctions "
                               "(from invocation till exit). This figure is accurate even for "
                               "recursive functions.",
            self.COL_CUM_TIME_PER_CALL: "Cumulative (Σ) time divided by the number of primitive "
                                        "calls",
        }

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
            self._statRows = [StatRow(k, v) for (k, v) in statsObject.stats.items()]
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
            if col <= 2:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                return int(Qt.AlignRight | Qt.AlignVCenter)
                
        elif role == Qt.DisplayRole:
            
            stat = self._statRows[row]
            
            if col == StatsTableModel.COL_PATH_LINE:
                return stat.pathAndLine
            elif col == StatsTableModel.COL_FILE_LINE:
                return stat.fileAndLine
            elif col == StatsTableModel.COL_FUNCTION: 
                return stat.functionName
            elif col == StatsTableModel.COL_NUM_CALLS:
                return str(stat.numCalls)
            elif col == StatsTableModel.COL_TIME:
                return "{:.3f}".format(stat.time)
            elif col == StatsTableModel.COL_TIME_PER_CALL:
                return "{:.7f}".format(stat.timePerCall)
            elif col == StatsTableModel.COL_NUM_PRIM_CALLS:
                return str(stat.numPrimCalls)
            elif col == StatsTableModel.COL_CUM_TIME:
                return "{:.3f}".format(stat.cumTime)
            elif col == StatsTableModel.COL_CUM_TIME_PER_CALL:
                return "{:.7f}".format(stat.cumTimePerCall)
            else:
                assert False, "BUG: column number = {}".format(col)

        elif role == StatsTableModel.SORT_ROLE:

            stat = self._statRows[row]

            if col == StatsTableModel.COL_PATH_LINE:
                return stat.filePath

            elif col == StatsTableModel.COL_FILE_LINE:
                return stat.fileName

            elif col == StatsTableModel.COL_FUNCTION:
                return stat.functionName

            elif col == StatsTableModel.COL_NUM_CALLS:
                return stat.numCalls

            elif col == StatsTableModel.COL_TIME:
                return stat.time

            elif col == StatsTableModel.COL_TIME_PER_CALL:
                return stat.timePerCall

            elif col == StatsTableModel.COL_NUM_PRIM_CALLS:
                return stat.numPrimCalls

            elif col == StatsTableModel.COL_CUM_TIME:
                return stat.cumTime

            elif col == StatsTableModel.COL_CUM_TIME_PER_CALL:
                return stat.cumTimePerCall

            else:
                assert False, "BUG: column number = {}".format(col)

        else: # other display roles
            return None


    def _oldheaderData(self, section, orientation, role):
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



    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Returns the data for the given role and section in the header with the
            specified orientation.
        """
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.HEADER_LABELS[section]
            elif role == Qt.ToolTipRole:
                return self._toolTips.get(section, "")
        else:
            if role == Qt.DisplayRole:
                return str(section + 1)

        return None


    def sort(self, column, order=Qt.AscendingOrder):
        """ ﻿Sorts the model by column in the given order.
        """
        logger.debug("sort col={}, order={}".format(column, order))

        # Sort the list of row in-place
        self.beginResetModel()
        key = self.SORT_KEY_METHODS[column]
        self._statRows.sort(key=key, reverse=bool(order))
        self.endResetModel()


