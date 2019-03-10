"""
    Main window functionality
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import logging
import sys

from .qt import Qt, QtGui, QtWidgets

from .utils import check_class
from .statstablemodel import StatsTableModel
from .togglecolumn import ToggleColumnTableView


logger = logging.getLogger(__name__)


class StatsTableView(ToggleColumnTableView):

    def __init__(self, model:StatsTableModel, parent=None):
        """ Constructor
        """
        super().__init__(parent)
        check_class(model, StatsTableModel)

        self._selectedItem = None # last selected item before a model reset.

        self.setModel(model)
        self._model = model
        self.setSortingEnabled(True)
        self.sortByColumn(StatsTableModel.COL_CUM_TIME, Qt.DescendingOrder)
        self.setTextElideMode(Qt.ElideMiddle)
        self.setWordWrap(False)
        self.setShowGrid(False)
        self.setCornerButtonEnabled(False)
        #self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # needed?
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.addHeaderContextMenu(enabled = {'function': False}, checked = {})

        # Set font so that all table cells have the same font size (was not the case one Windows 10)
        font = QtGui.QFont()
        if sys.platform == 'linux':
            pixelSize = 10
        elif sys.platform == 'win32' or sys.platform == 'cygwin':
            pixelSize = 13
        elif sys.platform == 'darwin':
            pixelSize = 13
        else:
            pixelSize = 13

        font.setPixelSize(pixelSize)
        self.setFont(font)

        tableHorHeader = self.horizontalHeader()
        tableHorHeader.setSectionsMovable(True)
        tableHorHeader.setTextElideMode(Qt.ElideMiddle)
        tableHorHeader.setStretchLastSection(False)

        # Setting vertical table header resize mode to fixed. Setting it to ResizeToContents is
        # slow because it then will read all the data items when displaying or sorting.
        tableVerHeader = self.verticalHeader()
        tableVerHeader.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        tableVerHeader.setDefaultSectionSize(24)
        tableVerHeader.setVisible(False) # Otherwise it distracts when typing the filter text.

        self._model.modelAboutToBeReset.connect(self.onModelAboutToBeReset)
        self._model.modelReset.connect(self.onModelReset)


    def onModelAboutToBeReset(self):
        """ ﻿This slot is called when a new item becomes the current item.
        """
        curIdx = self.currentIndex()

        curItem = self._model.itemAtIndex(curIdx)
        logger.debug("onModelAboutToBeReset: row={}, {}".format(curIdx.row(), curItem))
        if curItem is not None:
            self._selectedItem = curItem


    def onModelReset(self):
        """ Called when the statsTableModel is about to be reset.

            Makes sure that the selected index is selected again.
        """
        curIdx = self._model.findIndexForItem(self._selectedItem)
        if curIdx.isValid():
            self.setCurrentIndex(curIdx)
            self.scrollTo(curIdx, QtWidgets.QAbstractItemView.PositionAtCenter)
            logger.debug("after reset: row={}, {}".format(curIdx.row(), self._selectedItem))
            logger.debug('----------------------------------------\n')




