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




class EventData(object):
    def __init__(self, env, Collection_id=None):
        '''
            Init
        '''
        self.env = env
        self.db = self.env.get_db_cnx()
        

    def getEventData(self, req):
        '''
            Get event data...
            Default
            
            Event Types
            1. Milestones
            2. Tickets
            3. ChangeSets
            4. Custom Events
        
        
        Request Example
         Got this request: 
         <Request "GET '/pm/ajax'"> and 
         {
         'pm-cal-filter': 
         [
         u'milestone', 
         u'ticket', 
         u'changeset'
         ], 
         'end': u'1352610000', 
         'start': u'1348977600',
         'pm-cal-filter-opt': 
         [
         u'milestone_complete', 
         u'ticket_closed'
         ],  
         'pm_url': u'/tracfox/pm/ajax', 
         'areq': u'pm_cal_req'
         }
        
        '''
        args = req.args
        timeframe = {'START': args['start']  , 'END': args['end']}
        
        sql_list = []
        if (args.has_key('pm-cal-filter')):
            for item in args['pm-cal-filter']:
                if (item == 'milestone') :
                    sql_string =  '''
                  SELECT 
                  'MILESTONE'        as A,
                  'NULL'             as B,
                  name               as C,
                  'NULL'             as D,
                  'NULL'             as E,
                  substr(due,1,10)   as F,
                  substr(completed,1,10) as G
                  FROM
                  milestone
                  WHERE
                    completed = 0
                    and
                    CAST (substr(due, 1,10 ) as INT) 
                  BETWEEN
                   %(START)s and %(END)s
                  ''' 
                    sql_list.append(sql_string)
                    
                elif (item == 'ticket') :
                    sql_string = '''
                  SELECT  
                  'TICKET'           as A,
                  id                 as B,
                  milestone          as C,
                  summary            as D,
                  status             as E,
                  substr(time,1,10)   as F,
                  substr(changetime,1,10) as G
                  FROM
                  ticket
                  WHERE
                  status != 'closed'
                  AND
                    CAST(substr(time, 1,10 ) as INT) 
                  BETWEEN
                   %(START)s and %(END)s
                  ''' 
                    sql_list.append(sql_string)
                elif (item == 'changeset') :
                    sql_string = '''
                  SELECT  
                  'CHANGESET'           as A,
                  rev                   as B,
                  repos                 as C,
                  message               as D,
                  author                as E,
                  substr(time,1,10)     as F,
                  substr(changetime,1,10) as G
                  FROM
                  revision
                  WHERE
                    CAST(substr(time, 1,10 ) as INT) 
                  BETWEEN
                   %(START)s and %(END)s
                  '''  
                    sql_list.append(sql_string)
     
        if (args.has_key('pm-cal-filter-opt')):
        
            for item in args['pm-cal-filter-opt']:
                if (item == 'milestone_complete') :
                    sql_string = '''
                  SELECT 
                  'MILESTONE'        as A,
                  'NULL'             as B,
                  name               as C,
                  'NULL'             as D,
                  'NULL'             as E,
                  substr(due,1,10)   as F,
                  substr(completed,1,10) as G
                  FROM
                  milestone
                  WHERE
                    CAST(substr(completed, 1,10 ) as INT) 
                  BETWEEN
                   %(START)s and %(END)s
                  '''
                    sql_list.append(sql_string) 
                elif (item == 'ticket_closed') :
                    sql_string = '''
                  SELECT  
                  'TICKET'           as A,
                  id                 as B,
                  milestone          as C,
                  summary            as D,
                  status             as E,
                  substr(time,1,10)   as F,
                  substr(changetime,1,10) as G
                  FROM
                  ticket
                  WHERE
                  status = 'closed'
                  and 
                    CAST(substr(changetime, 1,10 ) as INT) 
                  BETWEEN
                   %(START)s and %(END)s
                  ''' 
                    sql_list.append(sql_string)
     
        sql = ' UNION '.join(sql_list)
        
        __sql = '''
        SELECT 
        'MILESTONE' as TYPE, 
        'NULL' as EVENT_ID,
        name as milestone_name,
        name as TITLE,
        'STATUS-NULL' as STATUS,  
         substr(due, 1, 10), 
         substr(completed, 1, 10) as last_update
        from 
        milestone
        where
        
        UNION
        SELECT    
        'TICKET' as TYPE,
        id as EVENT_ID,
        milestone as milestone_name,
        summary as TITLE,
        status as STATUS,
        substr(time, 1, 10),
        substr(changetime, 1,10) as last_update
        from 
        ticket 
        where milestone is not NULL
        order by   
        milestone_name,  
        last_update desc
        '''
        
        
        sql = sql % ( timeframe )
        self.env.log.debug("- SQL -  %s" %(sql))
        columns = ['TYPE', 'EVENT_ID', 'MILESTONE_NAME', 'TITLE', 'STATUS', 'EVENT_START', 'EVENT_END']
        cursor = self.db.cursor()
        
        
        
        cursor.execute(sql)

        # Convert events into dictionary object
        events = [dict(zip(columns, event)) for event in cursor]
        _json_array = []
        for event in events:
            # Process event data
            if(event['TYPE'] == 'MILESTONE'):
                ''' Create a milestone event '''
                self.env.log.debug("MILESTONE %s" %(event))
                _json_array.append({'title': event['TITLE'], 'start': event['EVENT_START'],'end': event['EVENT_END']})
                #event
                #_json_array.append()
            elif event['TYPE'] == 'TICKET':
                ''' Create a milestone event '''
                self.env.log.debug("TICKET %s" %(event))
                _json_array.append({'title': event['TITLE'], 'start': event['EVENT_START'],'end': event['EVENT_END']})
            
        json_feed = json.dumps(_json_array)
        self.env.log.debug("JSON DATA %s" %(_json_array))
        return json_feed


        
'''
---- With Workflow Transitions
(select 
'MILESTONE' as TYPE, 
 'NULL' as EVENT_ID,
 name as milestone_name,
 'MILESTONE_TITLE' as TITLE,
 'STATUS-NULL' as STATUS,  
 substr(due, 1, 10), 
 substr(completed, 1, 10) as last_update
from 
milestone)
union
(select
'TICKET' as TYPE,
id as EVENT_ID,
milestone as milestone_name,
summary as TITLE,
status as STATUS,
substr(time, 1, 10),
substr(changetime, 1,10) as last_update
from ticket 
where milestone is not NULL)
union
(select
'TICKET_WORKFLOW' as TYPE,
ticket as EVENT_ID,
'NULL' as milestone_name,
'NULL' as TITLE,
newvalue as STATUS,
'NULL',
substr(time, 1, 10) as last_update
FROM ticket_change 
where field = 'status') 
order by   milestone_name,  last_update desc
'''
        
        


        