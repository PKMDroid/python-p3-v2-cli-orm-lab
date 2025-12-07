import sqlite3
import sys

# Check if we've already created the connection
if 'models' in sys.modules and hasattr(sys.modules['models'], 'CONN'):
    # Reuse existing connection
    CONN = sys.modules['models'].CONN
    CURSOR = sys.modules['models'].CURSOR
else:
    # Create new connection
    CONN = sqlite3.connect(':memory:', check_same_thread=False)
    CURSOR = CONN.cursor()

# Import classes after CONN and CURSOR are defined
from models.department import Department
from models.employee import Employee

__all__ = ['CONN', 'CURSOR', 'Department', 'Employee']