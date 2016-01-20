"use strict";

 
/*****************************************************************************/
/*                          Associate Board with ID                          */
/*****************************************************************************/

/*
 * showAssociateByIdDialog() - Display the Associate with ID modal dialog box
 */
 
function showAssociateByIdDialog() {

    // Clear out any previous values
    document.getElementById("associateDevID").value = "";
    document.getElementById("associateDevServer").value = "";
    document.getElementById("associateDevProxy").value = "";
    
    // Show the dialog
    document.getElementById("associateDevDialog").style.display="block";
}

/*
 * hideAssociateDevDialog() - Hide the Device Creation modal dialog box
 */
function hideAssociateDevDialog() {
    document.getElementById("associateDevDialog").style.display="none";
}

/*
 * doAssocateDevWithID() - Associate the board with a pre-existing DeviceID on 
 * Helix App Cloud. It can have three inputs from the user:
 *
 * Device ID (associateDevID) - required
 * Server (IDHeixServer) - optional
 * Proxy (associateDevProxy) - optional
 *
 * These are passed to the script via a POST. The returned JSON is expected to be have 
 * the following name/value pairs:  (FIXME)
 *
 * "status" :    "ok" | "error"
 * "deviceName": "User Assigned Device Name"
 * "deviceID: :  "Server Assigned Device ID"
 * "server" :    "IP or DNS name of the HAC server"
 * "serverUrl":  "URL portion of the device registration" (no need to display this)
 * 
 */

function doAssociateDevWithID() {

    // Start the refresh icon to spin 
    startSpin();
    
    // Get the user input
    let deviceID = document.getElementById("associateDevID").value;
    let serverName = document.getElementById("associateDevServer").value;
    let serverProxy = document.getElementById("associateDevProxy").value;
   
    // Check the argument.  Only deviceID is required 
    if (deviceID.length <= 0) {    
        alert("Please fill out all the required fields");
        return;
      }
    
    
    // Build the request
    let cgi_req = "cgi-bin/registerServerId.cgi?";
    cgi_req += "dev_name=" + deviceID;
    
    if (serverName.length > 0) {
        cgi_req += "&server=" + serverName;
        }
        
    if (serverProxy.length > 0) {
        cgi_req += "&ta_proxy" + serverProxy;
        }
  
   
    let xh = new XMLHttpRequest();
    xh.open("POST", cgi_req, true);
    xh.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xh.send();
            
    // Callback when response is ready.  When we get it, parse the result.  
    xh.onreadystatechange=function() {
    if (xh.readyState === 4 ) {   
        if (xh.status !== 200)
            {
            let errmsg = "Unexpected Error: (" + xh.status + ") " + xh.statusText;
            alert(errmsg);
            stopSpin();
            return;
            }
        
        // Create an object from the reesponse
        let response = JSON.parse(xh.responseText);
        
        // If it failed, show a dialog box to the user with the error message
        if (response.status != "ok") {
            let message = "Error associating with\n" + deviceID + "\n\n" + response.message;
            alert(message);
            stopSpin();
            }
        
        // Clear off the dialog box and go back to the "home" screen
        stopSpin();
        hideAssociateDevDialog();
        loadStatusTbl();    
        return; // readyState == 4
        }

    return;   // readyState != 4        
    };  // End onreadystatechange              
return;
}
