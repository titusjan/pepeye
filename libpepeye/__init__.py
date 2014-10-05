""" PepEye package.
"""

# Define some function here that can be imported conveniently

import logging
from .mainwindow import browse

def loggingBasicConfig(level = 'WARN'):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)

