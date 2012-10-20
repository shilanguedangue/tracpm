


$('#pm-cal-submit').live('click', function() {
	// Reload 
	$('#pm-cal').fullCalendar( 'refetchEvents' );
});


/*
//Manual - Verified
events: [{start: '1350600300', end: '1350600300', title: 'Ticket The Future'}, {'start': '1350500281', 'end': '1350700281', 'title': 'Ticket 10000'}, {'start': '1350670268', 'end': '1350690268', 'title': 'Ticket 123'}, {'start': '1350591700', 'end': '1350594700', 'title': 'Test'}, ]
	*/
/*
events: [{"start": "1362373200", "end": "1350611732", "title": "Future"}, {"start": "1350600300", "end": "1350600300", "title": "Ticket The Future"}, {"start": "1348545600", "end": "1350611713", "title": "Old"}, {"start": "1350705600", "end": "1350611723", "title": "PM Test 2"}, {"start": "1350600281", "end": "1350600281", "title": "Ticket 10000"}, {"start": "1351569600", "end": "1350611728", "title": "PM Test 3"}, {"start": "1350600268", "end": "1350600268", "title": "Ticket 123"}, {"start": "1350187200", "end": "1350611717", "title": "PM-Test 1"}, {"start": "1350599700", "end": "1350599700", "title": "Test"}]
*/

/*
$(document).ready(function() {
    //Load Base Calendar      
	    
	
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
        	
        	$.ajax({
        		type: 'GET',
        		cache: true,
        		url: $('#_pm_ajax_url').val(),
        		data: pm_data,
        		error: function() {
                     alert('there was an error while fetching events!');
                 },
        	});  	
        }
        

	});
});

*/

/*
 *EXAMPLE 
 * 
 * $('#calendar').fullCalendar({
    events: function(start, end, callback) {
        $.ajax({
            url: 'myxmlfeed.php',
            dataType: 'xml',
            data: {
                // our hypothetical feed requires UNIX timestamps
                start: Math.round(start.getTime() / 1000),
                end: Math.round(end.getTime() / 1000)
            },
            success: function(doc) {
                var events = [];
                $(doc).find('event').each(function() {
                    events.push({
                        title: $(this).attr('title'),
                        start: $(this).attr('start') // will be parsed
                    });
                });
                callback(events);
            }
        });
    }
});

 */



$(document).ready(function() {
    //Load Base Calendar      
	    
	
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
        	
        	$.ajax({
        		type: 'GET',
        		cache: true,
        		dataType: 'json',
        		url: $('#_pm_ajax_url').val(),
        		data: pm_data,
        		success: function(response_data) {
        			// Send results back...
        			callback(response_data);
        		},
        		error: function() {
                     alert('there was an error while fetching events!');
                 },
        	});  	
        }
        

	});
});































