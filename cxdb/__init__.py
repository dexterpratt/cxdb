from .core import CXDB
from .cypher import CypherExecutor
from .ndex import NDExConnector

__version__ = "0.1.0"

# Optional: define what gets imported with `from cxdb import *`
__all__ = ['CXDB', 'CypherExecutor', 'NDExConnector']

# Optional: any initialization code the package needs
def initialize():
    # Perform any necessary setup
    pass

initialize()

# convenience function
def create_cxdb_instance():
    """Create and return a new CXDB instance."""
    return CXDB()