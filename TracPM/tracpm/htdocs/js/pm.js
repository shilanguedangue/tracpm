


$('#pm-cal-submit').live('click', function() {
	// Reload 
	$('#pm-cal').fullCalendar( 'refetchEvents' );
});

$('#pm-cal-event').live('click', function(){
	//alert('event btn pressed');
	$('#createEventDialog').dialog('open');
});



$(document).ready(function() {
    //Load Base Calendar      
	    
	$('#createEventDialog').dialog({
		autoOpen: false,
		height: 400,
		width: 300,
		modal: true,
		//buttons: {		}
		close: function() {
			allFields.val( "" ).removeClass( "ui-state-error" );
		}
		
	});

	

	
	
	
	$('#pm-cal').fullCalendar({
    	header: {
        	left: 'prev,next today',
            center: 'title',
            right: 'month,basicWeek,basicDay'
        },
        editable: false,

        
        // Define Event Sources (ajax callback)
        events: function(start, end, callback) {

        	// Get list of options
        	var pm_data = $('#prefs').serializeArray();
        	// Add Calendar UI start date (Unix Time Stamp)
        	pm_data.push({
        		name: 'start',
        		value: Math.round(start.getTime() / 1000)
        	});
        	//Add Calendar UI end date (Unix Time Stamp)
        	pm_data.push({
        		name: 'end',
        		value: Math.round(end.getTime() / 1000)
        	});
        	/*
        	pm_data.push ({
        		name: '_trac_url',
        		value: $('#_pm_trac_url').val()
        	});
        	*/
        	$.ajax({
        		type: 'GET',
        		cache: true,
        		dataType: 'json',
        		// URL from main.html prefs form...
        		url: $('#_pm_ajax_url').val(),
        		data: pm_data,
        		success: function(response_data) {
        			// Send results back...
        			callback(response_data);
        		},
        		error: function() {
                     alert('there was an error while fetching events!');
                 }
        	});  	
        }
        

	});
});































