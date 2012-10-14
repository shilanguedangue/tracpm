'''
    Set of common functions used to manage SQA activities
'''

# Standard imports.
import time

# Trac imports.
from trac.core import *
from trac.config import *
from trac.admin.api import IAdminPanelProvider
from trac.perm import IPermissionRequestor, PermissionCache, PermissionSystem
from trac.resource import IResourceManager
from trac.ticket.api import TicketSystem



class TracSqaConfig(Component):
    implements(IPermissionRequestor, IResourceManager)
    
    def __init__(self):
        self.log.debug('Starting Sqa Testing System API')
        ts = TicketSystem(self.env)
        '''
        When the object is created collect 
        a set of tickets configured in this
        running instance of track
        '''
        self.ticket_fields = ts.get_ticket_fields()
    
    def _get_config(self, config_param):
        '''
        General purpose function to collect sqa config values
        '''
        config = self.config.get('sqa', config_param)
        self.log.debug('----Read this from the config file %s' % (config) )
        
        return config.split(',')
    
    def get_test_types(self):
        '''
            Reads the config file (trac.ini)
            Process section [test-type] 
        '''
              
        return self._get_config('test_type') 
    
    def get_ticket_config(self):
        '''
        Return a listing of fields to display 
        in the test ticket dialog
        Note: By default the dialog only display the description field. Not expressed in this section
        '''

        return self._get_config('ticket_config')
    
    def get_register_config(self):
        '''
        Return a listing of fields to display 
        in the test register dialog
        Note: By default the register dialog does not include any ticker parameters
        '''
        fields = []
        param_list = self._get_config('register_config')
        for parm in param_list:
            '''
            Attempt to get the ticket values
            '''
            fields.append(self.get_ticket_attr(parm))
        return fields
    
    def get_ticket_attr(self, field_name=None):
        '''
        '''
        if not field_name:
            '''
            return all rows
            '''
            return self.ticket_fields
            
        else:
            '''
            If a particular field is requested return single set 
            '''     
            
            try:
                '''
                Attempt to get set
                '''
                for ticket_set in self.ticket_fields:
                    if ticket_set['name'] == field_name:
                        '''
                        Return set if match is found
                        ''' 
                        return ticket_set
                    
                return {}
                
            except:
                '''
                Something is off
                '''
                self.log.debug('[get_ticket_attr] failed to find ticket field by name'  )
        
           
        
    def get_sqa_tickets(self):
        '''
        Return a list of tickets to display in the test ticket dialog
        Used "default_fields" to set a list of field to always display
        '''
        # Default ticket attributes
        default_fields = ['description']
        
        ticket_config = self.get_ticket_config()
        for default in default_fields:
            ticket_config.append(default)
        
        
        for ticket_set in self.ticket_fields:
            '''
            Step through ticket list 
            update set property "display" used to determine
            which fields are visible in the sqa ticket interface 
            '''
            for field in ticket_config:
                '''
                Compare ticket_set items to the trac.ini file
                '''
                if ticket_set['name'] == field:
                    '''
                    Set the display property
                    '''
                    ticket_set['display'] = 'yes'
        
        '''
        Return Updated ticket fields
        '''
        return self.ticket_fields
    
    
    
    def get_ticket_args(self, dataset):
        '''
        Pass in a dataset from a request 
        Parse the names of fields that are tickets
        return a dataset with only ticket values
        '''
        ticket_items = []
        self.log.debug('[get_ticket_args] Initial data set: %s ' % dataset)  
        for ticket_set in self.ticket_fields:
            '''
            index through ticket fields
            '''
            try:
                if dataset.has_key(ticket_set['name']):
                    '''
                    If the dataset has a ticket attribute 
                    then add the key value pair to the list
                    '''
                    ticket_items.append(ticket_set['name'])
            except:
                '''
                Maybe its not a dictionary
                ''' 
                self.log.debug('[get_ticket_args] Failed to complete  dataset processing [%s] ' % dataset)   
                
        return ticket_items
                
                
                    
class TracSqaPermissions(Component):
    '''
        Add plugin permissions 
    '''
    

    implements(IAdminPanelProvider, IPermissionRequestor)


    # IPermissionRequestor methods
    def get_permission_actions(self):
        actions = ['SQA_EDIT', 'SQA_CREATE']
        return actions + [('SQA_ADMIN', actions)]
       
    def get_resource_realms(self):
        yield 'sqa'
    # IAdminPanelProvider methods
    '''
    def get_admin_panels(self, req):
        if 'PERMISSION_GRANT' in req.perm or 'PERMISSION_REVOKE' in req.perm:
            yield ('general', _('General'), 'perm', _('Permissions'))
    '''



    
                         
                         