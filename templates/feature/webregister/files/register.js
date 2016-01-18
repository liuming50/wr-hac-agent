"use strict";

var advancedSettings = false;

/*****************************************************************************/
/*                              Shared Utilities                             */
/*****************************************************************************/

/*
 * startSpin() - Start the "Working" icon spinning
 */
function startSpin() {
    document.getElementById('idRefresh').className = 'w3-spin fa fa-refresh';
}

/*
 * stopSpin() - Stop the "Working" icon spinning
 */
function stopSpin() {
    document.getElementById('idRefresh').className = 'fa fa-refresh';
}

/*
 * loadStatusTbl() - Ensures that the status table is visible on the screen,
 * fetches the current device settings, and displays it
 */
function loadStatusTbl() {
    document.location = "index.html#link3";
    displayDeviceReg();
}


/*****************************************************************************/
/*                              Display Status                               */
/*****************************************************************************/

/*
 * displayDeviceReg() -  Query the board registration data and display it.
 * 
 * The returned JSON is expected to be have the following name/value pairs:
 *
 * status:       "ok" | "error"
 * message:      Error message when status == error
 * deviceName:   User Assigned Device Name
 * deviceID:     Server Assigned Device ID
 * server:       IP or DNS name of the HAC server
 * serverPort:   Port number of the HAC server
 * serverUrl:    URL portion of the device registration (not displayed)
 * registered:   Servers registration status for device
 * ta_proxy:     Socks5 proxy used by target agent (or "none")
 * https_proxy:  URL to HTTPS proxy server
 * sdkName:      The name of the software load on the board
 * sdkVersion:   The version of the software load on the board
 * defHacServer: The default HAC server used if none is specified
 *
 */
function displayDeviceReg() {

	startSpin();

	let xh = new XMLHttpRequest();
	xh.open("POST", "cgi-bin/devicestatus.cgi", true);
	xh.send("METHOD=XML");

	xh.onreadystatechange = function() {
		if (xh.readyState === 4 && xh.status === 200) {
			let regData = JSON.parse(xh.responseText);
             
			if (regData.status === "ok") {
				document.getElementById("devStatName").innerHTML = regData.deviceName;
               	document.getElementById("devStatID").innerHTML = regData.deviceId;
               	document.getElementById("devStatServer").innerHTML = regData.server;
               	document.getElementById("devStatPort").innerHTML = regData.serverPort;
               	document.getElementById("devStatAgentProxy").innerHTML = regData.ta_proxy;
               	document.getElementById("devStatRegistered").innerHTML = "Registered";
               	if (regData.https_proxy !== "") {
					document.getElementById("devStatHttpsProxy").innerHTML = regData.https_proxy;
                   	}
				else {
					document.getElementById("devStatHttpsProxy").innerHTML = "Undefined";
				}
				document.getElementById("devStatSDKName").innerHTML = regData.sdkName;
               	document.getElementById("devStatSDKVersion").innerHTML = regData.sdkVersion;
               	document.getElementById("devStatDfltServer").innerHTML = regData.defHacServer;
               	document.getElementById("devStatRegistered").style.color = "black";
               	}
               	else {
				document.getElementById("devStatRegistered").innerHTML = regData.message;
               	document.getElementById("devStatName").innerHTML = "Unknown";
               	document.getElementById("devStatID").innerHTML =  "Unknown";
               	document.getElementById("devStatServer").innerHTML = "Unknown";
               	document.getElementById("devStatPort").innerHTML = "Unknown";
               	document.getElementById("devStatAgentProxy").innerHTML = "Unknown";
               	document.getElementById("devStatHttpsProxy").innerHTML = "Unknown";
               	document.getElementById("devStatSDKName").innerHTML = "Unknown";
               	document.getElementById("devStatSDKVersion").innerHTML = "Unknown";
               	document.getElementById("devStatDfltServer").innerHTML = "Unknown";
               	document.getElementById("devStatRegistered").style.color = "red";
               	}
			}
		stopSpin();
       	}; // End onreadystatechange
}

/*
 * toggleAdvanced() -  Show/Hide advanced settings on status page.
 */
 
function toggleAdvanced()
{

    if (advancedSettings === false)
        {
    	document.getElementById('displayDfltServer').style.visibility = "visible";
    	document.getElementById('displayHttpsProxy').style.visibility = "visible";
    	document.getElementById('displaySDKName').style.visibility = "visible";
    	document.getElementById('displaySDKVersion').style.visibility = "visible";
    	advancedSettings = true;
    	}
    else
        {
        document.getElementById('displayDfltServer').style.visibility = "hidden";
    	document.getElementById('displayHttpsProxy').style.visibility = "hidden";
    	document.getElementById('displaySDKName').style.visibility = "hidden";
    	document.getElementById('displaySDKVersion').style.visibility = "hidden";
    	advancedSettings = false;
    	}

}


/*****************************************************************************/
/*                         Reset and Restore Utilities                       */
/*****************************************************************************/

/*
 * doResetDevice() - Reset the device configuration to Factory Default state. Invoked
 * directly from the nav bar.
 *
 * The returned JSON is expected to have the following name/valur/pairs
 *
 * "status"  : "ok" | "error"
 * "message" : "Message to display to user".  (Mostly useful for errors)
 *
 *
 */
