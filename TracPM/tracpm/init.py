

# Trac imports.
from trac.core import *
from trac.db import *
from trac.config import PathOption

# Trac interfaces.
from trac.env import IEnvironmentSetupParticipant

# Local imports.
#from tracpm.db import * 
'''
db_version = 1

class TracPMInit(Component):
    """
      
       plugin.
    """
    implements(IEnvironmentSetupParticipant)

    # IEnvironmentSetupParticipanttr
    def environment_created(self):
        pass

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()

        # Is database up to date?
        self.log.debug('[environment_needs_upgrade] Checking version on DB')
        return (self._get_db_version(cursor) < db_version) 

    def upgrade_environment(self, db):
        cursor = db.cursor()

        # Create screenshots directory if not exists.
        if not os.path.isdir(self.path):
            os.mkdir(os.path.normpath(self.path))

        # Get current database schema version
        db_version = self._get_db_version(cursor)

        # Is this clean installation?
        if db_version == 0:
            # Perform single upgrade.
            module = __import__('tracsqa.db.db%s' % (last_db_version),
              globals(), locals(), ['do_upgrade'])
            module.do_upgrade(self.env, cursor, False)
        else:
            # Perform incremental upgrades
            for I in range(db_version + 1, last_db_version + 1):
                script_name  = 'db%i' % (I)
                module = __import__('tracsqa.db.%s' % (script_name),
                  globals(), locals(), ['do_upgrade'])
                module.do_upgrade(self.env, cursor, True)

    def _get_db_version(self, cursor):
        try:
            sql = ("""SELECT value
                      FROM system
                      WHERE name='sqa_version'""")
            self.log.debug(sql)
            cursor.execute(sql)
            for row in cursor:
                return int(row[0])
            return 0
        except:
            return 0

'''

