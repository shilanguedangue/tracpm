/*
 * ID = #
 * CLASS = .
 * 


$(document).ready(function() {
	$(’#test_ticket_frame′).load( function(){
	$(this.contentDocument).find(;
	});
});

$(’#frame2′).load( function(){
$(this.contentDocument).find(’body’).html(’This frame was modified with jQuery! Yay!!!’)
});
*/

$('#test_ticket_frame').ready(function() {
	$(this.contentDocument).find('#banner').hide();
});


$(document).ready(function() {
// render and element slow

	$("div.iframewrapper").fadeIn("slow");
	// http://simple.procoding.net/2008/03/21/how-to-access-iframe-in-jquery/
	
});

$(document).ready(function() {
// render and element slow

	  $('#TestTicket').fadeIn("slow");

});

$(document).ready(function() {
// Register pass event

	//$("#iframewarpper").fadeIn("slow");

	
	pathname = window.location.pathname;
	function countRemainingSteps() {
		/*
		 * Count the number if test items with a 
		 * radio buttion status of step_na (N/A)
		 * Data used to publish untested step count. 
		 */
		count = $('input[id=step_na]:checked').length
		return count;
	}
	

	// Get the initial count of untested steps
	initStepRemain = countRemainingSteps();
	// Update the UI
	$('#step_remain').text(initStepRemain);
	
	
	// Register pass event
	$(":radio").click(function() {
		// Collect details for ajax call
		name = $(this).attr('name')
		val = $(this).attr('value')
		regNum = $(this).attr('reg_num')
	
		// ticket url
		ticket = $('input[name="ticket_url"]').val();
		// Produces incomplete relative url
		//report = $('input[name="test_case_report"]').val();
		report = "/sqa/report/"+name+"/test_log"
		procedure = escape($('#'+name+'_procedure').text());
		expected = escape('Test Case URL: ['+report +']\nExpected Results:\n' + 
		$('#'+name+'_expected').text() +'\nActual Result:\n <Your text here>');
	
		// set the response for various types of alers
		
		// write to debug window
		$('#step_debug').text("Path: "+pathname+" URL:" +report+"\nPass this step radio " + name + ' value - ' + val + ' test Register ' + regNum );
		thisRow = '#row_'+name
		row_detail = name+"_detail"
				
		if (val == 'fail') {
			// Display the ticket location
			// Get the custom error processing form
			$.get("ajax", {ajax_request: "Failed", step_result:"Error", Step: name, TestReg: regNum}  );
			$.ajax({
			  type: "GET",
			  url: "ajax",
			  data: {ajax_request: "GetTestTicketForm", Step: name, TestReg: regNum},
			  cache: false,
			  success: function(html){
			    
				/* This method works 
				 * however when the form a step passes 
				 * all ShowForms are hidden not just that step
				 */
				//$(thisRow).after("<tr id=formrow_"+name+"><td colspan=20> <div id=ShowForm_"+name+" style='height:300px;'>"+ html+"</div></td></tr>");
				$(thisRow).after("<tr id=formrow_"+name+"><td colspan=20> <div id=ShowForm_"+name+" >"+ html+"</div></td></tr>");
				/*
			  	 * Fade in test report form
			  	 */
				/*
				 * Add Wiki syntax to description field
				 */

				$("#ShowForm_"+name).hide().html(html).fadeIn();
			  	
				
				$("#desc_wiki_"+name).each(function() { addWikiFormattingToolbar(this) });
				
			  }
			});
		} else  {
			// Exdecute the success ajax here
			if (val == 'pass') {
				// Execute ajax to update row
				//$.post("test.php", { name: "John", time: "2pm" } );
				/* Trac expects a form parameter with each post request
				 * Switching method to get
				 * 
				 */
				//$.post("ajax", {ajax_request: name, TestReq: regNum }  );
				$.get("ajax", {ajax_request: "Passed", step_result:"Result: Executed as expected", Step: name, TestReg: regNum }  );
				/*
				$.ajax({
					type: "POST",
  					url: "ajax",
					//data: "ajax_request="+name+"&TestReg="+regNum ,
  					cache: false,
  					success: function(html){
    					$("#results").append(html);
  					}
				});
				*/	
			}
			$('#ShowForm_'+name).hide()
			$('#formrow_'+name).hide()
		} 
		countRemain = countRemainingSteps();
		$('#step_remain').text(countRemain);
	});


});

/*
$('#step_pass').select(function() {
	alert("Pass this step select " + $(this).name);
});

//alert('Its dead jim');
			// Adds new to each row
			//$('#TestStepListing tr:parent').after("<tr><td  colspan=20> Hello </td></tr>");
			
			//$(thisRow).fadein
			$(thisRow).after("<tr id="+row_detail+"><td  colspan=20>Hello Row </td></tr>"); 
*/


/*
$(document).ready(function() {
	count = $('#step_na:checked').length
	alert("Steps remaining  " + count);
});
*/


/*
$("#step_pass").change(function() {
	alert("Pass this step change" + $(this).name);
}).change();

// Register Fail event
$("#step_fail").change(function() {
	alert("FAIL this step change " + $(this).name);
}).change();
*/