// Setup global variable preview_data_chart.
let preview_data_chart;
let preview_ctx;
let historical_data_chart;
let historical_ctx;

$(function() {
    // Destroy historical data tab if there is no data to display.
    $.ajax({
            url: "/calculator/historical_values.json",
            type: "get",
            success: (result) => {
                if (result.data.length === 0) {
                    $("#historical-data-tab").remove();
                }
            }
        })

    // get the range slider element.
    let electricity_factor_input = document.getElementById("clean_electricity_factor");

    // initialise tooltip for electricity factor input
    let electricity_factor_input_tooltip = new bootstrap.Tooltip(electricity_factor_input);

    // set up the default value
    electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");

    // Add event listener for clean electricity update
    electricity_factor_input.addEventListener("input", (_) => {
        electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");
        electricity_factor_input_tooltip.show();
    });

    // close the tooltip when the mouse leaves the slider
    electricity_factor_input.addEventListener("mouseleave", (_) => {
        electricity_factor_input_tooltip.hide();
    })


    // Add an event listener to create a chart when the preview tab is opened
    $("#preview-tab").on("shown.bs.tab", (event) => {
        // Set up variables for function
        var emission_values = {}
        const vehicle_type = $("#vehicle_type")

        // Select either the placeholder or value for each input in the page.
        document.querySelectorAll(".input-container input").forEach((element) => {
            emission_values[element.id] = element.value && !isNaN(element.value) ? element.value : element.placeholder;
        });

        // Ensure that a valid vehicle type is chosen, if somehow one is not chosen then default to other.
        emission_values["vehicle_type"] = vehicle_type.value ? vehicle_type.value : "Other";

        // Get the emission values from the costs given, and pass them to the chart.
        $.ajax({
            url: "/calculator/preview_values.json",
            type: "get",
            data: emission_values,
            success: create_preview

        })
    });

    // Add an event listener to create a chart when the historical data tab is opened
    $("#historical-data-tab").on("shown.bs.tab", (event) => {
        $.ajax({
            url: "/calculator/historical_values.json",
            type: "get",
            success: create_historical_chart
        })
    })

    // Add an event listener to focus alerts
    $("#submit").on("click", (event) => {
        show_toast_error("Missing data!", "There is some data missing, please check the form.", error_toast);
    });

    // Set up the "next" buttons to move the user to the next available tab
    $(".btn-next").click((event) => {
        $(".nav-item:has(a.active)").next("li").find("a").tab("show");
    });

    // Set up the "previous" buttons to move the user to the previous tab in the list.
    $(".btn-prev").click((event) => {
        $(".nav-item:has(a.active)").prev("li").find("a").tab("show");
    })

    // Set up toasts to confirm whether the data was saved or not
    var toast_element = $("#confirm-success");
    if (toast_element.length) {
        var toast = new bootstrap.Toast(toast_element);
        console.log(toast);
        toast.show();
    }

    var error_toast_element = $("#error-toast");
    var error_toast = new bootstrap.Toast(error_toast_element);

    // Setup charts
    preview_ctx = document.getElementById("preview-chart").getContext("2d");
    preview_data_chart = new Chart(preview_ctx);

    historical_ctx = document.getElementById("historical-data-chart").getContext("2d");
    historical_data_chart = new Chart(historical_ctx);

})

function create_preview(result) {
    // Destroy chart so that the new chart can be created in its place.
    preview_data_chart.destroy();

    const data = {
        labels: result.labels,
        datasets: [{
            labels: result.labels,
            data: result.data,
            // Colour scheme from coolors.io
            backgroundColor: [
                    'rgba(23, 48, 28, 0.2)',
                    'rgba(55, 147, 146, 0.2)',
                    'rgba(79, 176, 198, 0.2)',
                    'rgba(79, 134, 198, 0.2)',
                    'rgba(116, 79, 198, 0.2)'
                ],
                borderColor: [
                    'rgba(23, 48, 28, 1)',
                    'rgba(55, 147, 146, 1)',
                    'rgba(79, 176, 198, 1)',
                    'rgba(79, 134, 198, 1)',
                    'rgba(116, 79, 198, 1)'
                ],
                borderWidth: 1

        }]
    }

    const config = {
        type: "bar",
        data: data,
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Type of emission",
                        font: {
                            size: 14
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Emissions (kgCO2e/month)",
                        font: {
                            size: 14
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }

    // Create new chart with the data from the last page.
    preview_data_chart = new Chart(preview_ctx, config)
}

function create_historical_chart(result) {
    // Destroy old chart so that the new chart can be created,
    historical_data_chart.destroy();

    // Set up data parameter for chart given the result of the AJAX query
    const data = {
        labels: result.labels,
        datasets: [{
            label: "Your emissions",
            data: result.data,
            fill: true,
            borderColor: "rgb(55, 147, 146)",
            backgroundColor: "rgba(55, 147, 146, 0.2)",
            tension: 0.1
        }]
    }

    // Configure the visuals of the chart
    const config = {
        type: "line",
        data: data,
        options: {
            scales: {
                x: {
                    type: "time",
                    time: {
                        unit: "day"
                    },
                    title: {
                        display: true,
                        text: "Date Recorded",
                        font: {
                            size: 14
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Total Emissions (kgCO2e/month)",
                        font: {
                            size: 14
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }

    // Create new chart with the user's data
    historical_data_chart = new Chart(historical_ctx, config)
}

// Show error
function show_toast_error(head, body, toast) {
    document.getElementById("error-toast-header").innerHTML = head;
    document.getElementById("error-toast-body").innerHTML = body;

    toast.show();
}