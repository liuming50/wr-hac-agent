"use strict";

/*****************************************************************************/
/*                                 Get PIN Code                              */
/*****************************************************************************/
               
var pinCodeData = {
    timerID: 0,                 // TimerID used track PIN code expiration
    pinRequested: false,        // Flag indicating if a PIN code request is active
    percentRemain: 0,           // % of PIN code lifetime remaining
    ticksPerPercent: 0          // Used to set timeout events to decrement 1% 
    };
    
/*
 * showPinCodeDialog() - Display the PIN Code Generation modal dialog box
 */
 function showPinCodeDialog() {
    document.getElementById("genPinCodeDialog").style.display="block";

    document.getElementById('pinCodeGetButton').disabled = false;
}

/*
 * _hidePinCodeDialog() - Hide the PIN Code Generation modal dialog box 
 */
function _hidePinCodeDialog() {

    // If there is an active timer, cancel it so we don't get any more callbacks
	if (pinCodeData.timerID !== 0) { 
		clearTimeout(pinCodeData.timerID);
		pinCodeData.timerID = 0;
		}
		
	// If a token has been requested, clean up dialog elements
	if (pinCodeData.pinRequested === true) {
	    document.getElementById('pinCodeValue').innerHTML="INVALID";
        document.getElementById('pinCodeValue').style.visibility = "hidden";
        document.getElementById('pinCodeInstruction').style.visibility = "hidden";
        document.getElementById('pinCodeCancelButton').style.visibility = "hidden";
        stopPinCodeProgress();
        pinCodeData.pinRequested = false;
        }
        
    document.getElementById("genPinCodeDialog").style.display="none";
    
    loadStatusTbl();
}
  
/*
 * _initPinCodeProgress() - Initializes and displays the progress bar used to count 
 * down the time remaining on a PIN code
 */
function _initPinCodeProgress() {

	pinCodeData.percentRemain = 100;	// 100% of time remaining
	
	// Make the progress bar visible 
    document.getElementById('pinCodeBar').style.visibility = "visible";
    document.getElementById('pinCodeProgress').style.visibility = "visible";
    document.getElementById('pinCodeBar').style.width = pinCodeData.percentRemain +'%';    
}

/*
 * _stopPinCodeProgress() - Hides the PIN Code progress bar 
 */
function _stopPinCodeProgress() {
    document.getElementById('pinCodeBar').style.visibility = "hidden";
    document.getElementById('pinCodeProgress').style.visibility = "hidden";
}

/*
 * _decrPinCodeProgress() - Subtracts 1% from the width of the progress bar used to indicate 
 * time remaining on a temporary registration token.
 */
function _decrPinCodeProgress() {

    pinCodeData.percentRemain -= 1;			// Decrease width of bar
    
    if (pinCodeData.percentRemain < 0) {	// Prevent width less then 0
        pinCodeData.percentRemain = 0;
        }
        
    document.getElementById('pinCodeBar').style.width = pinCodeData.percentRemain + '%';
}
 
/*
 * _pinCodeTimeoutEvent() - Called each time a timeout event occurs to update the 
 * time remaining to use a temporary registration token. 
 *
 * Upon entry, it decrements the progress bar by 1% of the screen width.
 *
 * If time has expired, 0% of time remaining, it should cleanup the token
 * generation PIN Code Dialog box, remove it, and update the board status.
 * If there is still more time, it will just set the next timeout event
 */
