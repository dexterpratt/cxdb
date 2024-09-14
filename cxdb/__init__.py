from .core import CXDB
__version__ = "0.1.0"

# Optional: define what gets imported with `from cxdb import *`
__all__ = ['CXDB']

# Optional: any initialization code the package needs
def initialize():
    # Perform any necessary setup
    pass

initialize()

# convenience function
def create_cxdb_instance():
    """Create and return a new CXDB instance."""
    return CXDB()