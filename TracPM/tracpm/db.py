'''
    Database manager for PM Plugin
'''

from trac.core import *
from trac.db.schema import Table, Column, Index
from trac.env import IEnvironmentSetupParticipant

__all__ = ['PMSetup']

# Database version identifier for upgrades.
db_version = 3


"""
Drop tables used to reset environment

drop table test_plan;
drop table test_case;
drop table test_register;
drop table test_log;
drop table test_ticket;
drop table test_archive;

delete from system where name like 'sqa%';


"""

schema = [
    Table('test_plan', key=('id', 'plan_name', 'milestone')) [ 
        Column('id', type='int', auto_increment=True),
        Column('plan_name', type='text'),
        Column('test_type', type='int'),
        Column('milestone', type='text'),
        Column('description', type='text'),
        Column('creator', type='text', size=200),
        Column('create_ts', type='int'),
        Column('update_ts', type='int'),
        Column('active', type='int'),
        Index(['update_ts'])                      
    ],                                                
    Table('test_case', key=('case_id','plan_id')) [ 
        Column('case_id', type='int', auto_increment=True),
        Column('plan_id', type='int'),
        Column('item_name', type='text'),
        Column('test_order', type='int'),
        Column('test_procedure', type='text'),
        Column('expected_result', type='text'),
        Column('create_ts', type='int'),
        Column('update_ts', type='int'),
        Column('active', type='int'), 
        Index(['update_ts']) 
    ],
    Table('test_register', key=('id', 'plan_id')) [
        Column('id', type='int', auto_increment=True),
        Column('plan_id', type='int'),
        Column('tester', type='text', size=200),
        Column('test_detail', type='text'),
        Column('custom_detail', type='text'),
        Column('test_condition', type='text'),
        Column('test_comments', type='text'),
        Column('create_ts', type='int'),
        Index(['create_ts'])
    ],
    Table('test_log', key=('id', 'register_id', 'case_step_id')) [
        Column('id', type='int', auto_increment=True),
        Column('register_id', type='int'),
        Column('case_step_id', type='int'),
        Column('result_status', type='text'),
        Column('actual_result', type='text'),
        Column('update_ts', type='int'),
        Index(['update_ts'])
    ],
     Table('test_ticket', key=('plan_id', 'case_step_id', 'ticket_id')) [
        Column('ticket_id', type='int'),
        Column('register_id', type='int'),
        Column('plan_id', type='int'),
        Column('case_step_id', type='int'),
        Column('create_ts', type='int'),
        Index(['create_ts'])
    ], 
    Table('test_archive', key=('register_id')) [ 
        Column('register_id', type='int'),
        Column('archive_data', type='text')
    ],
    
    

] 


'''
ADD these tables
    Table('test_archive', key=('case_id')) [ 
        Column('id', type='int', auto_increment=True),
        Column('plan_name', type='text'),
        Column('test_type', type='int'),
        Column('milestone', type='text'),
        Column('description', type='text'),
        Column('creator', type='text', size=200),
        Column('create_ts', type='int'),
        Column('update_ts', type='int'),
        Column('active', type='int'),
        Index(['update_ts'])                      
    ],                                               
'''
'''
def to_sql(env, table):
    # Convenience function to get the to_sql for the active connector.
    from trac.db.api import DatabaseManager
    dc = DatabaseManager(env)._get_connector()[0]
    return dc.to_sql(table)

def create_tables(env, db):
    Creates the basic tables as defined by schema. using the active database connector.
    cursor = db.cursor()
    for table in schema:
        for stmt in to_sql(env, table):
            cursor.execute(stmt)
    cursor.execute("INSERT into system values ('pm_version', %s)",
                        str(db_version))
    cursor.execute("INSERT into system values ('pm_infotext', '')")

# Upgrades
def add_timeline_time_indexes(env, db):
    #Add time-based indexes to blog post and comment tables. 
    cursor = db.cursor()
    cursor.execute(
        "CREATE INDEX test_mgr_update_idx ON test_mgr (update_ts)")
    cursor.execute(
        "CREATE INDEX test_plan_update_idx ON test_mgr (update_ts)")

    cursor.execute(
        "CREATE INDEX test_case_update_idx ON test_mgr (update_ts)")

    cursor.execute(
        "CREATE INDEX test_exec_update_idx ON test_mgr (update_ts)")
 

upgrade_map = {
        2: add_timeline_time_indexes
}

'''




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
            cursor.execute("UPDATE system SET value=%s WHERE name='sqa_version'",
                                str(db_version))

    def _get_version(self, db):
        cursor = db.cursor()
        try:
            sql = "SELECT value FROM system WHERE name='sqa_version'"
            self.log.debug(sql)
            cursor.execute(sql)
            for row in cursor:
                return int(row[0])
            return 0
        except:
            return 0
