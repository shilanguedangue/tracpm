function setBrowserData() {
    /*Set information about the client
     * 
     * 
     */
    var host = window.location.hostname;
    //window.alert("this name is " + host);
    $('input[name="host_name"]').val(host);
    //$("#te_hostname").val('This is my data');

    var browser;
    if($.browser.mozilla)
      browser = "Firefox";
    else if($.browser.msie)
      browser = "Internet Explorer";
    else if($.browser.opera)
      browser = "Opera";
    else if($.browser.safari)
      browser = "Webkit";
    else if($.browser.webkit)
      browser = "Webkit";
    else
      browser = "Unknown";
    
    $('input[name="browser"]').val(browser);
    
    $('input[name="browser_ver"]').val($.browser.version);
    
    $('input[name="client_plfrm"]').val(navigator.platform);
    $('input[name="user_agent"]').val(navigator.userAgent);
    // copy user name to hidden input (Work around...)    
    $("#loginUser").val($("#_uid").val())
}

function loadTestCatalog(tabView){
    $("#refreshList, .condBtn, .EndCondBtn").hide();
    var choice = $("#"+ tabView).val()
	var updateDiv = null;
	if (tabView == "planChoice") {
		updateDiv = "#TestPlanDiv";
		
	} else if (tabView == "adminCatalogChoice") {  
		updateDiv = "#TestAdminDiv";
	} 
	
	
    if (choice != 'NoValue') {
        $.ajax({
            url: $("body").data('ws_plan_url'),
            data: {
                'milestone': choice
            },
            success: function(Response){
                $(updateDiv).html(Response).fadeIn(1000);
            }
        });
    }
};

function setTicketForm(_reg_id, _case_id, _step_id) {
    
    var url = $('body').data('ws_ticket_form_url') + "?reg_id="+ _reg_id + "&amp;case_step_id=" +_case_id + "&amp;step=" + _step_id;
    
    var result = '<tr>';
    result += '<td colspan="20">';
    result += '<iframe src="';
    result += url;
    
    result += '"  class="ticketFrame" >';
    result += '</iframe>';
    result += '</td>';
    result += '</tr>';
    
    alert(result);
    
    return result;
}

function startTest() {
    var testSteps = $("#numOfTestSteps").val();
    var reg_id = $("#_reg_id_").val();
    var user_id = $("#_uid").val();
    //alert('User =  ' + user_id);
    $.get("ajax", {ajax_request: "Event", step_result:"[INIT] Initializing Test; Loaded [ "+ testSteps +" ] Total Steps" , Step: 0, TestReg: reg_id }  );
    $.get("ajax", {ajax_request: "Event", step_result:"[START TEST] Test Started By User: " + user_id , Step: 0, TestReg: reg_id }  );
}