function _pinCodeTimeoutEvent(){
    
    // Decrement percent remaining.  
    _decrPinCodeProgress();
    
    // If time to stop then clean up else set next timeout
    if (pinCodeData.percentRemain <= 0)
        {
        pinCodeData.timerID = 0;			// No pending timeout
        pinCodeData.pinRequested = false;		// No token request active
        
        // Remove token, token instructions, and cancel button from dialog
        document.getElementById('pinCodeValue').innerHLML = "EXPIRED";
        document.getElementById('pinCodeValue').style.visibility = "hidden";
        document.getElementById('pinCodeInstruction').style.visibility = "hidden";
        document.getElementById('pinCodeCancelButton').style.visibility = "hidden";
        
        _stopPinCodeProgress();				// Clean up the progress bar
        _hidePinCodeDialog();	// Remove the Generate Token dialog box
        loadStatusTbl();			// Update current board status page 
        }
    else {
    	// Set next timeout
		pinCodeData.timerID = setTimeout("_pinCodeTimeoutEvent()", pinCodeData.ticksPerPercent);
		}

return;
}

 
/*
 * doGetPinCode() - Return a PIN code the user can enter on the HAC website to claim 
 * the board this page is served from. 
 * 
 * It is invoked from the Generate PIN button.  It will build a http request to 
 * run the CGI script to get the token.  The correct response will be a token
 * and a time out.  This gets displayed.  A timer is started to cause the number
 * of minutes remaining to decrement to 0 at which time the token is removed from
 * the screen.
 *
 * This routine works together with pinCodeTimeoutEvent() to implement the countdown.
 *
 * The following values are optional from the Dialog Box:
 *
 * Device Name (pinCodeDeviceName)  - required
 * SOCKS5 Proxy (pinCodeProxyURL) - optional 
 *
 * The  returned JSON is expected  to be have the following name/value pairs:
 *
 * status:      "ok" | "error"
 * message:     Error message" (only if status == error)
 * reg_code:    Registration code string
 * expires_min: Minutes until reg_code expires
 */
function doGetPinCode() {

   let dev_name = document.getElementById("pinCodeDeviceName").value;
   let ta_proxy = document.getElementById("pinCodeProxyURL").value;
   
   // Check the inputs. Throw an alert on error.     
	if (dev_name.length <= 0) {  
        alert("Please fill out all of the required fields");
        return;
        }
   
   let cgi_name = "cgi-bin/generate_reg.cgi";
   let cgi_req = "";
   
   if (dev_name.length > 0) {
       cgi_req = cgi_name + "?dev_name=" + dev_name;
       }
       
    if (ta_proxy.length > 0) {
        if (cgi_req === "") {
            cgi_req = cgi_name + "?ta_proxy=" + ta_proxy;
            }
        else {
            cgi_req = cgi_req + "&ta_proxy=" + ta_proxy;
            }
        }

    // Start the working spinner    
    startSpin();

    // Build a request
    let xh = new XMLHttpRequest();
    xh.open("GET", cgi_req, true);
    xh.send("some-body");
    pinCodeData.pinRequested = true;	// Flag that there is a request outstanding
    
    // Callback from the request
    xh.onreadystatechange = function() {
    if (xh.readyState === 4) { 
        if (xh.status !== 200)
            {
            let errmsg = "Unexpected Error: (" + xh.status + ") " + xh.statusText;
            alert(errmsg);
            pinCodeData.pinRequested = false;
            return;
            }
        
        // Build a Object from the response
        let response = JSON.parse(xh.responseText);

        
        if (response.status === "ok") {  
            // Determine ticks/percent so we can decrement the bar once per percent	
            pinCodeData.ticksPerPercent = (response.expires_mins * 60 * 1000) / 100;		 
        
            // Create a registration token message and make it visible to the user
            document.getElementById('pinCodeInstruction').style.visibility = "visible";       
            document.getElementById('pinCodeValue').innerHTML = "<mark>" +
            	response.reg_code + "</mark>";
            document.getElementById('pinCodeValue').style.visibility = "visible";
            
            // Display the percent remaining progress ar
            _initPinCodeProgress();		
            
            // Enable the cancel & done buttons
            document.getElementById('pinCodeCancelButton').style.visibility = "visible";
            document.getElementById('pinCodeUsedButton').style.visibility = "visible";
            
            // Disable the Generate Token button
            document.getElementById('pinCodeGetButton').disabled = true;
        
            // Set a timer to fire in 1 percent so we can update the time remaining
            pinCodeData.timerID = setTimeout("pinCodeTimeoutEvent()", pinCodeData.ticksPerPercent);
            }
        else
            {
            let message = "Error getting PIN Code\n" + response.message;
            alert(message);
            pinCodeData.pinRequested = false;
            }

         stopSpin();      
        return; // readyState == 4   
        }
        
    return;  // readyState != 4 (We don't care about these)
    }; // End onreadystatechange
        
return;
}


