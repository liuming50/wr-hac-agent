"use strict";

/*****************************************************************************/
/*                         Register Device Functions                         */
/*****************************************************************************/

/*
 * showRegisterDeviceDialog() - Display the Register Device modal dialog box
 */
function showRegisterDeviceDialog() {

    // Clear the input fields
    document.getElementById("regDeviceUserName").value = "";
    document.getElementById("regDeviceName").value = "";
    document.getElementById("regDevicePassword").value = "";
    document.getElementById('regDeviceProxyURL').value = "";
 
    document.getElementById("regDeviceDialog").style.display="block";
}

/*
 * hideRegisterDeviceDialog() - Hide the Register Device modal dialog box
 */
function hideRegisterDeviceDialog() {    
    document.getElementById("regDeviceDialog").style.display="none";
}

/*
 * doRegisterDevice() - Invoke device side CGI script to Register a device in the 
 * users Helix App  Cloud workspace.  It requires three inputs from the user:
 *
 * UserName (regDeviceUserName) - required
 * Password (regDevicePassword) - required
 * Device Name (regDeviceName)  - required
 * SOCKS5 Proxy (regDeviceProxyURL) - optional 
 *
 * These are passed to the script via a POST. The returned JSON string is expected to
 * have the following name/value pairs:
 *
 * status:     "ok" | "error"
 * message:    Error string when status == error
 * deviceName: User Assigned Device Name
 * deviceID:   Server Assigned Device ID"
 * server:     IP or DNS name of the HAC server"
 * serverUrl:  URL portion of the device registration"
 * ta_proxy:   hostname:port of Socks5 proxy"
 * 
 */

function doRegisterDevice() {
       
    // Start the refresh icon to spin 
    startSpin();
    
    // Get the user input
    let user_name = document.getElementById("regDeviceUserName").value;
    let password = document.getElementById("regDevicePassword").value;
    let dev_name = document.getElementById("regDeviceName").value;
    let proxy = document.getElementById('regDeviceProxyURL').value;
    
    
    // Check the inputs. Throw an alert on error. TODO: Highlight error     
	if (dev_name.length <= 0 || user_name.length <= 0 || password.length <= 0) {  
        alert("Please fill out all of the required fields");
        return;
        }
   
    // Build the request. Username, password, and device name are required.
    // Socks5 proxy is optional
    let cgi_req = "cgi-bin/create_dev.cgi?user_name=" + user_name + 
                  "&password=" + password + 
                  "&dev_name=" + dev_name;
                  
    if (proxy.length > 0) {
        cgi_req +="&ta_proxy=" + proxy; 
        }

   
    // Send the request
    let xh = new XMLHttpRequest();
    xh.open("POST", cgi_req, true);
    xh.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xh.send();
    
    // Callback for the response. When we get data, parse the result.  
    xh.onreadystatechange = function() {
    if (xh.readyState === 4 ) {   
        if (xh.status !== 200)
            {
            let errmsg = "Unexpected Error: (" + xh.status + ") " + xh.statusText;
            alert(errmsg);
            return;
            }
        
        // Create a Object with the response
        let response = JSON.parse(xh.responseText);
        
        // If it failed, show a dialog box to the user with the error message
        if (response.status !== "ok") {
            let message = "Error creating device" + dev_name + "\n" + response.message;
            alert(message);
            }
        
        // Clear off the dialog box and go back to the "home" screen
        stopSpin();
        hideRegisterDeviceDialog();
        loadStatusTbl();    
        return; // readyState == 4
        } 

    return;   // End of callback function.       
    }; // End onreadystatechange
               
return;
}