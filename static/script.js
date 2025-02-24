setInterval(function() {
    location.reload();
}, 3600000); // Refresh every 1 hour (3600000 milliseconds)


function updateDateTime() {
    var currentDate = new Date();
    var formattedDate = currentDate.toLocaleString(); // This will format the date in a human-readable format

    document.getElementById('datetime').textContent = "Accurate as at: " + formattedDate;
}


// Update date and time on page load
updateDateTime();