
	
	
	// Pass Fail callbacks
	$(".passfail_btn").click(function(){
		/// Call back function for updating test steps
		var case_id = $(this).attr('name');
		var step_id = $(this).attr('step_num');
		var reg_id = $("#_reg_id_").val();
		var result = $(this).val();
		var plan_id = $("#testExecPlanId").val();
		$(this).closest("tr").addClass("complete");
		// Mark Row Unique
		var thisRowId = "row_"+step_id;
		if (result == 'pass') {
			
			$('#'+thisRowId).hide();
			$.get("ajax", {ajax_request: "Passed", step_result:"Result: Executed as expected", Step: case_id, TestReg: reg_id }  );
		} else if (result == 'fail') {
			var ticketURL = $("#_ticket_url").val();
			
			$.get("ajax", {ajax_request: "Failed", step_result:"Error", Step: case_id, TestReg: reg_id}  );
			//$(this).closest("tr").after("<div id="+ thisRowId +" > Hello There </div>");
			//$(this).closest("tr").after("<tr><td> Hello There </td></tr>");
			
			
			$.extend({
				getTicketForm: function(_reg_id, _case_id, _step_id) {
					var result = null;
					/*
					 * Note: Following attributes must set for the call back to work 	
					 * dataType: 'json',
					 * async: false
					 */ 
					$.ajax({
					url: "${href.sqa('ws_get_ticket_form' )}",
					type: 'GET',
					async: false,
					data: {'reg_id': _reg_id, 'case_step_id': _case_id, 'step': _step_id},
						success: function(Response) {
							result = Response;
						}
					});
					// return result to caller
					return result;
				}
			});
			
			

			
			// Add Iframe
			var result = $.getTicketForm(reg_id, case_id, step_id);
			$(this).closest("tr").after( result).hide().fadeIn(1500);
			
			
			
			
			/*
			$.ajax({
				url: "${href.sqa('ws_ticket_form' )}",
				type: 'GET',
				async: false,
				data: {'reg_id': reg_id, 'case_step_id': case_id, 'step': step_id},
				success: function(Response) {
					//alert("Publishing: " + Response);
					//$(this).closest("tr").after("<tr><td><iframe>"+ Response +"</iframe></td></tr>");
					$(this).closest("tr").after(Response);
				}
			});
			*/
			
			
			
			
		}
		$("input[name="+step_id+"]").removeAttr("disabled");
		$(this).attr("disabled", "disabled");
	});
	
	$("._endTestCase").click(function(){
		var reg_id = $("#_reg_id_").val();
		$.get("ajax", {ajax_request: "Event", step_result:"[ Test Ended ] ", Step: 0, TestReg: reg_id }  );
		$("#TestPlanDiv").empty();
		$("#refreshList").trigger('click')
		//alert('Test Complete');
	});
	