$(function() {
	// update tab currently selected when user selects item from dropdown
	function getSelectedTab(type) {
		var $tabIndex = $("#sqa_tabs").tabs();
		var tabSelected = $tabIndex.tabs('option', 'selected' );
		
		if (type == 'id') {
			return $($("#sqa_tabs_ul li")[tabSelected]).find("a").attr("id")
		} else if (type == 'text') {
			return $($("#sqa_tabs_ul li")[tabSelected]).find("a").text();
		} else if (type == 'int')  {
			return tabSelected;	
		} else if (type == 'data')  {
			return $($("#sqa_tabs_ul li")[tabSelected]).find("a").data('map');	
		} else {
			return null;
		}
		
		
	}
	// get the values of current drop down selections
	function getMilestone() {
		return $("#milestoneSelect").val()
	}
	function getCase() {
		return $("#testCaseSelect").val()
	}
	$("#sqa_tabs").tabs();

	function updateUrl(url, item) {
		if (item == 'MS') {
			// replace with milestone
			var ms = getMilestone();
			return url.replace('-', ms);
		} else if (item == 'CS') {
			// replace with case id
			var cs = getCase();
			return url.replace('-', cs);
		} else {
			return null;
		}
	}
	// Load content of tab panel
	function UpdateTabContentDiv(url, div) {
		$.ajax( {
            url: url,
            type: 'GET',
            async: false,
			data: {'type': div},
            success: function(Response) {
                $('#'+div).html(Response)
            }
        });
	}

	// tab click event handler
	$('#sqa_tabs').bind('tabsselect', function(event, ui) {
		// Get the list selections
		var ms = getMilestone();
		var cs = getCase();
		if (ms != "NoValue" && cs != "NoValue") {
			// load reference page from tab definition
			//alert("this panel : " + $(ui.panel).attr('id'))
			var thisTab = $(ui.panel).data('map')
			thisTabUrl = updateUrl(thisTab.content_url, 'CS');
			//alert("this URL : " + thisTabUrl + " UpdateDiv: " + thisTab.content_div);	
			UpdateTabContentDiv(thisTabUrl, thisTab.content_div);
					
		} else {
			alert("Please select a project and test case.");
		}
	});

    $('#milestoneSelect').live('change', function() {
        $.ajax( {
            url: 'ajax',
            type: 'GET',
            async: false,
            data: {
                'milestone': $(this).val(),
                'ajax_request': 'GetCases'
            },
            success: function(Response) {
                $('#caseSelectWrapper').html(Response)
            }
        });
    });

	
	function getAdminEditor(operation, step_id, step_num, plan_id) {
		// 
		
		$.extend({
            getAdminForm: function(opt_type, step_id, step_num, plan_id) {
				var result = null;
                /*
                 * Note: Following attributes must set for the call back to work     
                 * dataType: 'json',
                 * async: false
                 */ 
                $.ajax({
	                url: $('body').data('admin_edit'),
	                type: 'GET',
	                async: false,
	                data: {'opt': opt_type, 'step_id': step_id, 'this_plan_id': plan_id, 'step_num': step_num},
	                success: function(Response) {
	                	// return result to caller
						result = Response;
                    }
                });
                // return result to caller
                return result;
            }
        });
		return $.getAdminForm(operation, step_id, step_num, plan_id);
		
	}



	// --- ADMIN EDIT STEP
	$(".editSave").live('click', function(){
		/* Button options presented when a step is edited under the admin tab. 
		 * Control the actvities of updates and cancel  */
		
		var thisForm = $(this).attr('id');
		
		
		if (thisForm == '_cancel') {
			// Cancel the edit... must return previous row
			$(this).closest('tr').remove();
			
		} else {
		
			thisForm = thisForm + '_data'
			// Update given set of data
			//var ACTION = $(this).closest('tr').find('.__adminEditAction :input').serialize();
			//var ACTION = $(this).closest('.__adminEditAction :input').serialize();
			//$($("#sqa_tabs_ul li")[tabSelected]).find("a").attr("id")
			//$("#registerTest :input").serialize(),
			var formData = $("#" + thisForm + " :input").serialize();
			
			//alert("Action: " + formData);	
			
			$.ajax({
				url: $('body').data('update_edit'),
				type: 'POST',
				async: false,
				data: formData,
				success: function(Response){
				// return result to caller
					alert('ROWID = ' + Response)
				
				}
			});
		}
		// Return the updated field
		
		

		


	});

	function editCheck(method, edit_id) {
		/*
		 * 	Check to see if a step edit is currently in progress.
		 * 	If a edit is in progress, prevent an additional step from 
		 *  being created...
		 *  Prototype: alert($('#testAdminDiv').find('#12_this').length)
		 */  
		var search = "#" + edit_id  + method;
		var test = $('#testAdminDiv').find(search).length;
		//alert("Edit Search: " + search + " Result -> " + test);
		if (test != 0 ) { 
			return true;
		} else {
			return false;
		}
	}

	// Live binding for admin hover menu
	/*
	 * Insert or replace the current step definition with form returned from 
	 * ajax_admin_edit.html template.
	 */
	$('#_Edit, #_Insert, #_Append, #_Delete').live('click', function(){
		
		var attrID = $(this).attr('id');
		var rowID = $(this).closest('tr').attr('id');
		var StepNum = $(this).closest('tr').find('.stepNum').text();
		var planID = $("#testExecPlanId").val();
		//alert("This "+attrID+" Row id = " + rowID);
		
		/*
		 * Check to see if an edit is in process
		 */
		//var testEdit = editCheck(attrID, rowID);
		if ( editCheck(attrID, rowID) ){
			alert("Please save current edits before continuing");
			return;
		} 
		
		// get un-formatted data from database and insert in edit window.
		// TODO Fix update search in inc_testPlanTable.html
		//$(this).parents().find('.expResult').empty();
		
		if (attrID != '_Delete') {
			var adminForm = getAdminEditor(attrID, rowID, StepNum, planID);	
		}
		
		if (attrID == '_Insert') {
			$(this).closest('tr').attr('edited', 'insert');
			// add edit dialog before current step
			 
			
			$("#testAdminDiv_tbl").find('#'+rowID).before(adminForm);
		} else if (attrID == '_Append') {
			// add edit dialog after current step
			$(this).closest('tr').attr('edited', 'append');
			$("#testAdminDiv_tbl").find('#'+rowID).after(adminForm);
			$(this).closest('tr').find("textarea.wikitext").each(function() { addWikiFormattingToolbar(this) })
			
			//$("textarea.wikitext").each(function() { addWikiFormattingToolbar(this) })
		} else if (attrID == '_Edit') {
			// get raw step data from database
			// show editing features used to update current step
			
			$(this).closest('tr').attr('edited', 'true');
			// change row color to yellow
			//alert('EDIT');
			$("#testAdminDiv_tbl").find('#'+rowID).css("background-color", "yellow");
			
			 
			// Edit current step
			//$("#testAdminDiv_tbl").find('#'+rowID).after(adminForm);
			
			/*
			 * Replace current step with the content provided by adminForm return
			 */
			$("#testAdminDiv_tbl").find('#'+rowID).replaceWith(adminForm);
			//find row by id
			
			
			//$("#testAdminDiv_tbl, #"+rowID).find('#testAdminDiv_expResult_'+rowID).html('<textarea name="test_procedure" class="stepProcedure adminEditor wikitext">${json_step.test_procedure}</textarea><label for="item_name">Step Name: </label><input type="text" name="item_name" value="${json_step.item_name}" size="40"/>');
			//$("#testAdminDiv_tbl, #"+rowID).find('#testAdminDiv_procedure_'+rowID).html('<input type="text" name="Admin_'+rowID+' value="edit This"/>');
		
		} else if (attrID == '_Delete') {
			// delete current step 
			$(this).closest('tr').attr('edited', 'delete');
			$("#testAdminDiv_tbl").find('#'+rowID).css("background-color", "red");
		
		} 
		
		
	});

	$("#UpdateChanges").live('click',function(){
        /*
         * Reload Edit changes from database
         */
		alert('Clicked UpdateChanges');
		
        
    });



	// add Wiki Toolbar when hovering over editable row
	$("#testAdminDiv_tbl tr.editHover").live('mouseenter', function(){
		$(this).find("textarea.wikitext").each(function(){
				addWikiFormattingToolbar(this);
				//TracWysiwyg.initialize(this);
			});
	});
	
	$("#testAdminDiv_tbl tr.editHover").live('mouseleave', function(){
		$(this).find(".wikitoolbar").remove();
		//$(this).find("wysiwyg-toolbar").remove();
		//$(this).find("editor-toggle").remove();

	});



	$('#testCaseSelect').live('change', function() {
        // when cascade test plan is selected update proper tab location...
		// var tabSelected = getSelectedTab('int');
		// $($("#sqa_tabs_ul li")[tabSelected]).find("a").attr("id")
		var tabSelected = getSelectedTab('data');
		//tabSelected = tabSelected.replace('-',cs);
		
		// updated url location for request
		tabSelectedUrl = updateUrl(tabSelected.content_url, 'CS');
		//alert("This tab: " + tabSelectedUrl + "  was selected..." + "Update: " + tabSelected.content_div);
		
		UpdateTabContentDiv(tabSelectedUrl, tabSelected.content_div);
		
		// get the name of the tab
		//var list = $($("#sqa_tabs_ul li")[1]).find("a").text();
		//alert("got: " + list);
		
		
			
		
		/*
		$.ajax( {
            url: 'ajax',
            type: 'GET',
            async: false,
            data: {
                'milestone': $(this).val(),
                'ajax_request': 'GetCases'
            },
            success: function(Response) {
                $('#caseSelectWrapper').html(Response)
            }
        });
        */
    });
	
	$("#testAdminDiv_tbl").live('mouseenter', function() {
		$("#testAdminDiv_tbl").tableDnD({
	    onDragClass: "tblDrag",
	    onDrop: function(table, row) {
            var rows = table.tBodies[0].rows;
            var debugStr = "";
            for (var i=0; i<rows.length; i++) {
                debugStr += rows[i].id+",";
            }
	        $('[name=table_order]').val(debugStr);
	    }
		});
	});
		
	



    $(".passfail_btn").live('click',function(){
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
            
            $.extend({
                getTicketForm: function(_reg_id, _case_id, _step_id) {
                    var result = null;
                    /*
                     * Note: Following attributes must set for the call back to work     
                     * dataType: 'json',
                     * async: false
                     */ 
                    $.ajax({
                    url: $('body').data('ws_ticket_form_url'),
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
            
            var result = $.getTicketForm(reg_id, case_id, step_id);
            var iframeResult = setTicketForm(reg_id, case_id, step_id);
            //$(this).closest("tr").after( result).hide().fadeIn(1500);
            $(this).closest("tr").after( iframeResult ).hide().fadeIn(1500);
            
        }
        $("input[name="+step_id+"]").removeAttr("disabled");
        $(this).attr("disabled", "disabled");
    });

    // Load test plan data
    //$("#planChoice, #adminCatalogChoice").live('change',function(){
    //    
	//	//alert("Clicked: " + $(this).attr("id"));
	//	var view = $(this).attr("id");
	//	loadTestCatalog(view);    
    //});






    $("#refreshList").live('click', function(){
        var view = $(this).attr("id");
		loadTestCatalog(view);    
    });
    
    $("#ExecuteCase").live('click',function(){
        // hide test table
        $("#testTable").hide();
        // show testing conditions form
        $("#testCondition").show();
        
        //Show test specific fields 
        $(".tp_exec").show();
        $("#ExecuteCase").hide();
    });
    
    
    $("#testConditionBtn").live('click', function(){
        // finish adding testing conditions
        var strAjaxUrl = $(this).data('ajax_url');
        $.ajax({
            url: strAjaxUrl,
            type: 'POST',
            async: false,
            data: $("#registerTest :input").serialize(),
            success: function(Response) {
                // Add registration ID to form
                $("#tesPlanRegID").html(Response);
                //alert('Test Info: ' + test_info);
                $("#testCondition").hide();
                $("#testTable, .EndCondBtn").show();
                startTest();
            },
            statusCode: {
                400: function() {
                  alert('page not found');
                }
            }
        });
    });

    $("input[name='ajax_button']").live('click', function() {  
        /*
         * Get the id of the form containing the button clicked
         */
        formName = $(this).parents('form:first').attr("id");
        /*
         * Get the serialized content of this form 
         */
        formData = $('#'+formName).serialize()
        
        // Debug message
        //alert("Clicked Button FormName[ " +formName+ " ]\nData - " + formData);
        /*
         * Steps to complete defect recording
         * 1.) Submit data via ajax
         * 1.1) Get result back and add to list of tickets open against this step 
         * 2.) Disable radio button selections 
         * 3.) Ask if the user would like to continue testing. 
         * 
         */
        $.ajax({
            type: "POST",
                url: "ajax",
                data: formData,
                cache: false,
                success: function(html){
                    
                    //result = jQuery.parsejson(json);
                    alert("Ticket Created " + html);
                }
        });
    });
    
    

	


});
