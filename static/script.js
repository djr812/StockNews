setInterval(function() {
    location.reload();
}, 3600000); // Refresh every 1 hour (3600000 milliseconds)


/**
 * Function Name: updateDateTime
 * 
 * Description: Updates the current time for the Index.html
 *              Footer information
 * 
 * Parameters:
 *  - none
 * 
 * Returns:
 *  - none
 * 
 * Author: David Rogers
 */
function updateDateTime() {
    let currentDate = new Date();
     // Format date and time as 'Monday Feb 24, 2025 2:25PM'
    let options = { 
        weekday: 'long',  
        year: 'numeric',  
        month: 'short',   
        day: 'numeric',   
        hour: 'numeric',  
        minute: 'numeric',
        hour12: true,    
        timeZoneName: 'short' 
    };

    let formattedDate = new Intl.DateTimeFormat('en-US', options).format(currentDate);
    
    formattedDate = formattedDate.replace(/(\w+), (\w+)/, '$1 $2'); // Remove the weekday comma

    document.getElementById('datetime').textContent = "Accurate as at: " + formattedDate;
    document.getElementById('cr').innerHTML = "&copy; " + currentDate.getFullYear() + " ASX. All Rights Reserved."
}


/**
 * Function Name: getStockData
 * 
 * Description: Triggers the /index2 route to update 
 *              stock news data. Refresh index2.html
 *              with the new data. 
 * 
 * Parameters:
 *  - none
 * 
 * Returns:
 *  - none
 * 
 * Author: David Rogers
 */
function getStockData() {
    fetch('/index2', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({  }),
    })
    .then(response => response.text())
    .then(html => {
        document.body.innerHTML = html;  // Replace the page content with the new HTML
    })
    .catch(error => console.error('Error:', error));
    
}

// Update date and time on page load
getStockData();
updateDateTime();