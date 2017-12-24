# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: sre.pyc
# Compiled at: 2016-06-25 21:46:10
"""This file is only retained for backwards compatibility.
It will be removed in the future.  sre was moved to re in version 2.5.
"""
import warnings
warnings.warn('The sre module is deprecated, please import re.', DeprecationWarning, 2)
from re import *
from re import __all__
from re import _compile