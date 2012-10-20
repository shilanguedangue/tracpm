
$(document).ready(function() {




	$(":radio").click(function() {
		this_reg_id = $(this).attr('reg_num')
		//alert("You clicked Row " + this_reg_id)
		$.ajax({
			type: "GET",
	  		url: "ajax",
			data: {ajax_request: "GetLog", regid: this_reg_id},
			dataType: "html",
	  		success: function(data) {
    			$('#_log_detail_'+this_reg_id).html(data);
	  		}
		});
		$('#row_'+this_reg_id).css("background-color","#A9D0F5");
		/*
		 * Show the testing log
		 */
		
		
		
		
		
		$("#detail_"+this_reg_id).fadeIn('slow');
		
		/*
		$("input").is(":not(:checked)")(function() {
			not_checked = $(this).attr('reg_num')
			alert("This radio is not checked: "+ not_checked);		
		
	    });
	    */
		
		
		

	});
	
	

});