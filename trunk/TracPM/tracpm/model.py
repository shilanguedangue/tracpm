'''
    Module used to support database lookups
    Support CRUD and search features 
'''

from datetime import datetime
import re


from trac.resource import Resource
from trac.search import search_to_sql
from trac.util.datefmt import from_utimestamp, to_utimestamp, utc, utcmax
from trac.attachment import Attachment
import trac.ticket.model as ticket_model
import trac.ticket.query as ticket_query
from trac.core import *
import json
from trac.ticket.api import TicketSystem
'''
    Notes on JSON Support
    http://docs.python.org/library/json.html
    
    '%(language)s has %(number)03d quote types.' % {"language": "Python", "number": 2}
    
'''


try:
    from trac.util.compat import itemgetter
    from trac.util.compat import sorted, set
except ImportError:
    from operator import itemgetter
''' Add local '''
from tracsqa.api import *


class TestData(object):
    # TODO: Breakout functional database calls 
    
    '''
        Class for managing test collections
    '''
    def __init__(self, env, Collection_id=None):
        '''
            Init
        '''
        self.env = env
        self.db = self.env.get_db_cnx()
        
        if (Collection_id != None):
            self._get_all_milestones()
           
    def _test_collection_attrs(self, id):
        '''
            Set internal data structures about a particular test collection
            id = collection  table id
        '''
        sql = "SELECT "  
        
    
    
    def getTestPlanMilestones(self):
        '''
        Return a list milestones that have testplans defined...
        '''
        
        sql = "select distinct(milestone) from test_plan where active = 1"
    
        columns = ['milestone']
        cursor = self.db.cursor()
        cursor.execute(sql)
        
        nav_milestones = [dict(zip(columns, mstone)) for mstone in cursor]
        
        return nav_milestones
    
    def get_test_plans(self, milestone=None, get_all=None):
        '''
            Get a listing of defined test collections
            Since the argument is from a GET request... sql lookup needs to be quoted
        '''
        sql = "SELECT * FROM test_plan "
        
        if milestone or not get_all:
            '''
                Add Criteria
            '''
            sql += " WHERE "
            
        
        if milestone:
            sql += " milestone = '%s' " % (milestone)
            if not get_all:
                sql += " AND "
        if not get_all:
            '''
                If Get all is set 
                sql will return all test cases
                enabled or disabled
            '''
            sql += " active = '1' "
        
        sql += " order by milestone asc, test_type asc"
        self.env.log.debug('--- SQL .. TYPE = %s ' %  sql)
        columns = ['id', 'plan_name', 'test_type', 'milestone', 'description',  'creator', 'create_ts', 'update_ts', 'active']
        cursor = self.db.cursor()
        cursor.execute(sql)
        test_plans = [dict(zip(columns, plan)) for plan in cursor]
        #row_set = cursor.fetchall()
        
        
        '''
        Group by milestone
        '''
        group_test_plans = {}
        for plan in test_plans:
            if group_test_plans.has_key(plan['milestone']):
                '''
                '''
                group_test_plans[plan['milestone']].append(plan)
            else:
                '''
                '''
                group_test_plans[plan['milestone']] = []
                group_test_plans[plan['milestone']].append(plan)
        
        self.env.log.debug('TestPlanGroup %s ' %  group_test_plans)
        return test_plans
        
        #return group_test_plans
        
    def get_plan_by_id(self, plan_id=None, get_all=None ):
        '''
            Lookup a test case within a plan by ID
        '''
        sql = "SELECT * FROM test_plan "        
        if plan_id != None:
            sql += " WHERE id = %s " % (plan_id)
        
        if not get_all:
            '''
                If Get all is set 
                sql will return all test cases
                enabled or disabled
            '''
            sql += " AND active = 1 "
        sql += " order by milestone asc, test_type asc"
        
        columns = ['id', 'plan_name', 'test_type', 'milestone', 'description',  'creator', 'create_ts', 'update_ts', 'active']
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        test_plan = dict(zip(columns, row))
        return test_plan
        
        
    def set_test_plan(self, dataset):
        '''
            Insert records onto database
        '''
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        sql = """insert 
        into test_plan (
        plan_name, 
        test_type,
        milestone,
        description, 
        creator, 
        create_ts, 
        update_ts, 
        active
        ) 
        values (%s,%s,%s,%s,%s,%s,%s,%s) """
        cursor = self.db.cursor()
        cursor.execute(sql, (args['plan_name'], args['test_type'], args['test_milestone'], args['c_desc_ta'],  dataset.authname, _now_ts, _now_ts, 1 ))
        self.db.commit()


    def get_test_step_by_id(self, id):
        sql = """select * from test_case where case_id = '%s' """ % id
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        columns = ['case_id', 'plan_id', 'item_name', 'test_order', 'test_procedure', 'expected_result', 'create_ts', 'update_ts', 'active' ]
        test_step = dict(zip(columns, row))
        
        #jsonFormat = json.dumps(test_step)
        #self.env.log.debug('--- JSON   =>> %s ' %  jsonFormat)
        #return jsonFormat
        return test_step


    def update_step_by_id(self, req):
        '''
        Update step in database
        '''
        
        args = req.args
        self.env.log.debug('--- ARGS   =>> %s ' %  args)
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        
        sql = """update test_case set 
        item_name = "%s",
        test_procedure = "%s",
        expected_result = "%s",
        update_ts = "%s"
        where case_id = "%s"
        """ % (args['item_name'], args['test_procedure'], args['expected_result'], _now_ts, args['case_id'] )
        self.env.log.debug('--- SQL   =>> %s ' %  sql)
        cursor = self.db.cursor()
        cursor.execute(sql )
        self.db.commit()

        return self.get_test_step_by_id(args['case_id'])
        
    def setJsonArchive(self, plan_id, reg_id):
        '''
            Convert a test case within a test plan
            into json format  
        '''
        result = self.get_test_case(plan_id)
        
        jsonFormat = json.dumps(result)
        
        #self.env.log.debug('--- JSON   =>> %s ' %  jsonFormat)
        sql = """insert 
            into test_archive (
            register_id, 
            archive_data
            )
            values (%s,%s)""" 
        cursor = self.db.cursor()
        cursor.execute(sql, (reg_id,jsonFormat ))
        self.db.commit()

    def getJsonArchive(self, reg_id):
        '''
            Get the test archive
        '''
        sql = """SELECT archive_data FROM test_archive WHERE register_id = '%s' """ % reg_id
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        '''
            Convert from json text to python objects
        '''
        
        #self.env.log.debug('-- Return JSON -> %s' % row )
        columns = ['json']
        test_case = dict(zip(columns, row))
        '''
            Convert from json text to python objects
        '''
        test_case['json'] = json.loads(test_case['json'])
        
        return test_case

    def set_test_register(self, dataset):
        '''
            Insert records onto database
            Note: Statements collected while running in Trac debug mode.
            
            2011-04-10 16:24:23,108 Trac[main] DEBUG: Dispatching <Request "GET '/chrome/site/your_project_logo.png'">
            2011-04-10 16:24:23,110 Trac[session] DEBUG: Retrieving session for ID u'admin'
            2011-04-10 16:24:23,113 Trac[chrome] WARNING: File your_project_logo.png not found in any of ['/swdata/apps/trac-dev/htdocs']
            2011-04-10 16:24:23,113 Trac[chrome] DEBUG: Prepare chrome data for request
            2011-04-10 16:24:23,118 Trac[main] WARNING: HTTPNotFound: 404 Not Found (File your_project_logo.png not found)
            2011-04-10 16:25:32,130 Trac[main] DEBUG: Dispatching <Request "POST '/newticket'">
            2011-04-10 16:25:32,133 Trac[api] INFO: Synchronized '' repository in 0.00 seconds
            2011-04-10 16:25:32,135 Trac[session] DEBUG: Retrieving session for ID u'admin'
            2011-04-10 16:25:32,287 Trac[main] DEBUG: Dispatching <Request "GET '/ticket/6'">
            2011-04-10 16:25:32,288 Trac[api] INFO: Synchronized '' repository in 0.00 seconds
            2011-04-10 16:25:32,289 Trac[session] DEBUG: Retrieving session for ID u'admin'
            2011-04-10 16:25:32,298 Trac[web_ui] DEBUG: [Ticket Resource] -   <Resource u'ticket:6'>, REQ = <Request "GET '/ticket/6'"> -----
            2011-04-10 16:25:32,299 Trac[web_ui] DEBUG: --------------- [CONTEXT] -   <Context <Resource u'ticket:6'>>

        '''
        args = dataset.args
        json_detail = '''{
            "browser_info": {
                "browser": "%s",
                "version": "%s",
                "user_agent": "%s"
            },
            "client_info": {
                "client_platform": "%s"
            }
        }
        ''' % (args['browser'], args['browser_ver'], args['user_agent'], args['client_plfrm'])
        
        '''
        Compile json information for ticket fields
        Save result in custom_detail
        '''
        SqaApi = TracSqaConfig(self.env)
        ticket_fields = SqaApi.get_ticket_args(args)
        self.env.log.debug('---Matching Ticket Fields -  %s ' %  ticket_fields )
        json_ticket = []
        for field in ticket_fields:
            '''
            write ticket information to json
            with ticket ordering
            '''
            json_ticket.append( {'name': field,  'value' : str(args[field]) } )
        
        '''
        Encode ticket information as an array of dictionaries
        '''
        self.env.log.debug('---Encoding Json -  %s ' %  json_ticket )
        
        
        try:
            json_custom = json.dumps(json_ticket)
        except:
            self.env.log.debug('---Can not encode Empty Set -  %s ' %  json_ticket )
            json_custom = None
        
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        sql = """insert 
        into test_register (
        plan_id, 
        tester,
        test_detail,
        custom_detail,
        test_condition,
        test_comments, 
        create_ts
        ) 
        values (%s,%s,%s,%s,%s,%s,%s) """
        test_id = {}
        cursor = self.db.cursor()
        cursor.execute(sql, (args['plan_id'], args['tester_name'], json_detail,  json_custom, args['_conditions'], args['_comments'],  _now_ts ))
        '''
            Pack test_id with information about the newly created 
            test execution plan. Include in the result set information 
            about the test plan and execution steps. 
        '''
        test_id['reg_id'] = self.db.get_last_id(cursor, 'test_register')
        test_id['plan_id'] = args['plan_id']
        self.env.log.debug('---Last Test Registration Id Is -> %s ' %  test_id)
        self.db.commit()
        
        '''
            Get newly created testing ID
        '''
        return test_id





    def get_test_case_summary(self):
        '''
            Render a listing of testing result metrics
            
        '''
        
        sql = ''' SELECT 
        p.milestone, p.plan_name, count(c.test_order), r.create_ts
        FROM 
        test_case c
        LEFT JOIN 
        (test_plan p, test_register r)
        ON
        (c.plan_id = p.plan_id AND c.plan_id = r.plan_id)
        WHERE 
        c.plan_id = %s
        ''' 




    def get_test_case(self, plan_id, get_all=None):
    
        '''
            def get_test_case(self, plan_id=None, milestone=None ):
            Return test case information 
            Conditions:
                case_id set:
                    return selected test_case
                milestone set:
                    return all test cases for selected milestion
                Both set:
                    Return test case for milestone
               
        '''
        sql = "SELECT * FROM test_case WHERE plan_id = %s " % (plan_id)
        
        if not get_all:
            '''
                If Get all is set 
                sql will return all test cases
                enabled or disabled
            '''
            sql += " AND active = 1 "
        
        
        sql += ' order by plan_id asc, test_order asc '
        
        columns = ['case_id', 'plan_id', 'item_name', 'test_order', 'test_procedure', 'expected_result', 'create_ts', 'update_ts', 'active' ]
        cursor = self.db.cursor()
        cursor.execute(sql)
        test_case = [dict(zip(columns, case)) for case in cursor]
        #self.env.log.debug('-- Return SQL -> %s' % test_case )
        return test_case

    def get_test_step_count(self, plan_id, get_all=None):
        '''
            Return number of ACTIVE steps in the test case
        '''
        sql = "SELECT count(*) FROM test_case WHERE plan_id = %s " % (plan_id)
        
        if not get_all:
            '''
                If get_all is set 
                sql will return a count of all test cases
                enabled or disabled
            '''
            sql += " AND active = 1 "
            
        columns = ['count']
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        step_count = dict(zip(columns, row))

        return step_count

    
    def disable_test_case(self, dataset):
        '''
            Set the active state to disabled
            removing the item from the test plan list BUT NOT A DELETE
        '''
        args = dataset.args
        self.env.log.debug('Disabling cases from test plan ')
        if (args.has_key('test_case_id')):
            '''
                If a list of test cases is given then 
                remove them from the list and update the order
            '''
            #self.env.log.debug('--- Checking type of object .. TYPE = %s ' % (type(args['remove_case']).__name__) )
            
            if (type(args['test_case_id']).__name__ == 'unicode'): 
                '''
                    Only selected one item
                    NOTE: TRAC will present single items as unicode
                '''
                #self.env.log.debug('Remove a single Item ')
                sql = "UPDATE test_plan set active = 0 WHERE id = '%s'" % (args['test_case_id'])
                self._exec_sql(sql)
                '''
                This will remove the direct link to the test case steps. 
                
                May not need to be disabled
                TODO: 
                '''
                #sql = "DELETE FROM test_case WHERE plan_id = '%s'" % (args['test_case_id'])
                #self._exec_sql(sql)
                
            elif(type(args['test_case_id']).__name__ == 'list'):    
                #self.env.log.debug('Remove Multiple items')
                for deleteCase in args['test_case_id']: 
                    sql = "UPDATE test_plan set active = 0 WHERE id = '%s'" % (deleteCase)
                    self._exec_sql(sql)
                    '''
                    Again since the link is removed. 
                    But may want to disable the test later. 
                    Add as TODO
                    '''
                    #sql = "DELETE FROM test_case WHERE plan_id = '%s'" % (deleteCase)
                    #self._exec_sql(sql)
                         
        
    
    
    def disable_test_case_step(self, dataset):
        '''
            Set the active state to disabled
            removing the item from the test case
            
            Set test_order to zero, if item is reactivated it will appear at the top for reordering
        '''
        args = dataset.args
        self.env.log.debug('Disable cases from test case ')
        if (args.has_key('test_case_step_id')):
            '''
                If a list of test cases is given then 
                remove them from the list and update the order
            '''
            #self.env.log.debug('--- Checking type of object .. TYPE = %s ' % (type(args['remove_case']).__name__) )
            
            if (type(args['test_case_step_id']).__name__ == 'unicode'): 
                '''
                    Only selected one item
                    NOTE: TRAC will present single items as unicode
                '''
                #self.env.log.debug('Remove a single Item ')
                sql = "UPDATE test_case SET active = 0, test_order = 0  WHERE case_id = '%s'" % (args['test_case_step_id'])
                self._exec_sql(sql)
                
            elif(type(args['test_case_step_id']).__name__ == 'list'):    
                #self.env.log.debug('Remove Multiple items')
                for deleteCase in args['test_case_step_id']: 
                    sql = "UPDATE test_case SET active = 0, test_order = 0 WHERE case_id = '%s'" % (deleteCase)
                    self._exec_sql(sql)
            
            
            '''
                Update list of items 
            '''
            self.update_test_case_order(args['plan_id'])    
    
    

    def remove_test_case(self, dataset):
        '''
            Remove a test case from the home page
        '''
        args = dataset.args
        self.env.log.debug('Removing cases from test plan ')
        if (args.has_key('test_case_id')):
            '''
                If a list of test cases is given then 
                remove them from the list and update the order
            '''
            #self.env.log.debug('--- Checking type of object .. TYPE = %s ' % (type(args['remove_case']).__name__) )
            
            if (type(args['test_case_id']).__name__ == 'unicode'): 
                '''
                    Only selected one item
                    NOTE: TRAC will present single items as unicode
                '''
                #self.env.log.debug('Remove a single Item ')
                sql = "DELETE FROM test_plan WHERE id = '%s'" % (args['test_case_id'])
                self._exec_sql(sql)
                sql = "DELETE FROM test_case WHERE plan_id = '%s'" % (args['test_case_id'])
                self._exec_sql(sql)
                
            elif(type(args['test_case_id']).__name__ == 'list'):    
                #self.env.log.debug('Remove Multiple items')
                for deleteCase in args['test_case_id']: 
                    sql = "DELETE FROM test_plan WHERE id = '%s'" % (deleteCase)
                    self._exec_sql(sql)
                    sql = "DELETE FROM test_case WHERE plan_id = '%s'" % (deleteCase)
                    self._exec_sql(sql)
                    '''
                    self.remove_test_step(dataset)
                    '''
        

    def remove_test_step(self, dataset):
        '''
            Remove selected test case by ID
        '''
        args = dataset.args
        self.env.log.debug('Removing cases from test case ')
        if (args.has_key('test_case_step_id')):
            '''
                If a list of test cases is given then 
                remove them from the list and update the order
            '''
            #self.env.log.debug('--- Checking type of object .. TYPE = %s ' % (type(args['remove_case']).__name__) )
            
            if (type(args['test_case_step_id']).__name__ == 'unicode'): 
                '''
                    Only selected one item
                    NOTE: TRAC will present single items as unicode
                '''
                #self.env.log.debug('Remove a single Item ')
                sql = "DELETE FROM test_case WHERE case_id = '%s'" % (args['test_case_step_id'])
                self._exec_sql(sql)
                
            elif(type(args['test_case_step_id']).__name__ == 'list'):    
                #self.env.log.debug('Remove Multiple items')
                for deleteCase in args['test_case_step_id']: 
                    sql = "DELETE FROM test_case WHERE case_id = '%s'" % (deleteCase)
                    self._exec_sql(sql)
            
            
            '''
                Update list of items 
            '''
            self.update_test_case_order(args['plan_id'])     
        
    def _exec_sql(self, sql):
        '''
            Excute sql
        '''
        #self.env.log.debug('EXECUTING SQL ----- ')
        self.env.log.debug(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()


    def update_test_case_order(self, plan_id):
        '''
            Reorder test cases after deleting an item 
            Update after delete
        '''
        update_order = 1
        cases = self.get_test_case(plan_id)
        self.env.log.debug('Updating test order after delete')
        for case in cases:
            '''
                Cycle through the cases an update the order
            '''
            
            sql = "UPDATE test_case SET test_order = '%s' WHERE  case_id = '%s'" % (update_order, case['case_id'])
            self._exec_sql(sql)
            update_order += 1


    



    def set_test_case_order(self, dataset):
        '''
            Reorder testing steps...
        '''
        args = dataset.args
        
        if (args['table_order'] == 'NOCHANGE'):
            pass
        else: 
            order = args['table_order'].split(',')
            new_order = 1
            for item in order[:-1]:
                sql = "UPDATE test_case SET test_order = '%s' WHERE plan_id = '%s' AND  case_id = '%s' AND active = 1" % (new_order, args['plan_id'], item)
                self._exec_sql(sql)
                new_order += 1
            
    def set_test_case(self, dataset):
        '''
            Insert test case records into database 
        '''
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        sql = """insert 
        into test_case 
        (
        plan_id,
        item_name,
        test_order,
        test_procedure,
        expected_result,
        create_ts, 
        update_ts, 
        active
        ) 
        values (%s,%s,%s,%s,%s,%s,%s,%s) """
        cursor = self.db.cursor()
        cursor.execute(sql, (args['plan_id'], args['item_name'], args['item_count'], args['test_procedure'], args['expected_result'],  _now_ts, _now_ts, 1 ))
        rowID = cursor.lastrowid
        self.db.commit()
        return rowID
    '''
    def ws_set_test_case(self, dataset):
        
        #Insert test case records into database 
        
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        sql = """insert 
        into test_case 
        (
        plan_id,
        item_name,
        test_order,
        test_procedure,
        expected_result,
        create_ts, 
        update_ts, 
        active
        ) 
        values (%s,%s,%s,%s,%s,%s,%s,%s) """
        cursor = self.db.cursor()
        cursor.execute(sql, (args['plan_id'], args['item_name'], args['item_count'], args['test_procedure'], args['expected_results'],  _now_ts, _now_ts, 1 ))
        lastRow = db.lastrowid
        self.db.commit()
        return lastRow
    '''
    def insert_test_log(self, dataset):
        '''
        Write to the testing log
        '''
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        sql = """INSERT 
        INTO test_log
        (
        register_id,
        case_step_id,
        result_status,
        actual_result,
        update_ts
        )
        values (%s, %s, %s, %s, %s ) 
        """
        cursor = self.db.cursor()
        cursor.execute(sql, (args['TestReg'], args['Step'], args['ajax_request'], args['step_result'],  _now_ts ))
        self.db.commit()
    
    

        
        
    
    
    
    
    
    def get_register_info(self, reg_id):
        '''
        Collect information about the test item 
        from the testing register
        '''
        #columns = ['reg_id','plan_id','tester','test_detail','build_number','create_ts','_plan_id','plan_name','test_type','milestone','description','creator','create_ts','update_ts','active']
        columns = ['reg_id','plan_id','tester','test_detail','custom_detail', 'test_condition', 'test_comments', 'create_ts','_plan_id','plan_name','test_type','milestone','description','creator','create_ts','update_ts','active']
        sql = """SELECT
        *
        FROM
        test_register r
        LEFT JOIN 
        test_plan p
        ON
        r.plan_id = p.id
        WHERE
        r.id = %s
        """ % (reg_id)
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        reg_details = dict(zip(columns, row))
        return reg_details
    
    def get_ticket_by_step(self, step, reg_id):
        '''
        Lookup other ticket for this step within this plan
        '''
        #columns = ['reg_id','plan_id','tester','test_detail','build_number','reg_create_ts', 'ticket_id','register_id','plan_id','case_step_id','log_create_ts']
        columns = ['ticket_id','status', 'resolution', 'sqa_review']
        sql = """SELECT
        t.ticket_id, q.status, q.resolution, c.value
        FROM
        test_register r
        LEFT JOIN 
        test_ticket t
        ON
        r.plan_id = t.plan_id 
        AND t.case_step_id = %s
        LEFT JOIN
        ticket q
        ON q.id = t.ticket_id
        LEFT JOIN
        ticket_custom c
        ON
        t.ticket_id = c.ticket
        AND
        c.name = 'sqa_review'
        WHERE
        r.id = %s
        order by t.create_ts desc
        """ % (step, reg_id)
        
        
        
        #self.env.log.debug('[get_ticket_by_step] SQL = %s' % sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        ticket_list = [dict(zip(columns, case)) for case in cursor]
        return ticket_list
    
    
    def create_sqa_ticket(self, dataset):
        '''
        Create ticket, publish results to various tables
        Ticket Creation
        1.) Create reference to ticket data model
        2.) Set ticket fields using data passed in from testing form
        3.) Set ticket data in ticket database, get ticket ID
         
        
        '''
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        
        ts = TicketSystem(self.env)
        fields = ts.get_ticket_fields()
        ''' Create ticket model reference '''
        ticket = ticket_model.Ticket(self.env)
        
        '''
        Get information about the test from the testing register.
        '''
        self.env.log.debug('Getting Testing information from REGISTER')
        test_detail = self.get_register_info(args['reg_id'])
        
        
        
        '''
        Set ticket properties
        Find values from system and update 
        fields based on data provided from user...
        '''
        
        for field in fields:
            name = field['name']
            ticket[name] = args[name]  
        
        '''
        Reset some custom fields used for testing. 
        Add the following:
        
        *Description*
        1.) link to test execution run /sqa/exec/3/21/run

        
        '''
        
        desc = """Error Report for Test Run [%s]
Expected Result:
See Step ID [%s] -> [/sqa/exec/%s/%s/run?step_error=%s]
        
Actual Result:
%s """ % (test_detail['reg_id'], args['case_step_id'], test_detail['plan_id'], test_detail['reg_id'], args['case_step_id'], args['description'])
        
        
        '''
        SQA Managed ticket attributes
        '''
        ticket['description'] = desc
        ticket['summary'] = "Defect in testing step(%s)" % (args['case_step_id'])
        ticket['milestone'] = test_detail['milestone']
        '''
        Creator of the test in the default ticket owner. 
        Typically this would be a QA admin a person that owns the test 
        and testing process. This person would be responsible for reviewing 
        the defect and presenting during a project review. 
        '''
        
        
        '''
        Update and ticket information that was captured 
        during the registration process
        '''
        custom_details = json.loads(test_detail['custom_detail'])
        for detail in custom_details:
            '''
            Set the ticket values from register
            '''
            ticket[detail['name']] = detail['value']
        
        
        '''
        Prevent model from over writing data
        '''
        
        if ticket['owner'] == "UNDEFINED":
            '''
            If the user has not set this value 
            use the SQA default (test creator)
            '''
            ticket['owner'] = test_detail['creator']
        if ticket['reporter'] == "UNDEFINED":
            '''
            If the reporter is not set use the SQA default 
            Default: Current User
            '''
            ticket['reporter'] = dataset.authname
        
        if ticket['keywords'] == "UNDEFINED":
            '''
            If the reporter is not set use the SQA default 
            Default: Test Case Name
            '''
            ticket['keywords'] = test_detail['plan_name']

        if ticket['status'] == "UNDEFINED":
            '''
            Create ticket with status of NEW
            '''
            ticket['status'] = 'new'
        
        '''
        Clear Resolution
        '''
        ticket['resolution'] = None
            
        self.env.log.debug('Creating ticket')
        ticket.insert(when=None)
        Ticket_id = ticket.id
        self.env.log.debug("New Ticket ID = %s" % (Ticket_id) )
        
        '''
        Update sqa ticket table
        '''
        sql = """INSERT INTO test_ticket
        values (%s, %s, %s, %s, %s)
        """ 
        
        cursor = self.db.cursor()
        cursor.execute(sql, (Ticket_id, test_detail['reg_id'], test_detail['plan_id'], args['case_step_id'], _now_ts ))
        self.db.commit()
        
        return Ticket_id
        

    # ==[+]== SQA Reports Section ==[+]==
    '''
    Return test case metrics. Metrics Include:
    1.) Recently created Test Plans
    2.) Recently created Test Cases
    3.) Number of Test Registrations
    4.) Number of reported defects
    5.) Number of newly created items
    '''
    def get_test_case_report(self):
        '''
        Return test case metrics. Metrics Include:

        '''


    def get_test_metrics(self):
        '''
        Return a set of results for
        '''
        

    def get_ticket_report(self):
        '''
        Return a set of tickets created within a time period
        '''
        
        


    # ==[-]== SQA Reports Section ==[-]==
    
    
    
    # ==[+]== SQA Log Section ==[+]==
    
    def get_log_index(self):
        '''
        Return a listing of test search criteria
        '''
        
        resultset = {}
        sortset = {}
        dataset = []
        '''
        CROSS REFERENCE THE COLUMS LIST WITH PATAMETERS
        '''
        #columns = ['Plan ID','Tester','Test Case Name','Test Type','Milestone']
        columns = ['Tester','Test Case Name','Test Type','Milestone']
        sql = """SELECT
        r.tester, p.plan_name, p.test_type, p.milestone
        FROM 
        test_register r
        LEFT JOIN
        test_plan p
        ON 
        r.plan_id = p.id
        GROUP BY r.plan_id, r.tester, p.plan_name, p.test_type, p.milestone
        ORDER BY
        r.create_ts desc
        
        """
        
        '''
        sql = """SELECT
        r.plan_id, r.tester, p.plan_name, p.test_type, p.milestone
        FROM 
        test_register r
        LEFT JOIN
        test_plan p
        ON 
        r.plan_id = p.id
        GROUP BY r.plan_id, r.tester, p.plan_name, p.test_type, p.milestone
        ORDER BY
        r.create_ts desc       
        """
        '''
        cursor = self.db.cursor()
        cursor.execute(sql)
        result = [dict(zip(columns, case)) for case in cursor]   
        
        '''
        DB may vary 
        Parse Unique
        '''
        
        for db_row in result:
            '''
            Set resultset
            Index through database rows
            '''
            #self.env.log.debug('[get_log_index] DB_ROW = %s' % db_row )
            for row_key in db_row.keys():
                '''
                Index through keys in database row
                count number of instances.
                '''
                #self.env.log.debug('[get_log_index] ROW_KEY = %s' % row_key )
                
                '''
                Check / Set result set
                '''
                if not resultset.has_key(row_key):
                    '''
                    If a result set container does not exist
                    then create container and continue inspection.
                    '''
                    resultset[row_key] = {}
                    
                    
                
                
                if resultset[row_key].has_key(db_row[row_key]):
                    '''
                    Determine if result set has this key
                    update instance number
                    '''
                     
                    resultset[row_key][db_row[row_key]] += 1
                else:
                    '''
                    Create new instance
                    '''
                    resultset[row_key][db_row[row_key]] = 1
                    
                            
        #self.env.log.debug('[get_log_index] RESULTSET = %s' % resultset )
        
        '''
        Convert to unique list of key values
        '''
        for key in resultset:
            '''
            Get embedded key value per category
            '''
            sortset[key] = resultset[key].keys()
            
        
        for key in sortset:
            
            '''
            Format into list of dictionaries
            '''
            dataset.append( {'name': key, 'type':'select', 'options': sortset[key], 'label': key } )
        
        
        
        #self.env.log.debug('[get_log_index] DATASET = %s' % dataset )
        return dataset
    
    

    def get_logs_by_search_attrs(self, dataset):
        '''
        Select a test log by registration_id
        '''
        args = dataset.args
        _now = datetime.now(utc)
        _now_ts = to_utimestamp(_now)
        
        '''
        Search the registration and log tables to find test logs.
        Publish results to page.
        Construct several requests
        
        1.) Show summary list
        2.) Hide comment fields
        3.) Create ajax calls for log listing. 
        '''
        columns = ['reg_id','plan_id','tester','plan_name','test_type','milestone', 'last_run', 'test_detail', 'test_condition', 'test_comments' ]
        
        sql = """SELECT 
        r.id, r.plan_id, r.tester, p.plan_name, p.test_type, p.milestone, 
        max(l.update_ts) as lastRun, r.test_detail, r.test_condition, r.test_comments
        FROM
        test_register r
        LEFT JOIN
        test_log l
        ON
        r.id = l.register_id
        LEFT JOIN 
        test_plan p
        ON
        r.plan_id = p.id 
        """
        ####
        
        '''
        SearchList is used for those items returned by the test search form 
        ''' 
        #searchList = ['Plan ID','Tester','Test Case Name','Test Type','Milestone']
        searchList = ['Tester','Test Case Name','Test Type','Milestone']
        sqlWhere = []
        
        for formParam in searchList:
            if args[formParam] != 'NoValue':
                '''
                User set a search value
                '''
                #if formParam == 'Plan ID':
                #    sqlWhere.append("r.plan_id = '%s' " % args[formParam])
                if formParam == 'Tester':
                    sqlWhere.append("r.tester = '%s' " % args[formParam])
                elif formParam == 'Test Case Name':
                    sqlWhere.append("p.plan_name = '%s' " % args[formParam])
                elif formParam == 'Test Type':
                    sqlWhere.append("p.test_type = '%s' " % args[formParam])
                elif formParam == 'Milestone':    
                    sqlWhere.append("p.milestone = '%s' " % args[formParam])

        if len(sqlWhere) >= 1:
            sql += "WHERE "
        sql += ' AND '.join(sqlWhere)
        sql += """GROUP BY r.id, p.id
        ORDER BY r.create_ts desc
        Limit %s
        """ % (args['row_count'])
        self.env.log.debug('[get_logs_by_search_attrs] SQL = %s' % sql )
        
     
        cursor = self.db.cursor()
        cursor.execute(sql)
        logset = [dict(zip(columns, case)) for case in cursor]
        
        for s in logset:
            s['last_run'] = from_utimestamp(s['last_run'])
            self.env.log.debug('[get_logs_by_search_attrs] Convert JSON = %s' % s['test_detail'] )
            s['test_detail'] = json.loads(s['test_detail'])
        '''
        Format Log Set
        '''
        
        
        
        
        return logset
    
    def get_log_details(self, reg_id):
        '''
        Ajax request for log details
        '''
        columns = ['log_id','register_id','case_step_id','result_status','actual_result','update_ts','ticket_id','__register_id','__plan_id','__case_step_id','tickt_create_ts']
        sql = """SELECT 
        * 
        FROM 
        test_log l 
        LEFT JOIN
        test_ticket t 
        ON 
        l.register_id = t.register_id 
        AND
        l.case_step_id = t.case_step_id 
        WHERE 
        l.register_id = '%s' 
        ORDER BY id asc
        """ % reg_id
         
        cursor = self.db.cursor()
        cursor.execute(sql)
        logdetail = [dict(zip(columns, case)) for case in cursor]
        for s in logdetail:
            s['update_ts'] = from_utimestamp(s['update_ts'])
            s['tickt_create_ts'] = from_utimestamp(s['tickt_create_ts'])
        

        '''
        Add step numbers from test run archive
        Ensure the proper ordering
        '''
        
        jsonArchive = self.getJsonArchive(reg_id)
        stepById = {}

        for logitem in jsonArchive['json']:
            '''
            Add log step number
            '''
            self.env.log.debug('LogItem = %s' % logitem  )
           
            stepById[logitem['case_id']] = logitem['test_order']
        
        
        for logItem in logdetail:
            '''
            Parse each line item and add the test order value
            Used to detect if steps were executed out of order
            ''' 
            try:
                logItem['test_order'] = stepById[logItem['case_step_id']]
            except:
                '''
                May not be a testing step
                '''
                pass
        
        
        
        return logdetail


""" TEST SQL FROM get_logs_by_search_attrs
SELECT
*
FROM 
test_register r
LEFT JOIN
test_log l,
test_plan p
ON 
r.id = l.register_id
AND
r.plan_id = p.id
WHERE
p.plan_name = 'TEST'
ORDER BY
r.create_ts desc
"""       

"""
 Passing in this data {'logset': [
 {'plan_id': 2, 'tester': u'admin', 'test_condition': u'sdafsdf', 'test_comments': u'asdfasdf', 'test_type': u'Functional', 'last_run': datetime.datetime(2011, 5, 1, 23, 22, 7, 620247, tzinfo=<FixedOffset "UTC" 0:00:00>), 'reg_id': 1, 'milestone': u'CI Phase 2', 'test_detail': {u'browser_info': {u'version': u'1.9.2.15', u'user_agent': u'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.15) Gecko/20110303 Ubuntu/10.10 (maverick) Firefox/3.6.15', u'browser': u'Firefox'}, u'client_info': {u'client_platform': u'Linux x86_64'}}, 'plan_name': u'New ECM Performance Test'}], 'index': [{'label': 'Milestone', 'type': 'select', 'name': 'Milestone', 'options': [u'CI Phase 2']}, {'label': 'Plan ID', 'type': 'select', 'name': 'Plan ID', 'options': [2]}, {'label': 'Test Case Name', 'type': 'select', 'name': 'Test Case Name', 'options': [u'New ECM Performance Test']}, {'label': 'Test Type', 'type': 'select', 'name': 'Test Type', 'options': [u'Functional']}, {'label': 'Tester', 'type': 'select', 'name': 'Tester', 'options': [u'admin']}], 'result_num': 1}
 

"""
        
    # ==[-]== SQA Log Section ==[-]==

        
        