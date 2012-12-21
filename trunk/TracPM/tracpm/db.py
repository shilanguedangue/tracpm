'''
    Database manager for PM Plugin
'''

from trac.core import *
from trac.db.schema import Table, Column, Index
from trac.env import IEnvironmentSetupParticipant

__all__ = ['PMSetup']

# Database version identifier for upgrades.
db_version = 4


schema = [
    Table('custom_events', key=('id')) [ 
        Column('id', type='int', auto_increment=True),
        Column('event_name', type='text'),
        Column('event_description', type='text'),
        Column('creator', type='text', size=200),
        Column('create_ts', type='int'),
        Column('update_ts', type='int'),
        Index(['update_ts'])                      
    ],                                                
] 




def to_sql(env, table):
    """ Convenience function to get the to_sql for the active connector."""
    from trac.db.api import DatabaseManager
    dc = DatabaseManager(env)._get_connector()[0]
    return dc.to_sql(table)



def create_tables(env, db):
    """ Creates the basic tables as defined by schema.
    using the active database connector. """
    cursor = db.cursor()
    for table in schema:
        for stmt in to_sql(env, table):
            cursor.execute(stmt)
    cursor.execute("INSERT into system values ('pm_version', %s)",
                        str(db_version))
    cursor.execute("INSERT into system values ('pm_infotext', 'Project Manager Version...')")

# Upgrades
def add_timeline_time_indexes(env, db):
    """ Add time-based indexes to blog post and comment tables. """
    cursor = db.cursor()
    cursor.execute( "CREATE INDEX pm_idx ON custom_events (id)")

    

upgrade_map = {
        db_version: add_timeline_time_indexes
}


class PMSetup(Component):
    """Component that deals with database setup and upgrades."""
    
    implements(IEnvironmentSetupParticipant)

    def environment_created(self):
        """Called when a new Trac environment is created."""
        pass

    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.
        Returns `True` if upgrade is needed, `False` otherwise."""
        return self._get_version(db) != db_version

    def upgrade_environment(self, db):
        """Code used to perform the upgrade to the Trac environment. """
        current_ver = self._get_version(db)
        if current_ver == 0:
            create_tables(self.env, db)
        else:
            while current_ver+1 <= db_version:
                '''
                    Used to upgrade map and indexes... 
                    TODO: Add this to the listing of activites
                '''
                upgrade_map[current_ver+1](self.env, db)
                current_ver += 1
            cursor = db.cursor()
            cursor.execute("UPDATE system SET value=%s WHERE name='pm_version'",
                                str(db_version))

    def _get_version(self, db):
        cursor = db.cursor()
        try:
            sql = "SELECT value FROM system WHERE name='pm_version'"
            self.log.debug(sql)
            cursor.execute(sql)
            for row in cursor:
                return int(row[0])
            return 0
        except:
            return 0





