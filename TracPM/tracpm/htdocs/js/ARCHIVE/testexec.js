
$(document).ready(function() {
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
		

});


