'''
    Database manager for PM Plugin
'''

from trac.core import *
from trac.db.schema import Table, Column, Index
from trac.env import IEnvironmentSetupParticipant

__all__ = ['PMSetup']

# Database version identifier for upgrades.
db_version = 3

