
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .config import Config


__all__ = ['__version__', 'Config']