function doResetDevice() {

    // If the user confirms this is their intention, create a CGI request to the device. 
    // There are no arguments.   
    if (confirm("Reset Device to Factory Defaults?") === true) {
       let xh = new XMLHttpRequest();
       xh.open("POST", "cgi-bin/resetdevice.cgi", true);
       startSpin();
       xh.send("METHOD=XML");
       xh.onreadystatechange=function() {
           if (xh.readyState === 4 && xh.status === 200) {
               let resetStat = JSON.parse(xh.responseText);
               
               if (resetStat.status === "error") {
                    let message = "Error reseting configuration\n" + resetStat.message;
                    alert(message);
                    }
               stopSpin();
               loadStatusTbl();
               }
           };  // End onreadystatechange
       }
}
  
/*
 * doRestoreDevice() - Restore the device configuration to it's prior state. Invoked 
 * directly from the nav bar. (Note, the CGI scripts on the device keep track of the 
 * device's prior state.  So nothing to do here other than call it.)
 * 
 * The returned JSON is expected to have the following name/value pairs
 *
 * "status"  : "ok" | "error"
 * "message" : "Message to display to user".  (Mostly useful for errors)
 *
 * 
 */
function doRestoreDevice() {

    // If the user confirms this is their intention, create a CGI request to the device. 
    // There are no arguments.  
    if (confirm("Restore Device to previous configuration?") === true) {
    	let xh = new XMLHttpRequest();
    	xh.open("POST", "cgi-bin/restoredevice.cgi", true);
       startSpin();
       xh.send("METHOD=XML");
       xh.onreadystatechange=function() {
           if (xh.readyState === 4 && xh.status === 200) {
               let resetStat = JSON.parse(xh.responseText);
               
               if (resetStat.status === "error") {
                    let message = "Error restoring configuration\n" + resetStat.message;
                    alert(message);
                    }
               stopSpin();
               loadStatusTbl();
               }
           };  // End onreadystatechange
       }
}

/*****************************************************************************/
/*                             HTTPS Proxy Utilities                         */
/*****************************************************************************/

/*
 * showHTTPSProxyDialog() - Display the HTTPS Proxy modal dialog box
 */
function showHttpsProxyDialog() {
    document.getElementById("httpsProxyDialog").style.display="block";
}

/*
 * hideHttpsProxyDialog() - Hide the HTTPS Proxy modal dialog box
 */
function hideHttpsProxyDialog() {
    document.getElementById("httpsProxyDialog").style.display="none";
}

/*
 * doSetHttpsProxy() - Set the HTTP Proxy Server to be used during device registration
 */
function doSetHttpsProxy() {
    // Start the refresh icon to spin 
    startSpin();
    
    // Get the user input
    let https_proxy = document.getElementById("httpsProxyURL").value;

    
    if (https_proxy.length <= 0 ) {    
        if (confirm("Remove HTTPS proxy settings") !== true) {
            return;
            }
      }
    
    
    // Build the request
    let cgi_req = "cgi-bin/registerproxy.cgi?proxy=" + https_proxy;
   
    let xh = new XMLHttpRequest();
    xh.open("POST", cgi_req, true);
    xh.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xh.send();
        
    // send() will return to the JS interpreter.  Function below will get called on 
    // state changes due to events on xh.
    
    // Wait for the response.  When we get it, parse the result.  
    xh.onreadystatechange=function() {
    if (xh.readyState === 4 ) {   
        if (xh.status !== 200)
            {
            let errmsg = "Unexpected Error: (" + xh.status + ") " + xh.statusText;
            alert(errmsg);
            return;
            }
        
        let response = JSON.parse(xh.responseText);
        
        // If it failed, show a dialog box to the user with the error message
        if (response.status !== "ok") {
            let message = "Error setting proxy" + https_proxy + "\n" + response.message;
            alert(message);
            }
        
        // Clear off the dialog box and go back to the "home" screen
        stopSpin();
        hideHttpsProxyDialog();   
        return; // readyState == 4
        }  

    return;   // readyState != 4        
    };  // End onreadystatechange

}

/*
 * getHttpsProxy() - Get the HTTP Proxy Server to be used during device registration
 */

function getHttpsProxy() {

    // Build the request
    let cgi_req = "cgi-bin/registerproxy.cgi";
   
    let xh = new XMLHttpRequest();
    
    xh.open("GET", cgi_req, true);
    xh.send();
        
    // send() will return to the JS interpreter.  Function below will get called on 
    // state changes due to events on xh.
    
    // Wait for the response.  When we get it, parse the result.  
    xh.onreadystatechange = function() {
    if (xh.readyState === 4 ) {   
        if (xh.status !== 200) {
            return;
            }
        
        let response = JSON.parse(xh.responseText);
        
        // If it failed, show a dialog box to the user with the error message
        if (response.status !== "ok")  {
            document.getElementById("devStatHttpsProxy").innerHTML=response.message;
            }
        else if (response.proxy !== "") {
            document.getElementById("devStatHttpsProxy").innerHTML=response.proxy;
            }
        else {
            document.getElementById("devStatHttpsProxy").innerHTML="Undefined";
            }
        }
    else {
        return;   // readyState != 4 
        }       
    }; // End onreadystatechange    
    return;
} 
