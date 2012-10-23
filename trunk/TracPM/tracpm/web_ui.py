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
'''
Helpful Links
http://trac.edgewall.org/wiki/TracDev
http://www.edgewall.org/docs/tags-trac-0.12.2/epydoc/
http://groups.google.com/group/trac-dev
http://groups.google.com/group/trac-users
'''


class PmPlugin(Component):
    '''
    Future Integration Reference 
    Trac 0.13 API 
    http://www.edgewall.org/docs/trac-trunk/html/api/index.html
    '''
    implements(INavigationContributor, IRequestHandler, ITemplateProvider, IPreferencePanelProvider, IPermissionRequestor)
    
    
    def get_permission_actions(self):
        view = 'PM_VIEW'
        filter = ('PM_FILTER', ['PM_VIEW'])
        order = ('PM_ORDER', ['PM_VIEW'])
        add = ('PM_ADD', ['PM_VIEW'])
        edit = ('PM_EDIT', ['PM_VIEW'])
        delete = ('PM_DELETE', ['PM_VIEW'])
        execute = ('PM_EXECUTE', ['PM_VIEW'])
        admin = ('PM_ADMIN', ['PM_ORDER',
          'PM_FILTER', 'PM_ADD', 'PM_EDIT',
          'PM_DELETE', 'PM_VIEW'])
        return [view, filter, order, add, edit, delete, admin, execute]
    
    
    
    def get_active_navigation_item(self, req):
        return 'pm'
        
    def get_navigation_items(self, req):
        '''
            Normal 
            ref=req.href.pm()
            
            Set default page
            href=req.href.pm('/')
        '''
        yield ('mainnav', 'pm',
               tag.a('PM', href=req.href.pm('/')))
            
        # -- Request Handler Methods
    def match_request(self, req):
        ''' REQUEST DISPATCHER - Controls what request this dispatcher will manage
        in this case the dispatcher is repsonsible for the pm domain.
        Accept any combination of values on the usr string
        pass request to parser to determine matching template'''
        
        return re.match(r'^/pm(?:/(.*)|$)', req.path_info)

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
	#return
        return [resource_filename('tracpm', 'templates')]

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('ht', resource_filename(__name__, 'htdocs'))]

    # IPreferencePanelProvider methods
    def get_preference_panels(self, req):
        '''Add tab to main menu preferences panel   
        '''
        yield 'pm', 'PM Options'

    def render_preference_panel(self, req, panel):
        '''
            Data rendered on the preferences panel.
        '''
        if req.method == 'POST':
            req.session['pm.js.enable_debug'] = req.args.get('enable_debug', '0')
        return 'pm/prefs_developer.html', {}


    def _get_milestones(self):
        #db = self.env.get_db_cnx()
        milestones = Milestone.select(self.env)
        return milestones
    
    #def _get_test_types(self):
    #    '''
    #        Read the trac.ini file, collect the listing of test types
    #    '''
    #    return TracPMConfig(self.env).get_test_types()
         
         
    def _parse_url_request(self, req):
        ''' Read the path string, passed from process_request
            break parts and return parsed attributes back to process request 
            for routine
        '''
        ''' Convert everything to lowercase prior to parsing'''
        parsed = {}
        string = req.query_string
        info = req.path_info
        #self.log.debug("Parsing Path  => [ %s ] string [ %s ]" % (info , string ))
        #self.log.debug("Parsing Path  => [ %s ]" % req)
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
        #self.log.debug("Here is the array of items parsed  => [ %s ]" % path_parts)
        if (len(path_parts) >= 2):
            parsed['route'] = path_parts[1]
            if (len(path_parts) >= 3):
                '''
                    Each render control will determine what to do with arguments
                '''
                parsed['args'] = path_parts[2:]
        else: 
            parsed['route'] = 'error'
       
        #self.log.debug("Returning this parsed list  => [ %s ]" % parsed)
        return parsed
        
    def process_request(self, req):
        '''
            Create a resource realm for the test item
        '''
        EventModel = EventData(self.env, None)
        context = Context.from_request(req)
        context.realm = 'pm'
	''' Render Content ''' 
        director = self._parse_url_request(req)
        data = {} 
        
        add_stylesheet(req, 'ht/css/pm.css')
        add_stylesheet(req, 'ht/css/fullcalendar.css')
        add_stylesheet(req, 'ht/css/jquery-ui-1.8.16.sqa.css')
                
        add_javascript(req, 'ht/js/fullcalendar.js')
        add_javascript(req, 'ht/js/jquery-ui-1.8.16.custom.min.js')
        add_javascript(req, 'ht/js/jquery.flot.js')
        add_javascript(req, 'ht/js/jquery.flot.pie.js')


        add_javascript(req, 'ht/js/pm.js')
        
        #self.log.debug("--> Got this request: %s and %s" % (req, req.args))
        
        if (req.args.has_key('areq')):
            '''
            Process AJAX request
            '''    
            #self.log.debug("Processing AJAX Request %s" %(req.args['areq']) )    
            if (req.args['areq'] == 'pm_cal_req'):
                ''' '''    
                
                json_data = EventModel.getEventData(req)
                
                #self.log.debug("JSON CONTENT - %s" %(json_data) ) 

                '''
                    BYPASS Trac template processing
                    Return RAW data feeds... no template
                '''                
                #self.log.debug("Length of Json String ----> %s" %(len(json_data)) )   
                
                req.send_header('content-length', len(json_data) )
                req.write(json_data)
                
                return 

                
                
                    
            
        return 'pm/main.html', data, None

        

        #return  
