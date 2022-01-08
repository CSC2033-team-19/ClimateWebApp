// Create script tag
var script = document.createElement("script"); // dynamically load script.
var map; // map variable.
var geolocation_error_toast; // show errors with geolocation to the user.
var deletion_warning_toast; // Warn the user that they are about to delete an event
var markers = []; // Store all the markers as well as the corresponding IDs here.
var ids_on_map = []; // Store all the ids that are on the map to ensure an event is not placed twice.
var previous_timestamp = 0;

const focused_event = document.currentScript.getAttribute("focus-event"); // Store which event is being focused
script.src = `https://maps.googleapis.com/maps/api/js?key=${document.currentScript.getAttribute("api-key")}&callback=init_map`;
script.async = true; // Ensure that the script is loaded asynchronously.

// Attach callback function to the window object
window.init_map = function () {
    /**
     * Once the JavaScript APIs are loaded, begin execution of setup.
     */

    // Create the toast elements which will be used for error handling.
    var geo_toast_element = document.getElementById("geo-toast");
    var deletion_toast_element = document.getElementById("deletion-toast");

    geolocation_error_toast = new bootstrap.Toast(geo_toast_element);
    deletion_warning_toast = new bootstrap.Toast(deletion_toast_element);

    // Create map
    map = new google.maps.Map(document.getElementById("event-map"), {
        center: {lat: 54.990446, lng: -1.6128411},  // Default location
        zoom: 8,
        markers: markers
    });

    // Load events relevant to the user to the map.
    $.ajax({
        type: "get",
        url: "/events/get_events.json",
        success: create_events_on_map
    });

    // Get the center of the map
    get_center();

    // Add event listener to the map to see when the center is changed
    map.addListener("center_changed", () => {
        if ((new Date() - previous_timestamp)/1000 > 10) {
            previous_timestamp = new Date();
            $.ajax({
                type: "get",
                url: "/events/get_local_events.json",
                data: {
                    "lat": map.getCenter().lat,
                    "lng": map.getCenter().lng
                },
                success: create_events_on_map
            })
        }
    })
}

// Add script tag to the head
document.head.appendChild(script);

// Handle geolocation
function center_map(center) {
    /**
     * Handle centering the map and rendering local events from the database.
     * @param {json} center the point at which the map will be centered.
     */
    var new_center = new google.maps.LatLng(center.coords.latitude, center.coords.longitude);
    map.setCenter(new_center);
    map.setZoom(13);

    // Load local events onto the map
    $.ajax({
        type: "get",
        url: "/events/get_local_events.json",
        data: {
            "lat": center.coords.latitude,
            "lng": center.coords.longitude
        },
        success: create_events_on_map
    })
}

// Find out where the map needs to be focused
function get_center() {
    /**
     * Get the type of centering that the user has selected, request their location and pass the data to center_map
     */
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
        $.ajax({
            type: "get",
            url: "/events/event_details.json",
            data: {
                id: parseInt(focused_event)
            },
            success: (event) => {
                // If the event could be found, set the center on the map and zoom in to it.
                if (event.success) {
                    center_map({coords: {latitude: event.result.lat, longitude: event.result.lng}})
                }
                else {
                    center_map({coords: {latitude: 54.990446, longitude: -1.6128411}}); // render map with default position
                }
            }
        })
    }
}

function create_events_on_map(result) {
    /**
     * This renders each marker onto the map and ensures that there are no duplicates.
     * @param {json} result the event object which is being put onto the map.
     */
    // Define variables
    var event_list_element = $("#event-list");

    if (!result.success) {
        return;
    }

    result.events.forEach(event => {
        // Check if event is already on the map, pass if it is so that duplicate events are not displayed.
        if (ids_on_map.includes(event.id)) {
            return;
        }

        // Add markers to marker array
        var marker = new google.maps.Marker({
            position: {lat: event.lat, lng: event.lng},
            map: map,
            title: `${event.head}`,
            optimized: false
        });

        // Create HTML for the event
        var rendered_event = render_event(event);

        // Create info window with HTML content with information from the marker.
        var infowindow = new google.maps.InfoWindow({
            content: rendered_event
        })

        // Check if the user is in the event to add to the event list.
        if (event.attending.current_user_attending || event.created_by_user) {
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
        ids_on_map.push(event.id);

        // Open corrseponding marker if relevant
        if (event.id === parseInt(focused_event)) {
            infowindow.open(map, marker);
        }
    })
}

// Display error in geolocation
function show_error(error) {
    /**
     * Display if any error occurs in the geolocation to the user.
     * @param {error} error the error which has occured.
     */
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

// Warn the user about deleting an event
function warning_deletion(id) {
    /**
     * Warn the user that they are
     * @param {number} id the id of the event which is being destroyed.
     */
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
    /**
     * Create an HTML card representation of an event object.
     * @param {json} event the event which is being rendered into HTML.
     */
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
            <a class="btn btn-${event.attending.current_user_attending === false ? "primary" : "danger"}" onClick="handle_event(event, ${event.id})">
                ${event.attending.current_user_attending === false ? "Join event" : "Leave event"}
            </a>`
    }
    return `
    
    <div class="card">
        <div id="event-${event.id}" class="card-body">
            <h5 class="card-title">
                ${event.head}
            </h5>
            <p class="card-text">
                ${event.body}
            </p> 
            
            <p class="card-text">
                 <small>Current attendance: ${event.attending.users}/${event.capacity}</small> 
            </p>
            <p class="card-text">
                <small>${event.address}</small><br>
                <small>${event.time}</small>
            </p>            
            ${button}     
        </div>
    </div>
    `
}

// Handles the joining and leaving of events
function handle_event(event, id) {
    /**
     * Handle the joining and leaving of an event.
     * @param {event} event the event which is being joined by the user.
     * @param {number} id the id of the event which is being joined by the user.
     */
    $.post("/events/handle_event",  // url
        {"event_id": id},  // pass ID of the event by parsing through the ID of the elmnt
        function(data, status, jqXHR) {
            // Reload page to update the infowindows, focus on infowindow which was previously open
            window.location.href = data.redirect_to;
        }
    )
}