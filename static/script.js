setInterval(function() {
    location.reload();
}, 3600000); // Refresh every 1 hour (3600000 milliseconds)


function updateDateTime() {
    let currentDate = new Date();
     // Format date and time as 'Monday Feb 24, 2025 2:25PM'
    let options = { 
        weekday: 'long',  // Full weekday name (e.g. "Friday")
        year: 'numeric',  // Full year (e.g. "2025")
        month: 'short',   // Abbreviated month name (e.g. "Feb")
        day: 'numeric',   // Day of the month (e.g. "24")
        hour: 'numeric',  // Hour (e.g. "2")
        minute: 'numeric',// Minute (e.g. "25")
        hour12: true      // 12-hour clock (e.g. "PM")
    };

    var formattedDate = new Intl.DateTimeFormat('en-US', options).format(currentDate);

    document.getElementById('datetime').textContent = "Accurate as at: " + formattedDate;
}


// Update date and time on page load
updateDateTime();