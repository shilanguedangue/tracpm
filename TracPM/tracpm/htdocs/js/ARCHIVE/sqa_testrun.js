
$(document).ready(function() {
// Register pass event

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
	// Collect information about the current test
	reg = $("input[name=test_reg_num]").val();
	def = $("input[name=_defect]").val();
	user = $("input[name=_user]").val();
	if (def == '_read') {
		// Update log 
		// Loading Defect report for user
		$.get("ajax", {ajax_request: "Event", step_result:"[DEFECT] Loading Defect Form;  Loaded [ "+ initStepRemain +" ] Total Steps" , Step: 0, TestReg: reg }  );
	} else {
		// Normal test run
		$.get("ajax", {ajax_request: "Event", step_result:"[INIT] Initializing Test; Loaded [ "+ initStepRemain +" ] Total Steps" , Step: 0, TestReg: reg }  );
		$.get("ajax", {ajax_request: "Event", step_result:"[START TEST] Test Started By User = "+ user , Step: 0, TestReg: reg }  );
	}
	// Update the UI
	$('#step_remain').text(initStepRemain);
	
	
	// Register pass event
	$(":radio").click(function() {
		// Collect details for ajax call
		
		
		case_id = $(this).attr('name');
		
		step = $(this).attr('step_num')
		val = $(this).attr('value')
		regNum = $(this).attr('reg_num')
	
		// ticket url
		ticket = $('input[name="ticket_url"]').val();
		//alert("Ticket Url = " + ticket);
		// Produces incomplete relative url
		//report = $('input[name="test_case_report"]').val();
		report = "/sqa/report/"+case_id+"/test_log"
		procedure = escape($('#'+case_id+'_procedure').text());
		expected = escape('Test Case URL: ['+report +']\nExpected Results:\n' + 
		$('#'+case_id+'_expected').text() +'\nActual Result:\n <Your text here>');
	
		// set the response for various types of alers
		
		// write to debug window
		$('#step_debug').text("Path: "+pathname+" URL:" +report+"\nPass this step radio " + case_id + ' value - ' + val + ' test Register ' + regNum );
		thisRow = '#row_'+case_id
		row_detail = case_id+"_detail"
				
		if (val == 'fail') {
			// Update log - test step failed
			$.get("ajax", {ajax_request: "Failed", step_result:"Error", Step: case_id, TestReg: regNum}  );
			
			// Show ticket log form
			$(thisRow).after("<tr id=formrow_"+case_id+"><td colspan=20><div id=ShowForm_"+case_id+" ><iframe id='test_ticket_frame'  style='display:block;width:98%; height:400px'  src='"+ticket+"&case_step_id="+case_id+"&step="+step+"'> </iframe></div> </td></tr>")
				
			$("#desc_wiki_"+case_id).each(function() { addWikiFormattingToolbar(this) });
		} else  {
			// Exdecute the success ajax here
			if (val == 'pass') {
				// Execute ajax to update row

				$.get("ajax", {ajax_request: "Passed", step_result:"Result: Executed as expected", Step: case_id, TestReg: regNum }  );

			}
			$('#ShowForm_'+case_id).hide()
			$('#formrow_'+case_id).hide()
		} 
		countRemain = countRemainingSteps();
		$('#step_remain').text(countRemain);
	});

	$("#_endtest").click(function() {
		countRemain = countRemainingSteps();
		
		if (countRemain == 0) {
			$.get("ajax", {
				ajax_request: "Event",
				step_result: "[FINISH] Testing Completed with all steps executed. User " + user,
				Step: 0,
				TestReg: reg
			});
		}
		else {
			$.get("ajax", {
				ajax_request: "Event",
				step_result: "[INCOMPLETE] Test ended without executing all testing steps. User " + user,
				Step: 0,
				TestReg: reg
			});
			
			$.get("ajax", {
				ajax_request: "Event",
				step_result: "[VERIFY] Test ended with [ " + countRemain + " ] untested steps. User " + user,
				Step: 0,
				TestReg: reg
			});
			
			$("input[id='step_na']:checked").each(function(){
				name = $(this).attr('name');
				//alert("Not tested: " + name);
				$.get("ajax", {
					ajax_request: "Event",
					step_result: "[UNTESTED] Step ID [ " + name + " ] was not tested by user " + user,
					Step: name,
					TestReg: reg
				});
			});
		}
		
		$.get("ajax", {ajax_request: "Event", step_result:"[END TEST] Test Ended By User "+ user , Step: 0, TestReg: reg }  );
		setTimeout("", 1);
		$('#TestForm').submit();

	});

	


});