/*
 * doPinCodeUsed() - Called when user acknowledges using a PIN Code
 * on the Helix App Cloud Server
 *
 * Cancel any outstanding operation and timers.  Check to see if the board and
 * server are in sync.  If not, alert the user and give the option to revert to last 
 * device registration state.
 *
 * Clean up the PIN Code dialog.
 */
function doPinCodeUsed() {

    pinCodeData.pinRequested = false;			// Token request done
    if (pinCodeData.timerID !== 0) {			// Clear any outstanding timer event
        clearTimeout(pinCodeData.timerID);
        }
        
    // Check to make sure the board and server data match
    let xh = new XMLHttpRequest();
    xh.open("POST", "cgi-bin/devicestatus.cgi", true);
    xh.send("METHOD=XML");
    
    xh.onreadystatechange = function() {
    	if (xh.readyState === 4 && xh.status === 200) {
    		let regData = JSON.parse(xh.responseText);
    		if (regData.status === "ok") {
    			if (regData.registered === "device not registered") {
    				alert("The board was not registered to your workspace");
    				doRestoreDevice();
    				}
    			}
    		}
    	}; // End onreadystatechange
    
    // Clean up the Token dialog for next time
    document.getElementById('pinCodeCancelButton').style.visibility = "hidden";
    document.getElementById('pinCodeValue').value = "INVALID";
    document.getElementById('pinCodeValue').style.visibility = "hidden";
    document.getElementById('pinCodeInstruction').style.visibility = "hidden";
    document.getElementById('pinCodeUsedButton').style.visibility = "hidden";
    
    _stopPinCodeProgress();	// Clean up progress bar
    _hidePinCodeDialog();	// Remove the Generate Token dialog
    loadStatusTbl();		// Update board status info
    
    return;
}
        
/*
 * doPinCodeCancel() - Cancel an outstanding PIN Code request and restore the board
 * to the last known state. Uses the restoredevice CGI. The returned JSON is expected 
 * to have the following name/valur/pairs
 *
 * "status"  : "ok" | "error"
 * "message" : "Message to display to user".  (Mostly useful for errors)
 *
 * 
 */
function doPinCodeCancel() {

     // If the user has not initiated a token request, just hide the dialog box, 
     // update the board status info, and return.
    if (pinCodeData.pinRequested === false) {
        _hidePinCodeDialog();
        loadStatusTbl();
        return;
        }
    else {
    	// User has initiated a request and wants to cancel it
        pinCodeData.pinRequested = false;
        }
        
    // If the time to use the token has expired, no outstanding timeout, there is 
    // nothing more to do
    if (pinCodeData.timerID === 0) { 
        return;
        }
    else {
    	// There is an outstanding timeout, cancel it
        clearTimeout(pinCodeData.timerID);
        }


	// The board has already been updated to use the new token.  Revert back to the 
	// previous configuration by sending restoredevice request if the user consents.         
    let xh = new XMLHttpRequest();
    xh.open("POST", "cgi-bin/restoredevice.cgi", true);
    
    if (confirm("Cancel PIN code request?") === true) {
       xh.send("METHOD=XML");
       xh.onreadystatechange = function() {
           if (xh.readyState === 4 && xh.status === 200) {
               let resetStat = JSON.parse(xh.responseText);
               
               if (resetStat.status === "error") {
                    let message = "Error restoring configuration\n" + resetStat.message;
                    alert(message);
                    }
               
               // Remove token message and Cancel button 
               document.getElementById('pinCodeCancelButton').style.visibility = "hidden";
               document.getElementById('pinCodeValue').value = "INVALID";
               document.getElementById('pinCodeValue').style.visibility = "hidden";
               document.getElementById('pinCodeInstruction').style.visibility = "hidden";
               document.getElementById('pinCodeUsedButton').style.visibility = "hidden";
               
               _stopPinCodeProgress();		// Clean up progress bar
               _hidePinCodeDialog();		// Remove the Generate Token dialog
               loadStatusTbl();				// Update board status info
               }
           };  // End onreadystatechange
       }
}

