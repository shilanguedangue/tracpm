import re
from genshi.builder import tag
from pkg_resources import resource_filename
from trac.core import *
from trac.resource import *
from trac.web import IRequestHandler
from trac.resource import Resource, ResourceNotFound, get_resource_url, \
                         render_resource_link, get_resource_shortname
from trac.web.chrome import INavigationContributor, ITemplateProvider, add_notice, add_stylesheet, add_warning, Chrome, add_javascript
from trac.prefs.api import IPreferencePanelProvider
from trac.ticket import Milestone
from trac.mimeview.api import Mimeview, IContentConverter, Context
from trac.wiki.model import WikiPage
from trac.util.datefmt import from_utimestamp, to_utimestamp, utc, utcmax, time
from trac.wiki import IWikiSyntaxProvider, WikiParser
from trac.wiki.formatter import format_to_html
from trac.perm import IPermissionRequestor

# Local plugin components 
from tracpm.model import *
#from tracsqa.api import *
'''
Helpful Links
http://trac.edgewall.org/wiki/TracDev
http://www.edgewall.org/docs/tags-trac-0.12.2/epydoc/
http://groups.google.com/group/trac-dev
http://groups.google.com/group/trac-users
'''

class SqaPlugin(Component):
    '''
    Future Integration Reference 
    Trac 0.13 API 
    http://www.edgewall.org/docs/trac-trunk/html/api/index.html
    '''
    implements(INavigationContributor, IRequestHandler, ITemplateProvider, IPreferencePanelProvider, IPermissionRequestor)
    
    
    def get_permission_actions(self):
        view = 'SQA_VIEW'
        filter = ('SQA_FILTER', ['SQA_VIEW'])
        order = ('SQA_ORDER', ['SQA_VIEW'])
        add = ('SQA_ADD', ['SQA_VIEW'])
        edit = ('SQA_EDIT', ['SQA_VIEW'])
        delete = ('SQA_DELETE', ['SQA_VIEW'])
        execute = ('SQA_EXECUTE', ['SQA_VIEW'])
        admin = ('SQA_ADMIN', ['SQA_ORDER',
          'SQA_FILTER', 'SQA_ADD', 'SQA_EDIT',
          'SQA_DELETE', 'SQA_VIEW'])
        return [view, filter, order, add, edit, delete, admin, execute]
    
    
    
    def get_active_navigation_item(self, req):
        return 'sqa'
        
    def get_navigation_items(self, req):
        '''
            Normal 
            ref=req.href.pm()
            
            Set default page
            href=req.href.pm('/')
        '''
        yield ('mainnav', 'sqa',
               tag.a('PM', href=req.href.pm('/')))
            
        # -- Request Handler Methods
    def match_request(self, req):
        ''' REQUEST DISPATCHER - Controls what request this dispatcher will manage
        in this case the dispatcher is repsonsible for the sqa domain.
        Accept any combination of values on the usr string
        pass request to parser to determine matching template'''
        
        return re.match(r'^/pm(?:/(.*)|$)', req.path_info)

    def process_request(self, req):
        '''
            Create a resource realm for the test item
        '''
        context = Context.from_request(req)
        context.realm = 'pm'
        
	SqaModel = TestData(self.env, None)
        SqaApi = TracSqaConfig(self.env)
        ''' Render Content ''' 
        director = self._parse_url_request(req)
        data = {} 
        '''
            Used in context see test case
        '''
        
        '''
        Note:
        Un-comment next line to enable test plan listing in nav panel
        '''
        #data['nav_plan'] = SqaModel.getTestPlanMilestones()
        
        pagename = req.args.get('page', 'TracSqa')
        page = WikiPage(self.env, pagename)

        
        '''
            Add HTDOC stylesheets and javascript
        '''
        #add_stylesheet(req, 'sp/css/sqa.css')
        add_stylesheet(req, 'sp/css/sqa_1.css')
        add_stylesheet(req, 'sp/css/jquery-ui-1.8.16.sqa.css')
        # Jquery Table plugin uses trac default version of jquery 1.4.2 (as of version 0.12.2)
        
        add_javascript(req, 'common/js/wikitoolbar.js')
        add_javascript(req, 'common/js/folding.js')
        add_javascript(req, 'sp/js/jquery.validate.min.js')
        add_javascript(req, 'sp/js/jquery-ui-1.8.16.custom.min.js')
        add_javascript(req, 'sp/js/sqa_jquery.js')
        add_javascript(req, 'sp/js/jquery.tablednd_0_5.js')
        #add_javascript(req, 'sp/js/ws_tcTable.js')

        
        ''' REQUEST CONTROLLER - Determine the actions to perform 
            req.args - reurn a dictionary of key value pairs passed as url arguments
            http://trac.edgewall.org/browser/trunk/trac/web/api.py
            Working with the REQ Objects
            In this example if the following URL is passed to this requestor it will render the following
            
            Example Code: 
            path = req.args.get('action', 'view')
            
            scenarios
            1.) Pass GET arg
                URL: http://trac/this/sqa/foo?action=new
                Result
                path = [new]
            2.) No Argument passed 
                URL: http://trac/this/sqa/foo
                Result
                path = [view] - returns default defined in get request....


        '''
        
        
        self.log.debug("Got this request: %s and %s" % (req, req.args))
        '''Break out the type of handlers used to servicer requests'''    
        # --------------------------------------------------------------
        #                     GET Requests
        # --------------------------------------------------------------
        '''
        Setup post requests for ajax calls
        '''

        if (req.args.has_key('ajax_request')):
            '''
            Process AJAX request
            '''    
            self.log.debug("Processing AJAX Request %s" %(req.args['ajax_request']) )    
            if (req.args['ajax_request'] == 'Passed'):
                '''
                Process the Ajax Request
                '''
                self.log.debug("Passing AJAX request" ) 
                SqaModel.insert_test_log(req)
                return
            elif (req.args['ajax_request'] == 'Failed'):
                '''
                Process the Ajax Request
                '''
                self.log.debug("Passing AJAX request" ) 
                SqaModel.insert_test_log(req)
                return
            elif (req.args['ajax_request'] == 'Event'):
                '''
                Process the Ajax Request
                '''
                
                SqaModel.insert_test_log(req)
                return
            elif (req.args['ajax_request'] == 'GetTestTicketForm'):
                '''
                    Accesss the ticket system
                '''
                ts = TicketSystem(self.env)
                fields = ts.get_ticket_fields()
                ticket_config = SqaApi.get_ticket_config()
                '''
                Always display description
                '''
                ticket_config.append('description')
                self.log.debug("TICKET CONFIG = %s " % (ticket_config))
                '''
                Add a field to the ticket dictionary 
                indicates the field can be displayed in the testing window.
                '''
                for tdict in fields:
                    for field in ticket_config:
                        if tdict['name'] == field:
                            #self.log.debug("-Match- TICKET Check [%s = %s] " % (tdict['name'], field ))
                            tdict['display'] = 'yes'

                
                #self.log.debug("---->>>> Ticket Fields =====> %s" %(fields) )
                data['step'] = req.args['Step']
                data['reg'] = req.args['TestReg']
                try:
                    data['plan'] = director['args'][2]
                except:
                    data['plan'] = 'Undefined'
                
                
                data['ticket'] = fields
                ''' Render page '''
                return 'sqa/sqaTicketForm.html', data, None
            elif (req.args['ajax_request'] == 'GetLog'):
                '''
                Fetch the log set and return the result
                '''
                
                data['test_log'] = SqaModel.get_log_details(req.args['regid'])
                data['log_count'] = len(data['test_log'])
                self.log.debug("Sending Ajax Data:: %s" %(data) )
                return 'sqa/testLogDetail.html', data, None
            elif (req.args['ajax_request'] == 'GetCases'):
                data['plans'] = SqaModel.get_test_plans(req.args['milestone'], True)
                self.log.debug("Sending Ajax Data:: %s" %(data) )
                return 'sqa/ajax_plans.html', data, None
                
            
        # --------------------------------------------------------------
        #                     POST Requests 
        # --------------------------------------------------------------
        if (req.method == 'POST'):
            '''
            Post handler for form data
            When a post is submitted, route form data to the proper 
            form processing handler. 
            If there is an error processing the data post a notice to the screen 
            
            Once complete pass back control to the Content Rendering System.
            
            '''
            if (req.args.has_key('sqa_control')):
                self.log.debug("Processing Post request for %s" %(req.args['sqa_control']) )
                if (req.args['sqa_control'] == 'Add Test Case'):
                    '''
                        Send the request object 'req' to the 
                        sqa manager for processing form data
                    '''
                    SqaModel.set_test_plan(req)
                elif (req.args['sqa_control'] == 'add_case'):
                    
                    '''
                        Send the request object 'req' to the 
                        sqa manager for processing form data
                    '''
                    SqaModel.set_test_case(req)
                elif (req.args['sqa_control'] == 'Reorder Steps'):
                    '''
                        CAll this control
                    '''
                    SqaModel.set_test_case_order(req)
               
               
                elif (req.args['sqa_control'] == 'Remove Step'):
                    '''
                        CAll this control
                    '''
                    SqaModel.remove_test_step(req)
                elif (req.args['sqa_control'] == 'Remove Test Case'):
                    '''
                        CAll this control
                    '''
                    SqaModel.remove_test_case(req)
                elif (req.args['sqa_control'] == 'Disable Test Case'):
                    '''
                        CAll this control
                    '''
                    SqaModel.disable_test_case(req)
                elif (req.args['sqa_control'] == 'Disable Step'):
                    '''
                        CAll this control
                    '''
                    SqaModel.disable_test_case_step(req)
                elif (req.args['sqa_control'] == 'Register Test'):
                    '''
                        Register test in testing system 
                    '''
                    test_reg = SqaModel.set_test_register(req)
                    '''
                        Redirect to new test registration
                    '''
                    SqaModel.setJsonArchive(test_reg['plan_id'], test_reg['reg_id'])
                    '''
                        Archive the test to json format
                        Redirect a GET request to display the test form
                        
                    '''
                    req.redirect(req.href.sqa('exec', test_reg['plan_id'], test_reg['reg_id'], 'run' ))
            
                elif (req.args['sqa_control'] == 'End Test'):
                    '''
                        Test ended
                    '''
                    
                    data['complete'] = '1'
                    self.log.debug("[end test] - Passing in this data %s" %(data) )
                    return 'sqa/testexec.html', data, None
                
                elif (req.args['sqa_control'] == 'Create Ticket'):
                    '''
                    Create ticket
                    '''
                    self.log.debug("Calling Create Ticket" )
                    ticket_id = SqaModel.create_sqa_ticket(req)
                    data['ticket_created'] = ticket_id
                    '''
                    Continue to ticket_form
                    '''
                elif (req.args['sqa_control'] == 'Search Logs'):
                    '''
                    Search The logs
                    '''
                    log_search_results = SqaModel.get_logs_by_search_attrs(req)
                    data['result_num'] = len(log_search_results)
                    data['logset'] = self.renderWiki(context, log_search_results, ['test_condition', 'test_comments'] )
            if (director['route'] == 'ws_reg'):
                '''
                    Register test in testing system 
                '''
                test_reg = SqaModel.set_test_register(req)
                '''
                    Redirect to new test registration
                '''
                SqaModel.setJsonArchive(test_reg['plan_id'], test_reg['reg_id'])
                '''
                    Archive the test to json format
                    Redirect a GET request to display the test form
                    
                '''
                
                return 'sqa/inc_testRegData.html', test_reg, None
                #req.redirect(req.href.sqa('exec', test_reg['plan_id'], test_reg['reg_id'], 'run' ))
                   
                    
                    
                    
        #==============================================================
        #    Route request based on director 
        #==============================================================
        
        # --------------------------------------------------------------
        #         TEST PLAN 
        # --------------------------------------------------------------
        if (director['route'] == 'plan'):
            '''
                The default screen will present the Test plan page. 
                This page relates milestones to testing activities. 
                
            '''
            self.log.debug("Rendering Manager Page" )
            
            '''Set data '''
            data['user'] = req.authname
              
            '''
                Determine if a specific milestone is requested
                if so only render test cases related to given milestone
                
                Otherwise render complete list...
            '''
            if (req.args.has_key('milestone')):
                self.log.debug("Request Information on Milestone %s" %(req.args['milestone']) )
                data['plans'] = SqaModel.get_test_plans(req.args['milestone'])
            else:
                data['plans'] = SqaModel.get_test_plans()
            
            
            #wiki = WikiParser(self.env)
            
            data['plans'] = self.renderWiki(context, data['plans'], ['description'] )
            
            '''
            for s in data['plans']:
                
                
                rendered = format_to_html(self.env, context, s['description'])
                #data['parsed'] = wiki.parse(s['description'])
                
                
                
                s['description'] = format_to_html(self.env, context, s['description'])
                self.log.debug("This is wiki -  Parsed?  -> %s" %(rendered ))
            '''   
               

            
            data['types'] = SqaApi.get_test_types()
            
            # MOVE TO ADMIN
            data['ms_list'] = self._get_milestones()
            
            self.log.debug("[plan] - Passing in this data %s" %(data) )
            #return 'sqa/testplan.html', data, None
            return 'sqa/base.html', data, None
            '''
                END PLAN
            '''
        elif (director['route'] == 'ws_plan'):
            self.log.debug("ROUTE WS_PLAN" )
            if (req.args.has_key('milestone')):
                self.log.debug("Request Information on Milestone %s" %(req.args['milestone']) )
                data['plans'] = SqaModel.get_test_plans(req.args['milestone'])
            else:
                self.log.debug("NO MILESTONE" )
            return 'sqa/ws_plan.html', data, None
            
    
        # --------------------------------------------------------------
        #         TEST CASE 
        # --------------------------------------------------------------
        elif (director['route'] == 'case'):
            '''
                Prepare test case rendering
            '''
            
            if (director.has_key('args')):
                ''' Determine how to handle arguments 
                Ignoring them is a choice...'''
                if (director['args'][-1] == 'edit'):
                    ''' 
                        Set editing mode
                    '''
                    add_javascript(req, 'sp/js/jquery.tablednd_0_5.js')
                    data['edit'] = 'parameter here'
                
                ''' Get test plan information for given test case id'''
                data['plan'] = SqaModel.get_plan_by_id(director['args'][0])
                #data['plan'] = self.renderWiki(context, data['plan'], ['description'] )
                
                '''
                    Render the test case relative to this test plan
                '''
                data['case'] = SqaModel.get_test_case(director['args'][0])
                data['steps'] = SqaModel.get_test_step_count(director['args'][0])
                parse_fields =  ['test_procedure', 'expected_result']
                data['case'] = self.renderWiki(context, data['case'], parse_fields )
                
                '''
                WIKI RENDERING
                    Context Info
                    http://trac.edgewall.org/wiki/WikiContext
                
                context = Context.from_request(req, page.resource)
                #context = Context.from_request(req)
                rendered = {}
                for step in data['case']:
                    self.log.debug("[case] - This is a Step  %s" %(step.__getitem__('test_procedure')) )
                    item = step.__getitem__('test_procedure')
                    rendered['rendered'] = format_to_oneliner(self.env, context, item)
                
                
                data['render'] = rendered
                '''
                add_javascript(req, 'sp/js/tcTable.js')
            else:
                '''
                    Render complete listing of ALL tests 
                '''
                #data['case'] = SqaModel.get_test_case()
            
            
            self.log.debug("[case] - Passing in this data %s" %(data) )
            return 'sqa/testcase.html', data, None
        
        
        elif (director['route'] == 'ws_case'):
            '''
                Prepare test case rendering
            '''
            
            if (director.has_key('args')):
                ''' Determine how to handle arguments 
                Ignoring them is a choice...'''
                if (director['args'][-1] == 'edit'):
                    ''' 
                        Set editing mode
                    '''
                    add_javascript(req, 'sp/js/jquery.tablednd_0_5.js')
                    data['edit'] = 'parameter here'
                
                ''' Get test plan information for given test case id'''
                data['plan'] = SqaModel.get_plan_by_id(director['args'][0])
                #data['plan'] = self.renderWiki(context, data['plan'], ['description'] )
                
                '''
                    Render the test case relative to this test plan
                '''
                data['case'] = SqaModel.get_test_case(director['args'][0])
                data['steps'] = SqaModel.get_test_step_count(director['args'][0])
                parse_fields =  ['test_procedure', 'expected_result']
                data['case'] = self.renderWiki(context, data['case'], parse_fields )
                data['type'] = req.args['type']
                '''
                WIKI RENDERING
                    Context Info
                    http://trac.edgewall.org/wiki/WikiContext
                
                context = Context.from_request(req, page.resource)
                #context = Context.from_request(req)
                rendered = {}
                for step in data['case']:
                    self.log.debug("[case] - This is a Step  %s" %(step.__getitem__('test_procedure')) )
                    item = step.__getitem__('test_procedure')
                    rendered['rendered'] = format_to_oneliner(self.env, context, item)
                
                
                data['render'] = rendered
                '''
                add_javascript(req, 'sp/js/tcTable.js')
            else:
                '''
                    Render complete listing of ALL tests 
                '''
                #data['case'] = SqaModel.get_test_case()
            
            data['ticket'] = SqaApi.get_register_config() 
            self.log.debug("[case] - Passing in this data %s" %(data) )
            return 'sqa/ws_testcase.html', data, None
        
        # --------------------------------------------------------------
        #         ADMIN FORM TEMPLATE 
        # --------------------------------------------------------------
        
        elif (director['route'] == 'ws_admin_update'):
            '''
            Update / insert step return result for UI rendering 
            '''
            rowID = None
            if req.args['_action'] == 'EDIT':
                '''
                Update existing step
                '''
                data['update'] = SqaModel.update_step_by_id(req)
                self.log.debug("[ws_admin_update] - Row ID %s" %(data['update']) )
                #SqaModel.update_step_by_id(req)
                
                rowID = req.args['case_id']
                
                self.log.debug("[ws_admin_update] - Edit CASE_ID = %s" %(rowID) )
                print ""
                
                
            else:
                '''
                Insert new step based on position
                _Insert = before step
                _Append = after step
                '''
                new_row_id = SqaModel.set_test_case(req)
                self.log.debug("[ws_admin_update] - Row ID %s" %(new_row_id) )
                data['new'] = SqaModel.get_test_step_by_id(new_row_id)
                rowID = data['new']
                self.log.debug("[ws_admin_update] - (INSERT / APPEND)  CASE_ID =  %s" %(rowID) )
                
            '''
            Get the step updated information
            '''
            
            data['json_step'] = SqaModel.get_test_step_by_id(rowID)
            
            self.log.debug("[ws_admin_update] - JSON CASE_ID -> %s " %(data['json_step']) )
            data['_Update'] = 1
            return 'sqa/ajax_admin_edit.html', data, None
            
            
            
        
        
        # --------------------------------------------------------------
        #         ADMIN FORM TEMPLATE 
        # --------------------------------------------------------------
        
        elif (director['route'] == 'ws_admin_form'):
            '''
            Render a row form for the user
            '''
            
            '''
            set type or result to render in template
            Current options:
                1.) insert_admin
                2.) append_admin
                3.) delete_admin
                4.) edit_admin
            '''
            
            data[req.args['opt']] = 1
            
            '''
            If the request is for editing 
            Get data from database to load into form template
            
            '''
            #data['edit_step_id'] = "%s%s" %(req.args['step_id'], req.args['opt'])
            data['edit_step'] = "%s%s" %(req.args['step_num'], req.args['opt'])
            data['step_num'] = req.args['step_num']
            data['step_id'] = req.args['step_id']
            data['this_plan_id'] = req.args['this_plan_id']
            
            if req.args['opt'] == '_Edit':
                '''
                For items that are to be edited perform the following additional steps:
                1.) include the step ID to be changed
                2.) load step content from the database. 
                3.) send addition rendering information to UI layer for processing an edit. 
                
                '''
                #data['edit_step'] = "%s_%s" %(req.args['step_id'], 'this')
                data['step_id'] = req.args['step_id']
                data['json_step'] = SqaModel.get_test_step_by_id(req.args['step_id'])
                
            
            if req.args['opt'] == '_Update':
                '''
                Return updated fields
                '''
                
            
            '''    
            else:
                
                #Send the step number to the admin edit form
                  
                #data['edit_step'] = "%s_%s" %(req.args['step_id'], time.time())
                data['edit_step_id'] = "%s%s" %(req.args['step_id'], req.args['opt'])

            '''  
            self.log.debug("[ws_admin_form] - Passing in this data %s" %(data) )
            return 'sqa/ajax_admin_edit.html', data, None
        
               
               
        # --------------------------------------------------------------
        #         REPORT 
        # --------------------------------------------------------------
        elif (director['route'] == 'ws_report'):
            
            return 'sqa/inc_testReports.html', {}, None
        
        
        # --------------------------------------------------------------
        #         Execute Plan 
        # --------------------------------------------------------------
        elif (director['route'] == 'exec'):
            '''
                Register this version of the test case with 
                the test execution sub-system. Following the registration process
                the registration will preserve a record of the version of the test begin executed. 
                
                Current version of the software will archive test case to a XML or JSON file 
                and preserve the test revision information within subversion. 
                
                Methods:
                http://goessner.net/articles/JsonPath/
                http://json.org/xml.html
                http://code.google.com/p/simplejson/
                 
                Integration Option(s):
                http://pysvn.tigris.org/docs/pysvn_prog_guide.html
                
                Sequence
                1. ) Register Test (Setup test execution)
                1.1) Preserve test steps with test execution ID
                2.) Execute Test steps
                
            '''
            
            
            #add_javascript(req, 'sp/js/testexec.js')
            
            ''' Get test plan information for given test case id'''
            data['plan'] = SqaModel.get_plan_by_id(director['args'][0])
            '''
                Render the test case relative to this test plan
            '''
            data['user'] = req.authname
            #data['case'] = SqaModel.get_test_case(director['args'][0])
            data['steps'] = SqaModel.get_test_step_count(director['args'][0])
            '''
            Send custom ticket fields to register form 
            '''
            data['ticket'] = SqaApi.get_register_config()
            if (director.has_key('args')):
                ''' Determine how to handle arguments 
                Ignoring them is a choice...'''
                
                if (director['args'][-1] == 'run'):
                    ''' 
                        Run TEST
                        Show test steps and execute test
                    '''
                    
                    if (req.args.has_key('step_error')): 
                        data['stepError'] = req.args['step_error']
                    '''
                        Set the registration number
                    '''
                    add_javascript(req, 'sp/js/sqa_testrun.js')
                    data['reg'] = director['args'][-2]
                    data['reg_info'] = SqaModel.get_register_info(data['reg'])
                    
                    '''
                        As soon as the test is registered
                        store the values of the testing steps in the 
                        test_archive. This will preserve the test_case in the current 
                        form, allow this user to execute the steps at this point in time 
                        while allowing other test manager the ability to change the 
                        testing steps.
                    '''
                    archive = SqaModel.getJsonArchive(data['reg'])
                    '''
                    Run test from archived copy
                    
                    The archive is used to protect against the scenario below.
                    Scenario: TEST CASE EDIT
                    1.) User registers test 
                    2.) starts execution
                    3.) Execution disrupted, tester stops testing
                    4.) Test admin updates test case
                    5.) tester returns, starts testing again.
                    6.) tester confused, due to test case steps changing.
                    7.) test admin loses history of change. 
                    
                    This will perserve the steps even if the tester does not 
                    complete this test within a reasonable amount of time. 
                    
                    '''
                    data['run'] = archive['json']
                    data['run'] = self.renderWiki(context, data['run'], ['test_procedure', 'expected_result' ])
                                    
            self.log.debug("[exec] - Passing in this data %s" %(data) )
            return 'sqa/testexec.html', data, None
        
        # --------------------------------------------------------------
        #         Ticket Binding
        # --------------------------------------------------------------
    
        elif (director['route'] == 'ticket_form'):        
            '''
            Render a ticket form
            '''
            
            try:
                '''
                Copy select parameters to ticket form 
                '''
                data['step'] = req.args['step']
                data['case_id'] = req.args['case_step_id']
                data['reg'] = req.args['reg_id']
            except:
                return 'sqa/sqa_error.html', {}, None
            
            data['opened'] = SqaModel.get_ticket_by_step(data['case_id'], data['reg'] )
            self.log.debug("[ticket_form] - Opened: %s" %(data['opened']) )
            if data.has_key('ticket_created'):
                return 'sqa/testTicketForm.html', data, None
            
            data['ticket'] = SqaApi.get_sqa_tickets()

            return 'sqa/testTicketForm.html', data, None
        
        elif (director['route'] == 'ws_get_ticket_form'):
            '''Create iframe for ticket load '''
            data['step'] = req.args['step']
            data['case_id'] = req.args['case_step_id']
            data['reg'] = req.args['reg_id']


        
            return 'sqa/inc_ticketFormIframe.html', data, None
        
        
        elif (director['route'] == 'ws_ticket_form'):        
            '''
            Render a ticket form
            '''
            
            try:
                '''
                Copy select parameters to ticket form 
                '''
                data['step'] = req.args['step']
                data['case_id'] = req.args['case_step_id']
                data['reg'] = req.args['reg_id']
            except:
                return 'sqa/sqa_error.html', {}, None
            
            data['opened'] = SqaModel.get_ticket_by_step(data['case_id'], data['reg'] )
            self.log.debug("[ticket_form] - Opened: %s" %(data['opened']) )
            if data.has_key('ticket_created'):
                return 'sqa/testTicketForm.html', data, None
            
            data['ticket'] = SqaApi.get_sqa_tickets()

            return 'sqa/inc_testTicketForm.html', data, None
        
        
        # --------------------------------------------------------------
        #         Testing Logs
        # --------------------------------------------------------------
        elif (director['route'] == 'log'):
            '''
            Render testing log results
            '''
            add_javascript(req, 'sp/js/showLog.js')
            data['index'] = SqaModel.get_log_index()
            
            self.log.debug("[log] - Passing in this data %s" %(data) )
            return 'sqa/testlogs.html', data, None
        
        elif (director['route'] == 'ws_log'):
            '''
            Render testing log results
            '''
            add_javascript(req, 'sp/js/showLog.js')
            data['index'] = SqaModel.get_log_index()
            
            self.log.debug("[log] - Passing in this data %s" %(data) )
            return 'sqa/ws_testLogs.html', data, None
        # --------------------------------------------------------------
        #         Query Test Result Statistics 
        # --------------------------------------------------------------
        elif (director['route'] == 'query'):
            return 'sqa/testticket.html', {}, None
        else:
            '''unknown or default route, go to main screen'''
            return 'sqa/sqa_error.html', {}, None
    

        
        
    def renderWiki(self, context, items, convertList):
        '''
        Convert selected wiki fields from the database into html
        Return values to calling application for publishing to the web page. 
        '''
        
        for data_row in items:
            '''
            Index through data row, process select elements of record set.
            '''
            for wikify in convertList:
                data_row[wikify] = format_to_html(self.env, context, data_row[wikify])
        return items



    def get_templates_dirs(self):
        '''Reference link for genshi
        
        http://genshi.edgewall.org/wiki/Documentation/xml-templates.html
        '''
        return [resource_filename('tracsqa', 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('sp', resource_filename(__name__, 'htdocs'))]

    # IPreferencePanelProvider methods
    def get_preference_panels(self, req):
        '''Add tab to main menu preferences panel   
        '''
        yield 'sqa', 'SQA Options'

    def render_preference_panel(self, req, panel):
        '''
            Data rendered on the preferences panel.
        '''
        if req.method == 'POST':
            req.session['sqa.js.enable_debug'] = req.args.get('enable_debug', '0')
        return 'sqa/prefs_developer.html', {}


    def _get_milestones(self):
        #db = self.env.get_db_cnx()
        milestones = Milestone.select(self.env)
        return milestones
    
    def _get_test_types(self):
        '''
            Read the trac.ini file, collect the listing of test types
        '''
        return TracSqaConfig(self.env).get_test_types()
         
         
    def _parse_url_request(self, req):
        ''' Read the path string, passed from process_request
            break parts and return parsed attributes back to process request 
            for routine
        '''
        ''' Convert everything to lowercase prior to parsing'''
        parsed = {}
        string = req.query_string
        info = req.path_info
        self.log.debug("Parsing Path  => [ %s ] string [ %s ]" % (info , string ))
        self.log.debug("Parsing Path  => [ %s ]" % req)
        path_str = str(req.path_info)
        path_parts = path_str.split('/')
        
        ''' remove any blanks or doulble // from the listing.'''
        path_parts = [part for part in path_parts if part ]
        ''' 
            Removed bouncing lower 
            use list comprehension to bounce everything to lower case 
        '''
        path_parts = [part.lower() for part in path_parts]
        ''' First element is based on matching rule so skip it'''
        self.log.debug("Here is the array of items parsed  => [ %s ]" % path_parts)
        if (len(path_parts) >= 2):
            parsed['route'] = path_parts[1]
            if (len(path_parts) >= 3):
                '''
                    Each render control will determine what to do with arguments
                '''
                parsed['args'] = path_parts[2:]
        else: 
            parsed['route'] = 'error'
       
        self.log.debug("Returning this parsed list  => [ %s ]" % parsed)
        return parsed
        


        
        
