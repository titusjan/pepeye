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
        (self.nPrimCalls, self.nCalls, self.time, self.cumTime, self.callers) = statsValue
        
        self.fileName = os.path.basename(self.filePath)
        self.fileAndLine = "{}:{}".format(self.fileName, self.lineNr)
        self.pathAndLine = "{}:{}".format(self.filePath, self.lineNr)
        self.timePerCall = self.time / self.nCalls
        self.cumTimePerCall = self.cumTime / self.nPrimCalls
          
          

class StatsTableModel(QtCore.QAbstractTableModel):
    """ Model for a table view to access pstats from the Python profiles
    """
    SORT_ROLE = Qt.UserRole
    
    COL_PATH_LINE = 0
    COL_FILE_LINE = 1
    COL_FUNCTION = 2
    COL_N_CALLS = 3
    COL_TIME = 4
    COL_TIME_PER_CALL = 5
    COL_PRIM_CALLS = 6
    COL_CUM_TIME = 7
    COL_CUM_TIME_PER_CALL = 8
    
    HEADER_LABELS = [
        'path:line', 'file:line', 'function', 
        'calls', 'time', 'time per call',  
        'primitive calls', 'Σ time', 'Σ time per call']
        #'cumulative time', 'cumulative time per call']

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
            elif col == StatsTableModel.COL_N_CALLS:
                return str(stat.nCalls)
            elif col == StatsTableModel.COL_TIME:
                return "{:.3f}".format(stat.time)
            elif col == StatsTableModel.COL_TIME_PER_CALL:
                return "{:.7f}".format(stat.timePerCall)
            elif col == StatsTableModel.COL_PRIM_CALLS:
                return str(stat.nPrimCalls)
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



#
#
# class StatsTableProxyModel(QtCore.QSortFilterProxyModel):
#     """ Proxy model that overrides the sorting.
#
#         Needed to override the vertical header to always be increasing.
#     """
#     def __init__(self, parent):
#         super(StatsTableProxyModel, self).__init__(parent)
#
#         self._srcModel = self.sourceModel()
#
#
#     # def lessThan(self, leftIndex, rightIndex):
#     #     """ Returns true if the value of the item referred to by the given index left is less than
#     #         the value of the item referred to by the given index right, otherwise returns false.
#     #     """
#     #     dataFn = self.sourceModel().data
#     #     leftData  = dataFn(leftIndex,  StatsTableModel.SORT_ROLE)
#     #     rightData = dataFn(rightIndex, StatsTableModel.SORT_ROLE)
#     #
#     #     return leftData < rightData
#     #
#     #
#
#
#     def lessThan(self, leftIndex, rightIndex):
#         """ Returns true if the value of the item referred to by the given index left is less than
#             the value of the item referred to by the given index right, otherwise returns false.
#         """
#         dataFn = self.sourceModel().data
#         leftData  = dataFn(leftIndex,  StatsTableModel.SORT_ROLE)
#         rightData = dataFn(rightIndex, StatsTableModel.SORT_ROLE)
#
#         if leftData != rightData:
#             return leftData < rightData
#         else:
#             # Tie breaker on filePath:LineNr
#             leftHandPath =  dataFn(leftIndex,   StatsTableModel.SORT_ROLE)
#             rightHandPath = dataFn(rightIndex,  StatsTableModel.SORT_ROLE)
#
#             if leftHandPath != leftHandPath:
#                 return leftHandPath < rightHandPath
#             else:
#                 # Tie breaker on filePath:LineNr
#                 leftHandFname =  dataFn(leftIndex,   StatsTableModel.SORT_ROLE)
#                 rightHandFname = dataFn(rightIndex,  StatsTableModel.SORT_ROLE)
#
#                 return leftHandFname < rightHandFname
#
#
#
#
#     def headerData(self, section, orientation, role):
#         """ Returns the data for the given role and section in the header with the
#             specified orientation.
#         """
#         # Take horizontal headers from the source model but override the vertical header
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return self.sourceModel().headerData(section, orientation, role)
#             else:
#                 return str(section + 1)
#         else:
#             return None
#