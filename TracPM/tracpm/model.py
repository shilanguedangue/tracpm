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
                  'NULL'               as C,
                  name             as D,
                  'NULL'             as E,
                  substr(due,1,10)   as F,
                  substr(due + 300000000,1,10)   as G
                  FROM
                  milestone
                  WHERE
                    completed = 0
                    and
                    CAST(substr(due, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1} + 300
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
                  substr(time + 300000000,1,10)   as G
                  FROM
                  ticket
                  WHERE
                  status != 'closed'
                  AND
                    CAST(substr(time, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
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
                    CAST(substr(time, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
                  '''  
                    sql_list.append(sql_string)
     
        if (args.has_key('pm-cal-filter-opt')):
        
            for item in args['pm-cal-filter-opt']:
                if (item == 'milestone_complete') :
                    sql_string = '''
                  SELECT 
                  'MILESTONE_CLOSED'        as A,
                  'NULL'             as B,
                  'NULL'               as C,
                  name             as D,
                  'NULL'             as E,
                  substr(completed,1,10) as F,
                  substr(completed + 300000000,1,10) as G
                  FROM
                  milestone
                  WHERE
                    CAST(substr(completed, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
                  '''
                    sql_list.append(sql_string) 
                elif (item == 'ticket_closed') :
                    sql_string = '''
                  SELECT  
                  'TICKET_CLOSED'           as A,
                  id                 as B,
                  milestone          as C,
                  summary            as D,
                  status             as E,
                  substr(changetime,1,10) as F,
                  substr(changetime + 300000000,1,10) as G
                  FROM
                  ticket
                  WHERE
                  status = 'closed'
                  and 
                    CAST(substr(changetime, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
                  ''' 
                    sql_list.append(sql_string) 
                elif (item == 'ticket_milestone') :
                    # show ticket by milestone
                    sql_string = '''
                  SELECT  
                  'TICKET_MILESTONE' as A,
                  id                 as B,
                  milestone          as C,
                  summary            as D,
                  status             as E,
                  substr(time,1,10)   as F,
                  substr(time + 300000000,1,10)   as G
                  FROM
                  ticket
                  WHERE
                    CAST(substr(changetime, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
                   '''
                    sql_list.append(sql_string) 
                elif (item == 'ticket_workflow') :
                    # needs work.... 
                    sql_string = '''
                  SELECT  
                  'TICKET_WORKFLOW'  as A,
                  ticket                 as B,
                  milestone          as C,
                  summary            as D,
                  newvalue             as E,
                  substr(time,1,10)   as F,
                  substr(changetime,1,10) as G
                  FROM
                  ticket_change
                  WHERE
                  field = 'status'
                  and 
                    CAST(substr(changetime, 1,10 ) as signed) 
                  BETWEEN
                   {0} and {1}
                  ''' 
                    sql_list.append(sql_string)
                elif (item == 'ticket_due') :
                    # Show ticket by due date 
                    sql_string = '''
                  SELECT  
                  'TICKET_DUE'               as A, -- Type
                  t.id                     as B,     -- EVENT_ID
                  t.milestone                  as C, -- MILESTONE_NAME
                  t.summary                    as D, -- TITLE
                  t.status                   as E, -- STATUS
                  strftime('%s', tc.value) +15000         as F,          -- EVENT_START (Pad for strftime calc)
                  strftime('%s', tc.value) +16000 as G  -- EVENT_END
                  FROM
                  ticket t
                  inner join ticket_custom tc on (
                    t.id = tc.ticket
                    and
                    tc.name = 'due_date'
                    and 
                    tc.value != ''
                  ) 
                  WHERE
                    CAST(strftime('%s',tc.value) as signed) 
                  BETWEEN
                   {0} and {1}
                  ''' 
                    sql_list.append(sql_string)
        sql = ' UNION '.join(sql_list)      
        
        
        sql = sql.format(timeframe['START'], timeframe['END'])
        self.env.log.debug("- SQL -  %s" %(sql))
        columns = ['TYPE', 'EVENT_ID', 'MILESTONE_NAME', 'TITLE', 'STATUS', 'EVENT_START', 'EVENT_END']
        cursor = self.db.cursor()
        
        cursor.execute(sql)
        EVENT_COLORS = {
        'MILESTONE': 'red',
        'TICKET' : 'green',
        'TICKET_DUE': '#8A4B08',
        'MILESTONE_CLOSED': 'black',
        'TICKET_CLOSED': 'grey',
        'TICKET_MILESTONE': 'blue'
        }

        # Convert events into dictionary object
        events = [dict(zip(columns, event)) for event in cursor]
        _json_array = []
        for event in events:
            # Process event data
            if(event['TYPE'] == 'MILESTONE'):
                ''' Create a milestone event '''
                #self.env.log.debug("MILESTONE %s" %(event))
                event_url = args['_trac_url'] + '/milestone/' +  event['TITLE'] 
                _json_array.append({'title': event['TITLE'], 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
                #event
                #_json_array.append()
            elif event['TYPE'] == 'TICKET':
                ''' Show milestone event '''
                #self.env.log.debug("TICKET %s" %(event))
                ticket_display = '#' + str(event['EVENT_ID']) + ' ' + event['TITLE']
                event_url = args['_trac_url'] + '/ticket/' +  str(event['EVENT_ID']) 
                _json_array.append({'title':  ticket_display, 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
            elif event['TYPE'] == 'TICKET_CLOSED':
                ''' Show tickets closed Total ticket time Open -> Closed '''
                #self.env.log.debug("TICKET %s" %(event))
                ticket_display = '#' + str(event['EVENT_ID']) + ' ' + event['TITLE']
                event_url = args['_trac_url'] + '/ticket/' +  str(event['EVENT_ID']) 
                _json_array.append({'title':  ticket_display, 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
            elif event['TYPE'] == 'MILESTONE_CLOSED':
                ''' Show milestoned closed '''
                #self.env.log.debug("TICKET %s" %(event))
                ticket_display = '#' + str(event['EVENT_ID']) + ' ' + event['TITLE']
                event_url = args['_trac_url'] + '/milestone/' +  event['TITLE'] 
                _json_array.append({'title':  event['TITLE'], 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
            elif event['TYPE'] == 'TICKET_MILESTONE':
                ''' Show Milestone based on ticket status '''
                #self.env.log.debug("TICKET %s" %(event))
                event_display = '#' + str(event['EVENT_ID']) + ' ' + event['MILESTONE_NAME']
                event_url = args['_trac_url'] + '/milestone/' +  event['MILESTONE_NAME'] 
                _json_array.append({'title':  event_display, 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
            elif event['TYPE'] == 'TICKET_DUE':
                ''' Show milestone event '''
                #self.env.log.debug("TICKET %s" %(event))
                ticket_display = '#' + str(event['EVENT_ID']) + ' ' + event['TITLE']
                event_url = args['_trac_url'] + '/ticket/' +  str(event['EVENT_ID']) 
                _json_array.append({'title':  ticket_display, 'start': event['EVENT_START'],'end': event['EVENT_END'] , 'color': EVENT_COLORS[event['TYPE']], 'url': event_url })
        json_feed = json.dumps(_json_array)
        #self.env.log.debug("JSON DATA %s" %(_json_array))
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



                  SELECT  
                  'TICKET_DUE'               as A, -- Type
                  t.id                     as B,     -- EVENT_ID
                  t.milestone                  as C, -- MILESTONE_NAME
                  t.summary                    as D, -- TITLE
                  t.status                   as E, -- STATUS
                  strftime('%s', tc.value)          as F,          -- EVENT_START
                  strftime('%s', tc.value) + 3000000    as G  -- EVENT_END
                  FROM
                  ticket t
                  inner join ticket_custom tc on (
                    t.id = tc.ticket
                    and
                    tc.name = 'due_date'
                    and 
                    tc.value != ''
                  ) 
                  WHERE
                    CAST(strftime('%s',tc.value) as signed) 
                  BETWEEN
                   1396152000 and 1399780800



'''
        


        