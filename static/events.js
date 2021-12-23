// Create script tag
var script = document.createElement("script"); // dynamically load script.
var map; // map variable.
var toast; // show errors with geolocation to the user.
script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyDpYkMZmAvZrRN6cEh29n8cqsLkYLFkL-c&callback=init_map";
script.async = true;

// Attach callback function to the window object
window.init_map = function () {
    // JS API is loaded and available
    // Get markers
    let markers = [];

    $.ajax({
        type: "get",
        url: "/events/get_events.json",
        success: (result) => {
            result.events.forEach(event => {

                // Add markers to marker array
                var marker = new google.maps.Marker({
                    position: {lat: event.lat, lng: event.lng},
                    map: map
                });

                // Create info window with HTML content with information from the marker.
                var infowindow = new google.maps.InfoWindow({
                    content: `
                       <div class="info-window-head" id="event-head-${event.id}">
                            <p><strong>${event.head}</strong></p>
                            <p><small>${event.address}, ${event.time}</small></p>
                       </div>                       
                       <div class="info-window-body" id="event-body-${event.id}">
                            <p>${event.body}</p>
                            <p>
                                <a class="info-window-event-booking" id="booking-${event.id}" href="#">
                                    Book your place! ${event.attending.length === undefined ? 0 : event.attending.length}/${event.capacity}
                                </a>
                            </p>
                       </div>
                    `
                })
                // Pin each info window to the corresponding marker.
                marker.addListener("click", () => {
                    infowindow.open({
                        anchor: marker,
                        map,
                        shouldFocus: false,
                    })
                })

                // Store markers and corresponding info windows in a dict.
                markers.push({marker: marker, info_window: infowindow});
            })
        }
    })

    // Create map
    map = new google.maps.Map(document.getElementById("event-map"), {
        center: {lat: 54, lng: -1},  // Default location
        zoom: 8,
        markers: markers
    });

    // Ask user for their location (after map is loaded)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(center_map, show_error);
    } else {
        toast.innerHTML("Geolocation is not supported on this browser.");
        toast.show()
    }
}

// Add script tag to the head
document.head.appendChild(script);

// Handle geolocation
function center_map(center) {
    var new_center = new google.maps.LatLng(center.coords.latitude, center.coords.longitude);
    map.setCenter(new_center);
    map.setZoom(13);
}

function show_error(error) {
    let body = document.getElementById("geo-toast-body");
    switch (error.code) {
        case error.PERMISSION_DENIED:
            console.log("User denied request for location.")
            break;
        case error.POSITION_UNAVAILABLE:
            body.innerHTML = "Location information is unavailable at this time.";
            toast.show();
            break;
        case error.TIMEOUT:
            body.innerHTML = "Request for user location timed out.";
            toast.show();
            break;
        case error.UNKNOWN_ERR:
            body.innerHTML = "An unknown error occurred."
            toast.show();
            break;
    }
}

// Initialise toast error displaying for geolocation
$(function() {
    var toast_element = document.getElementsByClassName("toast")[0];
    toast = new bootstrap.Toast(toast_element);
})