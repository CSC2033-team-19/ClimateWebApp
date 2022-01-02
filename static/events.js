// Create script tag
var script = document.createElement("script"); // dynamically load script.
var map; // map variable.
var geolocation_error_toast; // show errors with geolocation to the user.
var deletion_warning_toast; // Warn the user that they are about to delete an event
var markers = []; // Store all the markers as well as the corresponding IDs here.
const focused_event = document.currentScript.getAttribute("focus-event"); // Store which event is being focused
script.src = `https://maps.googleapis.com/maps/api/js?key=${document.currentScript.getAttribute("api-key")}&callback=init_map`;
script.async = true; // Ensure that the script is loaded asynchronously.

// Attach callback function to the window object
window.init_map = async function () {
    // JS API is loaded and available

    // Create map
    map = new google.maps.Map(document.getElementById("event-map"), {
        center: {lat: 54, lng: -1},  // Default location
        zoom: 8,
        markers: markers
    });

    // Get markers, create infowindows and handle the centering of the map.
    $.ajax({
        type: "get",
        url: "/events/get_events.json",
        success: (result) => {
            // Define variables
            var event_list_element = $("#event-list");

            result.events.forEach(event => {

                // Add markers to marker array
                var marker = new google.maps.Marker({
                    position: {lat: event.lat, lng: event.lng},
                    map: map
                });

                // Create HTML for the event
                var rendered_event = render_event(event);

                // Create info window with HTML content with information from the marker.
                var infowindow = new google.maps.InfoWindow({
                    content: rendered_event
                })

                // Check if the user is in the event to add to the event list.
                if (event.attending.current_user_attending === true) {
                    event_list_element.append(rendered_event);
                }

                // Pin each info window to the corresponding marker.
                marker.addListener("click", () => {
                    infowindow.open({
                        anchor: marker,
                        map,
                        shouldFocus: false,
                    })
                })

                // Store markers and corresponding info windows in a dict.
                markers.push({id: event.id, marker: marker, info_window: infowindow});
            })
            get_center();
        },
    })
}

// Add script tag to the head
document.head.appendChild(script);

// Handle geolocation
function center_map(center) {
    var new_center = new google.maps.LatLng(center.coords.latitude, center.coords.longitude);
    map.setCenter(new_center);
    map.setZoom(13);
}

// Find out where the map needs to be focused
function get_center() {
    console.log(focused_event==="False");
    if (focused_event==="False") {
        // Ask user for their location (after map is loaded)
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(center_map, show_error);
        } else {
            geolocation_error_toast.innerHTML("Geolocation is not supported on this browser.");
            geolocation_error_toast.show()
        }
    } else {
        // Focus the event which the user has been refreshed from (ensure correct casting is done with parseInt)
        var focus_marker = map.markers.filter(event => event.id === parseInt(focused_event));
        focus_marker[0].info_window.open(map, focus_marker[0].marker);
        map.setZoom(13);
    }
}

// Display error in geolocation
function show_error(error) {
    let body = document.getElementById("geo-toast-body");
    switch (error.code) {
        case error.PERMISSION_DENIED:
            console.log("User denied request for location.")
            break;
        case error.POSITION_UNAVAILABLE:
            body.innerHTML = "Location information is unavailable at this time.";
            geolocation_error_toast.show();
            break;
        case error.TIMEOUT:
            body.innerHTML = "Request for user location timed out.";
            geolocation_error_toast.show();
            break;
        case error.UNKNOWN_ERR:
            body.innerHTML = "An unknown error occurred."
            geolocation_error_toast.show();
            break;
    }
}

// Initialise toast error displaying for geolocation and warning admins when deleting their events.
$(function() {
    var geo_toast_element = document.getElementById("geo-toast");
    var deletion_toast_element = document.getElementById("deletion-toast");

    geolocation_error_toast = new bootstrap.Toast(geo_toast_element);
    deletion_warning_toast = new bootstrap.Toast(deletion_toast_element);
})

// Handles the joining and leaving of events
function handle_event(event, id) {
    $.post("/events/handle_event",  // url
        {"event_id": id},  // pass ID of the event by parsing through the ID of the elmnt
        function(data, status, jqXHR) {
            // Reload page to update the infowindows, focus on infowindow which was previously open
            window.location.href = data.redirect_to;
        }
    )
}

// Warn the user about deleting an event
function warning_deletion(id) {
    var toast_element = document.getElementById("deletion-toast-body");

    // Create the confirmation button in the toast which will show to warn the user
    toast_element.innerHTML = `
        <a class="btn btn-danger" href="/events/delete_event/${id}">
            I am sure that I want to delete this event.
        </a>
    `

    // Show the toast now that the content is loaded.
    deletion_warning_toast.show()
}

// Create an HTML representation of an event
function render_event(event) {
    var button

    if (event.created_by_user) {
        button = `
            <a class="btn btn-primary" href="/events/update_event/${event.id}">
                Update Event Details
            </a>
            <a class="btn btn-danger" onclick="warning_deletion(${event.id})">
                Delete Event
            </a>
        `
    }
    else {
        button = `
            <a class="btn btn-primary" onClick="handle_event(event, ${event.id})">
                ${event.attending.current_user_attending === false ? "Join event" : "Leave event"}<br>
            </a>`
    }
    return `
    
    <div class="card">
        <div id="event-${event.id}" class="card-body">
            <h5 class="card-title">
                ${event.head}
                
            </h5>
            <p class="card-text">
                <small>${event.time}, ${event.address}</small>
            </p>
            <p class="card-text">
                 <small>Current attendance: ${event.attending.users}/${event.capacity}</small> 
            </p>
            <p class="card-text">
                ${event.body}
            </p> 
            ${button}     
        </div>
    </div>
    `
}