__doc__ = """\
Package for data analysis of optical trap experiments
"""

import os
import glob



SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

__version__ = (0, 0, 1)