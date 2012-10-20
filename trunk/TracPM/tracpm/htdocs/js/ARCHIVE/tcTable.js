	$(document).ready(function() {
		$(".listing tr:even").addClass('evenRow');
		$("#tc_steplist-1").tableDnD({
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
